LIDAR Data ETL Pipeline
This project implements an Extract, Transform, Load (ETL) pipeline for processing LIDAR data from NetCDF files, transforming it, and storing it in a relational database. The pipeline is designed to handle LIDAR observations with variables such as azimuth, elevation, time, range, cnr, and radial_wind_speed, and supports a robust database schema for storing observations, profiles, and dimensions.
Table of Contents

Project Overview
Features
Requirements
Installation
Configuration
Usage
Testing
Project Structure
Logging
Contributing
License

Project Overview
The LIDAR ETL pipeline processes NetCDF files containing LIDAR data, performs transformations (e.g., finding the maximum elevation index, converting timestamps), and loads the data into a relational database using SQLAlchemy. The pipeline is modular, with separate classes for extraction (NetCDFFile), transformation (SensorWLS200sTransformer), and loading (Load). It includes comprehensive logging and a test suite for reliability.
Features

Extraction: Reads LIDAR data (e.g., azimuth, elevation, time, range, cnr, radial_wind_speed) from NetCDF files.
Transformation: Converts timestamps to datetime strings and identifies the maximum elevation index matching a target (e.g., 89 degrees).
Loading: Stores data in a database with tables for observations (LidarObservation), profiles (LidarElevationRange, LidarTimeProfile, LidarRangeProfile), and dimensions (DimRange, DimTime).
Configuration: Supports configuration via config/settings.py and config/config.yaml.
Logging: Detailed logs for debugging and monitoring, output to both console and file.
Testing: Unit and integration tests using pytest, covering happy paths, edge cases, and errors.

Requirements

Python 3.9+
Dependencies listed in requirements.txt and requirements-test.txt (for testing)
A relational database (e.g., PostgreSQL, SQLite) with SQLAlchemy support
NetCDF files containing LIDAR data (optional for testing, as tests use mocks)

Installation

Clone the repository:
git clone <repository-url>
cd sensor-data-pipeline


Set up a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install runtime dependencies:
pip install -r requirements.txt

Example requirements.txt:
netCDF4==1.6.5
pandas==2.2.2
sqlalchemy==2.0.30
pyyaml==6.0.1


Install test dependencies (optional, for running tests):
pip install -r requirements-test.txt

Example requirements-test.txt:
pytest==7.4.0
pytest-mock==3.11.1
pytest-cov==4.1.0


Set up the database:

Configure the database connection in config/settings.py or config/config.yaml (e.g., set the SQLAlchemy database URL).
Create the required tables using the models in db/models/lidar.py and db/models/sensor.py. For example:from db.models.lidar import Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///lidar.db')  # Or your database URL
Base.metadata.create_all(engine)





Configuration
The pipeline uses configuration files in the config/ directory:

config/settings.py: Python module for configuration settings (e.g., database URL, logging level).Example:DATABASE_URL = "sqlite:///lidar.db"
LOG_LEVEL = "INFO"
NETCDF_DIR = "path/to/netcdf/files"


config/config.yaml: YAML file for additional settings (e.g., file paths, database credentials).Example:database:
  url: "sqlite:///lidar.db"
logging:
  level: "INFO"
netcdf:
  directory: "path/to/netcdf/files"



Update these files with your database URL and file paths before running the pipeline.
Usage

Prepare a NetCDF file:Ensure you have a NetCDF file containing LIDAR data with variables: azimuth, elevation, time, range, cnr, radial_wind_speed. Expected data shapes:

azimuth, elevation, time: (236,)
range: (120,)
cnr, radial_wind_speed: (236, 120)


Ensure database records:

Add a sensor record to the sensors table with a valid sensor_id.
Add a file record to the files table with a valid file_id, linked to the sensor_id.


Run the ETL pipeline:Execute the pipeline using main.py. Update main.py to load configurations from config/settings.py or config/config.yaml. Example usage:
from main import process_lidar_data
from config.settings import NETCDF_DIR
import os

file_path = os.path.join(NETCDF_DIR, "data.nc")
sensor_id = 1
file_id = 1
process_lidar_data(file_path, sensor_id, file_id)

Run from the command line:
python main.py


Output:

Data is extracted, transformed, and loaded into the database.
Logs are written to the console and a file (e.g., lidar_pipeline_20251005_1345.log).



Testing
The project includes a comprehensive test suite in tests/test_wls200s.py, covering unit and integration tests for the ETL pipeline.

Run tests:
pytest tests/ -v


Run tests with coverage:
pytest tests/ --cov=etl --cov-report=html

Open htmlcov/index.html to view the coverage report.

Test details:

Unit Tests: Test individual methods in NetCDFFile, SensorWLS200sTransformer, and Load (e.g., file reading, transformation logic, database loading).
Integration Tests: Test the full ETL pipeline (process_lidar_data) with mocked data.
Edge Cases: Test missing variables, invalid files, and database errors.
Dependencies: Tests use mocks for netCDF4.Dataset and SQLAlchemy sessions, so no real files or database are needed.



Project Structure
sensor-data-pipeline/
├── config/
│   ├── settings.py       # Python configuration settings
│   ├── config.yaml       # YAML configuration file
├── db/
│   ├── models/
│   │   ├── __init__.py   # Makes models a package
│   │   ├── lidar.py      # SQLAlchemy models for LIDAR data
│   │   ├── sensor.py     # SQLAlchemy models for sensor data
│   ├── session.py        # Database session management
│   ├── base.py           # SQLAlchemy base class
├── etl/
│   ├── extract/
│   │   ├── base_file.py  # Base class for file extraction
│   │   ├── NetCDFFile.py # Extracts data from NetCDF files
│   ├── load/
│   │   ├── load_lidar.py # Loads transformed data into the database
│   ├── transform/
│   │   ├── base_transformer.py      # Base class for transformations
│   │   ├── sensor_WLS200s_transformer.py  # Transforms LIDAR data
├── tests/
│   ├── test_wls200s.py   # Unit and integration tests
├── requirements.txt      # Runtime dependencies
├── requirements-test.txt  # Test dependencies
├── README.md             # This file
├── main.py               # Main script to run the ETL pipeline

Logging

The pipeline uses Python’s logging module to log to both console and file.
Log levels: INFO for progress, DEBUG for detailed steps, WARNING for non-critical issues, ERROR for failures.
Log files are timestamped (e.g., lidar_pipeline_20251005_1345.log).
Example log entry:2025-10-05 13:45:00,123 [INFO] main: Starting LIDAR data processing for file: data.nc



To enable DEBUG logs, update config/settings.py or config/config.yaml:
LOG_LEVEL = "DEBUG"

or
logging:
  level: "DEBUG"

Contributing

Fork the repository and create a feature branch.
Follow coding standards (e.g., PEP 8).
Add tests for new features in tests/test_wls200s.py.
Ensure tests pass and coverage remains above 80%:pytest tests/ --cov=etl --cov-fail-under=80


Submit a pull request with a clear description of changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.