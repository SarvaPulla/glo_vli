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
    var gs_wms_url,
        input_counter,
        layers,
        map,
        m_uploading_data,
        m_results_per_page,
        $modalUpdate,
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
        var $meta_element = $("#metadata");
        gs_wms_url = $meta_element.attr('data-wms-url');
        $modalUpdate = $("#update-modal");
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
            params: {'LAYERS': 'glo_vli:polygons'},
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

        var scaleLineControl = new ol.control.ScaleLine({units:'us'});
        map.addControl(scaleLineControl);

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
                url: gs_wms_url,
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
        $('.submit-update-form').off().click(function(){
             $modalUpdate.modal('show');
             $("#meta-group").html('');
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
            var polygon_layer_name = checkTableCellInputWithError(parent_row.find('.polygon-layer-name'),safe_to_submit);

            var polygon_attribute = checkTableCellInputWithError(parent_row.find('.polygon-attribute'),safe_to_submit);
            polygon_attribute = polygon_attribute.replace(/\'/g, "\"");
            polygon_attribute = JSON.parse(polygon_attribute);
            polygon_attribute = Object.keys(polygon_attribute).map( function(key){ return key+":"+polygon_attribute[key] }).join(",");

            var polygon_approved = checkTableCellInputWithError(parent_row.find('.polygon-approved'),safe_to_submit);
            var polygon_meta = checkTableCellInputWithError(parent_row.find('.polygon-meta'),safe_to_submit);
            polygon_meta = polygon_meta.replace(/\'/g, "\"");
            polygon_meta = JSON.parse(polygon_meta);
            input_counter = Object.keys(polygon_meta).length + 1;

            $("#id-input").val(polygon_id);
            $("#layer-input").val(polygon_layer_name);
            $("#attribute-input").val(polygon_attribute);
            $("#approved-input").val(polygon_approved).change();

            $.map(polygon_meta, function(key, val){
                var input_id = val;

                if(val.indexOf('text') !== -1){
                    $("#meta-group").append('<div class="input-group">\n' +
                        '<input type="text" class="form-control"  id="' + input_id +'" placeholder="External Link" value="'+key+'">' +
                        '<div class="input-group-btn">' +
                        '<button class="btn btn-default remove" type="submit">' +
                        '<i class="glyphicon glyphicon-remove"></i>' +
                        '</button>' +
                        '</div>' +
                        '</div>');
                    $('.remove').click(function() {
                        $(this).parent().parent().remove();
                    });
                }
                if(val.indexOf('file') !== -1){
                    $("#meta-group").append('<div class="input-group">\n' +
                        '<input type="text" class="form-control"  id="' + input_id +'" placeholder="External File" value="'+key+'" readonly>' +
                        '<div class="input-group-btn">' +
                        '<button class="btn btn-default remove" type="submit">' +
                        '<i class="glyphicon glyphicon-remove"></i>' +
                        '</button>' +
                        '</div>' +
                        '</div>');
                    $('.remove').click(function() {
                        $(this).parent().parent().remove();
                    });
                }
            });

        });

        $('.submit-update-polygon').off().click(function(){
            var safe_to_submit = {val: true, error:""};
            var polygon_id = $("#id-input").val();
            var polygon_layer_name = $("#layer-input").val();
            var polygon_attribute = $("#attribute-input").val();
            var polygon_approved = $("#approved-input").val();

            var data = new FormData();


            data.append("polygon_id", polygon_id);
            data.append("polygon_layer_name", polygon_layer_name);
            data.append("polygon_attribute", polygon_attribute);
            data.append("polygon_approved", polygon_approved);

            var meta_text = [];
            var meta_file = [];

            var inputValues = $('#meta-group :input').map(function() {
                var type = $(this).prop("type");
                var id = $(this).prop("id");

                if (id.indexOf("text") !== -1) {
                    var link_text = $(this).val();
                    data.append(id, link_text);
                    meta_text.push(id);
                }

                else if (id.indexOf("file") !== -1) {
                    if(type=="file"){
                        var file_content = $(this)[0].files;
                        data.append(id, file_content[0]);
                        meta_file.push(id);
                    }else{
                        data.append(id, $(this).val());
                        meta_file.push(id);
                    }

                }
            });

            data.append("meta_text", meta_text);
            data.append("meta_file", meta_file);

            var xhr = ajax_update_database_with_file("submit", data);
            xhr.done(function(return_data){
                if("success" in return_data){
                    // reset_form(return_data)
                    addSuccessMessage("Polygon Update Successful!");
                }else if("error" in return_data){
                    addErrorMessage(return_data["error"]);
                }
            });
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
