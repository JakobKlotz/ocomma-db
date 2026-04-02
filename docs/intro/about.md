---
outline: deep
---

# About

This project builds a reproducible, harmonized inventory for mass movement data
in Austria. By curating multiple open data sets, a single PostGIS data base is
provided.

::: warning

This project is under active development. The data base schema and its records
are subject to change.

:::

## Project Goal

Austria has various data sets on mass movements, but they are often maintained
in different formats and silos by various institutes and regional authorities.
This fragmentation makes comprehensive, large-scale analysis difficult.

This project aims to solve that problem by providing a single, harmonized and 
reproducible data base of mass movement events in Austria, specifically for 
the research community.

## Scope & Limitations

This data set is a research-oriented tool. It is designed to support 
exploratory analysis, statistical modeling and the development of new methods.

### What to Expect

- **Harmonized data:** Historic mass movement events aggregated from multiple 
  public sources.
- **Attributes:** Records include event date, harmonized event classifications
  and point geometry. Where available, metadata is provided.
- **Duplicate handling**: To reduce redundancy across sources, an automated 
  process identifies potential duplicates using a 500-meter radius and same-day
  event date.
- **Provenance:** Each record links back to its original source, ensuring 
  traceability and proper attribution.
- **Two data formats:** The data is provided as a ready-to-use GeoPackage for 
  quick exploration and a PostGIS data base for reproducible ingestion and 
  advanced workflows.
- **Quick Start:** This project serves as a practical resource for researchers
  who need a consolidated data set for analysis, modeling or method testing.
- **Transparency:** Due to the open-source nature of the project, code for data
  ingestion, harmonization and de-duplication is comprehensible and documented 
  which enables inspection, reproducibility and reuse.

### Important Limitations

- **Not comprehensive:** Events can be missing! This inventory is a best-effort
  aggregation of known public data sources and most likely will never be 
  exhaustive. 
- **Not error-free:** This inventory inherits all inconsistencies, inaccuracies
  and omissions from its sources. Be aware, that data quality can verify.
- **Positional uncertainty:** Point geometries can be imprecise. Positional 
  uncertainty is generally not reported by the sources and can not be reliably 
  estimated. Where reported, imprecision can range significantly, GeoSphere 
  Austria, for example, documents a positional uncertainty of 50–2000 m.
  In general, do not use this database for high-accuracy applications.
- **Imperfect duplicate detection:** The automated check helps reduce 
  redundancy but is not exhaustive. Some duplicates may remain, especially 
  considering imprecision regarding point geometries.
- **Not for real-time use:** Updates depend on upstream sources. Data refreshes
  are irregular and not guaranteed, new event data can lag or be incomplete.
  Check the source metadata for recency.

## Data Coverage

The data base encompasses different mass movement phenomena, including:

- Gravity slide or flow
- Rockfall
- Mass movement (undefined)
- Deep‑seated rock slope deformation
- Collapse / sinkhole

## Getting Started

### Quick Access (GeoPackage)

For users who want to quickly explore the data without setting up a data base,
we provide a ready-to-use GeoPackage file. This is ideal for:

- Quick data exploration and visualization
- One-time analyses or prototyping
- Users without data base management experience

::: tip

The GeoPackage dump contains a single table with all events and is located in
the repository's
[`db-dump/`](https://github.com/JakobKlotz/landslides-db/tree/main/db-dump)
directory. Simply download and open it in your favorite GIS application.

:::

### PostGIS Setup

For a proper workflow with reproducible data pipelines, advanced querying and
integration into existing infrastructure, we recommend deploying the full
PostGIS data base using Docker.

To set up the data base, please refer to the
[Quick Start Guide](../guide/quick-start).

## Data Sources

The inventory incorporates data from the following sources:

| Source Name                                                                                                                             |                                                                      License                                                                       | Last Updated |
|-----------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------:|:------------:|
| [GeoSphere Austria](https://data.inspire.gv.at/d69f276f-24b4-4c16-aed7-349135921fa1)                                                            |                                             [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)                                              | 6 Feb 2025  |
| [Global Fatal Landslides](https://www.arcgis.com/home/item.html?id=7c9397b261aa436ebfbc41396bd96d06)                                    |                       [Open Government License](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/)                        | 9 Sept 2019  |
| [NASA COOLR](https://maps.nccs.nasa.gov/arcgis/apps/MapAndAppGallery/index.html?appid=574f26408683485799d02e857e5d9521)                 |                                                       Custom License (provided in the repo)                                                        |   unknown    |
| [WLV](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527) | [No Limitations](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527) | 20 Jun 2025  |
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
