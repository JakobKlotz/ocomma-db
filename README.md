![PostGIS](https://img.shields.io/badge/PostGIS-3840A0?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=white)
![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg?style=for-the-badge)

<div align="center">
  <img src="./docs/public/logo.png" alt="Header" width="250"/>
</div>

# oCoMMA | open Collection of Mass Movements in Austria

This project is dedicated to compiling and sharing **event data on mass 
movements across Austria**. The goal is to provide researchers with accessible 
information to accelerate their work.

By consolidating data from various national and international sources, we 
provide a PostGIS data base that can be easily setup using Docker.

> [!WARNING]
> This project is under active development. The data base schema and its 
> records are subject to change.

> [!TIP]
> For quick access without setting up the data base, a GeoPackage dump is 
> available. It contains a single table of the events and is located in the
> [`db-dump/`](./db-dump/) directory.

## Getting Started

To get your own instance of the data base up and running, please follow the 
setup instructions which use Docker for easy deployment.

Please refer to the
[**Quick Start Guide**](https://docs.geohub.at/guide/quick-start.html).

## Help

Documentation is available at [docs.geohub.at](https://docs.geohub.at).

## Data Sources

The inventory is built by incorporating data from the following sources:

- [GeoSphere](https://data.inspire.gv.at/d69f276f-24b4-4c16-aed7-349135921fa1):
    CC BY 4.0 ([link](https://creativecommons.org/licenses/by/4.0/))
- [Global Fatal Landslides](https://www.arcgis.com/home/item.html?id=7c9397b261aa436ebfbc41396bd96d06):
    Open Government License ([link](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/))
- [NASA COOLR](https://maps.nccs.nasa.gov/arcgis/apps/MapAndAppGallery/index.html?appid=574f26408683485799d02e857e5d9521): 
    Custom License ([link](./data/raw/nasa-coolr/LICENSE))
- [WLV](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527)
    No Limitations ([link](https://geometadatensuche.inspire.gv.at/metadatensuche/inspire/ger/catalog.search#/metadata/ccca05aa-728d-4218-9f4c-81286c537527))
- [Land Kärnten (Carinthia)](https://www.data.gv.at/datasets/70b85305-d3d1-487a-beff-75fa6d712c28?locale=de)
    CC BY 4.0 ([link](https://creativecommons.org/licenses/by/4.0/))

> [!NOTE]
> Each record in the data base is linked to its original source to ensure clear
> data provenance and proper attribution.

We are continuously working on adding more data sources to enhance the
comprehensiveness of the inventory.

## Classifications

The data base stores a classification for each event and includes multiple 
types of mass-movement phenomena. Types present are:

- gravity slide or flow
- rockfall
- mass movement (undefined)
- deep‑seated rock slope deformation
- collapse / sinkhole

## Contributing

Contributions are always welcome! 😊
Please refer to the [**Contribution Guidelines**](./CONTRIBUTING.md) for more
details on how to setup your development environment.

## Financial Support

This work has been funded by *Land Tirol*.

Project: *DigiSchutz*

<img src="./docs/public/land-tirol.png" width="100px">
