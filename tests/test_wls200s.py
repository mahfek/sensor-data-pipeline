import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from etl.extract import NetCDFFile
from etl.transform import SensorWLS200sTransformer
from etl.load import load_lidar
from main import process_lidar_data, logger as main_logger

# Configure logging for tests (suppress output unless needed)
logging.getLogger().setLevel(logging.WARNING)

@pytest.fixture
def sample_raw_data():
    """
    Fixture for sample raw data from extraction (mimics NetCDF output).
    Shapes: azimuth/elevation/time: (236,), range: (120,), cnr/radial_wind_speed: (236, 120)
    """
    return {
        'azimuth': [1.0] * 236,
        'elevation': [89.0] * 236,  # All match ELEVATION_TARGET for easy testing
        'time': [i for i in range(236)],  # Unix timestamps
        'range': [j for j in range(120)],
        'cnr': [[float(i + j) for j in range(120)] for i in range(236)],
        'radial_wind_speed': [[float(i + j + 100) for j in range(120)] for i in range(236)]
    }

@pytest.fixture
def mock_netcdf_dataset():
    """
    Fixture to mock a NetCDF Dataset and its groups/variables.
    """
    mock_ds = MagicMock()
    mock_group = MagicMock()
    mock_ds.groups = {'group1': mock_group}
    mock_variables = {}
    for var_name in NetCDFFile.target_vars:
        mock_var = MagicMock()
        if var_name == 'range':
            mock_var[:] = [j for j in range(120)]
        elif var_name in ['azimuth', 'elevation', 'time']:
            mock_var[:] = [i for i in range(236)]
        else:  # cnr, radial_wind_speed
            mock_var[:] = [[float(i + j) for j in range(120)] for i in range(236)]
        mock_variables[var_name] = mock_var
        mock_group.variables[var_name] = mock_var
    mock_group.variables = mock_variables
    return mock_ds

@pytest.fixture
def mock_session():
    """
    Fixture to mock SQLAlchemy session for Load tests.
    """
    mock_session = Mock()
    mock_session.add = Mock()
    mock_session.flush = Mock()
    mock_session.commit = Mock()
    mock_session.rollback = Mock()
    mock_observation = Mock(id=1)
    mock_dim_range = Mock(id=1)
    mock_dim_time = Mock(id=1)
    mock_session.add.return_value = [mock_observation, mock_dim_range, mock_dim_time]
    return mock_session

@pytest.fixture
def mock_get_session(mock_session):
    """
    Fixture to patch get_session to return the mock session.
    """
    with patch('src.load.get_session', return_value=mock_session):
        yield mock_session

### Unit Tests for Extract (NetCDFFile)

def test_netcdf_file_read_success(sample_raw_data, mock_netcdf_dataset, caplog):
    """
    Test successful reading of NetCDF file with all target variables.
    """
    with patch('netCDF4.Dataset', return_value=mock_netcdf_dataset):
        extractor = NetCDFFile('mock_path.nc')
        data = extractor.read()
    
    # Verify data extraction
    assert set(data.keys()) == set(NetCDFFile.target_vars)
    assert len(data['azimuth']) == 236
    assert data['range'][0] == 0  # First range value
    assert data['cnr'][0][0] == 0.0  # First cnr value
    
    # Verify logging
    assert "Reading NetCDF file: mock_path.nc" in caplog.text
    assert "NetCDF file read successfully" in caplog.text

def test_netcdf_file_read_missing_vars(mock_netcdf_dataset, caplog):
    """
    Test handling of missing variables in NetCDF file.
    """
    mock_netcdf_dataset.groups['group1'].variables = {}  # Empty variables
    with patch('netCDF4.Dataset', return_value=mock_netcdf_dataset):
        extractor = NetCDFFile('mock_path.nc')
        data = extractor.read()
    
    # All data should be empty lists
    assert all(len(v) == 0 for v in data.values())
    assert "Missing variables in NetCDF file" in caplog.text  # WARNING log

def test_netcdf_file_read_error(caplog):
    """
    Test error handling for invalid file path.
    """
    with patch('netCDF4.Dataset', side_effect=FileNotFoundError("File not found")):
        extractor = NetCDFFile('invalid_path.nc')
        with pytest.raises(FileNotFoundError):
            extractor.read()
    
    assert "NetCDF file not found: invalid_path.nc" in caplog.text

### Unit Tests for Transform (SensorWLS200sTransformer)

def test_transformer_run_transformations_success(sample_raw_data, caplog):
    """
    Test successful transformation: elevation_index and time conversion.
    """
    transformer = SensorWLS200sTransformer(sample_raw_data)
    transformed_data = transformer.run_transformations()
    
    # Verify elevation_index (should be 0 since all elevations are 89.0)
    assert transformed_data['elevation_index'] == 0
    
    # Verify time conversion (first time should be 1970-01-01 00:00:01.000)
    assert transformed_data['time'][0] == '1970-01-01 00:00:00.000'
    
    # Verify logging
    assert "Starting data transformation" in caplog.text
    assert "Data transformation completed successfully" in caplog.text

