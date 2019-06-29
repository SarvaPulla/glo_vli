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
from .utils import user_permission_test
import requests
import shapely.geometry
import os

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

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()
        point_obj = Layer(layer_name=layer, latitude=latitude, longitude=longitude, year=year,
                          source=source, elevation=elevation, approved=False)
        session.add(point_obj)
        session.commit()
        session.close()

        response = {"success": "success"}

        return JsonResponse(response)

@user_passes_test(user_permission_test)
def point_update(request):
    """
    Controller for updating a geoserver.
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

        # check data
        if not point_id or not point_layer_name or not point_approved or not \
                point_latitude or not point_longitude or not point_year or not point_source:
            return JsonResponse({'error': "Missing input data."})
        # make sure id is id
        try:
            int(point_id)
        except ValueError:
            return JsonResponse({'error': 'Geoserver id is faulty.'})

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()

        point = session.query(Layer).get(point_id)
        # try:

        point.latitude = point_latitude
        point.longitude = point_longitude
        point.year = point_year
        point.source = point_source
        point.elevation = point_elevation
        point.approved = eval(point_approved)
        point.geometry = 'SRID=4326;POINT({0} {1})'.format(point_longitude, point_latitude)

        session.commit()
        session.close()
        return JsonResponse({'success': "Point sucessfully updated!"})
        # except:
        #     return JsonResponse({'error': "There is a problem with your request"})
