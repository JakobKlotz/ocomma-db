from datetime import date, datetime
from typing import List, Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from db.constants import TARGET_CRS


class Base(DeclarativeBase):
    pass


class Landslides(Base):
    __tablename__ = "landslides"

    id: Mapped[int] = mapped_column(primary_key=True)

    datetime: Mapped[datetime]
    report: Mapped[Optional[str]]
    report_source: Mapped[Optional[str]]
    report_url: Mapped[Optional[str]]
    original_classification: Mapped[str]

    # Point geom must always be present
    geometry: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=TARGET_CRS)
    )

    classification_id: Mapped[int] = mapped_column(
        ForeignKey("classification.id")
    )
    classification: Mapped["Classification"] = relationship(
        back_populates="landslides"
    )

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped["Sources"] = relationship(back_populates="landslides")

    # No UniqueConstraint - that's handled by the import logic
    # The combination of date & geom within a certain radius defines a unique
    # record


class Classification(Base):
    __tablename__ = "classification"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    landslides: Mapped[List["Landslides"]] = relationship(
        back_populates="classification"
    )


class Sources(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    downloaded: Mapped[date]
    modified: Mapped[Optional[date]]
    license: Mapped[str]
    url: Mapped[str]
    description: Mapped[Optional[str]]
    doi: Mapped[Optional[str]]

    landslides: Mapped[List["Landslides"]] = relationship(
        back_populates="source"
    )


class Version(Base):
    __tablename__ = "version"

    id: Mapped[int] = mapped_column(primary_key=True)
    imported_with_version: Mapped[str]
