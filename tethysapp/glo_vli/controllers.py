from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from tethys_sdk.gizmos import Button, MVDraw, MapView, TextInput, SelectInput
from .utils import add_points, user_permission_test, add_polygons, get_counties_options, get_county_name
from .app import GloVli
from .model import *
from .config import geoserver_wms_url


def home(request):
    """
    Controller for the app home page.
    """

    # add_points()
    # add_polygons()

    counties_options = get_counties_options()

    select_counties_input = SelectInput(display_text='Select County(s)',
                                        name='select-county',
                                        multiple=True,
                                        original=False,
                                        options=counties_options,
                                        # initial=counties_options[0],
                                        attributes={'id': 'select-county'})


    context = {
        'select_counties_input': select_counties_input,
        'geoserver_wms_url': geoserver_wms_url
    }

    return render(request, 'glo_vli/home.html', context)


@user_passes_test(user_permission_test)
def add_point(request):

    lon_lat_input = TextInput(display_text='Longitude, Latitude',
                              name='lon-lat-input',
                              placeholder='e.g.: 30.5, -90.3',
                              attributes={'id': 'lon-lat-input', 'readonly': 'true'},)

    select_layer_input = SelectInput(display_text='Select Layer',
                                     name='select-layer',
                                     multiple=False,
                                     original=True,
                                     options=[('LowWaterCrossings', 'LowWaterCrossings'), ('HighWaterMarks', 'HighWaterMarks')],
                                     initial=['LowWaterCrossings_Int'])

    year_input = TextInput(display_text='Year',
                           name='year-input',
                           placeholder='e.g.: 2019',
                           attributes={'id': 'year-input'})

    source_input = TextInput(display_text='Source',
                             name='source-input',
                             placeholder='e.g.: FIS',
                             attributes={'id': 'source-input'})

    elevation_input = TextInput(display_text='Elevation',
                                name='elevation-input',
                                placeholder='e.g.: 8',
                                attributes={'id': 'elevation-input'})

    add_button = Button(display_text='Add Point',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-point',
                        attributes={'id': 'submit-add-point'}, )

    add_meta_button = Button(display_text='Add Metadata',
                        icon='glyphicon glyphicon-plus',
                        style='primary',
                        name='submit-add-meta',
                        attributes={'id': 'submit-add-meta'}, )

    select_meta_input = SelectInput(display_text='Select Metadata Type',
                                     name='select-meta',
                                     multiple=False,
                                     original=True,
                                     options=[('External Link', 'text'),
                                              ('File', 'file')],)

    context = {
        'lon_lat_input': lon_lat_input,
        'select_layer_input': select_layer_input,
        'year_input': year_input,
        'source_input': source_input,
        'elevation_input': elevation_input,
        'add_meta_button': add_meta_button,
        'select_meta_input': select_meta_input,
        'add_button': add_button

    }

    return render(request, 'glo_vli/add_point.html', context)


@user_passes_test(user_permission_test)
def approve_points(request):

    # initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    num_points = session.query(Points).filter_by(approved=False).count()
    session.close()

    context = {
        'num_points': num_points,
        'initial_page': 0
    }

    return render(request, 'glo_vli/approve_points.html', context)


@user_passes_test(user_permission_test)
def approve_points_table(request):

    # initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    RESULTS_PER_PAGE = 5

    page = int(request.GET.get('page'))

    # Query DB for data store types
    points = session.query(Points)\
                    .order_by(Points.id) \
                    .filter_by(approved=False)[(page * RESULTS_PER_PAGE):((page + 1)*RESULTS_PER_PAGE)]

    prev_button = Button(display_text='Previous',
                         name='prev_button',
                         attributes={'class': 'nav_button'},)

    next_button = Button(display_text='Next',
                         name='next_button',
                         attributes={'class': 'nav_button'},)

    context = {
                'prev_button': prev_button,
                'next_button': next_button,
                'points': points,
              }

    session.close()

    return render(request, 'glo_vli/approve_points_table.html', context)


@user_passes_test(user_permission_test)
def add_polygon(request):

    polygon_input = TextInput(display_text='Polygon input',
                              name='polygon-input',
                              placeholder='e.g.: Polygon',
                              attributes={'id': 'polygon-input', 'readonly': 'true'},)

    select_layer_input = SelectInput(display_text='Select Layer',
                                     name='select-layer',
                                     multiple=False,
                                     original=True,
                                     options=[('S_FIRM_PAN', 'S_FIRM_PAN'), ('S_FLD_HAZ_AR', 'S_FLD_HAZ_AR')],
                                     initial=['S_FLD_HAZ_AR'])

    year_input = TextInput(display_text='Year',
                           name='year-input',
                           placeholder='e.g.: 2019',
                           attributes={'id': 'year-input'})

    source_input = TextInput(display_text='Source',
                             name='source-input',
                             placeholder='e.g.: FIS',
                             attributes={'id': 'source-input'})

    add_button = Button(display_text='Add Polygon',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-point',
                        attributes={'id': 'submit-add-polygon'}, )

    context = {
        'polygon_input': polygon_input,
        'select_layer_input': select_layer_input,
        'year_input': year_input,
        'source_input': source_input,
        'add_button': add_button

    }

    return render(request, 'glo_vli/add_polygon.html', context)


@user_passes_test(user_permission_test)
def approve_polygons(request):

    # initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    num_polygons = session.query(Polygons).filter_by(approved=False).count()
    session.close()

    context = {
        'num_polygons': num_polygons,
        'initial_page': 0
    }

    return render(request, 'glo_vli/approve_polygons.html', context)


@user_passes_test(user_permission_test)
def approve_polygons_table(request):

    # initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    RESULTS_PER_PAGE = 5

    page = int(request.GET.get('page'))

    # Query DB for data store types
    polygons = session.query(Polygons)\
                    .order_by(Polygons.id) \
                    .filter_by(approved=False)[(page * RESULTS_PER_PAGE):((page + 1)*RESULTS_PER_PAGE)]

    prev_button = Button(display_text='Previous',
                         name='prev_button',
                         attributes={'class': 'nav_button'},)

    next_button = Button(display_text='Next',
                         name='next_button',
                         attributes={'class': 'nav_button'},)

    context = {
                'prev_button': prev_button,
                'next_button': next_button,
                'polygons': polygons
              }

    session.close()

    return render(request, 'glo_vli/approve_polygons_table.html', context)

