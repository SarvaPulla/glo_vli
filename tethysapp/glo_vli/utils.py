import pandas as pd
import geopandas as gpd
import os
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import *
from tethysapp.glo_vli.app import GloVli as app
from tethysapp.glo_vli.model import Points, Polygons
from geoserver.catalog import Catalog
from owslib.wfs import WebFeatureService
from owslib.etree import etree
from owslib.fes import *
import requests
import json
from .config import geoserver_rest_url, geoserver_wfs_url


def user_permission_test(user):
    return user.is_superuser or user.is_staff


def add_points():
    data_dir = '/home/dev/appsdev/glo_vli/tethysapp/glo_vli/public/data/'
    layers = os.listdir(data_dir)
    # Creating SQLAlchemy's engine to use
    # engine = create_engine('postgresql://tethys_super:pass@142.93.88.165:5435/layers')
    for layer in layers:
        l_files = os.listdir(os.path.join(data_dir, layer))
        for f in l_files:
            if f.endswith('.shp'):
                f_path = os.path.join(data_dir, layer, f)
                gdf = gpd.read_file(f_path)
                Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
                session = Session()

                for index, row in gdf.iterrows():

                    if 'LowWaterCrossings_Int' in f:
                        latitude = row.get('LAT')
                        longitude = row.get('LONG')
                        source = row.get('SOURCE')
                        county = row.get('CNTY_NM')
                        table_name = 'LowWaterCrossings'

                    if 'HighWaterMarks_Int' in f:
                        latitude = row.get('Lat')
                        longitude = row.get('Long')
                        source = row.get('Source')
                        county = row.get('CNTY_NM')
                        table_name = 'HighWaterMarks'

                    point = Points(table_name, latitude, longitude, 2019, source, 10, county, approved=True)
                    session.add(point)
                session.commit()
                session.close()


def add_polygons():
    data_dir = '/home/dev/appsdev/glo_vli/tethysapp/glo_vli/public/data/'
    layers = os.listdir(data_dir)

    wfs_request_url = geoserver_wfs_url + '?version=1.0.0&request=GetFeature&' \
                                          'typeNames=glo_vli:TexasCounties&outputFormat=application/json'

    counties_gdf = gpd.read_file(wfs_request_url)
    counties_gdf = counties_gdf.to_crs({'init': 'epsg:4326'})

    for layer in layers:
        if 'FirmPan' in layer or 'FldHaz' in layer:
            l_files = os.listdir(os.path.join(data_dir, layer))
            for f in l_files:
                if f.endswith('.shp'):
                    f_path = os.path.join(data_dir, layer, f)
                    gdf = gpd.read_file(f_path)
                    gdf = gdf.to_crs({'init': 'epsg:4326'})
                    gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4326))
                    c_join = gpd.sjoin(gdf, counties_gdf)
                    Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
                    session = Session()
                    for index, row in c_join.iterrows():
                        source = row['SOURCE_CIT']
                        geometry = row['geom']
                        f_name = f.split('.')[0]
                        year = '2019'
                        county = row.get('CNTY_NM')
                        polygon = Polygons(layer_name=f_name, year=year, source=source,
                                           county=county, geometry=geometry, approved=True)
                        session.add(polygon)
                    session.commit()
                    session.close()


def get_counties_options():

    wfs_request_url = geoserver_wfs_url + '?version=1.0.0&request=GetFeature&' \
                                          'typeNames=glo_vli:TexasCounties&outputFormat=application/json'

    resp = requests.get(wfs_request_url)
    data = json.loads(resp.text)

    counties_options = []

    for feature in data['features']:

        counties_options.append((feature["properties"]["CNTY_NM"], feature["properties"]["CNTY_NM"]))

    return counties_options

