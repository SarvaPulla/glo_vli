from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from tethys_sdk.gizmos import Button, TextInput, SelectInput
from .utils import user_permission_test, get_counties_options, \
    get_legend_options, get_layer_options, get_endpoint_options
from .app import GloVli
from .model import *
from .config import geoserver_wms_url


def home(request):
    """
    Controller for the app home page.
    """

    counties_options = get_counties_options()

    select_counties_input = SelectInput(display_text='Select County(s)',
                                        name='select-county',
                                        multiple=True,
                                        original=False,
                                        options=counties_options,
                                        # initial=counties_options[0],
                                        attributes={'id': 'select-county'})

    layer_options = get_layer_options()

    legend_options = get_legend_options()

    endpoint_options = get_endpoint_options()

    context = {
        'select_counties_input': select_counties_input,
        'geoserver_wms_url': geoserver_wms_url,
        'legend_options': legend_options,
        'layer_options': json.dumps(layer_options),
        'endpoint_options': json.dumps(endpoint_options)
    }

    return render(request, 'glo_vli/home.html', context)


@user_passes_test(user_permission_test)
def add_point(request):

    lon_lat_input = TextInput(display_text='Longitude, Latitude',
                              name='lon-lat-input',
                              placeholder='e.g.: 30.5, -90.3',
                              attributes={'id': 'lon-lat-input', 'readonly': 'true'},)

    layer_options = get_layer_options()
    points = layer_options["points"]
    point_layers = [(layer, layer) for layer in points]

    select_layer_input = SelectInput(display_text='Select Layer',
                                     name='select-layer',
                                     multiple=False,
                                     original=True,
                                     options=point_layers,
                                     initial=point_layers[0])

    attribute_input = TextInput(display_text='Attributes',
                                name='attribute-input',
                                placeholder='e.g.: YEAR:2019,SOURCE:GLO,....',
                                attributes={'id': 'attribute-input'})

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
        'attribute_input': attribute_input,
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

    num_points = session.query(Points).count()
    session.close()

    id_input = TextInput(display_text='Feature ID',
                         name='id-input',
                         placeholder='',
                         attributes={'id': 'id-input', 'readonly': 'true'})

    layer_input = TextInput(display_text='Layer',
                            name='layer-input',
                            placeholder='',
                            attributes={'id': 'layer-input', 'readonly': 'true'})

    lon_input = TextInput(display_text='Longitude',
                          name='lon-input',
                          placeholder='e.g.: -90.3',
                          attributes={'id': 'lon-input'}, )

    lat_input = TextInput(display_text='Latitude',
                          name='lat-input',
                          placeholder='e.g.: 30.5',
                          attributes={'id': 'lat-input'}, )

    approved_input = SelectInput(display_text='Approved',
                                 name='approved-input',
                                 attributes={'id': 'approved-input'},
                                 multiple=False,
                                 options=[('true', 'true'),
                                          ('false', 'false')]
                                 )

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

    attribute_input = TextInput(display_text='Attributes',
                                name='attribute-input',
                                placeholder='e.g.: YEAR:2019,SOURCE:GLO,....',
                                attributes={'id': 'attribute-input'})

    context = {
        'num_points': num_points,
        'initial_page': 0,
        'geoserver_wms_url': geoserver_wms_url,
        'add_meta_button': add_meta_button,
        'id_input': id_input,
        'select_meta_input': select_meta_input,
        'attribute_input': attribute_input,
        'lon_input': lon_input,
        'lat_input': lat_input,
        'layer_input': layer_input,
        'approved_input': approved_input
    }

    return render(request, 'glo_vli/approve_points.html', context)


@user_passes_test(user_permission_test)
def add_polygon(request):

    polygon_input = TextInput(display_text='Polygon input',
                              name='polygon-input',
                              placeholder='e.g.: Polygon',
                              attributes={'id': 'polygon-input', 'readonly': 'true'},)

    layer_options = get_layer_options()
    polygons = layer_options["polygons"]
    polygon_layers = [(layer, layer) for layer in polygons]

    select_layer_input = SelectInput(display_text='Select Layer',
                                     name='select-layer',
                                     multiple=False,
                                     original=True,
                                     options=polygon_layers,
                                     initial=polygon_layers[0])

    attribute_input = TextInput(display_text='Attributes',
                                name='attribute-input',
                                placeholder='e.g.: YEAR:2019,SOURCE:GLO,....',
                                attributes={'id': 'attribute-input'})

    add_button = Button(display_text='Add Polygon',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-point',
                        attributes={'id': 'submit-add-polygon'}, )

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
        'polygon_input': polygon_input,
        'select_layer_input': select_layer_input,
        'attribute_input': attribute_input,
        'add_button': add_button,
        'add_meta_button': add_meta_button,
        'select_meta_input': select_meta_input
    }

    return render(request, 'glo_vli/add_polygon.html', context)


