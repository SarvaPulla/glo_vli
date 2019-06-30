/*****************************************************************************
 * FILE:    Approve Polygond JS
 * DATE:    29 JUNE 2019
 * AUTHOR: Sarva Pulla
 * COPYRIGHT: (c) 2019
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var LIBRARY_OBJECT = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
    var layers,
        map,
        m_uploading_data,
        m_results_per_page,
        public_interface,				// Object returned by the module
        wms_source,
        wms_layer;





    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var clear_coords,
        displayResultsText,
        getTablePage,
        initializeTableFunctions,
        init_events,
        init_jquery_vars,
        init_all,
        init_map,
        reset_alert,
        reset_form;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    m_results_per_page = 5;

    clear_coords = function(){
        $("#polygon-lon").val('');
    };

    //Reset the alerts if everything is going well
    reset_alert = function(){
        $("#message").addClass('hidden');
        $("#message").empty()
            .addClass('hidden')
            .removeClass('alert-success')
            .removeClass('alert-info')
            .removeClass('alert-warning')
            .removeClass('alert-danger');
    };

    //Reset the form when the request is made succesfully
    reset_form = function(result){
        if("success" in result){
            $("#polygon-input").val('');
            $("#year-input").val('');
            $("#source-input").val('');
            $("#elevation-input").val('');
            addSuccessMessage('Polygon Upload Complete!');
        }
    };

    init_jquery_vars = function(){

    };

    init_map = function(){
        var projection = ol.proj.get('EPSG:3857');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
            })
        });
        var fullScreenControl = new ol.control.FullScreen();
        var view = new ol.View({
            center: ol.proj.transform([-95.4,29.76], 'EPSG:4326','EPSG:3857'),
            projection: projection,
            zoom: 6
        });

        wms_source = new ol.source.ImageWMS({
            url: 'http://hydropad.org:8181/geoserver/wms',
            params: {'LAYERS': 'glo_vli:layers'},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        // 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
        wms_layer = new ol.layer.Image({
            source: wms_source
        });


        layers = [baseLayer];

        map = new ol.Map({
            target: document.getElementById("map"),
            layers: layers,
            view: view
        });

        var mousePositionControl = new ol.control.MousePosition({
            coordinateFormat: ol.coordinate.createStringXY(4),
            projection: 'EPSG:4326',
            // comment the following two lines to have the mouse position
            // be placed within the map.
            className: 'custom-mouse-position',
            target: document.getElementById('mouse-position'),
            undefinedHTML: '&nbsp;'
        });
        map.addControl(mousePositionControl);



    };

    init_events = function(){

    };

    initializeTableFunctions = function() {

        $('.view-polygon').off().click(function(){
            var parent_row = $(this).parent().parent().parent();
            var polygon_id = parent_row.find('.polygon-id').text();
            // map.removeLayer(wms_layer);
            var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>glo_vli:polygons</Name><UserStyle><FeatureTypeStyle>\
                        <Rule>\
                        <PointSymbolizer>\
                        <Graphic>\
                        <Mark>\
                        <WellKnownName>circle</WellKnownName>\
                        <Fill>\
                        <CssParameter name="fill">#FF0000</CssParameter>\
                        </Fill>\
                        </Mark>\
                        <Size>16</Size>\
                        </Graphic>\
                        </PointSymbolizer>\
                        </Rule>\
                        </FeatureTypeStyle>\
                        </UserStyle>\
                        </NamedLayer>\
                        </StyledLayerDescriptor>';
            wms_source = new ol.source.ImageWMS({
                url: 'http://hydropad.org:8181/geoserver/wms',
                params: {'LAYERS': 'glo_vli:polygons',
                    'FeatureID': polygon_id},
                serverType: 'geoserver',
                crossOrigin: 'Anonymous'
            });
            wms_layer = new ol.layer.Image({
                source: wms_source
            });

            map.addLayer(wms_layer);

        });



        //handle the submit update event
        $('.submit-update-polygon').off().click(function(){
            //scroll back to top
            window.scrollTo(0,0);
            //clear messages
            $('#message').addClass('hidden');
            $('#message').empty()
                .addClass('hidden')
                .removeClass('alert-success')
                .removeClass('alert-info')
                .removeClass('alert-warning')
                .removeClass('alert-danger');

            //check data store input
            var safe_to_submit = {val: true, error:""};
            var parent_row = $(this).parent().parent().parent();
            var polygon_id = parent_row.find('.polygon-id').text();
            var polygon_year = checkTableCellInputWithError(parent_row.find('.polygon-year'),safe_to_submit);
            var polygon_source = checkTableCellInputWithError(parent_row.find('.polygon-source'),safe_to_submit);
            var polygon_approved = checkTableCellInputWithError(parent_row.find('.polygon-approved'),safe_to_submit);


            var data = {
                polygon_id: polygon_id,
                polygon_year: polygon_year,
                polygon_source: polygon_source,
                polygon_approved: polygon_approved
            };

            //update database
            var xhr = submitRowData($(this), data, safe_to_submit);
            if (xhr != null) {
                xhr.done(function (data) {
                    if ('success' in data) {
                        addSuccessMessage("Polygon Update Success!");
                    }
                });
            }
        });

        //handle the submit delete event
        $('.submit-delete-polygon').click(function(){
            var data = {
                polygon_id: $(this).parent().parent().parent()
                    .find('.polygon-id').text()
            };
            //update database
            var xhr = deleteRowData($(this), data);
            if (xhr != null) {
                xhr.done(function (data) {
                    if ('success' in data) {
                        addSuccessMessage("Polygon Successfully Deleted!");
                        var num_polygons_data = $('#approve_polygons_table').data('num_polygons');
                        var page = parseInt($('#approve_polygons_table').data('page'));
                        $('#approve_polygons_table').data('num_polygons', Math.max(0, parseInt(num_polygons_data) - 1));
                        if (parseInt($('#approve_polygons_table').data('num_polygons_data')) <= m_results_per_page * page) {
                            $('#num_polygons_data').data('page', Math.max(0, page - 1));
                        }
                        getTablePage();
                    }
                });
            }
        });

        displayResultsText();
        if (m_results_per_page >= $('#num_polygons_data').data('num_polygons')) {
            $('[name="prev_button"]').addClass('hidden');
            $('[name="next_button"]').addClass('hidden');
        }

        //pagination next and previous button update
        $('[name="prev_button"]').click(function(){
            var page = parseInt($('#approve_polygons_table').data('page'));
            $('#approve_polygons_table').data('page', Math.max(0, page-1));
            getTablePage();
        });
        $('[name="next_button"]').click(function(){
            var page = parseInt($('#approve_polygons_table').data('page'));
            $('#approve_polygons_table').data('page', Math.min(page+1,
                Math.floor(parseInt($('#approve_polygons_table').data('num_polygons')) / m_results_per_page - 0.1)));
            getTablePage();
        });
    };


    displayResultsText = function() {
        //dynamically show table results display info text on page
        var page = parseInt($('#approve_polygons_table').data('page'));
        var num_polygons_data = $('#approve_polygons_table').data('num_polygons');
        var display_min;
        if (num_polygons_data == 0){
            display_min = 0
        }
        else{
            display_min = ((page + 1) * m_results_per_page) - (m_results_per_page - 1);
        }
        var display_max = Math.min(num_polygons_data, ((page + 1) * m_results_per_page));
        $('[name="prev_button"]').removeClass('hidden');
        $('[name="next_button"]').removeClass('hidden');
        if (page == 0){
            $('[name="prev_button"]').addClass('hidden');
        } else if (page == Math.floor(num_polygons_data / m_results_per_page - 0.1)) {
            $('[name="next_button"]').addClass('hidden');
        }
        if (num_polygons_data != 0) {
            $('#display-info').append('Displaying Polygons ' + display_min + ' - ' +
                display_max + ' of ' + num_polygons_data);
        }else {
            $('#display-info').append('No polygons to display' + '<br>To add one, ' +
                'click <a href="../add-polygon">here</a>.');
        }
    };

    getTablePage = function() {
        $.ajax({
            url: 'table',
            method: 'GET',
            data: {'page': $('#approve_polygons_table').data('page')},
            success: function(data) {
                $("#approve_polygons_table").html(data);
                initializeTableFunctions();
            }
        });
    };

    init_all = function(){
        init_jquery_vars();
        init_map();
        init_events();
    };
    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/
    /*
     * Library object that contains public facing functions of the package.
     * This is the object that is returned by the library wrapper function.
     * See below.
     * NOTE: The functions in the public interface have access to the private
     * functions of the library because of JavaScript function scope.
     */
    public_interface = {

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {

        init_all();
        m_uploading_data = false;
        getTablePage();
    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
