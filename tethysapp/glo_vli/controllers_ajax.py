from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from tethys_sdk.gizmos import *
import json
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.exc import IntegrityError
from .model import  *
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