@user_passes_test(user_permission_test)
def approve_polygons(request):

    # initialize session
    Session = GloVli.get_persistent_store_database('layers', as_sessionmaker=True)
    session = Session()
    num_polygons = session.query(Polygons).count()
    session.close()

    id_input = TextInput(display_text='Feature ID',
                         name='id-input',
                         placeholder='',
                         attributes={'id': 'id-input', 'readonly': 'true'})

    layer_input = TextInput(display_text='Layer',
                            name='layer-input',
                            placeholder='',
                            attributes={'id': 'layer-input', 'readonly': 'true'})

    approved_input = SelectInput(display_text='Approved',
                                 name='approved-input',
                                 attributes={'id': 'approved-input'},
                                 multiple=False,
                                 options=[('true', 'true'),
                                          ('false', 'false')]
                                 )

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

    attribute_input = TextInput(display_text='Attributes',
                                name='attribute-input',
                                placeholder='e.g.: YEAR:2019,SOURCE:GLO,....',
                                attributes={'id': 'attribute-input'})

    context = {
        'num_polygons': num_polygons,
        'initial_page': 0,
        'geoserver_wms_url': geoserver_wms_url,
        'id_input': id_input,
        'layer_input': layer_input,
        'attribute_input': attribute_input,
        'approved_input': approved_input,
        'add_meta_button': add_meta_button,
        'select_meta_input': select_meta_input
    }

    return render(request, 'glo_vli/approve_polygons.html', context)


@user_passes_test(user_permission_test)
def add_new_layer(request):
    """
    Controller for the upload layer page.
    """

    add_new_select = SelectInput(display_text='Add New Layer',
                                 name='add-new-select',
                                 attributes={'id': 'add-new-select'},
                                 multiple=False,
                                 options=[('True', 'True'),
                                          ('False', 'False')]
                                 )

    layer_text_input = TextInput(display_text='Layer Name',
                                 name='layer-text-input',
                                 placeholder='e.g.: Hospitals',
                                 attributes={'id': 'layer-text-input'},
                                 )

    layer_options = get_layer_options()
    layer_list = [(layer, layer) for key, val in layer_options.items() for layer in val]

    layer_select_input = SelectInput(display_text='Select Layer',
                                     name='layer-select-input',
                                     multiple=False,
                                     original=True,
                                     options=layer_list,)

    attributes_button = Button(display_text='Get Shapefile Attributes',
                               icon='glyphicon glyphicon-plus',
                               style='primary',
                               name='submit-get-attributes',
                               attributes={'id': 'submit-get-attributes'}, )

    add_button = Button(display_text='Add Layer',
                        icon='glyphicon glyphicon-plus',
                        style='primary',
                        name='submit-add-layer',
                        attributes={'id': 'submit-add-layer'},
                        classes="hidden add")

    context = {
        'add_new_select': add_new_select,
        'layer_text_input': layer_text_input,
        'layer_select_input': layer_select_input,
        'attributes_button': attributes_button,
        'add_button': add_button
    }

    return render(request, 'glo_vli/add_new_layer.html', context)


@user_passes_test(user_permission_test)
def delete_layer(request):
    """
    Controller for the upload layer page.
    """

    layer_options = get_layer_options()
    layer_list = [(layer, layer) for key, val in layer_options.items() for layer in val]

    layer_select_input = SelectInput(display_text='Select Layer',
                                     name='layer-select-input',
                                     multiple=False,
                                     original=True,
                                     options=layer_list,)

    counties_options = get_counties_options()

    select_counties_input = SelectInput(display_text='Select County(s)',
                                        name='select-county',
                                        multiple=True,
                                        original=False,
                                        options=counties_options,
                                        # initial=counties_options[0],
                                        attributes={'id': 'select-county'})

    delete_button = Button(display_text='Delete Layer',
                           icon='glyphicon glyphicon-minus',
                           style='danger',
                           name='submit-delete-layer',
                           attributes={'id': 'submit-delete-layer'},
                           classes="delete")

    context = {
        'layer_select_input': layer_select_input,
        'delete_button': delete_button,
        'select_counties_input': select_counties_input
    }

    return render(request, 'glo_vli/delete_layer.html', context)


