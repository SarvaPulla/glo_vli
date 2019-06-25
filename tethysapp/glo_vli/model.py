import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry, WKTElement

from .app import GloVli as app

Base = declarative_base()


# SQLAlchemy ORM definition for the dams table
class Layer(Base):
    """
    SQLAlchemy Layer Database table
    """
    __tablename__ = 'layers'

    # Columns
    id = Column(Integer, primary_key=True)
    layer_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    year = Column(String)
    source = Column(String)
    elevation = Column(Float)
    approved = Column(Boolean)
    geometry = Column(Geometry('POINT', srid=4326))

    def __init__(self, layer_name, latitude, longitude, year, source, elevation, approved):
        """
        Constructor for a gage
        """

        self.layer_name = layer_name
        self.latitude = latitude
        self.longitude = longitude
        self.year = year
        self.source = source
        self.elevation = elevation
        self.approved = approved
        self.geometry = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)

def init_layer_db(engine, first_time):
    """
    Initializer for the primary database.
    """
    # Create all the tables
    Base.metadata.create_all(engine)

    # Add data
    if first_time:
        # Make session
        Session = sessionmaker(bind=engine)
        session = Session()
        session.commit()
        session.close()
