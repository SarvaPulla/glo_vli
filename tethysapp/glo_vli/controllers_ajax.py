from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from tethys_sdk.gizmos import *
import json
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.exc import IntegrityError
from .model import *
from .app import GloVli
from .utils import user_permission_test, process_meta_file, get_point_county_name, get_polygon_county_name
import requests
from shapely.geometry import shape
import os
import json
from mimetypes import guess_type
import geojson


@user_passes_test(user_permission_test)
def point_add(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        year = info.get('year')
        source = info.get('source')
        layer = info.get('layer')
        elevation = info.get('elevation')
        point = info.get('point')
        longitude = point.split(',')[0]
        latitude = point.split(',')[1]

        county = get_point_county_name(longitude, latitude)

        meta_dict = {}

        meta_text = info.get('meta_text')
        meta_file = info.get('meta_file')

        if meta_text:
            meta_text = meta_text.split(',')

        if meta_file:
            meta_file = meta_file.split(',')

        if len(meta_text) > 0:
            for txt in meta_text:
                meta_dict[txt] = info.get(txt)

        if len(meta_file) > 0:
            for file in meta_file:
                meta_dict[file] = process_meta_file(request.FILES.getlist(file)[0])

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()
        point_obj = Points(layer_name=layer, latitude=latitude, longitude=longitude, year=year,
                           source=source, elevation=elevation, county=county, approved=False, meta_dict=meta_dict)
        session.add(point_obj)
        session.commit()
        session.close()

        response = {"success": "success"}

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def point_update(request):
    """
    Controller for updating a point.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        point_id = post_info.get('point_id')
        point_layer_name = post_info.get('point_layer_name')
        point_latitude = post_info.get('point_latitude')
        point_longitude = post_info.get('point_longitude')
        point_year = post_info.get('point_year')
        point_source = post_info.get('point_source')
        point_elevation = post_info.get('point_elevation')
        point_approved = post_info.get('point_approved')

        county = get_point_county_name(point_longitude, point_latitude)

        meta_text = post_info.get('meta_text')
        meta_file = post_info.get('meta_file')

        meta_dict = {}

        if meta_text:
            meta_text = meta_text.split(',')

        if meta_file:
            meta_file = meta_file.split(',')

        if len(meta_text) > 0:
            for txt in meta_text:
                meta_dict[txt] = post_info.get(txt)

        if len(meta_file) > 0:
            for file in meta_file:
                f_result = post_info.get(file)
                if f_result is not None:
                    meta_dict[file] = f_result
                else:
                    meta_dict[file] = process_meta_file(request.FILES.getlist(file)[0])

        # check data
        if not point_id or not point_layer_name or not point_approved or not \
                point_latitude or not point_longitude or not point_year or not point_source:
            return JsonResponse({'error': "Missing input data."})
        # make sure id is id
        try:
            int(point_id)
        except ValueError:
            return JsonResponse({'error': 'Point id is faulty.'})

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()

        point = session.query(Points).get(point_id)
        try:

            point.latitude = point_latitude
            point.longitude = point_longitude
            point.year = point_year
            point.source = point_source
            point.elevation = point_elevation
            point.approved = eval(point_approved)
            point.geometry = 'SRID=4326;POINT({0} {1})'.format(point_longitude, point_latitude)
            point.meta_dict = meta_dict
            point.county = county

            session.commit()
            session.close()
            return JsonResponse({'success': "Point successfully updated!"})
        except Exception as e:
            return JsonResponse({'error': "There is a problem with your request. " + str(e)})


@user_passes_test(user_permission_test)
def point_delete(request):
    """
    Controller for deleting a point.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        point_id = post_info.get('point_id')

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()
        try:
            # delete point
            try:
                point = session.query(Points).get(point_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The point to delete does not exist."})

            session.delete(point)
            session.commit()
            session.close()
            return JsonResponse({'success': "Point successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})


@user_passes_test(user_permission_test)
def polygon_add(request):

    response = {}
    try:
        if request.is_ajax() and request.method == 'POST':
            info = request.POST

            year = info.get('year')
            source = info.get('source')
            layer = info.get('layer')
            polygon = info.get('polygon')
            polygon = geojson.loads(polygon)
            geom = shape(polygon)

            county = get_polygon_county_name(geom.wkt)

            meta_dict = {}

            meta_text = info.get('meta_text')
            meta_file = info.get('meta_file')

            if meta_text:
                meta_text = meta_text.split(',')

            if meta_file:
                meta_file = meta_file.split(',')

            if len(meta_text) > 0:
                for txt in meta_text:
                    meta_dict[txt] = info.get(txt)

            if len(meta_file) > 0:
                for file in meta_file:
                    meta_dict[file] = process_meta_file(request.FILES.getlist(file)[0])

            Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
            session = Session()
            point_obj = Polygons(layer_name=layer, year=year, source=source, county=county,
                                 approved=False, geometry=geom.wkt, meta_dict=meta_dict)
            session.add(point_obj)
            session.commit()
            session.close()

            response = {"success": "success"}

            return JsonResponse(response)
    except Exception as e:

        response = {"error": str(e)}
        return JsonResponse(response)


@user_passes_test(user_permission_test)
def polygon_update(request):
    """
    Controller for updating a polygon.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST
        polygon_id = post_info.get('polygon_id')
        polygon_year = post_info.get('polygon_year')
        polygon_source = post_info.get('polygon_source')
        polygon_approved = post_info.get('polygon_approved')

        # check data
        if not polygon_id or not polygon_approved or not \
                polygon_year or not polygon_source:
            return JsonResponse({'error': "Missing input data."})
        # make sure id is id
        try:
            int(polygon_id)
        except ValueError:
            return JsonResponse({'error': 'Polygon id is faulty.'})

        meta_text = post_info.get('meta_text')
        meta_file = post_info.get('meta_file')

        meta_dict = {}

        if meta_text:
            meta_text = meta_text.split(',')

        if meta_file:
            meta_file = meta_file.split(',')

        if len(meta_text) > 0:
            for txt in meta_text:
                meta_dict[txt] = post_info.get(txt)

        if len(meta_file) > 0:
            for file in meta_file:
                f_result = post_info.get(file)
                if f_result is not None:
                    meta_dict[file] = f_result
                else:
                    meta_dict[file] = process_meta_file(request.FILES.getlist(file)[0])

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()

        polygon = session.query(Polygons).get(polygon_id)
        try:
            polygon.year = polygon_year
            polygon.source = polygon_source
            polygon.approved = eval(polygon_approved)
            polygon.meta_dict = meta_dict

            session.commit()
            session.close()
            return JsonResponse({'success': "polygon successfully updated!"})
        except Exception as e:
            return JsonResponse({'error': "There is a problem with your request. " + str(e)})


@user_passes_test(user_permission_test)
def polygon_delete(request):
    """
    Controller for deleting a polygon.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        polygon_id = post_info.get('polygon_id')

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()
        try:
            # delete point
            try:
                polygon = session.query(Polygons).get(polygon_id)
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The point to delete does not exist."})

            session.delete(polygon)
            session.commit()
            session.close()
            return JsonResponse({'success': "Point successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})


def get_popup_info(request):
    """
    Controller for getting relevant data to populate the popup
    """

    post_info = request.POST

    id = post_info.get("id")
    primary_key = id.split('.')[1]
    table = id.split('.')[0]

    json_obj = {}

    json_obj['type'] = table

    try:
        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()

        if table == 'points':
            info = session.query(Points).get(primary_key)
            json_obj['county'] = info.county
            json_obj['meta_dict'] = info.meta_dict
            json_obj['layer_name'] = info.layer_name
            json_obj['source'] = info.source
            json_obj['year'] = info.year
            json_obj['success'] = 'success'

            for key, val in info.meta_dict.items():
                if 'file' in key:
                    app_workspace = app.get_app_workspace()
                    f_path = os.path.join(app_workspace.path, val)
                    print(f_path)

        elif table == 'polygons':
            info = session.query(Polygons).get(primary_key)
            json_obj['county'] = info.county
            json_obj['layer_name'] = info.layer_name
            json_obj['source'] = info.source
            json_obj['year'] = info.year
            json_obj['success'] = 'success'

    except Exception as e:

        json_obj['error'] = str(e)

    return JsonResponse(json_obj)


def get_meta_file(request):

    file = request.GET['file']

    app_workspace = app.get_app_workspace()
    f_path = os.path.join(app_workspace.path, file)

    if os.path.exists(f_path):
        with open(f_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=guess_type(f_path)[0])
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(f_path)
            return response
    raise Http404

