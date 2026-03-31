import json
from pathlib import Path

import pandas as pd

from db.duplicates import flag_temporal_duplicates
from db.processors.base import BaseProcessor


class LandKaernten(BaseProcessor):
    """Land Kärnten data set."""

    def __init__(self, file_path: str | Path):
        # determine and read landslide mapping file based on given GeoPackage
        landslides_mapping_file = (
            Path(file_path).parent / "kaernten-landslide-mapping.json"
        )

        with landslides_mapping_file.open("r") as f:
            self.landslides_mapping = json.load(f)

        super().__init__(file_path=file_path, dataset_name="Land Kärnten")

    def clean(self):
        """Subset and clean the data."""
        # Check if all entries have geometries
        if self.data["geometry"].isna().any():
            raise RuntimeError(
                f"Not all geometries in data set {self.dataset_name} given"
            )

        # TODO rewrite
        self.data["validFrom"] = pd.to_datetime(
            self.data["validFrom"], errors="coerce"
        ).dt.date
        # remove hidden missing classifications
        self.data = self.data[self.data["QualitativeValue"] != "keine Angabe"]

        # subset data
        self.data = self.data[
            ["validFrom", "QualitativeValue", "TypeOfHazard", "geometry"]
        ]
        # remove entries with missing values among any attribute
        self.data = self.data.dropna().sort_values(by=["validFrom"])

        # remove duplicates with same date and exact same geometry
        self.data = self.data.drop_duplicates(
            subset=["validFrom", "geometry"], keep="last"
        )

    def classify(self):
        base_data = self.data.copy()

        base_url = (
            "https://inspire.ec.europa.eu/codelist/NaturalHazardCategoryValue/"
        )

        # drop all snow avalanche entries
        base_data = base_data[
            base_data["TypeOfHazard"] != f"{base_url}snowAvalanche"
        ]

        # quick sanity check
        if set(base_data["TypeOfHazard"].unique()) != set(
            (f"{base_url}flood", f"{base_url}landslide")
        ):
            raise ValueError(
                f"Expected two remaining hazard types in the "
                f"{self.dataset_name} data"
            )
        # get flood types
        floods = base_data[base_data["TypeOfHazard"] == f"{base_url}flood"]

        # TypeOfHazard field can contain multiple,
        # semicolon/comma-separated hazard labels. Classification is based
        # upon the first label! Only rows where the first listed hazard
        # is "Murgang" are kept.

        # E.g., "starker fluv. Feststofftransport; Murgang" -> ignore
        # "Murgang, mehrmals beob. (30 - 100 Jahre)" -> keep
        floods = floods[floods["QualitativeValue"].str.startswith("Murgang")]

        # these entries are classified as gravity slide or flow
        floods["classification"] = "gravity slide or flow"

        # "landslide" is remaining
        landslides = base_data[
            base_data["TypeOfHazard"] == f"{base_url}landslide"
        ].copy()

        # again, classification is mapped on the first hazard label
        # (assigned by Land Kärnten)
        landslides["first_classification_label"] = (
            # split on whitespace
            landslides["QualitativeValue"]
            .str.partition(" ")[0]
            .str.replace(";", "")
        )
        landslides["classification"] = landslides[
            "first_classification_label"
        ].map(self.landslides_mapping)

        # check if all entries have a classification assigned
        remaining = landslides[landslides["classification"].isna()]

        if not remaining.empty:
            raise RuntimeError(
                f"{self.dataset_name}: Encountered following hazard "
                f"labels which could not be assigned to any classification: "
                f"{remaining['first_classification_label'].unique()}"
            )
        landslides = landslides.drop(columns=["first_classification_label"])

        # merge both
        data = pd.concat([floods, landslides], axis=0, ignore_index=True)

        # assign
        self.data = data

    def remove_temporal_duplicates(self):
        # look for any temporal duplicates and remove them
        self.data = flag_temporal_duplicates(
            data=self.data,
            date_column="validFrom",
            geometry_column="geometry",
            classification_column="classification",
            days=1,  # analogue to GeoSphere data processing
            remove=True,
            dataset_name=self.dataset_name,
        )

    def import_to_db(self, file_dump: str | None = None):
        """Import the data into a PostGIS database."""
        column_map = {
            "classification": "classification",
            "date": "validFrom",
            # import original hazard labels
            "original_classification": "QualitativeValue",
        }
        self._import_to_db(
            data_to_import=self.data,
            column_map=column_map,
            file_dump=file_dump,
            check_duplicates=True,
        )

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self.clean()
        self.classify()
        # remove temporal duplicates based on new mapped classification
        self.remove_temporal_duplicates()
        self.import_to_db(file_dump=file_dump)

    def __call__(self, file_dump: str | None = None):
        """Allow instances to be called like functions."""
        self.run(file_dump=file_dump)
