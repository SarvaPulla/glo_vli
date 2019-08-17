import pandas as pd
import geopandas as gpd
import os
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import *
from tethysapp.glo_vli.app import GloVli as app
from tethysapp.glo_vli.model import Points, Polygons
import requests
import json
from shapely import wkt
from .config import geoserver_wfs_url, geoserver_wms_url, data_dir


def user_permission_test(user):
    return user.is_superuser or user.is_staff


def add_points():
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
                                    table_name = 'Low Water Crossings'
                                    point = Points(table_name, latitude, longitude, 2019, source, 10, county,
                                                   approved=True, meta_dict={})
                                    session.add(point)

                                if 'HWM' in f:
                                    latitude = row.get('Lat')
                                    longitude = row.get('Long')
                                    source = row.get('Source')
                                    county = row.get('County')
                                    county = county.title()
                                    elevation = row.get('Original_E')
                                    year = row.get('Year')
                                    table_name = 'High Water Marks'
                                    point = Points(table_name, latitude, longitude, year, source, elevation, county,
                                                   approved=True, meta_dict={})
                                    session.add(point)

                            session.commit()
                            session.close()


def add_polygons():
    counties_dir = os.listdir(data_dir)
    counties_opts = get_counties_options()
    counties = [county[0] for county in counties_opts]

    counties_gdf = get_counties_gdf()

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
                                    f_name = 'FEMA 100 Yr Flood'
                                    year = '2019'
                                    county = row.get('CNTY_NM')
                                    polygon = Polygons(layer_name=f_name, year=year, source=source,
                                                       county=county, geometry=geometry, approved=True, meta_dict={})
                                    session.add(polygon)
                                if 'WTR' in f:
                                    source = row['SOURCE_CIT']
                                    geometry = row['geom']
                                    year = '2019'
                                    county = row.get('CNTY_NM')
                                    f_name = 'Surface Water'
                                    polygon = Polygons(layer_name=f_name, year=year, source=source,
                                                       county=county, geometry=geometry, approved=True, meta_dict={})
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


def process_meta_file(file):

    app_workspace = app.get_app_workspace()

    f_name = file.name
    f_path = os.path.join(app_workspace.path, f_name)

    with open(f_path, 'wb') as f_local:
        f_local.write(file.read())

    return f_name


def get_counties_gdf():
    wfs_request_url = geoserver_wfs_url + '?version=1.0.0&request=GetFeature&' \
                                          'typeNames=glo_vli:TexasCounties&outputFormat=application/json'

    counties_gdf = gpd.read_file(wfs_request_url)
    counties_gdf.crs = {'init': 'epsg:4326'}

    return counties_gdf


def get_point_county_name(longitude, latitude):

    counties_gdf = get_counties_gdf()
    pdf = pd.DataFrame({'Name': ['point'], 'Latitude': [float(latitude)], 'Longitude': [float(longitude)]})
    pgdf = gpd.GeoDataFrame(pdf, geometry=gpd.points_from_xy(pdf.Longitude, pdf.Latitude))
    pgdf.crs = {'init': 'epsg:4326'}
    point_in_poly = gpd.sjoin(pgdf, counties_gdf, op='within')
    county = point_in_poly.CNTY_NM[0]

    return county


def get_polygon_county_name(geom):

    counties_gdf = get_counties_gdf()
    pdf = pd.DataFrame({'Name': ['polygon'], 'geometry': [geom]})
    pdf['geometry'] = pdf['geometry'].apply(wkt.loads)
    pgdf = gpd.GeoDataFrame(pdf, geometry='geometry')
    pgdf.crs = {'init': 'epsg:4326'}
    poly_in_poly = gpd.sjoin(pgdf, counties_gdf, op='intersects')
    county = poly_in_poly.CNTY_NM.values[0]

    return county


def get_layer_options():

    Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()

    point_layers = [layer[0] for layer in session.query(Points.layer_name).distinct()]

    polygon_layers = [layer[0] for layer in session.query(Polygons.layer_name).distinct()]

    layer_options = {}

    layer_options["polygons"] = polygon_layers
    layer_options["points"] = point_layers

    session.close()

    return layer_options


def get_legend_options():

    legend_options = []

    common_req_str = "?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&" \
                     "WIDTH=20&HEIGHT=20&LEGEND_OPTIONS=forceLabels:on;"

    options = get_layer_options()

    for type, layers in options.items():
        for layer in layers:
            style = layer.replace(" ", "_").lower()
            legend_url = geoserver_wms_url + common_req_str + "&LAYER=glo_vli:" + type + "&STYLE=" + style
            legend_options.append((legend_url, style))

    return legend_options
