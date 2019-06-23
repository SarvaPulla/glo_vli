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
		element,
		layers,
		map,
		popup,
		public_interface,				// Object returned by the module
		wms_layer,
		wms_source;



	/************************************************************************
	 *                    PRIVATE FUNCTION DECLARATIONS
	 *************************************************************************/
	var get_popup,
		init_events,
		init_jquery_vars,
		init_all,
		init_map;

	/************************************************************************
	 *                    PRIVATE FUNCTION IMPLEMENTATIONS
	 *************************************************************************/
	init_jquery_vars = function(){

	};

	init_map = function(){

		var base_map =  new ol.layer.Tile({
			source: new ol.source.OSM()
		});

		wms_source = new ol.source.ImageWMS({
			url: 'http://127.0.0.1:8181/geoserver/wms',
			params: {'LAYERS': 'glo_vli:layers'},
			serverType: 'geoserver',
			crossOrigin: 'Anonymous'
		});
		// 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
		wms_layer = new ol.layer.Image({
			source: wms_source
		});

		layers = [base_map, wms_layer];

		map = new ol.Map({
			target: 'map',
			view: new ol.View({
				center: ol.proj.transform([-94.40, 30.20], 'EPSG:4326', 'EPSG:3857'),
				zoom: 10,
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
	};

	get_popup = function(evt){
		var clickCoord = evt.coordinate; //Get the coordinate of the clicked point
		popup.setPosition(clickCoord);
		// map.getLayers().item(1).getSource().clear();

		var view = map.getView();
		var viewResolution = view.getResolution();


		var wms_url = current_layer.getSource().getGetFeatureInfoUrl(evt.coordinate, viewResolution, view.getProjection(), {'INFO_FORMAT': 'application/json'}); //Get the wms url for the clicked point
		if (wms_url) {
			//Retrieving the details for clicked point via the url
			$.ajax({
				type: "GET",
				url: wms_url,
				dataType: 'json',


				success: function (result) {
					var lname = result["features"][0]["properties"]["layer_name"];
					var source = result["features"][0]["properties"]["source"];
					var year = result["features"][0]["properties"]["year"];
					var elevation = result["features"][0]["properties"]["elevation"];

					$(element).popover({
						'placement': 'top',
						'html': true,
						//Dynamically Generating the popup content
						'content':
							'<table border="1"><tbody><tr><th>Layer Name</th><th>Source</th><th>Year</th><th>Elevation</th></tr>'+
							'<tr><td>'+lname+'</td><td>'+source+'</td><td>'+year+'</td><td>'+elevation+'</td></tr></tbody></table>'
					});

					$(element).popover('show');
					$(element).next().css('cursor', 'text');

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
				if (layer != layers[0] ){
					current_layer = layer;
					return true;
				}
			});
			map.getTargetElement().style.cursor = hit ? 'pointer' : '';
		});

		map.on('singleclick', function(evt) {
			$(element).popover('destroy');

			if (map.getTargetElement().style.cursor == "pointer") {
				get_popup(evt);
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
	});

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
