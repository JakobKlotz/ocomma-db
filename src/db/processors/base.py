import warnings
from abc import ABC, abstractmethod
from pathlib import Path

import geopandas as gpd
from sqlalchemy.dialects.postgresql import insert

from db.constants import AUSTRIA, TARGET_CRS
from db.duplicates import is_duplicated
from db.models import Classification, Landslides
from db.utils import (
    create_db_session,
    create_source_from_metadata,
    dump_gpkg,
    read_metadata,
)


class BaseProcessor(ABC):
    """Abstract base class for data processors."""

    def __init__(self, *, file_path: str | Path, dataset_name: str, **kwargs):
        self.target_crs = TARGET_CRS
        self.austria = AUSTRIA
        self.file_path = file_path
        self.dataset_name = dataset_name
        self.kwargs = kwargs
        self.data = self.read_file()
        self.metadata = read_metadata(file_path=self.file_path)

    def read_file(self) -> gpd.GeoDataFrame:
        # Ensure that points are within Austria
        # CRS mis-match between the two files is handled internally by
        # geopandas
        return gpd.read_file(
            self.file_path, mask=self.austria, **self.kwargs
        ).to_crs(crs=self.target_crs)

    @abstractmethod
    def run(self):
        """Run all processing steps."""
        raise NotImplementedError

    @abstractmethod
    def __call__(self):
        """Allow instances to be called like functions."""
        raise NotImplementedError

    def _import_to_db(
        self,
        data_to_import: gpd.GeoDataFrame,
        column_map: dict,
        file_dump: str | None = None,
        check_duplicates: bool = True,
    ):
        """
        Import cleaned data into the PostGIS database.

        Args:
            data_to_import (gpd.GeoDataFrame): Data to import.
            column_map (dict): Dictionary mapping DataFrame columns
                to database columns. Expected keys: 'date', 'classification',
                'report', 'report_source', 'report_url'.
            file_dump (str | None): Optional path to dump the data for
                inspection.
            check_duplicates (bool): If True, check for duplicates against
                the database.
        """
        if not data_to_import.crs == self.target_crs:
            raise ValueError(
                f"CRS mismatch. Data is in {data_to_import.crs}."
                f"Expected {self.target_crs}"
            )
        Session = create_db_session()  # noqa: N806
        with Session() as session:
            # The source object needs to be added to the session to get an ID
            # before we can reference it.
            source = create_source_from_metadata(self.metadata)
            session.add(source)
            session.flush()

            # Fetch all classifications to map names to IDs
            classifications = session.query(Classification).all()
            classification_map = {c.name: c.id for c in classifications}

            import_data = data_to_import.copy()
            # see https://geoalchemy-2.readthedocs.io/en/latest/orm_tutorial.html#create-an-instance-of-the-mapped-class
            import_data["geom_wkt"] = (
                f"SRID={self.target_crs};" + import_data["geometry"].to_wkt()
            )

            if check_duplicates:
                # Check all events, and flag potential duplicates
                import_data["duplicated"] = import_data.apply(
                    lambda row: is_duplicated(
                        session=session,
                        landslide_date=row[column_map["date"]].date()
                        if hasattr(row[column_map["date"]], "date")
                        else row[column_map["date"]],
                        landslide_geom=row["geom_wkt"],
                    ),
                    axis=1,
                )
                n_duplicates = import_data["duplicated"].sum()
                if n_duplicates > 0:
                    warnings.warn(
                        f"Found {n_duplicates} duplicate/s in the "
                        f"{self.dataset_name} data.",
                        stacklevel=2,
                    )
                if file_dump:
                    dump_gpkg(import_data, output_file=file_dump)
                # Remove the duplicates
                import_data = import_data[~import_data["duplicated"]]

            elif file_dump:
                dump_gpkg(import_data, output_file=file_dump)

            if import_data.empty:
                print(f"No new records to import for {self.dataset_name}.")
                return

            # must be a list of dicts for the insert statement
            landslide_records = import_data.apply(
                lambda row: {
                    "date": row[column_map["date"]].date()
                    if hasattr(row[column_map["date"]], "date")
                    else row[column_map["date"]],
                    # all nullable
                    "report": row.get(column_map.get("report")),
                    "report_source": row.get(column_map.get("report_source")),
                    "report_url": row.get(column_map.get("report_url")),
                    "geom": row["geom_wkt"],
                    "classification_id": classification_map.get(
                        row.get(column_map.get("classification"))
                    ),
                    "source_id": source.id,
                },
                axis=1,
            ).tolist()

            stmt = insert(Landslides).values(landslide_records)

            try:
                session.execute(stmt)
                session.commit()
                print(
                    f"Successfully imported {len(landslide_records)} "
                    f"{self.dataset_name} records."
                )
            except Exception as e:
                session.rollback()
                print(f"An error occurred during import: {e}")
