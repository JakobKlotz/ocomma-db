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

    def _filter_debris_flows(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Get all debris flows within the Water ('Wasser') category."""
        water = data[data["category"] == "Wasser"].copy()

        # filter by subcategories Murgang & Murartiger Feststofftransport
        # Example value for nameOfEvent:
        # "Wasser: Murgang - Intensität: extrem"  # noqa: ERA001
        sub = (
            water["nameOfEvent"]
            .str.partition("-")[0]
            .str.partition(":")[2]
            .str.strip()
        )
        water = water.assign(subcategory=sub)

        unexpected_water_subcategories = set(
            water["subcategory"].unique()
        ).difference(self.EXPECTED_WATER_SUBCATEGORIES)

        if unexpected_water_subcategories:
            raise ValueError(
                f"Unexpected subcategories found in Water entries: "
                f"{unexpected_water_subcategories}"
            )

        # Filter by Murgang & Murartiger Feststofftransport
        return water[
            water["subcategory"].isin(
                ("Murgang", "Murartiger Feststofftransport")
            )
        ]

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

        # Get all debris flows
        debris_flows = self._filter_debris_flows(data)

        # Keep slides and rockfalls
        data = data[data["category"].isin(("Rutschung", "Steinschlag"))]

        # Append debris flows
        data = pd.concat([data, debris_flows], axis=0, ignore_index=True)

        # Map them to the GeoSphere classifications
        data["classification"] = data["category"].replace(
            {
                "Rutschung": "gravity slide or flow",
                "Steinschlag": "rockfall",
                # 'Wasser' has only the subcategories
                # Murgang & Murartiger Feststofftransport remaining
                "Wasser": "gravity slide or flow",
            }
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
