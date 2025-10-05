import logging
import os
from datetime import datetime
from etl.extract import NetCDFFile
from etl.transform import SensorWLS200sTransformer
from etl.load import load_lidar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(f'lidar_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_lidar_data(file_path, sensor_id, file_id):
    """
    Process LIDAR data from a NetCDF file, transform it, and load it into the database.
    :param file_path: Path to the NetCDF file
    :param sensor_id: ID of the sensor in the database
    :param file_id: ID of the file in the database
    """
    logger.info(f"Starting LIDAR data processing for file: {file_path}, sensor_id: {sensor_id}, file_id: {file_id}")

    try:
        # Step 1: Extract data
        logger.debug("Initializing NetCDFFile for extraction")
        extractor = NetCDFFile(file_path)
        raw_data = extractor.read()
        logger.info(f"Extracted data with keys: {list(raw_data.keys())}")

        # Step 2: Transform data
        logger.debug("Initializing SensorWLS200sTransformer for transformation")
        transformer = SensorWLS200sTransformer(raw_data)
        transformed_data = transformer.run_transformations()
        logger.info("Data transformation completed")

        # Step 3: Load data
        logger.debug("Initializing Load for database storage")
        loader = Load(sensor_id=sensor_id, file_id=file_id)
        loader.load_lidars(transformed_data)
        logger.info("Data successfully loaded into database")

        logger.info("LIDAR data processing completed successfully")
    except Exception as e:
        logger.error(f"Error processing LIDAR data: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    file_path = "path/to/your/data.nc"
    sensor_id = 1
    file_id = 1
    process_lidar_data(file_path, sensor_id, file_id)