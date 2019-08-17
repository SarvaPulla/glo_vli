import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Boolean, JSON
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry, WKTElement

from .app import GloVli as app

Base = declarative_base()


# SQLAlchemy ORM definition for the Points table
class Points(Base):
    """
    SQLAlchemy Layer Database table
    """
    __tablename__ = 'points'

    # Columns
    id = Column(Integer, primary_key=True)
    layer_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    year = Column(String)
    source = Column(String)
    elevation = Column(Float)
    county = Column(String)
    approved = Column(Boolean)
    meta_dict = Column(JSON)
    geometry = Column(Geometry('POINT', srid=4326))

    def __init__(self, layer_name, latitude, longitude, year, source, elevation, county, approved, meta_dict):
        """
        Constructor for a gage
        """

        self.layer_name = layer_name
        self.latitude = latitude
        self.longitude = longitude
        self.year = year
        self.source = source
        self.elevation = elevation
        self.county = county
        self.approved = approved
        self.meta_dict = meta_dict
        self.geometry = 'SRID=4326;POINT({0} {1})'.format(longitude, latitude)


# SQLAlchemy ORM definition for the Polygon table
class Polygons(Base):
    """
    SQLAlchemy Layer Database table
    """
    __tablename__ = 'polygons'

    # Columns
    id = Column(Integer, primary_key=True)
    layer_name = Column(String)
    year = Column(String)
    source = Column(String)
    county = Column(String)
    approved = Column(Boolean)
    meta_dict = Column(JSON)
    geometry = Column(Geometry('GEOMETRY', srid=4326))

    def __init__(self, layer_name, year, source, county, approved, geometry, meta_dict):
        """
        Constructor for a gage
        """

        self.layer_name = layer_name
        self.year = year
        self.source = source
        self.county = county
        self.approved = approved
        self.meta_dict = meta_dict
        self.geometry = 'SRID=4326;{0}'.format(geometry)


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
