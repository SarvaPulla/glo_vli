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
    counties_dir = os.listdir(data_dir)
    counties_opts = get_counties_options()
    counties = [county[0] for county in counties_opts]
    for county_dir in counties_dir:
        if any(county in county_dir for county in counties):
            county_path = os.path.join(data_dir, county_dir)
            layers_dir = os.listdir(county_path)
            for layer in layers_dir:
                if 'High' in layer or 'Low' in layer:
                    layer_dir = os.path.join(county_path, layer)
                    l_files = os.listdir(layer_dir)
                    for f in l_files:
                        if f.endswith('.shp'):
                            f_path = os.path.join(layer_dir, f)
                            gdf = gpd.read_file(f_path)
                            Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
                            session = Session()
                            for index, row in gdf.iterrows():

                                if 'LWX' in f:
                                    latitude = row.get('LAT')
                                    longitude = row.get('LONG')
                                    source = row.get('SOURCE')
                                    county = row.get('COUNTY')
                                    county = county.title()
                                    table_name = 'LowWaterCrossings'
                                    point = Points(table_name, latitude, longitude, 2019, source, 10, county,
                                                   approved=True)
                                    session.add(point)

                                if 'HWM' in f:
                                    latitude = row.get('Lat')
                                    longitude = row.get('Long')
                                    source = row.get('Source')
                                    county = row.get('County')
                                    county = county.title()
                                    elevation = row.get('Original_E')
                                    year = row.get('Year')
                                    table_name = 'HighWaterMarks'
                                    point = Points(table_name, latitude, longitude, year, source, elevation, county,
                                                   approved=True)
                                    session.add(point)

                            session.commit()
                            session.close()


def add_polygons():
    data_dir = '/home/dev/appsdev/glo_vli/tethysapp/glo_vli/public/data/'
    counties_dir = os.listdir(data_dir)
    counties_opts = get_counties_options()
    counties = [county[0] for county in counties_opts]

    wfs_request_url = geoserver_wfs_url + '?version=1.0.0&request=GetFeature&' \
                                          'typeNames=glo_vli:TexasCounties&outputFormat=application/json'

    counties_gdf = gpd.read_file(wfs_request_url)
    counties_gdf = counties_gdf.to_crs({'init': 'epsg:4326'})

    for county_dir in counties_dir:
        if any(county in county_dir for county in counties):
            county_path = os.path.join(data_dir, county_dir)
            layers_dir = os.listdir(county_path)
            for layer in layers_dir:
                if 'Flood' in layer:
                    layer_dir = os.path.join(county_path, layer)
                    l_files = os.listdir(layer_dir)
                    for f in l_files:
                        if f.endswith('.shp'):
                            f_path = os.path.join(layer_dir, f)
                            gdf = gpd.read_file(f_path)
                            gdf = gdf.to_crs({'init': 'epsg:4326'})
                            gdf['geom'] = gdf['geometry'].apply(lambda x: WKTElement(x.wkt, srid=4326))
                            c_join = gpd.sjoin(gdf, counties_gdf)
                            Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
                            session = Session()
                            for index, row in c_join.iterrows():
                                if 'FLD' in f:
                                    source = row['SOURCE_CIT']
                                    geometry = row['geom']
                                    f_name = 'FLD_HAZ_AR'
                                    year = '2019'
                                    county = row.get('CNTY_NM')
                                    polygon = Polygons(layer_name=f_name, year=year, source=source,
                                                       county=county, geometry=geometry, approved=True)
                                    session.add(polygon)
                                if 'WTR' in f:
                                    source = row['SOURCE_CIT']
                                    geometry = row['geom']
                                    year = '2019'
                                    county = row.get('CNTY_NM')
                                    f_name = 'WTR_AR'
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
        county = feature["properties"]["CNTY_NM"]
        counties_options.append((county, county))

    return counties_options

