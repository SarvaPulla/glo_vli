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
		counties_source,
		counties_layer,
		element,
		gs_wms_url,
		layers,
		layersDict,
		map,
		popup,
		popup_content,
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
		generate_popup_content,
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
		vli_layers = ['FLD_HAZ_AR', 'WTR_AR','HighWaterMarks', 'LowWaterCrossings'];
		var $meta_element = $("#metadata");
		gs_wms_url = $meta_element.attr('data-wms-url');
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
				extent: true
			});

		map.addControl(switcher);
	};

	generate_popup_content = function(id){


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


					// var lname = result["features"][0]["properties"]["layer_name"];
					// var source = result["features"][0]["properties"]["source"];
					// var year = result["features"][0]["properties"]["year"];
					// var elevation = result["features"][0]["properties"]["elevation"];
					var id = result["features"][0]["id"];
					var data = {"id": id};
					var xhr = ajax_update_database("popup-info", data);

					xhr.done(function(return_data){
						if("success" in return_data){

							if(return_data['type'] == 'points'){
								var lname = return_data["layer_name"];
								var year = return_data["year"];
								var source = return_data["source"];
								var meta_dict = return_data["meta_dict"];
								var file_text_html = '';
								if(Object.keys(meta_dict).length>0){
									$.each(meta_dict, function (key, val) {
										if(key.indexOf('file') !== -1){
											var get_req = '/apps/glo-vli/get-meta-file/?file='+val;
											file_text_html += '<a href="'+get_req+'">'+val+'</a><br>'
										}
										if(key.indexOf('text') !== -1){
											file_text_html += '<a href="'+val+'">'+val+'</a><br>'
										}
									});
								}else{
									file_text_html += 'No Links/Files';
								}

								popup_content = '<table border="1"><tbody><tr><th>Layer Name</th><th>Source</th><th>Year</th><th>Links/Files</th></tr>'+
									'<tr><td>'+lname+'</td><td>'+source+'</td><td>'+year+'</td><td>'+file_text_html+'</td></tr></tbody></table>';
							}else{
								var lname = return_data["layer_name"];
								var year = return_data["year"];
								var source = return_data["source"];
								popup_content = '<table border="1"><tbody><tr><th>Layer Name</th><th>Source</th><th>Year</th></tr>'+
									'<tr><td>'+lname+'</td><td>'+source+'</td><td>'+year+'</td></tr></tbody></table>';
							}
						}else if("error" in return_data){
							console.log(return_data["error"]);
						}

						// popup_content = generate_popup_content(id);
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
				if (layer != layers[0] && layer != layers[1] && layer != layers[2] && layer != layers[3]){
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
			if( i == 'FLD_HAZ_AR'|| i == 'WTR_AR' ){
				var lyr_name = vli_layers[val];

				$('<li class="ui-state-default"' + 'layer-name="' + lyr_name + '"' + '><input class="chkbx-layer" type="checkbox" checked><span class="layer-name">' + lyr_name + '</span><div class="hmbrgr-div"><img src="/static/glo_vli/images/hamburger.svg"></div></li>').appendTo('#current-layers');
				var $list_item = $('#current-layers').find('li:last-child');
				var cql_str = 'layer_name=' + '\'' + lyr_name + '\' AND approved=True';
				// if(i == 'FLD_HAZ_AR'){
				// 	var style = 'glo_vli:floodhaz';
				// }else{
				// 	var style= 'glo_vli:floodzone';
				// }

				// addContextMenuToListItem($list_item);
				wms_source = new ol.source.ImageWMS({
					url: gs_wms_url,
					params: {
						'LAYERS': 'glo_vli:polygons',
						'CQL_FILTER': cql_str,
						// 'STYLES': style
					},
					serverType: 'geoserver',
					crossOrigin: 'Anonymous'
				});
				// 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
				wms_layer = new ol.layer.Image({
					source: wms_source,
					name:lyr_name,
					visible:true,
					title: lyr_name
				});
				map.addLayer(wms_layer);

				layersDict[lyr_name] = wms_layer;
			}
			else
			{
				var lyr_name = vli_layers[val];
				// if(i == 'LowWaterCrossings'){
				// 	var style = 'point';
				// }else{
				// 	var style= 'glo_vli:star';
				// }

				$('<li class="ui-state-default"' + 'layer-name="' + lyr_name + '"' + '><input class="chkbx-layer" type="checkbox" checked><span class="layer-name">' + lyr_name + '</span><div class="hmbrgr-div"><img src="/static/glo_vli/images/hamburger.svg"></div></li>').appendTo('#current-layers');
				var $list_item = $('#current-layers').find('li:last-child');
				var cql_str = 'layer_name=' + '\'' + lyr_name + '\' AND approved=True';

				// addContextMenuToListItem($list_item);
				wms_source = new ol.source.ImageWMS({
					url: gs_wms_url,
					params: {
						'LAYERS': 'glo_vli:points',
						'CQL_FILTER': cql_str,
						// 'STYLES': style
					},
					serverType: 'geoserver',
					crossOrigin: 'Anonymous'
				});
				// 'CQL_FILTER': 'layer_name=\'HighWaterMarks_Int\''
				wms_layer = new ol.layer.Image({
					source: wms_source,
					name:lyr_name,
					visible:true,
					title: lyr_name
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
		$("#select-county").change(function() {
			var counties = ($("#select-county").val());

			if(counties){
				var county_str = "'" + counties.join("','") + "'";
				counties_source.updateParams({'CQL_FILTER': 'CNTY_NM IN ('+ county_str +')'});
				for (var key in layersDict) {
					var layer_source = layersDict[key].getSource();
					var layer_name = layersDict[key].get('name');
					map.getLayers().forEach(function (el) {
						if (el.get('name') == key) {
							console.log(el.get('name'));
							layer_source.updateParams({'CQL_FILTER': 'county IN ('+ county_str +')'});
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
						if (el.get('name') == key) {
							layer_source.updateParams({'CQL_FILTER': 'county IN ('+ county_str +')'});
						}
					});
				}
			}

		});
	});

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