def test_transformer_no_elevation_match(sample_raw_data, caplog):
    """
    Test transformation when no elevation matches ELEVATION_TARGET.
    """
    sample_raw_data['elevation'] = [90.0] * 236  # No match
    transformer = SensorWLS200sTransformer(sample_raw_data)
    transformed_data = transformer.run_transformations()
    
    assert transformed_data['elevation_index'] is None
    assert "No elevation index found matching target" in caplog.text  # WARNING log

def test_transformer_time_conversion_error(sample_raw_data):
    """
    Test error in time conversion (e.g., invalid timestamp).
    """
    sample_raw_data['time'] = [-1]  # Invalid timestamp
    transformer = SensorWLS200sTransformer(sample_raw_data)
    with pytest.raises(ValueError):  # fromtimestamp expects non-negative
        transformer.run_transformations()

### Unit Tests for Load (Load Class)

def test_load_lidars_success(sample_raw_data, mock_get_session, caplog):
    """
    Test successful loading of data into database.
    """
    loader = Load(sensor_id=1, file_id=1)
    loader.load_lidars(sample_raw_data)
    
    # Verify session interactions
    mock_session = mock_get_session
    assert mock_session.add.call_count > 3  # At least observation, ranges, time
    assert mock_session.flush.call_count == 3
    assert mock_session.commit.called
    assert mock_session.rollback.not_called
    
    # Verify logging
    assert "Starting to load LIDAR data into database" in caplog.text
    assert "LIDAR data successfully loaded into database" in caplog.text

def test_load_lidars_no_elevation_index(sample_raw_data, mock_get_session, caplog):
    """
    Test loading without elevation_index (should skip LidarElevationRange).
    """
    sample_raw_data.pop('elevation_index', None)
    loader = Load(sensor_id=1, file_id=1)
    loader.load_lidars(sample_raw_data)
    
    assert "No elevation_index provided, skipping LidarElevationRange" in caplog.text  # WARNING log

def test_load_lidars_database_error(sample_raw_data, mock_get_session, caplog):
    """
    Test error during database load (e.g., commit fails).
    """
    mock_get_session.commit.side_effect = Exception("DB Error")
    loader = Load(sensor_id=1, file_id=1)
    with pytest.raises(Exception):
        loader.load_lidars(sample_raw_data)
    
    assert mock_get_session.rollback.called
    assert "Error loading data into database" in caplog.text

### Integration Tests for Full Pipeline

@patch('src.main.logger')
def test_process_lidar_data_success(mock_logger, sample_raw_data, mock_netcdf_dataset, mock_get_session, caplog):
    """
    Test the full ETL pipeline with mocks.
    """
    # Patch extraction
    with patch('src.extract.NetCDFFile.read', return_value=sample_raw_data):
        # Patch transformation (assume it returns sample data with elevation_index)
        with patch('src.transform.SensorWLS200sTransformer.run_transformations', return_value={**sample_raw_data, 'elevation_index': 0}):
            process_lidar_data('mock_path.nc', sensor_id=1, file_id=1)
    
    # Verify pipeline logging
    assert "Starting LIDAR data processing" in caplog.text
    assert "LIDAR data processing completed successfully" in caplog.text
    
    # Verify mocks were called
    assert mock_get_session.commit.called

def test_process_lidar_data_error(caplog):
    """
    Test pipeline error handling (e.g., extraction fails).
    """
    with patch('src.extract.NetCDFFile.read', side_effect=Exception("Extraction Error")):
        with pytest.raises(Exception):
            process_lidar_data('mock_path.nc', sensor_id=1, file_id=1)
    
    assert "Error processing LIDAR data" in caplog.text

### Parameterized Tests for Edge Cases

@pytest.mark.parametrize("missing_key", ['azimuth', 'cnr'])
def test_pipeline_with_missing_data(missing_key, sample_raw_data, caplog):
    """
    Parameterized test for missing data keys in extraction.
    """
    del sample_raw_data[missing_key]
    with patch('src.extract.NetCDFFile.read', return_value=sample_raw_data):
        with patch('src.transform.SensorWLS200sTransformer.run_transformations', return_value=sample_raw_data):
            with pytest.raises(KeyError):  # Assume Load expects all keys
                with patch('src.load.Load.load_lidars'):
                    process_lidar_data('mock_path.nc', sensor_id=1, file_id=1)
    
    # Verify warning logs for missing data
    assert f"Missing variables" in caplog.text or "WARNING" in caplog.text