# Define your REST API endpoints here.
# In the comments below is an example.
# For more information, see:
# http://docs.tethysplatform.org/en/dev/tethys_sdk/rest_api.html
"""
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes

@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
def get_data(request):
    '''
    API Controller for getting data
    '''
    name = request.GET.get('name')
    data = {"name": name}
    return JsonResponse(data)
"""
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render_to_response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
import json
# @api_view(['GET'])
# @authentication_classes((TokenAuthentication,))


from .utils import get_layer_options, \
    get_county_layers, \
    get_layer_points,\
    get_layer_polygons


def get_layers_info(request):

    json_obj = {}
    if request.method == 'GET':
        layer_options = get_layer_options()
        json_obj['layers_options'] = layer_options

        return JsonResponse(json_obj)


def get_layers_by_county(request):

    json_obj = {}
    if request.method == 'GET':
        county = None

        if request.GET.get('county'):
            county = request.GET['county']

        points_json, polygons_json = get_county_layers(county)
        json_obj['success'] = 'success'
        json_obj['points'] = json.loads(points_json)
        json_obj['polygons'] = json.loads(polygons_json)
        return JsonResponse(json_obj)


def get_points_by_county(request):

    json_obj = {}
    if request.method == 'GET':
        county = None

        if request.GET.get('county'):
            county = request.GET['county']

        points_json, polygons_json = get_county_layers(county)
        json_obj['success'] = 'success'
        json_obj['points'] = json.loads(points_json)
        return JsonResponse(json_obj)


def get_polygons_by_county(request):

    json_obj = {}
    if request.method == 'GET':
        county = None

        if request.GET.get('county'):
            county = request.GET['county']

        polygons_json = get_county_layers(county)
        json_obj['success'] = 'success'
        json_obj['polygons'] = json.loads(polygons_json)
        return JsonResponse(json_obj)


def get_points_by_layer(request):

    json_obj = {}
    if request.method == 'GET':
        layer = None

        if request.GET.get('layer'):
            layer = request.GET['layer']

        points_json = get_layer_points(layer)
        json_obj['success'] = 'success'
        json_obj['points'] = json.loads(points_json)
        return JsonResponse(json_obj)


def get_polygons_by_layer(request):

    json_obj = {}
    if request.method == 'GET':
        layer = None

        if request.GET.get('layer'):
            layer = request.GET['layer']

        polygons_json = get_layer_polygons(layer)
        json_obj['success'] = 'success'
        json_obj['polygons'] = json.loads(polygons_json)
        return JsonResponse(json_obj)

