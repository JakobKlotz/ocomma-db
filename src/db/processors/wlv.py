from pathlib import Path

import geopandas as gpd
import pandas as pd

from db.processors.base import BaseProcessor


class WLV(BaseProcessor):
    """Wildbach- und Lawinenverbauung data set."""

    def __init__(self, *, file_path: str | Path):
        self.EXPECTED_CATEGORIES = {
            "Wasser",
            "Lawine",
            "Rutschung",
            "Steinschlag",
        }
        self.EXPECTED_WATER_SUBCATEGORIES = {
            "Hochwasser",
            "Fluviatiler Feststofftransport",
            "Murgang",
            "Murartiger Feststofftransport",
            "Oberflächenabfluss",
        }
        super().__init__(
            file_path=file_path,
            dataset_name="Wildbach- und Lawinenverbauung",
            layer="WLV_Ereignisse_INSPIRE",
        )

    def _build_categories(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Extract the WLV categories from their description string."""
        # To prevent SettingWithCopy warning
        data = data.copy()
        # Extract broad classification
        data["category"] = data["nameOfEvent"].str.split(": ").str[0]

        # Sanity check
        unexpected_categories = set(data["category"].unique()).difference(
            self.EXPECTED_CATEGORIES
        )
        if unexpected_categories:
            raise ValueError(
                f"Unexpected categories found: {unexpected_categories}"
            )

        return data

    def _filter_sediment_transport_events(
        self, data: gpd.GeoDataFrame
    ) -> gpd.GeoDataFrame:
        """Get all sediment transports within the Water ('Wasser') category."""
        sediment_transport = data[data["category"] == "Wasser"].copy()

        # Example value for nameOfEvent:
        # "Wasser: Murgang - Intensität: extrem"  # noqa: ERA001
        sub = (
            sediment_transport["nameOfEvent"]
            .str.partition("-")[0]
            .str.partition(":")[2]
            .str.strip()
        )
        sediment_transport = sediment_transport.assign(subcategory=sub)

        unexpected_water_subcategories = set(
            sediment_transport["subcategory"].unique()
        ).difference(self.EXPECTED_WATER_SUBCATEGORIES)

        if unexpected_water_subcategories:
            raise ValueError(
                f"Unexpected subcategories found in Water entries: "
                f"{unexpected_water_subcategories}"
            )

        # Filter by Murgang, Murartiger Feststofftransport &
        # Fluviatiler Feststofftransport
        sediment_transport = sediment_transport[
            sediment_transport["subcategory"].isin(
                (
                    "Murgang",
                    "Murartiger Feststofftransport",
                    "Fluviatiler Feststofftransport",
                )
            )
        ]

        # Map GeoSphere classifications
        sediment_transport["classification"] = sediment_transport[
            "subcategory"
        ].map(
            {
                "Murgang": "gravity slide or flow",
                "Murartiger Feststofftransport": "gravity slide or flow",
                "Fluviatiler Feststofftransport": "mass movement (undefined type)",  # noqa: E501
            }
        )

    def clean(self):
        """Subset and clean the data."""
        # Work on a local copy
        data = self.data.copy()
        # Remove all "unbekannt" dates
        data = data[data["validFrom"] != "unbekannt"]
        # validFrom to date (coerce - historical dates are in there)
        data["validFrom"] = pd.to_datetime(data["validFrom"], errors="coerce")
        # Remove all entries with no date
        data = data[~data["validFrom"].isna()]

        # Get WLV categories
        data = self._build_categories(data)

        # Get all sediment transports
        sediment_transports = self._filter_sediment_transport_events(data)

        # Keep slides and rockfalls
        slides_rockfalls = data[
            data["category"].isin(("Rutschung", "Steinschlag"))
        ]
        # Map them to the GeoSphere classifications
        slides_rockfalls["classification"] = slides_rockfalls["category"].map(
            {
                "Rutschung": "gravity slide or flow",
                "Steinschlag": "rockfall",
            },
        )

        # Check each entry as a GeoSphere classification assigned
        if slides_rockfalls["classification"].isna().any():
            unmapped = slides_rockfalls.loc[
                slides_rockfalls["classification"].isna(), "category"
            ].unique()
            raise ValueError(f"Unmapped categories: {unmapped}")

        # Concat slides, rockfalls and sediment transports
        data = pd.concat(
            [slides_rockfalls, sediment_transports], axis=0, ignore_index=True
        )

        # Subset & assign as attribute
        self.data = data[
            [
                "classification",
                "validFrom",
                "geometry",
                "nameOfEvent",
            ]
        ]

    def import_to_db(self, file_dump: str | None = None):
        column_map = {
            "classification": "classification",
            "datetime": "validFrom",
            "original_classification": "nameOfEvent",
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
        self.import_to_db(file_dump=file_dump)

    def __call__(self, file_dump: str | None = None):
        """Allow instances to be called like functions."""
        self.run(file_dump=file_dump)
