import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from db.processors.base import BaseProcessor


class GlobalFatalLandslides(BaseProcessor):
    """Global Fatal Landslides data set."""

    def __init__(self, *, file_path: str | Path):
        super().__init__(
            file_path=file_path, dataset_name="Global Fatal Landslides"
        )

    def subset(self):
        """Subset the data"""
        self.data = self.data.query("Country == 'Austria'")
        # remove potential newlines
        self.data["Report_1"] = self.data["Report_1"].str.replace("\n", " ")
        # Select necessary columns
        self.data = self.data[
            [
                "Date",
                "Report_1",
                "Source_1",
                "geometry",
                "Trigger",
            ]
        ]
        # Combination represents the original classification, to be imported
        self.data["original_classification"] = (
            self.data["Report_1"] + " | Trigger: " + self.data["Trigger"]
        )
        self.data = self.data.sort_values("Date").reset_index(drop=True)

    def clean(self):
        """Clean the data."""
        # Manually assign classification (landslide, rockfall)
        warnings.warn(
            message="Caution: Landslide classifications are assigned to the "
            "data. If you have changed the source data of the global fatal "
            "landslide database check the results",
            stacklevel=2,
        )

        # Remove Z coordinate from points
        self.data["geometry"] = self.data["geometry"].force_2d()

        # Combination of date & geometry is unique
        # Those two events were rockfalls, see their description
        rockfall_events = gpd.GeoDataFrame(
            data={
                "Date": pd.to_datetime(
                    ["2005-08-23 00:00:00", "2008-03-01 00:00:00"]
                ),
                "geometry": [
                    Point(651192.3868625985, 5212271.343543028),
                    Point(807247.7813673844, 5256032.494610518),
                ],
                "classification_override": ["rockfall", "rockfall"],
            },
            crs=self.data.crs,
        )

        # Perform a spatial join (to account for slight floating point
        # differences in the geometries)
        self.data = gpd.sjoin_nearest(
            self.data,
            rockfall_events,
            how="left",
            max_distance=1,
        )
        # A spatial match is only valid if the dates also match.
        # Invalidate matches where the dates are different.
        date_mismatch = self.data["Date_left"] != self.data["Date_right"]
        self.data.loc[date_mismatch, "classification_override"] = None

        # Default event is mapped to "mass movement (undefined type)" stemming
        # from the GeoSphere data set
        self.data["classification"] = self.data[
            "classification_override"
        ].fillna("mass movement (undefined type)")
        # Drop helper columns from the join
        self.data = self.data.drop(
            columns=["classification_override", "index_right", "Date_right"]
        ).rename(columns={"Date_left": "date"})

    def import_to_db(self, file_dump: str | None = None):
        """Import to PostGIS database."""
        column_map = {
            "classification": "classification",
            "datetime": "date",
            "description": "description",
            "report": "Report_1",
            "report_url": "Source_1",
            # original classification is part of `Report_1` and `Trigger`
            "original_classification": "original_classification",
        }
        self._import_to_db(
            data_to_import=self.data,
            column_map=column_map,
            file_dump=file_dump,
            check_duplicates=True,
        )

    def run(self, file_dump: str | None = None):
        """Run all processing steps."""
        self.subset()
        self.clean()
        self.import_to_db(file_dump=file_dump)

    def __call__(self, file_dump: str | None = None):
        """Allow instances to be called like functions."""
        self.run(file_dump=file_dump)
