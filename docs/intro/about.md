---
outline: deep
---

# About

Austria has various inventories on mass movements, but they are often maintained
in different formats and silos across institutes and regional authorities.
This fragmentation makes large-scale analysis difficult.

This project addresses that by providing a single, harmonized and reproducible
PostGIS database of mass movement events in Austria, built from multiple open
data sets and designed as a research-oriented tool.

::: warning

This project is under active development. The database schema and its records
are subject to change.

:::

## Limitations

The database is a best-effort aggregation of open data sets. Be aware of
the following limitations before using it.

::: danger

- **Not comprehensive:** Events can be missing. This inventory is an 
  aggregation of known public data sources and will never be exhaustive.
- **Not error-free:** This database inherits all inconsistencies, inaccuracies
  and omissions from its sources. Data quality can vary.
  - **Temporal uncertainty:** Every record carries a timestamp, but most sources
    only report the event date, in those cases the time is set to midnight.
    Temporal uncertainty is generally not reported by the sources. Hence, treat
    all timestamps as approximate and account for this uncertainty in any 
    time-sensitive analysis.
  - **Positional uncertainty:** Most records have no positional uncertainty
    reported at all. GeoSphere Austria, the primary base data set, is an
    exception and documents an uncertainty of 50–2000 m.
- **Imperfect duplicate detection:** Duplicates are identified using a 2 km
  spatial radius and same-day event date (ignoring the timestamp). The radius 
  is driven by GeoSphere Austria's maximum positional uncertainty. Considering 
  the temporal and spatial uncertainty, duplicates may remain.
- **Not for real-time use:** Updates depend on upstream sources. Data refreshes
  are irregular and not guaranteed; new event data can lag or be incomplete.

:::

## Data Coverage

The database encompasses different mass movement phenomena, including:

- Gravity slide or flow
- Rockfall
- Mass movement (undefined)
- Deep‑seated rock slope deformation
- Collapse / sinkhole

## Getting Started

### Quick Access

For users who want to quickly explore the data without setting up a database,
we provide a ready-to-use GeoPackage file. This is ideal for:

- Quick data exploration and visualization
- One-time analyses or prototyping
- Users without database management experience

::: tip

The GeoPackage dump contains a single table with all events and is located in
the repository's
[`db-dump/`](https://github.com/JakobKlotz/ocomma-db/tree/main/db-dump)
directory. Simply download and open it in your favorite GIS application.

:::

### PostGIS Setup

For a proper workflow with reproducible data pipelines, advanced querying and
integration into existing infrastructure, we recommend deploying the full
PostGIS database using Docker.

To set up the database, please refer to the
[Quick Start Guide](../guide/quick-start).

## Data Sources

The inventory incorporates data from the following sources:

| Source Name                                                                                                                             |                                                                      License                                                                       | Last Updated |
|-----------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------:|:------------:|
| [GeoSphere Austria](https://data.inspire.gv.at/d69f276f-24b4-4c16-aed7-349135921fa1)                                                            |                                             [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                              | 25 Nov 2025  |
| [Global Fatal Landslides](https://www.arcgis.com/home/item.html?id=7c9397b261aa436ebfbc41396bd96d06)                                    |                       [Open Government License](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/)                        | 9 Sept 2019  |
| [NASA COOLR](https://maps.nccs.nasa.gov/arcgis/apps/MapAndAppGallery/index.html?appid=574f26408683485799d02e857e5d9521)                 |                                                       Custom License (provided in the repo)                                                        |   unknown    |
| [WLV](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527) | [No Limitations](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527) | 19 Feb 2026  |
| [Land Kärnten (Carinthia)](https://www.data.gv.at/datasets/70b85305-d3d1-487a-beff-75fa6d712c28?locale=de)                              |                                             [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                              |  6 Dec 2025  |

Each data source listed above contributes records to the inventory while
maintaining full traceability to the original source. The *Last Updated* column
indicates the most recent modification date for each source, helping users 
assess data recency.

Additional sources are evaluated continuously to expand the inventory's 
coverage.

## Attributions

Website icon by <a target="_blank" href="https://icons8.com">Icons8</a>

## License

This project is licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Financial Support

This work has been funded by *Land Tirol*.

Project: *DigiSchutz*

<img src="/land-tirol.png" width="100px">
