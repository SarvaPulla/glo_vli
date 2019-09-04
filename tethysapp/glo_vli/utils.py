import pandas as pd
import geopandas as gpd
import os
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import *
from .app import GloVli as app
from .model import Points, Polygons
import requests
import json
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPolygon
import tempfile
import shutil
from django.http import JsonResponse
import uuid
from .config import geoserver_wfs_url, geoserver_wms_url


def user_permission_test(user):
    return user.is_superuser or user.is_staff


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


def get_shapefile_attributes(shapefile):

    app_workspace = app.get_app_workspace()

    temp_id = uuid.uuid4()
    temp_dir = os.path.join(app_workspace.path, str(temp_id))
    os.makedirs(temp_dir)
    gbyos_pol_shp = None

    try:

        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(temp_dir, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(temp_dir):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(temp_dir, file)
                gbyos_pol_shp = f_path

        gdf = gpd.read_file(gbyos_pol_shp)
        attributes = gdf.columns.values.tolist()
        attributes = attributes[:-1]
        return attributes

    except Exception as e:
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return str(e)
    finally:
        # Delete the temporary directory once the shapefile is processed
        print(temp_dir)
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def process_shapefile(shapefile, layer_name, attributes):

    app_workspace = app.get_app_workspace()
    temp_id = uuid.uuid4()
    temp_dir = os.path.join(app_workspace.path, str(temp_id))
    os.makedirs(temp_dir)
    gbyos_pol_shp = None
    counties_gdf = get_counties_gdf()

    try:

        for f in shapefile:
            f_name = f.name
            f_path = os.path.join(temp_dir, f_name)

            with open(f_path, 'wb') as f_local:
                f_local.write(f.read())

        for file in os.listdir(temp_dir):
            # Reading the shapefile only
            if file.endswith(".shp"):
                f_path = os.path.join(temp_dir, file)
                gbyos_pol_shp = f_path

        gdf = gpd.read_file(gbyos_pol_shp)

        c_join = gpd.sjoin(gdf, counties_gdf)

        c_join = c_join[attributes + ['CNTY_NM', 'geometry']]

        Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()

        for index, row in c_join.iterrows():
            if type(row.geometry) == Point:
                county = row.get('CNTY_NM')
                latitude = row.geometry.y
                longitude = row.geometry.x
                attribute_info = {attr: row[attr] for attr in attributes}
                point = Points(layer_name=layer_name, latitude=latitude, longitude=longitude, county=county,
                               approved=True, attr_dict=attribute_info, meta_dict={})
                session.add(point)
            else:
                county = row.get('CNTY_NM')
                geometry = row.get('geometry')
                attribute_info = {attr: row[attr] for attr in attributes}
                polygon = Polygons(layer_name=layer_name, county=county, geometry=geometry,
                                   approved=True, attr_dict=attribute_info, meta_dict={})
                session.add(polygon)

        session.commit()
        session.close()

        return {"success": "success"}

    except Exception as e:
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return {"error": str(e)}
    finally:
        print(temp_dir)
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
