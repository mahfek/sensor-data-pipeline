# LIDAR Data ETL Pipeline

This project implements an Extract, Transform, Load (ETL) pipeline for processing LIDAR data from NetCDF files, transforming it, and storing it in a relational database. The pipeline handles LIDAR observations with variables such as `azimuth`, `elevation`, `time`, `range`, `cnr`, and `radial_wind_speed`, using a robust database schema.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The LIDAR ETL pipeline extracts data from NetCDF files, transforms it (e.g., converting timestamps, identifying maximum elevation), and loads it into a relational database using SQLAlchemy. The pipeline is modular, with separate classes for extraction (`NetCDFFile`), transformation (`SensorWLS200sTransformer`), and loading (`Load`). It includes comprehensive logging and a test suite for reliability.

## Features

- **Extraction**: Reads LIDAR data (`azimuth`, `elevation`, `time`, `range`, `cnr`, `radial_wind_speed`) from NetCDF files.
- **Transformation**: Converts timestamps to datetime strings and identifies the maximum elevation index (e.g., 89 degrees).
- **Loading**: Stores data in database tables: `LidarObservation`, `LidarElevationRange`, `LidarTimeProfile`, `LidarRangeProfile`, `DimRange`, and `DimTime`.
- **Configuration**: Supports settings via `config/settings.py` and `config/config.yaml`.
- **Logging**: Detailed logs to console and file for debugging and monitoring.
- **Testing**: Unit and integration tests using `pytest`, covering happy paths and edge cases.

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt` and `requirements-test.txt` (for testing)
- A relational database (e.g., PostgreSQL, SQLite) with SQLAlchemy support
- NetCDF files with LIDAR data (optional for testing, as tests use mocks)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/sensor-data-pipeline.git
   cd sensor-data-pipeline
   ```

2. **Set up a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install runtime dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Example `requirements.txt`:
   ```text
   netCDF4==1.6.5
   pandas==2.2.2
   sqlalchemy==2.0.30
   pyyaml==6.0.1
   ```

4. **Install test dependencies** (optional, for testing):

   ```bash
   pip install -r requirements-test.txt
   ```

   Example `requirements-test.txt`:
   ```text
   pytest==7.4.0
   pytest-mock==3.11.1
   pytest-cov==4.1.0
   ```

5. **Set up the database**:

   - Configure the database connection in `config/settings.py` or `config/config.yaml`.
   - Create tables using the models in `db/models/lidar.py` and `db/models/sensor.py`:

     ```python
     from db.models.lidar import Base
     from sqlalchemy import create_engine
     engine = create_engine('sqlite:///lidar.db')  # Or your database URL
     Base.metadata.create_all(engine)
     ```

## Configuration

The pipeline uses configuration files in the `config/` directory:

- **`config/settings.py`**: Python module for settings like database URL and logging level.

  Example:
  ```python
  DATABASE_URL = "sqlite:///lidar.db"
  LOG_LEVEL = "INFO"
  NETCDF_DIR = "path/to/netcdf/files"
  ```

- **`config/config.yaml`**: YAML file for additional settings.

  Example:
  ```yaml
  database:
    url: "sqlite:///lidar.db"
  logging:
    level: "INFO"
  netcdf:
    directory: "path/to/netcdf/files"
  ```

Update these files with your database URL and NetCDF file paths before running the pipeline.

## Usage

1. **Prepare a NetCDF file**:
   Ensure you have a NetCDF file with variables: `azimuth`, `elevation`, `time`, `range`, `cnr`, `radial_wind_speed`. Expected shapes:
   - `azimuth`, `elevation`, `time`: `(236,)`
   - `range`: `(120,)`
   - `cnr`, `radial_wind_speed`: `(236, 120)`

2. **Ensure database records**:
   - Add a `sensor` record to the `sensors` table with a valid `sensor_id`.
   - Add a `file` record to the `files` table with a valid `file_id`, linked to the `sensor_id`.

3. **Run the ETL pipeline**:
   Update `main.py` to load configurations and run the pipeline:

   ```python
   from main import process_lidar_data
   from config.settings import NETCDF_DIR
   import os

   file_path = os.path.join(NETCDF_DIR, "data.nc")
   sensor_id = 1
   file_id = 1
   process_lidar_data(file_path, sensor_id, file_id)
   ```

   Run from the command line:
   ```bash
   python main.py
   ```

4. **Output**:
   - Data is extracted, transformed, and loaded into the database.
   - Logs are written to the console and a file (e.g., `lidar_pipeline_20251005_1423.log`).

## Testing

The project includes a test suite in `tests/test_wls200s.py`, covering unit and integration tests.

1. **Run tests**:

   ```bash
   pytest tests/ -v
   ```

2. **Run tests with coverage**:

   ```bash
   pytest tests/ --cov=etl --cov-report=html
   ```

   Open `htmlcov/index.html` to view the coverage report.

3. **Test details**:
   - **Unit Tests**: Test methods in `NetCDFFile`, `SensorWLS200sTransformer`, and `Load`.
   - **Integration Tests**: Test the full `process_lidar_data` pipeline with mocked data.
   - **Edge Cases**: Test missing variables, invalid files, and database errors.
   - **Dependencies**: Tests use mocks for `netCDF4.Dataset` and SQLAlchemy sessions.

## Project Structure

```plaintext
sensor-data-pipeline/
├── config/
│   ├── settings.py              # Python configuration settings
│   ├── config.yaml              # YAML configuration file
├── db/
│   ├── models/
│   │   ├── __init__.py          # Makes models a package
│   │   ├── lidar.py             # SQLAlchemy models for LIDAR data
│   │   ├── sensor.py            # SQLAlchemy models for sensor data
│   ├── session.py               # Database session management
│   ├── base.py                  # SQLAlchemy base class
├── etl/
│   ├── extract/
│   │   ├── base_file.py         # Base class for file extraction
│   │   ├── NetCDFFile.py        # Extracts data from NetCDF files
│   ├── load/
│   │   ├── load_lidar.py        # Loads transformed data into the database
│   ├── transform/
│   │   ├── base_transformer.py  # Base class for transformations
│   │   ├── sensor_WLS200s_transformer.py  # Transforms LIDAR data
├── tests/
│   ├── test_wls200s.py          # Unit and integration tests
├── requirements.txt             # Runtime dependencies
├── requirements-test.txt        # Test dependencies
├── README.md                   # This file
├── main.py                     # Main script to run the ETL pipeline
```

## Logging

- Logs are output to console and timestamped files (e.g., `lidar_pipeline_20251005_1423.log`).
- Log levels: `INFO` for progress, `DEBUG` for details, `WARNING` for non-critical issues, `ERROR` for failures.
- Example log entry:
  ```plaintext
  2025-10-05 14:23:00,123 [INFO] main: Starting LIDAR data processing for file: data.nc
  ```

To enable `DEBUG` logs, update `config/settings.py` or `config/config.yaml`:
```python
LOG_LEVEL = "DEBUG"
```
```yaml
logging:
  level: "DEBUG"
```

## Contributing

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Follow PEP 8 coding standards.
3. Add tests in `tests/test_wls200s.py`.
4. Ensure tests pass and coverage is above 80%:
   ```bash
   pytest tests/ --cov=etl --cov-fail-under=80
   ```
5. Submit a pull request with a clear description of changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
