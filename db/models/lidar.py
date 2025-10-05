from sqlalchemy import Column, Integer, String, ForeignKey, relationship, DateTime, ARRAY
from db.base import Base

class LidarObservation(Base):
    __tablename__ = 'lidar_observations'
    id = Column(Integer, primary_key=True)
    observ_datetime = Column(DateTime)
    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship('SensorFile', back_populates='lidar_observations')
    elevation_ranges = relationship('LidarElevationRange', cascade="all,delete", back_populates='observation')
    time_profiles = relationship('LidarTimeProfile', cascade="all,delete", back_populates='observation')
    range_profiles = relationship('LidarRangeProfile', cascade="all,delete", back_populates='observation')


class LidarElevationRange(Base):
    __tablename__ = 'lidar_elevation_range'
    id = Column(Integer, primary_key=True)
    observ_id = Column(Integer, ForeignKey('lidar_observations.id'))
    observation = relationship('LidarObservation', back_populates='elevation_ranges')
    elevation_index = Column(Integer)
    range_id = Column(Integer, ForeignKey('dim_range.id'))
    range = relationship('DimRange', back_populates='lidar_elevation_ranges')
    parameter = Column(String)  # "CNR", "Radial Wind Speed", ...
    value = Column(ARRAY(String, dimensions=1))


class LidarTimeProfile(Base):
    __tablename__ = 'lidar_time_profile'
    id = Column(Integer, primary_key=True)
    observ_id = Column(Integer, ForeignKey('lidar_observations.id'))
    observation = relationship('LidarObservation', back_populates='time_profiles')
    time_id = Column(Integer, ForeignKey('dim_time.id'))
    time = relationship('DimTime', back_populates='lidar_time_profiles')
    parameter = Column(String)  # "CNR", "Radial Wind Speed", ...
    value = Column(ARRAY(String, dimensions=1))


class LidarRangeProfile(Base):
    __tablename__ = 'lidar_range_profile'
    id = Column(Integer, primary_key=True)
    observ_id = Column(Integer, ForeignKey('lidar_observations.id'))
    observation = relationship('LidarObservation', back_populates='range_profiles')
    range_id = Column(Integer, ForeignKey('dim_range.id'))
    range = relationship('DimRange', back_populates='lidar_range_profiles')
    parameter = Column(String)  # "CNR", "Radial Wind Speed", ...
    value = Column(ARRAY(String, dimensions=1))

class DimRange(Base):
    __tablename__ = 'dim_range'

    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    lidar_range_profiles = relationship('LidarRangeProfile', cascade="all,delete", back_populates='range')
    lidar_elevation_ranges = relationship('LidarElevationRange', cascade="all,delete", back_populates='range')


class DimTime(Base):
    __tablename__ = 'dim_time'
    id = Column(Integer, primary_key=True)
    observation_id = Column(Integer, ForeignKey('lidar_observations.id'))
    observation = relationship('LidarObservation', back_populates='time_profiles')
    time = Column(ARRAY(DateTime, dimensions=1))
    lidar_time_profiles = relationship('LidarTimeProfile', cascade="all,delete", back_populates='time')


