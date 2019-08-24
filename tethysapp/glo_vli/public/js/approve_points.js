/*****************************************************************************
 * FILE:    Approve Points JS
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
    var add_meta_input,
        clear_coords,
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
        $("#point-lat-lon").val('');
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
            $("#attribute-input").val('');
            $("#lat-input").val('');
            $("#lon-input").val('');
            addSuccessMessage('Point Update Complete!');
        }
        if("reset" in result){
            $("#attribute-input").val('');
            $("#lat-input").val('');
            $("#lon-input").val('');
            $("#id-input").val('');
            $("#layer-input").val('');
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
            url: gs_wms_url,
            params: {'LAYERS': 'glo_vli:points'},
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

        $('.view-point').off().click(function(){
            var parent_row = $(this).parent().parent().parent();
            var point_id = parent_row.find('.point-id').text();

            map.removeLayer(wms_layer);
            var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>glo_vli:points</Name><UserStyle><FeatureTypeStyle>\
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
                params: {'LAYERS': 'glo_vli:points', 'SLD_BODY':sld_string,
                    'FeatureID': point_id},
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
            // clear messages
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
            var point_id = parent_row.find('.point-id').text();
            var point_layer_name = checkTableCellInputWithError(parent_row.find('.point-layer-name'),safe_to_submit);
            var point_latitude = checkTableCellInputWithError(parent_row.find('.point-latitude'),safe_to_submit);
            var point_longitude = checkTableCellInputWithError(parent_row.find('.point-longitude'),safe_to_submit);
            var point_attribute = checkTableCellInputWithError(parent_row.find('.point-attribute'),safe_to_submit);
            point_attribute = point_attribute.replace(/\'/g, "\"");
            point_attribute = JSON.parse(point_attribute);
            point_attribute = Object.keys(point_attribute).map( function(key){ return key+":"+point_attribute[key] }).join(",");

            var point_approved = checkTableCellInputWithError(parent_row.find('.point-approved'),safe_to_submit);
            var point_meta = checkTableCellInputWithError(parent_row.find('.point-meta'),safe_to_submit);
            point_meta = point_meta.replace(/\'/g, "\"");
            point_meta = JSON.parse(point_meta);
            input_counter = Object.keys(point_meta).length + 1;

            $("#id-input").val(point_id);
            $("#lat-input").val(point_latitude);
            $("#lon-input").val(point_longitude);
            $("#layer-input").val(point_layer_name);
            $("#attribute-input").val(point_attribute);
            $("#approved-input").val(point_approved).change();


            $.map(point_meta, function(key, val){
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

        $('.submit-update-point').off().click(function(){
            var safe_to_submit = {val: true, error:""};
            var point_id = $("#id-input").val();
            var point_latitude = $("#lat-input").val();
            var point_longitude = $("#lon-input").val();
            var point_layer_name = $("#layer-input").val();
            var point_attribute = $("#attribute-input").val();
            var point_approved = $("#approved-input").val();

            var data = new FormData();


            data.append("point_id", point_id);
            data.append("point_layer_name", point_layer_name);
            data.append("point_latitude", point_latitude);
            data.append("point_longitude", point_longitude);
            data.append("point_attribute", point_attribute);
            data.append("point_approved", point_approved);

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
                    addSuccessMessage("Point Update Successful!");
                }else if("error" in return_data){
                    addErrorMessage(return_data["error"]);
                }
            });
        });

        //handle the submit delete event
        $('.submit-delete-point').click(function(){
            var data = {
                point_id: $(this).parent().parent().parent()
                    .find('.point-id').text()
            };
            //update database
            var xhr = deleteRowData($(this), data);
            if (xhr != null) {
                xhr.done(function (data) {
                    if ('success' in data) {
                        addSuccessMessage("Point Successfully Deleted!");
                        var num_points_data = $('#approve_points_table').data('num_points');
                        var page = parseInt($('#approve_points_table').data('page'));
                        $('#approve_points_table').data('num_points', Math.max(0, parseInt(num_points_data) - 1));
                        if (parseInt($('#approve_points_table').data('num_points')) <= m_results_per_page * page) {
                            $('#num_points_data').data('page', Math.max(0, page - 1));
                        }
                        getTablePage();
                    }
                });
            }
        });

        displayResultsText();
        if (m_results_per_page >= $('#num_points_data').data('num_points')) {
            $('[name="prev_button"]').addClass('hidden');
            $('[name="next_button"]').addClass('hidden');
        }

        //pagination next and previous button update
        $('[name="prev_button"]').click(function(){
            var page = parseInt($('#approve_points_table').data('page'));
            $('#approve_points_table').data('page', Math.max(0, page-1));
            getTablePage();
        });
        $('[name="next_button"]').click(function(){
            var page = parseInt($('#approve_points_table').data('page'));
            $('#approve_points_table').data('page', Math.min(page+1,
                Math.floor(parseInt($('#approve_points_table').data('num_points')) / m_results_per_page - 0.1)));
            getTablePage();
        });
    };


    displayResultsText = function() {
        //dynamically show table results display info text on page
        var page = parseInt($('#approve_points_table').data('page'));
        var num_points_data = $('#approve_points_table').data('num_points');
        var display_min;
        if (num_points_data == 0){
            display_min = 0
        }
        else{
            display_min = ((page + 1) * m_results_per_page) - (m_results_per_page - 1);
        }
        var display_max = Math.min(num_points_data, ((page + 1) * m_results_per_page));
        $('[name="prev_button"]').removeClass('hidden');
        $('[name="next_button"]').removeClass('hidden');
        if (page == 0){
            $('[name="prev_button"]').addClass('hidden');
        } else if (page == Math.floor(num_points_data / m_results_per_page - 0.1)) {
            $('[name="next_button"]').addClass('hidden');
        }
        if (num_points_data != 0) {
            $('#display-info').append('Displaying points ' + display_min + ' - ' +
                display_max + ' of ' + num_points_data);
        }else {
            $('#display-info').append('No points to display' + '<br>To add one, ' +
                'click <a href="../add-point">here</a>.');
        }
    };

    getTablePage = function() {
        $.ajax({
            url: 'table',
            method: 'GET',
            data: {'page': $('#approve_points_table').data('page')},
            success: function(data) {
                $("#approve_points_table").html(data);
                initializeTableFunctions();
            }
        });
    };

    add_meta_input = function(){
        var input_type = $("#select-meta option:selected").val();
        if(input_type == 'text'){
            var input_id = 'meta_'+input_counter+'_'+input_type;
            $("#meta-group").append('<div class="input-group">\n' +
                '<input type="text" class="form-control"  id="' + input_id +'" placeholder="External Link" >' +
                '<div class="input-group-btn">' +
                '<button class="btn btn-default remove" type="submit">' +
                '<i class="glyphicon glyphicon-remove"></i>' +
                '</button>' +
                '</div>' +
                '</div>');
            $('.remove').click(function() {
                $(this).parent().parent().remove();
            });
            input_counter ++;
        }
        if(input_type == 'file'){
            var input_id = 'meta_'+input_counter+'_'+input_type;
            $("#meta-group").append('<div class="input-group">\n' +
                '<input type="file" class="form-control"  id="' + input_id +'" placeholder="External File" >' +
                '<div class="input-group-btn">' +
                '<button class="btn btn-default remove" type="submit">' +
                '<i class="glyphicon glyphicon-remove"></i>' +
                '</button>' +
                '</div>' +
                '</div>');
            $('.remove').click(function() {
                $(this).parent().parent().remove();
            });
            input_counter ++;
        }


    };

    $("#submit-add-meta").click(add_meta_input);

    $('#update-modal').on('hide.bs.modal', function () {
        reset_form({"reset": "reset"});
    });

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
