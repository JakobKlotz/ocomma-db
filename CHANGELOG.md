## Version: `0.1.5`

### 🌟 Features

- Plotting script to generate overview plots of the events (e.g., map,
    events per year and ratio of classifications)
- Within the documentation the most recent modification for each data source is
    given, for easier assessment of data recency.

### 🛠 Dev changes

- Updated `alembic` (encountered an issue with the `script_location` from 
    `alembic.ini`)
- Added a `Version` table to save the package version used to import the data

## Version: `0.1.4`

### 🌟 Features

- Added new data:
    - Implemented preprocessing and importing steps for the Land Kärnten 
        (Carinthia) data set which adds more than 2600 observations.
    - `db/processors/kaernten.py` adds a corresponding `LandKaernten`
        processor class, to clean, classify and import the data.

### 🛠 Dev changes

- Refactoring: Flag temporal duplicates:
    The function `flag_temporal_duplicates()` flags potential 
    duplicates based on time proximity and identical geometry plus
    classification. The functionality was refactored and added to 
    `db.duplicates.py` for reuse.

## Version: `0.1.3`

### 🌟 Features

- Improvements to the documentation:
    - Section on "Scope & Limitations" to clarify the expectations for this 
        project.
    - Guide to configure the radius during the de-duplication check and how to
        change the default PostGIS port.
- The data base (`db` Docker service) now restarts by default.

### 🛠 Dev changes

- Documentation:
    - Fixed the prev / next links (a missing leading slash for the file paths
    led to issues).
    - Adjusted the folder structure to the defined sidebar (in `config.mjs`).
    - Used the latest stable `vitepress` version.

### 🐞 Fixes

- The WLV DOI was previously stored as an empty string; it is now saved as 
    null.

## Version: `0.1.2`

### 🌟 Features

- Imported 7,070 additional events from the WLV dataset. Records in the WLV 
    "water" category were reviewed and the subcategories "Murgang" and 
    "Murartiger Feststofftransport" were mapped to the debris-flow class and 
    imported accordingly. Thanks to @willevk!
- Detailed description of the data base schema and its tables including 
    examples. All housed in the documentation's schema section.

### 🛠 Dev changes

- Two additional workflows:
    - `build.yml`: Checks if the VitePress page can be built. Aims to prevent 
    merges into main with a broken documentation site.
    - `ruff.yml`: Runs the `ruff` linter and formatter (without fixing them)
    to prevent pushing code that does not fulfill the enabled `ruff` rules.

## Version: `0.1.1`

### 🌟 Features

- For quick access without setting up the data base, a GeoPackage dump is 
available in [`db-dump/`](./db-dump)
- Individual processed source files are now stored in a new 
`data/processed-layers` directory to avoid confusion with the main dump.
- Added a documentation site with:
    - About: project overview and goals
    - Quick Start: step-by-step usage guide
    - Configuration: options and examples (coming soon)

Provides a single, user-friendly reference to replace the README files.

### 🛠 Dev changes

- Refactored the project into an installable Python package. This allows for 
consistent and simplified module imports for the data import logic across the 
project.
- Incorporated the `TARGET_CRS` re-projection in the `BaseProcessor` class 
for a unified approach.
- `typer` was added as dependency to convert `scripts/import.py` to a simple
CLI
    - A `--dump-layers` flag has been added to the import CLI. This flag must
    now be used to explicitly generate the individual processed files.

## Version: `0.1.0`

First instance of the data base with records from four different sources.

### 🌟 Features

- Unified records of landslides and other mass movements in Austria
- Docker services to setup the data base and a dedicated API 
(which is optional) but can serve as an entrypoint for further applications
- Automatic duplicate check during import, based on event dates and a 500-meter
radius
- Each record is linked to its original source for data provenance
- Unified event classifications such as gravity slides or rockfalls
