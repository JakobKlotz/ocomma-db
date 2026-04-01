from datetime import datetime

import geopandas as gpd
import pandas as pd
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import WKTElement
from sqlalchemy.orm import Session

from db.models import Landslides


def find_duplicate(
    session: Session,
    landslide_datetime: datetime,
    landslide_geom: WKTElement,
    search_radius_meters: int = 500,
) -> Landslides | None:
    """
    Checks for existing landslides at the same date within a given radius.

    Args:
        session (Session): Active SQLAlchemy session used to execute the query.
        landslide_datetime (datetime): Datetime of the new landslide; only
            records with the same date are considered, time info is discarded.
        landslide_geom (WKTElement): WKTElement representing the new
            landslide's geometry (must be in the same spatial reference as
            stored geometries).
        search_radius_meters (int, optional): Radius in meters within which an
            existing landslide is considered a potential duplicate. Defaults to
            500.
    Returns:
        Landslides | None: The first matching Landslides instance if a
        potential duplicate is found; otherwise None.
    """
    return (
        session.query(Landslides)
        .filter(
            # strip the time information, to account for temporal uncertainty
            # duplicate check based on exact time info makes no sense
            Landslides.datetime == landslide_datetime.date(),
            ST_DWithin(
                Landslides.geometry, landslide_geom, search_radius_meters
            ),
        )
        .first()
    )


def is_duplicated(
    session: Session,
    landslide_datetime: datetime,
    landslide_geom: WKTElement,
    search_radius_meters: int = 500,
) -> bool:
    """
    Boolean check for an existing event at the same date within a given radius.

    Args:
        session (Session): Active SQLAlchemy session used to execute the query.
        landslide_datetime (datetime): Datetime of the new landslide; only
            records with the same date are considered, time info is discarded.
        landslide_geom (WKTElement): WKTElement representing the new
            landslide's geometry (must be in the same spatial reference as
            stored geometries).
        search_radius_meters (int, optional): Radius in meters within which an
            existing landslide is considered a potential duplicate. Defaults to
            500.
    Returns:
        bool: True if a potential duplicate is found; otherwise False.
    """
    result = find_duplicate(
        session,
        landslide_datetime,
        landslide_geom,
        search_radius_meters,
    )

    return result is not None


def flag_temporal_duplicates(
    *,
    data: gpd.GeoDataFrame,
    date_column: str,
    geometry_column: str,
    classification_column: str,
    days: int = 1,
    remove: bool = False,
    dataset_name: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Flags potential duplicates based on time proximity and identical geometry
    plus classification. Adds a column `duplicated` to the data.
    Used for a data preparation pipeline, no checks with the data base are
    performed.

    Args:
        data (gpd.GeoDataFrame): The geopandas data frame containing a date,
            classification and geometry column.
        date_column (str): Column name of the event date.
        geometry_column (str): Name of the geometry column.
        classification_column (str): Name of the column containing
            classifications.
        days (int): The time gap to flag potential duplicates.
        remove (bool): Whether to remove flagged entries. By default, they are
            kept.
        data_set_name(str | None): Optional data set name used for messages.
    Returns:
        gpd.GeoDataFrame: With an added boolean column `duplicated`.
    """
    # check if required columns exist
    required_cols = [date_column, geometry_column, classification_column]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_cols)}"
        )
    # get all duplicates (with keep=False)
    dup = data[
        data.duplicated(subset=[geometry_column], keep=False)
    ].sort_values(by=[geometry_column, date_column])
    # need a datetime
    dup[date_column] = pd.to_datetime(dup[date_column])
    # Calculate the time difference in days to the previous entry within
    # the same geometry group
    dup["time_diff_days"] = (
        # use to_wkt(), else groupby fails
        dup.groupby(dup[geometry_column].to_wkt())[date_column].diff()
    ).dt.days

    # Check if the classification is the same as the previous entry
    # in the group
    dup["same_classification"] = dup.groupby(dup[geometry_column].to_wkt())[
        classification_column
    ].transform(lambda x: x.eq(x.shift()))

    # Flag potential errors if the time gap is small (e.g., <= 1 day)
    # and classification is the same
    dup["duplicated"] = (dup["time_diff_days"] <= days) & (
        dup["same_classification"]
    )
    msg = (
        f"Found {dup['duplicated'].sum()} "
        f"likely duplicates with a {days}-day threshold. "
        "Flagged them for removal."
    )
    if dataset_name:
        msg = f"{dataset_name}: {msg}"

    print(msg)

    # map results back to original data (by default join on Index)
    data = data.join(dup["duplicated"])

    # use mask() instead of fillna() to avoid upcasting warning
    # convert NaN to False
    data["duplicated"] = data["duplicated"].mask(
        data["duplicated"].isna(), False
    )
    data["duplicated"] = data["duplicated"].astype(bool)

    if remove:
        data = data[~data["duplicated"]]
        msg = "Removed duplicates."
        if dataset_name:
            msg = f"{dataset_name}: {msg}"
        print(msg)

    return data
