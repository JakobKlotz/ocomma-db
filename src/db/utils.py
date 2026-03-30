import json
from importlib.metadata import version
from pathlib import Path
from typing import Any, Dict

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Sources, Version
from db.settings import DB_URI


def convert_to_gpkg(
    *, input_file: str | Path, output_file: str | Path
) -> None:
    supported_formats = (".shp", ".geojson", ".gml")
    if Path(input_file).suffix not in supported_formats:
        raise ValueError(
            f"Input file is not supported."
            f" Supported formats are: {supported_formats}"
        )

    gpd.read_file(input_file).to_file(output_file, driver="GPKG")
    print("Converted!")


def dump_gpkg(
    data: gpd.GeoDataFrame,
    output_file: str | Path,
    overwrite: bool = True,
) -> None:
    """Dump the processed data to a file."""
    if Path(output_file).exists() and not overwrite:
        raise FileExistsError(
            f"File {output_file} already exists. Skipping dump. "
            f"Set overwrite=True to overwrite."
        )
    # delete an existing GeoPackage, overwriting leads to issues
    Path(output_file).unlink(missing_ok=True)
    data.to_file(output_file, driver="GPKG")


def create_db_session():
    engine = create_engine(DB_URI, echo=False, plugins=["geoalchemy2"])
    return sessionmaker(bind=engine)


def read_metadata(file_path: str | Path) -> dict[str, Any]:
    """Determine and read the metadata file name based on the given
    GeoPackage.

    Args:
        file_path (str | Path): Path to the GeoPackage.

    Returns:
        dict[str, Any]: The content of the metadata file.
    """
    file_path = Path(file_path)
    metadata_file = file_path.parent / f"{file_path.stem}.meta.json"

    if not metadata_file.exists():
        raise FileNotFoundError(
            f"The metadata file {metadata_file} does not "
            "exists. Alongside the GeoPackage a metadata file is needed."
        )

    with metadata_file.open() as f:
        return json.load(f)


def create_source_from_metadata(metadata: Dict[str, Any]) -> Sources:
    """Creates a Source object from a metadata dictionary."""
    # modified is nullable
    modified_date = metadata.get("modified")
    if modified_date:
        modified_date = pd.to_datetime(modified_date).date()

    return Sources(
        name=metadata["name"],
        downloaded=pd.to_datetime(metadata["downloaded"]).date(),
        modified=modified_date,
        license=metadata["license"],
        url=metadata["url"],
        description=metadata.get("description"),  # nullable
        doi=metadata.get("doi"),  # nullable
    )


def import_version() -> None:
    """Add the current package version to a dedicated table."""
    __version__ = version("landslides-db")

    Session = create_db_session()  # noqa: N806
    with Session() as session:
        session.add(Version(imported_with_version=__version__))
        session.commit()
