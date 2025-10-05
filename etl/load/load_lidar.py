from db.models.lidar import LidarObservation, LidarElevationRange, LidarTimeProfile, LidarRangeProfile, DimRange, DimTime
from db.models.sensor import SensorFile
from db.session import get_session
from datetime import datetime

class Load:
    def __init__(self, sensor_id, file_id):
        self.sensor_id = sensor_id
        self.file_id = file_id

    def load_lidars(self, data):
        """
        Loads LIDAR data into the database.
        :param data: Dictionary containing extracted and transformed data
                     (e.g., azimuth, elevation, time, range, cnr, radial_wind_speed)
        """
        with get_session() as session:
            # Create a new LidarObservation
            observation = LidarObservation(
                observ_datetime=datetime.now(),  # Current time; can use data['time'] if needed
                file_id=self.file_id
            )
            session.add(observation)
            session.flush()  # Flush to get observ_id before committing

            # Store DimRange (for range values)
            ranges = data.get('range', [])
            dim_ranges = []
            for range_val in ranges:
                dim_range = DimRange(value=int(range_val))
                session.add(dim_range)
                dim_ranges.append(dim_range)
            session.flush()  # Flush to get DimRange IDs

            # Store DimTime (for time values)
            times = data.get('time', [])
            dim_time = DimTime(
                observation_id=observation.id,
                time=times  # Assumes times are in datetime string format
            )
            session.add(dim_time)
            session.flush()  # Flush to get DimTime ID

            # Store LidarElevationRange (for elevation and related data)
            elevation_index = data.get('elevation_index', None)
            if elevation_index is not None:
                for i, dim_range in enumerate(dim_ranges):
                    # For each parameter (cnr, radial_wind_speed)
                    for param in ['cnr', 'radial_wind_speed']:
                        values = data.get(param, [])[elevation_index]  # Get values for specific elevation
                        if i < len(values):
                            elevation_range = LidarElevationRange(
                                observ_id=observation.id,
                                elevation_index=elevation_index,
                                range_id=dim_range.id,
                                parameter=param,
                                value=[str(values[i])]  # Convert to list of strings
                            )
                            session.add(elevation_range)

            # Store LidarTimeProfile (for time and related data)
            for i, time_val in enumerate(times):
                for param in ['cnr', 'radial_wind_speed']:
                    values = data.get(param, [])[i]  # Get values for specific time
                    time_profile = LidarTimeProfile(
                        observ_id=observation.id,
                        time_id=dim_time.id,
                        parameter=param,
                        value=[str(val) for val in values]  # Convert array to list of strings
                    )
                    session.add(time_profile)

            # Store LidarRangeProfile (for range and related data)
            for i, dim_range in enumerate(dim_ranges):
                for param in ['cnr', 'radial_wind_speed']:
                    values = [data.get(param, [])[j][i] for j in range(len(data.get(param, [])))]  # Values for specific range
                    range_profile = LidarRangeProfile(
                        observ_id=observation.id,
                        range_id=dim_range.id,
                        parameter=param,
                        value=[str(val) for val in values]  # Convert array to list of strings
                    )
                    session.add(range_profile)

            # Commit all changes
            session.commit()