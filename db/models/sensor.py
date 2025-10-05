from sqlalchemy import Column, Integer, String, ForeignKey, relationship, DateTime, Boolean, Time, Date
from db.base import Base

class Sensor(Base):
    __tablename__ = 'sensors'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)
    description = Column(String(200))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    directory = Column(String(200))
    filetype = Column(Integer)
    isready = Column(Boolean, default=False)
    isstatic = Column(Boolean, default=False)
    responsible_id = Column(Integer, ForeignKey('responsibles.id'))
    responsible = relationship('Responsible', back_populates='sensors')
    files = relationship('SensorFile', cascade="all,delete", back_populates='sensor')
    group_id = Column(Integer)

class SensorFile(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    observation_time = Column(Integer)
    func_name = Column(String(50))
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    sensor = relationship('Sensor', back_populates='files')
    lidar_observations = relationship('LidarObservation', cascade="all,delete", back_populates='file')
    #obs_file = relationship('ObservationFile', cascade="all,delete", back_populates='file')

class Responsible(Base):
    __tablename__ = 'responsibles'

    id = Column(Integer, primary_key=True)
    email = Column(String(60), index=True, unique=True)
    username = Column(String(60), index=True, unique=True)
    first_name = Column(String(60), index=True)
    last_name = Column(String(60), index=True)
    password_hash = Column(String(128))
    sensors = relationship('Sensor', back_populates='responsible')
   