@user_passes_test(user_permission_test)
def set_layer_style(request):
    """
    Controller for the upload layer page.
    """

    layer_options = get_layer_options()
    layer_list = [(layer, str(layer)+'|'+str(key)) for key, val in layer_options.items() for layer in val]

    layer_select_input = SelectInput(display_text='Select Layer',
                                     name='layer-select-input',
                                     multiple=False,
                                     original=True,
                                     options=layer_list,)

    set_style_button = Button(display_text='Set Layer Style',
                              icon='glyphicon glyphicon-plus',
                              style='danger',
                              name='submit-delete-layer',
                              attributes={'id': 'submit-set-layer'},
                              classes="submit")

    point_size_input = TextInput(display_text='Point Size',
                                 name='point-size-input',
                                 placeholder='e.g.: 10',
                                 attributes={'id': 'point-size-input'},
                                 )

    select_point_symbology = SelectInput(display_text='Select Point Symbology',
                                         name='select-point-symbology',
                                         attributes={'id': 'select-point-symbology'},
                                         multiple=False,
                                         options=[('circle', 'circle'),
                                                  ('square', 'square'),
                                                  ('triangle', 'triangle'),
                                                  ('arrow', 'arrow'),
                                                  ('cross', 'cross'),
                                                  ('star', 'star'),
                                                  ('x', 'x')])

    polygon_fill_opacity = TextInput(display_text='Polygon Fill Opacity',
                                     name='polygon-fill-opacity',
                                     placeholder='e.g.: 0.7. Goes from 0 to 1.',
                                     attributes={'id': 'polygon-fill-opacity'},
                                     )

    polygon_stroke_width = TextInput(display_text='Polygon Stroke Width',
                                     name='polygon-stroke-width',
                                     placeholder='e.g.: 2. The thickness of the fill stroke.',
                                     attributes={'id': 'polygon-stroke-width'},
                                     )

    context = {
        'layer_select_input': layer_select_input,
        'set_style_button': set_style_button,
        'select_point_symbology': select_point_symbology,
        'point_size_input': point_size_input,
        'polygon_fill_opacity': polygon_fill_opacity,
        'polygon_stroke_width': polygon_stroke_width
    }

    return render(request, 'glo_vli/set_layer_style.html', context)


@user_passes_test(user_permission_test)
def add_endpoint(request):

    name_input = TextInput(display_text='Layer Name',
                           name='name-input',
                           placeholder='',
                           attributes={'id': 'name-input'})

    endpoint_input = TextInput(display_text='REST Endpoint',
                               name='endpoint-input',
                               placeholder='e.g.: REST Endpoint',
                               attributes={'id': 'endpoint-input'},
                               )

    endpoint_type =  SelectInput(display_text='Endpoint Type',
                                 name='endpoint-type',
                                 attributes={'id': 'endpoint-type'},
                                 multiple=False,
                                 options=[('wfs', 'wfs'), ('wms', 'wms')]
                                 )

    wms_text_input = TextInput(display_text='WMS Layer Name',
                               name='wms-text-input',
                               placeholder='e.g.: cite:qpf24hr_day1_latest',
                               attributes={'id': 'wms-text-input'},
                               classes='wms_layer hidden'
                               )

    add_button = Button(display_text='Add Endpoint',
                        icon='glyphicon glyphicon-plus',
                        style='primary',
                        name='submit-add-endpoint',
                        attributes={'id': 'submit-add-endpoint'},
                        classes="add")

    context = {"name_input": name_input,
               "endpoint_input": endpoint_input,
               "endpoint_type": endpoint_type,
               "wms_text_input": wms_text_input,
               "add_button": add_button}

    return render(request, 'glo_vli/add_endpoint.html', context)


@user_passes_test(user_permission_test)
def delete_endpoint(request):
    """
    Controller for the upload layer page.
    """

    endpoint_options = get_endpoint_options()

    layer_list = [(opt['layer_name'], opt['layer_name']) for opt in endpoint_options]

    layer_select_input = SelectInput(display_text='Select Endpoint',
                                     name='layer-select-input',
                                     multiple=False,
                                     original=True,
                                     options=layer_list,)

    delete_button = Button(display_text='Delete Layer',
                           icon='glyphicon glyphicon-minus',
                           style='danger',
                           name='submit-delete-endpoint',
                           attributes={'id': 'submit-delete-endpoint'},
                           classes="delete")

    context = {
        'layer_select_input': layer_select_input,
        'delete_button': delete_button
    }

    return render(request, 'glo_vli/delete_endpoint.html', context)
