from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.exc import IntegrityError
from .model import *
from .app import GloVli
from .utils import user_permission_test, process_meta_file, \
    get_point_county_name, get_polygon_county_name, process_shapefile, \
    get_shapefile_attributes, get_layer_options
from shapely.geometry import shape
import os
import json
from django.utils.encoding import smart_str
import geojson
import math


@user_passes_test(user_permission_test)
def point_add(request):

    try:

        if request.is_ajax() and request.method == 'POST':
            info = request.POST

            attributes = info.get('attributes')
            layer_name = info.get('layer_name')
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

            attr_dict = {}

            if attributes:
                attributes = attributes.split(',')
                attr_dict = {attr.split(':')[0]: attr.split(':')[1] for attr in attributes}

            Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
            session = Session()
            point = Points(layer_name=layer_name, latitude=latitude, longitude=longitude, county=county,
                           approved=False, attr_dict=attr_dict, meta_dict=meta_dict)
            session.add(point)

            session.commit()
            session.close()

            response = {"success": "success"}

            return JsonResponse(response)

    except Exception as e:
        return JsonResponse({'error': "There is a problem with your request. " + str(e)})


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
        point_attribute = post_info.get('point_attribute')
        point_approved = post_info.get('point_approved')
        point_approved = json.loads(point_approved)

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

        attr_dict = {}

        if point_attribute:
            attributes = point_attribute.split(',')
            attr_dict = {attr.split(':')[0]: attr.split(':')[1] for attr in attributes}

        # check data
        if not point_id or not point_layer_name  or not \
                point_latitude or not point_longitude:
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
            point.attr_dict = attr_dict
            point.approved = point_approved
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

    try:
        if request.is_ajax() and request.method == 'POST':
            info = request.POST

            attributes = info.get('attributes')
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

            attr_dict = {}

            if attributes:
                attributes = attributes.split(',')
                attr_dict = {attr.split(':')[0]: attr.split(':')[1] for attr in attributes}

            Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
            session = Session()
            polygon = Polygons(layer_name=layer, county=county, attr_dict=attr_dict,
                               approved=False, geometry=geom.wkt, meta_dict=meta_dict)
            session.add(polygon)
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
        polygon_approved = post_info.get('polygon_approved')
        polygon_attribute = post_info.get('polygon_attribute')
        polygon_approved = json.loads(polygon_approved)


        # check data
        if not polygon_id:
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

        attr_dict = {}

        if polygon_attribute:
            attributes = polygon_attribute.split(',')
            attr_dict = {attr.split(':')[0]: attr.split(':')[1] for attr in attributes}

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()

        polygon = session.query(Polygons).get(polygon_id)
        try:

            polygon.approved = polygon_approved
            polygon.meta_dict = meta_dict
            polygon.attr_dict = attr_dict

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

        info = None

        if table == 'points':
            info = session.query(Points).get(primary_key)
        elif table == 'polygons':
            info = session.query(Polygons).get(primary_key)

        json_obj['county'] = info.county
        json_obj['meta_dict'] = info.meta_dict
        json_obj['attr_dict'] = info.attr_dict
        json_obj['layer_name'] = info.layer_name
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
            response = HttpResponse(fh.read(), content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file)
            response['X-Sendfile'] = smart_str(f_path)
            return response
    raise Http404


@user_passes_test(user_permission_test)
def get_shp_attributes(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':

        try:

            shapefile = request.FILES.getlist('shapefile')

            attributes = get_shapefile_attributes(shapefile)

            response = {"success": "success",
                        "attributes": attributes}

            return JsonResponse(response)

        except Exception as e:
            json_obj = {'error': str(e)}

            return JsonResponse(json_obj)


@user_passes_test(user_permission_test)
def new_layer_add(request):

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        layer_name = info.get('layer')

        shapefile = request.FILES.getlist('shapefile')

        attributes = info.get('attributes')

        attributes = attributes.split(',')

        response = process_shapefile(shapefile, layer_name, attributes)

        return JsonResponse(response)


@user_passes_test(user_permission_test)
def points_tabulator(request):

    json_obj = {}

    info = request.GET

    page = int(request.GET.get('page'))
    page = page - 1
    size = int(request.GET.get('size'))

    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    # RESULTS_PER_PAGE = 10
    num_points = session.query(Points).count()
    last_page = math.ceil(int(num_points) / int(size))

    # # Query DB for data store types
    points = session.query(Points) \
             .order_by(Points.id) \
             [(page * size):((page+1) * size)]

    data_dict = []

    for point in points:
        json_obj = {}
        json_obj["id"] = point.id
        json_obj["layer_name"] = point.layer_name
        json_obj["latitude"] = point.latitude
        json_obj["longitude"] = point.longitude
        json_obj["county"] = point.county
        json_obj["attributes"] = json.dumps(point.attr_dict)
        json_obj["metadata"] = json.dumps(point.meta_dict)
        json_obj["approved"] = point.approved
        data_dict.append(json_obj)

    response = {"data": data_dict, "last_page": last_page}

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def polygons_tabulator(request):

    json_obj = {}

    info = request.GET

    page = int(request.GET.get('page'))
    page = page - 1
    size = int(request.GET.get('size'))

    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    # RESULTS_PER_PAGE = 10
    num_polygons = session.query(Polygons).count()
    last_page = math.ceil(int(num_polygons) / int(size))

    # # Query DB for data store types
    polygons = session.query(Polygons) \
             .order_by(Polygons.id) \
             [(page * size):((page+1) * size)]

    data_dict = []

    for polygon in polygons:
        json_obj = {}
        json_obj["id"] = polygon.id
        json_obj["layer_name"] = polygon.layer_name
        json_obj["county"] = polygon.county
        json_obj["attributes"] = json.dumps(polygon.attr_dict)
        json_obj["metadata"] = json.dumps(polygon.meta_dict)
        json_obj["approved"] = polygon.approved
        data_dict.append(json_obj)

    response = {"data": data_dict, "last_page": last_page}

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def layer_delete(request):
    """
    Controller for deleting a polygon.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        post_info = request.POST

        layer = post_info.get('layer')
        counties = post_info.get('counties')
        counties = tuple(counties.split(','))

        layer_options = get_layer_options()
        table_type = [key for key, value in layer_options.items() if layer in layer_options[key]][0]

        Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
        session = Session()
        try:
            # delete layer
            try:
                if table_type == 'polygons':
                    polygons = session.query(Polygons).filter(Polygons.layer_name == layer,
                                                              Polygons.county.in_(counties))
                    polygons.delete(synchronize_session=False)
                    session.commit()
                else:
                    points = session.query(Points).filter(Points.layer_name == layer, Points.county.in_(counties))
                    points.delete(synchronize_session=False)
                    session.commit()
            except ObjectDeletedError:
                session.close()
                return JsonResponse({'error': "The layer to delete does not exist."})

            session.close()
            return JsonResponse({'success': "Layer successfully deleted!"})
        except IntegrityError:
            session.close()
            return JsonResponse({'error': "There is a problem with your request."})

