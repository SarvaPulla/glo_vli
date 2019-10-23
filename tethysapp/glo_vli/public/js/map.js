/*****************************************************************************
 * FILE:    MAP JS
 * DATE:    1 JUNE 2019
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
    var current_layer,
        counties_source,
        counties_layer,
        element,
        endpoint_options,
        gs_wms_url,
        layers,
        layersDict,
        layer_options,
        map,
        popup,
        popup_content,
        public_interface,				// Object returned by the module
        wms_layer,
        wms_source;



    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var add_vli_layers,
        get_popup,
        init_events,
        init_jquery_vars,
        init_all,
        init_map;

    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    init_jquery_vars = function(){
        var $meta_element = $("#metadata");
        gs_wms_url = $meta_element.attr('data-wms-url');
        layer_options = $meta_element.attr('data-layer-options');
        layer_options = JSON.parse(layer_options);
        endpoint_options = $meta_element.attr('data-endpoint-options');
        endpoint_options = JSON.parse(endpoint_options);
    };

    init_map = function(){

        // var base_map =  new ol.layer.Tile({
        // 	source: new ol.source.OSM()
        // });

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

        var attribution = new ol.Attribution({
            html: 'Tiles © <a href="https://services.arcgisonline.com/ArcGIS/rest/services/">ArcGIS</a>'
        });

        layersDict = {};

        var base_map = new ol.layer.Tile({
            name:'Base Map 1',
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
            }),
            baseLayer:true,
            title:"Bing",
            visible:false
        });
        var base_map2 = new ol.layer.Tile({
            name:'Base Map 2',
            crossOrigin: 'anonymous',
            source: new ol.source.XYZ({
                attributions: [attribution],
                url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer' +
                    '/tile/{z}/{y}/{x}'
            }),
            baseLayer:true,
            visible:false,
            title: "World Imagery"

        });

        var base_map3 = new ol.layer.Tile({
            name:'Base Map 3',
            crossOrigin: 'anonymous',
            source: new ol.source.OSM(),
            baseLayer:true,
            title: "Open Street Map"

        });

        counties_source = new ol.source.ImageWMS({
            url: gs_wms_url,
            params: {
                'LAYERS': 'glo_vli:TexasCounties'
            },
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        counties_layer = new ol.layer.Image({
            name: 'Counties',
            title: "Counties",
            source: counties_source
        });


        layers = [base_map, base_map2, base_map3, counties_layer];

        map = new ol.Map({
            target: 'map',
            view: new ol.View({
                center: ol.proj.transform([-94.40, 30.20], 'EPSG:4326', 'EPSG:3857'),
                zoom: 9,
                minZoom: 2,
                maxZoom: 18
            }),
            layers: layers
        });

        element = document.getElementById('popup');

        popup = new ol.Overlay({
            element: element,
            positioning: 'bottom-center',
            stopEvent: true
        });
        map.addOverlay(popup);

        var scaleLineControl = new ol.control.ScaleLine({units:'us'});
        map.addControl(scaleLineControl);

        var switcher = new ol.control.LayerSwitcher(
            {	target:$(".layerSwitcher").get(0),
                show_progress:true,
                extent: true,
            });

        map.addControl(switcher);


    };

    get_popup = function(evt){

        var clickCoord = evt.coordinate; //Get the coordinate of the clicked point
        popup.setPosition(clickCoord);
        // map.getLayers().item(1).getSource().clear();

        var view = map.getView();
        var viewResolution = view.getResolution();

        var layer_type = current_layer.get('layer_type');

        if(layer_type==='wfs') {
            var lname = current_layer.get('title');
            var attr_text_html = '';
            var feature = map.forEachFeatureAtPixel(evt.pixel,
                function (feature, layer) {
                    return feature;
                });
            if (feature) {
                var props = feature.getProperties();
                if (Object.keys(props).length > 0) {
                    $.each(props, function (key, val) {
                        if (key !== 'geometry') {
                            attr_text_html += '<tr><td><span>'+key+':' +val+'</span></td></tr>'
                        }

                    });
                    popup_content = '<table class="table"><tr class="bg-primary"><td>Layer Name: '+lname+'</td></tr>'+attr_text_html;

                    $(element).popover({
                        'placement': 'top',
                        'html': true,
                        //Dynamically Generating the popup content
                        'content': popup_content
                    });

                    $(element).popover('show');
                    $(element).next().css('cursor', 'text');
                }
            }
        }

        if(layer_type === 'wms' || layer_type==='dbms') {
            var wms_url = current_layer.getSource().getGetFeatureInfoUrl(evt.coordinate, viewResolution, view.getProjection(), {'INFO_FORMAT': 'application/json'}); //Get the wms url for the clicked point
        }
        if (layer_type==='wms') {
            //Retrieving the details for clicked point via the url
            $.ajax({
                type: "GET",
                url: wms_url,
                dataType: 'json',
                success: function (result) {
                    var lname = current_layer.get('title');
                    var attr_text_html = '';
                    var feature = result["features"][0];
                    var prop = feature["properties"];
                    $.each(prop, function (key, val) {
                        if (key !== 'geometry') {
                            attr_text_html += '<tr><td><span>'+key+':' +val+'</span></td></tr>'
                        }
                    });

                    popup_content = '<table class="table"><tr class="bg-primary"><td>Layer Name: '+lname+'</td></tr>'+attr_text_html;

                    $(element).popover({
                        'placement': 'top',
                        'html': true,
                        //Dynamically Generating the popup content
                        'content': popup_content
                    });

                    $(element).popover('show');
                    $(element).next().css('cursor', 'text');

                }
            })
        }
        if (layer_type==='dbms') {
            //Retrieving the details for clicked point via the url
            $.ajax({
                type: "GET",
                url: wms_url,
                dataType: 'json',
                success: function (result) {

                    var id = result["features"][0]["id"];
                    var data = {"id": id};
                    var xhr = ajax_update_database("popup-info", data);

                    xhr.done(function(return_data){

                        if("success" in return_data){
                            var lname = return_data["layer_name"];
                            var meta_dict = return_data["meta_dict"];
                            var file_text_html = '';
                            var attr_text_html = '';
                            if(Object.keys(meta_dict).length>0){
                                $.each(meta_dict, function (key, val) {
                                    if(key.indexOf('file') !== -1){
                                        var get_req = '/apps/glo-vli/get-meta-file/?file='+val;
                                        file_text_html += '<a href="'+get_req+'">'+val+'</a><br>'
                                    }
                                    if(key.indexOf('text') !== -1){
                                        file_text_html += '<a href="'+val+'" target="_blank">'+val+'</a><br>'
                                    }
                                });
                            }else{
                                file_text_html += 'No Links/Files';
                            }
                            var attr_dict = return_data["attr_dict"];
                            if(Object.keys(attr_dict).length>0){
                                $.each(attr_dict, function (key, val) {
                                    attr_text_html += '<tr><td><span>'+key+':'+val+'</span></td></tr>'
                                    // attr_text_html += '<span>'+key+':'+val+'</span><br>'
                                });
                            }else{
                                attr_text_html += 'No Attributes';
                            }
                            // popup_content = '<table class="table"><tbody><tr class="bg-primary"><th>Layer Name</th><th>Attributes</th><th colspan="10"></th><th>Links/Files</th></tr>'+
                            //     '<tr><td>'+lname+'</td><td colspan="11">'+attr_text_html+'</td><td>'+file_text_html+'</td></tr></tbody></table>';
                            popup_content = '<table class="table"><tr class="bg-primary"><td>Layer Name: '+lname+'</td></tr>'+attr_text_html+'<tr><td>Links/Files<br>'+file_text_html+'</td></tr>'
                        }else if("error" in return_data){
                            console.log(return_data["error"]);
                        }


                        $(element).popover({
                            'placement': 'top',
                            'html': true,
                            //Dynamically Generating the popup content
                            'content': popup_content
                        });

                        $(element).popover('show');
                        $(element).next().css('cursor', 'text');
                    });



                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    console.log(Error);
                }
            });
        }
    };

    init_events = function(){
        (function () {
            var target, observer, config;
            // select the target node
            target = $('#app-content-wrapper')[0];

            observer = new MutationObserver(function () {
                window.setTimeout(function () {
                    map.updateSize();
                }, 350);
            });
            $(window).on('resize', function () {
                map.updateSize();
            });

            config = {attributes: true};

            observer.observe(target, config);
        }());

        //Only show the pointer for layers that aren't base layer, shapefile layer and the point/polygon feature layer
        map.on('pointermove', function(evt) {
            if (evt.dragging) {
                return;
            }
            var pixel = map.getEventPixel(evt.originalEvent);
            var hit = map.forEachLayerAtPixel(pixel, function(layer) {
                if (layer !== layers[0] && layer !== layers[1] && layer !== layers[2] && layer !== layers[3]){
                    current_layer = layer;
                    return true;
                }
            });
            map.getTargetElement().style.cursor = hit ? 'pointer' : '';
        });

        map.on('singleclick', function(evt) {
            $(element).popover('destroy');

            if (map.getTargetElement().style.cursor === "pointer") {
                get_popup(evt);
            }
        });
    };


    add_vli_layers = function(){
        $.each(layer_options, function(lyr_key, lyrs){
            lyrs.forEach(function(lyr, i){
                var gs_layer = 'glo_vli:' + lyr_key;
                var cql_str = 'layer_name=' + '\'' + lyr + '\' AND approved=True';
                var style = lyr.replace(/ /g,"_").toLowerCase();

                wms_source = new ol.source.TileWMS({
                    url: gs_wms_url,
                    params: {
                        'LAYERS': gs_layer,
                        'CQL_FILTER': cql_str,
                        'STYLES': style,
                        'TILED': true
                    },
                    serverType: 'geoserver',
                    crossOrigin: 'Anonymous'
                });

                wms_layer = new ol.layer.Tile({
                    source: wms_source,
                    name:lyr,
                    visible:false,
                    title: lyr,
                    layer_type: 'dbms'
                });

                map.addLayer(wms_layer);

                layersDict[lyr] = wms_layer;
            });
        });
        $.each(endpoint_options, function(lyr_key, lyrs){
            if(lyrs.layer_type==='wfs'){
                var vectorSource = new ol.source.Vector({
                    format: new ol.format.GeoJSON(),
                    crossOrigin: 'Anonymous',
                    url: function(extent) {
                        return lyrs.url+'&srsname=EPSG:3857&' +
                            'bbox=' + extent.join(',') + ',EPSG:3857';
                    },
                    strategy: ol.loadingstrategy.bbox,
                });

                var vector = new ol.layer.Vector({
                    source: vectorSource,
                    title: lyrs.layer_name,
                    layer_type: lyrs.layer_type,
                    visible:false
                });
                map.addLayer(vector);
            }else{

                var wms_url = lyrs.url.split('|')[0];
                var wms_layers = lyrs.url.split('|')[1];
                var wms_legend_url = lyrs.legend_url;
                wms_source = new ol.source.TileWMS({
                    url: wms_url,
                    params: {
                        'LAYERS': wms_layers,
                        'TILED': true
                    },
                    // serverType: 'geoserver',
                    crossOrigin: 'Anonymous'
                });
                //
                wms_layer = new ol.layer.Tile({
                    source: wms_source,
                    name:lyrs.layer_name,
                    visible:false,
                    title: lyrs.layer_name,
                    layer_type: 'wms'
                });
                //
                map.addLayer(wms_layer);
            }

        });
    };


    init_all = function(){
        init_jquery_vars();
        init_map();
        add_vli_layers();
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

        $("#select-county").change(function() {
            var counties = ($("#select-county").val());

            if(counties){
                var county_str = "'" + counties.join("','") + "'";
                counties_source.updateParams({'CQL_FILTER': 'CNTY_NM IN ('+ county_str +')'});
                for (var key in layersDict) {
                    var layer_source = layersDict[key].getSource();
                    var layer_name = layersDict[key].get('name');
                    map.getLayers().forEach(function (el) {
                        if (el.get('name') === key) {
                            var county_cql_str = ' AND layer_name=' + '\'' + layer_name + '\' AND approved=True';
                            layer_source.updateParams({'CQL_FILTER': 'county IN ('+ county_str +')'+ county_cql_str});
                        }
                    });
                }
            }else{
                var county_options = $("#select-county")[0].options;
                var values = $.map(county_options, function( elem ) {
                    return (elem.value);
                });
                var county_str = "'" + values.join("','") + "'";
                counties_source.updateParams({'CQL_FILTER': 'CNTY_NM IN ('+ county_str +')'});
                for (var key in layersDict) {
                    var layer_source = layersDict[key].getSource();
                    var layer_name = layersDict[key].get('name');
                    map.getLayers().forEach(function (el) {
                        if (el.get('name') === key) {
                            var county_cql_str = ' AND layer_name=' + '\'' + layer_name + '\' AND approved=True';
                            layer_source.updateParams({'CQL_FILTER': 'county IN ('+ county_str +')' + county_cql_str});
                        }
                    });
                }
            }

        });

        $.each(layersDict, function(key, val){
            val.on('change:visible', function(e){
                var legend_class = key.replace(/ /g,"_").toLowerCase();
                if(val.getVisible()){
                    $('.'+legend_class).removeClass('hidden');
                }else{
                    $('.'+legend_class).addClass('hidden');
                }

            });
        });

    });

    return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
