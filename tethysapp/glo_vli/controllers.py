from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from tethys_sdk.gizmos import Button, MVDraw, MapView, TextInput, SelectInput
from .utils import add_points, user_permission_test
from .app import GloVli
from .model import *

def home(request):
    """
    Controller for the app home page.
    """

    # add_points()

    context = {

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

    context = {
        'lon_lat_input': lon_lat_input,
        'select_layer_input': select_layer_input,
        'year_input': year_input,
        'source_input': source_input,
        'elevation_input': elevation_input,
        'add_button': add_button

    }

    return render(request, 'glo_vli/add_point.html', context)


@user_passes_test(user_permission_test)
def approve_points(request):

    add_button = Button(display_text='Approve Point',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-point',
                        attributes={'id': 'submit-approve-point'}, )
    #initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    num_points = session.query(Layer).filter_by(approved=False).count()
    session.close()

    context = {
        'num_points': num_points,
        'initial_page': 0
    }

    return render(request, 'glo_vli/approve_points.html', context)

@user_passes_test(user_permission_test)
def approve_points_table(request):

    #initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    RESULTS_PER_PAGE = 5

    page = int(request.GET.get('page'))

    # Query DB for data store types
    points = session.query(Layer)\
                    .order_by(Layer.id) \
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
