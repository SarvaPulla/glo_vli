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
from urllib.parse import urljoin
from .config import geoserver_wfs_url, geoserver_wms_url, \
    geoserver_credentials, geoserver_rest_url


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
    counties_gdf = counties_gdf[['CNTY_NM', 'geometry']]

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
    upload_csv = None
    gdf = None

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
            if file.endswith(".csv"):
                f_path = os.path.join(temp_dir, file)
                upload_csv = f_path

        if gbyos_pol_shp is not None:
            gdf = gpd.read_file(gbyos_pol_shp)

        if upload_csv is not None:
            df = pd.read_csv(upload_csv)
            gdf = gpd.GeoDataFrame(df, crs={'init': 'epsg:4326'}, geometry=df['geometry'].apply(wkt.loads))

        attributes = gdf.columns.values.tolist()

        return attributes

    except Exception as e:
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        return str(e)
    finally:
        # Delete the temporary directory once the shapefile is processed
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def process_shapefile(shapefile, layer_name, attributes):

    app_workspace = app.get_app_workspace()
    temp_id = uuid.uuid4()
    temp_dir = os.path.join(app_workspace.path, str(temp_id))
    os.makedirs(temp_dir)
    gbyos_pol_shp = None
    upload_csv = None
    gdf = None
    counties_gdf = get_counties_gdf()

    Session = app.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()

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

            if file.endswith(".csv"):
                f_path = os.path.join(temp_dir, file)
                upload_csv = f_path

        if gbyos_pol_shp is not None:
            gdf = gpd.read_file(gbyos_pol_shp)

        if upload_csv is not None:
            df = pd.read_csv(upload_csv)
            gdf = gpd.GeoDataFrame(df, crs={'init': 'epsg:4326'}, geometry=df['geometry'].apply(wkt.loads))

        c_join = gpd.sjoin(gdf, counties_gdf)

        c_join = c_join[attributes + ['CNTY_NM', 'geometry']]

        c_join = c_join.dropna()

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
        session.close()
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


def get_point_style_xml(point_size, point_symbology, point_fill, layer_name, style_exists):

    style_name = layer_name.replace(r' ', '_').lower()
    point_size = str(point_size)

    sld_string = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
    sld_string += '<StyledLayerDescriptor version="1.0.0"\n'
    sld_string += '\txsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd"\n'
    sld_string += '\txmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc"\n'
    sld_string += '\txmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
    sld_string += '\t\t<NamedLayer>\n'
    sld_string += '\t\t<Name>{}</Name>\n'.format(layer_name)
    sld_string += '\t\t<UserStyle>\n'
    sld_string += '\t\t<Title>{}</Title>\n'.format(layer_name)
    sld_string += '\t\t\t<FeatureTypeStyle>\n'
    sld_string += '\t\t\t\t<Rule>\n'
    sld_string += '\t\t\t\t\t<Title>{}</Title>\n'.format(layer_name)
    sld_string += '\t\t\t\t\t\t<PointSymbolizer>\n'
    sld_string += '\t\t\t\t\t\t\t<Graphic>\n'
    sld_string += '\t\t\t\t\t\t\t\t<Mark>\n'
    sld_string += '\t\t\t\t\t\t\t\t\t<WellKnownName>{}</WellKnownName>\n'.format(point_symbology)
    sld_string += '\t\t\t\t\t\t\t\t\t<Fill>\n'
    sld_string += '\t\t\t\t\t\t\t\t\t\t<CssParameter name="fill">#{}</CssParameter>\n'.format(point_fill)
    sld_string += '\t\t\t\t\t\t\t\t\t</Fill>\n'
    sld_string += '\t\t\t\t\t\t\t\t</Mark>\n'
    sld_string += '\t\t\t\t\t\t\t\t<Size>{}</Size>\n'.format(point_size)
    sld_string += '\t\t\t\t\t\t\t</Graphic>\n'
    sld_string += '\t\t\t\t\t\t</PointSymbolizer>\n'
    sld_string += '\t\t\t\t</Rule>\n'
    sld_string += '\t\t\t</FeatureTypeStyle>\n'
    sld_string += '\t\t</UserStyle>\n'
    sld_string += '\t</NamedLayer>\n'
    sld_string += '</StyledLayerDescriptor>\n'

    sld_name = style_name + '.sld'

    app_workspace = app.get_app_workspace()
    temp_id = uuid.uuid4()
    temp_dir = os.path.join(app_workspace.path, str(temp_id))
    os.makedirs(temp_dir)
    f_path = os.path.join(temp_dir, sld_name)
    fh = open(f_path, 'w')
    fh.write(sld_string)
    fh.close()

    if style_exists:
        headers = {'content-type': 'application/vnd.ogc.sld+xml'}
        resource = 'styles/{}'.format(sld_name)

        request_url = urljoin(geoserver_rest_url, resource)
        with open(f_path, 'rb') as f:
            r = requests.put(
                request_url,
                data=f,
                headers=headers,
                auth=geoserver_credentials
            )

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    else:
        resource = 'styles'
        payload = \
            '<style><name>{0}</name><filename>{1}</filename></style>'.format(style_name, sld_name)
        headers = {'content-type': 'text/xml'}

        request_url = urljoin(geoserver_rest_url, resource)

        r = requests.post(
            request_url,
            data=payload,
            headers=headers,
            auth=geoserver_credentials
        )

        resource2 = 'styles/{}'.format(sld_name)
        request_url2 = urljoin(geoserver_rest_url, resource2)
        headers2 = {'content-type': 'application/vnd.ogc.sld+xml'}
        with open(f_path, 'rb') as f:
            r = requests.put(
                request_url2,
                data=f,
                headers=headers2,
                auth=geoserver_credentials
            )

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return sld_string
