---
outline: deep
---

# Schema

To work with the data base, it helps to understand its public schema. The 
`landslides` data base follows a simple layout. A screenshot is shown below: 

<figure>
  <img
    src="/schema.png" alt="Landslides View in the API preview"
    loading="lazy" width="100%" style="border-radius: 10px;"
  >
</figure>

## Table Description

| Table             | Description                                                                                    |
|-------------------|------------------------------------------------------------------------------------------------|
| `alembic_version` | Single row containing the Alembic migration version.                                           |
| `spatial_ref_sys` | Coordinate reference systems (CRS) available.                                                  |
| `landslides`      | Mass movement event records (e.g., rockfalls, debris flows, ...) with date and point geometry. |
| `classification`  | Lookup table with classification labels used by the `landslides` table.                        |
| `sources`         | Metadata about original data sources linked to event records.                                  |
| `version`         | Stores the Python Package version used to import the data.                                     |

### alembic_version

Migration of the data base is done with the Python package 
[`alembic`](https://alembic.sqlalchemy.org/en/latest/). "Alembic provides 
for the creation, management, and invocation of change management scripts for a
relational database, using SQLAlchemy as the underlying engine."[^1]

[^1]: See the Alembic [tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html#tutorial)

The alembic_version table is automatically added by the tool, it serves as 
information.

::: info

Alembic is used to auto-generate the schema from the models defined with
`sqlalchemy`. The alembic migration scripts are in `alembic/versions/`.

:::

### spatial_ref_sys

The spatial_ref_sys table is included in every PostGIS data base and stores
coordinate reference system (CRS) definitions (SRID, proj4/WKT text). In 
PostGIS each geometry is linked to an SRID. For example, the landslides table
contains events including point geometries (longitude, latitude) that are 
linked to an SRID. The spatial_ref_sys table is used to interpret that SRID.

### landslides

The landslides table contains the mass movement events, including a event date
with time (`datetime`) and point geometry (`geom`). All records are linked to
source and classification via the `source_id` and `classification_id`
respectively. Find the first two records below:

| id | datetime            | report | report_source | report_url | original_classification | geometry      | classification_id | source_id |
|----|---------------------|--------|---------------|------------|-------------------------|---------------|-------------------|-----------|
| 1  | 2024-11-01 00:00:00 | NULL   | NULL          | NULL       | rockfall                | 0101000020... | 5                 | 1         |
| 2  | 2024-10-22 00:00:00 | NULL   | NULL          | NULL       | rockfall                | 0101000020... | 5                 | 1         |

::: details

The SQL query for above table:

```sql
SELECT *
FROM public.landslides
LIMIT 2;
```

:::

#### Column Overview

Some fields are nullable whereas other must always be present, see below table
for an overview.

| Field                   | Nullable | Description                                                                           |
|-------------------------|----------|---------------------------------------------------------------------------------------|
| datetime                | No       | Event datetime (assumed Austrian local time, CET/CEST;no timezone conversion applied) |
| report                  | Yes      | Optional report describing the event                                                  |
| report_source           | Yes      | Optional name of the report source                                                    |
| report_url              | Yes      | Optional URL linking to the original report/resource                                  |
| original_classification | No       | Original classification provided by the source                                        |
| geometry                | No       | Point geometry in **EPSG:32632**                                                      |
| classification_id       | No       | Foreign key to the `classification` table                                             |
| source_id               | No       | Foreign key to the `sources` table                                                    |

::: info

Geometries are all in [EPSG:32632](https://epsg.io/32632)!

:::

In short, `datetime`, `geometry`, `original_classification`, `source_id` and 
`classification_id` are always present.

::: info

By default, the point geometry `geometry` is returned as hex-encoded binary.
To get the geometry as string, use the `ST_AsText` function. For example:

```sql
SELECT id, datetime, ST_AsText(geometry) AS wkt
FROM public.landslides
LIMIT 2;
```

| id | datetime            | wkt                                 |
|----|---------------------|-------------------------------------|
| 1  | 2024-11-01 00:00:00 | POINT(748676.21304 5272749.179051)  |
| 2  | 2024-10-22 00:00:00 | POINT(641802.697946 5196727.447737) |

:::

::: tip

With the `ST_AsEWKT` function, the SRID can be included as well.

```sql
SELECT id, ST_AsEWKT(geometry) AS ewkt
FROM public.landslides
LIMIT 2;
```

| id | wkt                                            |
|----|------------------------------------------------|
| 1  | SRID=32632;POINT(748676.21304 5272749.179051)  |
| 2  | SRID=32632;POINT(641802.697946 5196727.447737) |

:::

### classification

This table stores the classification labels referenced by the `landslides`
table (via `classification_id`). The available values are listed below:

| name                               |
|------------------------------------|
| rockfall                           |
| collapse, sinkhole                 |
| mass movement (undefined type)     |
| gravity slide or flow              |
| deep seated rock slope deformation |

Each record is classified into one of these categories. The categories itself
were derived from the GeoSphere data set (see 
[Data Sources](../intro/about#data-sources) for more info).

::: details

The corresponding query to the above table:

```sql
SELECT name
FROM public.classification;
```

:::

### sources

The sources table stores metadata for each original data set referenced by 
`landslides`. It captures provenance, access details and licensing to ensure 
traceability and reproducibility. The `id` column is referenced by 
`landslides.source_id`.

| Field       | Nullable | Description                                             |
|-------------|----------|---------------------------------------------------------|
| name        | No       | Source name (data set title or institution)             |
| downloaded  | No       | Date the data set was retrieved                         |
| modified    | Yes      | Optional: last modified date from the provider          |
| license     | No       | License type of the source                              |
| url         | No       | Link to the original data set or metadata page          |
| description | Yes      | Optional: Short, human‑readable summary of the data set |
| doi         | Yes      | Optional: persistent identifier (DOI)                   |

## Views

### landslides_view

For convenience, a view, called `landslides_view`, is available that 
*encompasses information from all three tables* (`landslides`, 
`classification`, `sources`). The view provides information on all mass 
movement phenomena in the data base including their source information and 
classification.

::: tip

If you are looking for an entry point to the data base, use this view.

Retrieve everything with:

```sql
SELECT *
FROM landslides_view;
```

:::

::: info

As an optional (Docker) service a API is provided which could serve as an entry
point for further applications. The API serves data from this 
`landslides_view`. See the [Quick Start](../guide/quick-start.md#optional-api) 
section for more details.

:::
