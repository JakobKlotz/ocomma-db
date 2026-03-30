# Dedicated import script
from pathlib import Path

import typer

from db import WLV, GeoSphere, GlobalFatalLandslides, LandKaernten, Nasa
from db.utils import import_version

in_base_path, out_base_path = (
    Path("./data/raw"),
    Path("./data/processed-layers"),
)

processors = [
    # GeoSphere must be first, to populate the classification table
    (GeoSphere, "geosphere/geosphere.gpkg"),
    (
        GlobalFatalLandslides,
        "global-fatal-landslides/global-fatal-landslides.gpkg",
    ),
    (Nasa, "nasa-coolr/nasa-coolr-reports-point.gpkg"),
    (WLV, "wlv/wlv.gpkg"),
    (LandKaernten, "kaernten/kaernten.gpkg"),
]


def import_data(dump_layers: bool = False):
    """Import and process data files from various sources.

    Args:
        dump_layers (bool, optional): Dump each processed data source as an
            individual file. Defaults to False.
    """
    # Add the current package version to a dedicated table
    import_version()

    for proc_class, rel_path in processors:
        in_path = in_base_path / rel_path
        proc = proc_class(file_path=in_path)

        if dump_layers:
            out_path = out_base_path / rel_path

            # create parent folders if they don't exist
            out_path.parent.mkdir(parents=True, exist_ok=True)
            proc(file_dump=out_path)
        else:
            proc()


if __name__ == "__main__":
    typer.run(import_data)
