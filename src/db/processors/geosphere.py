from pathlib import Path

import pandas as pd

from db.duplicates import flag_temporal_duplicates
from db.models import Classification
from db.processors.base import BaseProcessor
from db.utils import create_db_session


class GeoSphere(BaseProcessor):
    """GeoSphere Austria data."""

    def __init__(self, *, file_path: str | Path):
        super().__init__(file_path=file_path, dataset_name="GeoSphere")

    def _check_geom(self):
        """Check if geometries are given."""
        if any(self.data.geometry.isna()):
            raise ValueError("Some geometries are null.")

    def subset(self):
        """Subset the data to only include necessary columns."""
        necessary_columns = [
            "inspireId_localId",
            "validFrom",
            "description",
            "geometry",
        ]
        # all other columns have no real meaning, often unpopulated or
        # a constant
        self.data = self.data[necessary_columns]
        # description is a classification
        # (rockfall, gravity slide or flow, ...)
        self.data = self.data.rename(columns={"description": "classification"})

    def clean(self):
        """Clean the data."""
        # validFrom to date (coerce - historical dates are in there)
        self.data["validFrom"] = pd.to_datetime(
            self.data["validFrom"], errors="coerce"
        ).dt.date
        # Remove all entries with no date
        self.data = self.data[~self.data["validFrom"].isna()]

        self.data = self.data.sort_values(by="validFrom", ascending=False)
        # remove all *obvious* duplicates, keep most recent entry
        self.data = self.data.drop_duplicates(
            subset=["validFrom", "classification", "geometry"], keep="last"
        )

    def remove_temporal_duplicates(self):
        # For GeoSphere, we only remove likely errors, no check for duplicates
        # against the DB as it's considered our base dataset.
        self.data = flag_temporal_duplicates(
            data=self.data,
            date_column="validFrom",
            geometry_column="geometry",
            classification_column="classification",
            days=1,
            remove=True,
            dataset_name=self.dataset_name,
        )

    def populate_classification_table(self):
        """Populate the classification table with unique landslide
        classifications."""
        Session = create_db_session()  # noqa: N806
        with Session() as session:
            unique_classifications = set(
                sorted(self.data["classification"].unique())
            )
            expected_classifications = set(
                [
                    "collapse, sinkhole",
                    "deep seated rock slope deformation",
                    "gravity slide or flow",
                    "mass movement (undefined type)",
                    "rockfall",
                ]
            )
            if not unique_classifications == expected_classifications:
                raise RuntimeError(
                    "Did not find all expected classifications: "
                    f"{expected_classifications}"
                )

            if not unique_classifications:
                raise RuntimeError("No classifications found!")

            new_classifications = [
                Classification(name=classification)
                for classification in unique_classifications
            ]
            session.add_all(new_classifications)
            session.commit()
            print(f"Added {len(unique_classifications)} classifications.")

    def import_to_db(self, file_dump: str | None = None):
        """Import the data into a PostGIS database."""
        data_to_import = self.data.copy()

        column_map = {
            "classification": "classification",
            "date": "validFrom",
            # report fields are None (no appropriate field)
            # generally, from each source the original classifications are
            # preserved
            "original_classification": "classification",
        }
        self._import_to_db(
            data_to_import=data_to_import,
            column_map=column_map,
            file_dump=file_dump,
            check_duplicates=False,
        )

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self._check_geom()
        self.subset()
        self.clean()
        self.remove_temporal_duplicates()
        self.populate_classification_table()
        self.import_to_db(file_dump=file_dump)

    def __call__(self, file_dump: str | None = None):
        """Allow instances to be called like functions."""
        self.run(file_dump=file_dump)
