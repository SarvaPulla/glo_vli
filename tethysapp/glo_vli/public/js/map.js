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
		ContextMenuBase,
		element,
		layers,
		layersDict,
		map,
		popup,
		public_interface,				// Object returned by the module
		vli_layers,
		wms_layer,
		wms_source;



	/************************************************************************
	 *                    PRIVATE FUNCTION DECLARATIONS
	 *************************************************************************/
	var addContextMenuToListItem,
		add_vli_layers,
		get_popup,
		init_events,
		init_jquery_vars,
		init_all,
		init_map,
		init_menu,
		onClickZoomTo;

	/************************************************************************
	 *                    PRIVATE FUNCTION IMPLEMENTATIONS
	 *************************************************************************/
	init_jquery_vars = function(){
		vli_layers = ['S_FIRM_PAN', 'S_FLD_HAZ_AR','HighWaterMarks', 'LowWaterCrossings'];
		var $layers_element = $('#layers');
	};

	init_map = function(){

		var base_map =  new ol.layer.Tile({
			source: new ol.source.OSM()
		});

		wms_source = new ol.source.ImageWMS({
			url: 'http://hydropad.org:8181/geoserver/wms',
			params: {'LAYERS': 'glo_vli:points'},
			serverType: 'geoserver',
			crossOrigin: 'Anonymous'
		});
		// 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
		wms_layer = new ol.layer.Image({
			source: wms_source
		});

		layersDict = {};

		layers = [base_map];

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

	addContextMenuToListItem = function ($listItem) {
		var contextMenuId;
		console.log($listItem);
		$listItem.find('.hmbrgr-div img')
			.contextMenu('menu', ContextMenuBase, {
				'triggerOn': 'click',
				'displayAround': 'trigger',
				'mouseClick': 'left',
				'position': 'right',
				'onOpen': function (e) {
					$('.hmbrgr-div').removeClass('hmbrgr-open');
					$(e.trigger.context).parent().addClass('hmbrgr-open');
				},
				'onClose': function (e) {
					$(e.trigger.context).parent().removeClass('hmbrgr-open');
				}
			});
		contextMenuId = $('.iw-contextMenu:last-child').attr('id');
		$listItem.attr('data-context-menu', contextMenuId);
	};


	init_menu = function(){
		ContextMenuBase = [];
	};

	//On click zoom to the relevant layer
	onClickZoomTo = function(e){
		var clickedElement = e.trigger.context;
		var $lyrListItem = $(clickedElement).parent().parent();
		var layer_name = $lyrListItem.attr('layer-name');
		var layer_extent = layersDict[layer_name].getExtent();
		map.getView().fit(layer_extent,map.getSize());
		map.updateSize();
	};

	add_vli_layers = function(){
		vli_layers.forEach(function(i, val){
			if( i == 'S_FLD_HAZ_AR'|| i == 'S_FIRM_PAN' ){
				var lyr_name = vli_layers[val];

				$('<li class="ui-state-default"' + 'layer-name="' + lyr_name + '"' + '><input class="chkbx-layer" type="checkbox" checked><span class="layer-name">' + lyr_name + '</span><div class="hmbrgr-div"><img src="/static/glo_vli/images/hamburger.svg"></div></li>').appendTo('#current-layers');
				var $list_item = $('#current-layers').find('li:last-child');
				var cql_str = 'layer_name=' + '\'' + lyr_name + '\' AND approved=True';

				// addContextMenuToListItem($list_item);
				wms_source = new ol.source.ImageWMS({
					url: 'http://hydropad.org:8181/geoserver/wms',
					params: {
						'LAYERS': 'glo_vli:polygons',
						'CQL_FILTER': cql_str
					},
					serverType: 'geoserver',
					crossOrigin: 'Anonymous'
				});
				// 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
				wms_layer = new ol.layer.Image({
					source: wms_source
				});
				map.addLayer(wms_layer);

				layersDict[lyr_name] = wms_layer;
			}
			else
			{
				var lyr_name = vli_layers[val];

				$('<li class="ui-state-default"' + 'layer-name="' + lyr_name + '"' + '><input class="chkbx-layer" type="checkbox" checked><span class="layer-name">' + lyr_name + '</span><div class="hmbrgr-div"><img src="/static/glo_vli/images/hamburger.svg"></div></li>').appendTo('#current-layers');
				var $list_item = $('#current-layers').find('li:last-child');
				var cql_str = 'layer_name=' + '\'' + lyr_name + '\' AND approved=True';

				// addContextMenuToListItem($list_item);
				wms_source = new ol.source.ImageWMS({
					url: 'http://hydropad.org:8181/geoserver/wms',
					params: {
						'LAYERS': 'glo_vli:points',
						'CQL_FILTER': cql_str
					},
					serverType: 'geoserver',
					crossOrigin: 'Anonymous'
				});
				// 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
				wms_layer = new ol.layer.Image({
					source: wms_source
				});
				map.addLayer(wms_layer);

				layersDict[lyr_name] = wms_layer;
			}
		});
	};


	$(document).on('change', '.chkbx-layer', function () {
		var displayName = $(this).next().text();
		layersDict[displayName].setVisible($(this).is(':checked'));
	});

	init_all = function(){
		init_menu();
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
	});

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
