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
 	var map,
        public_interface;				// Object returned by the module

		
		
	
	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var init_events,
        init_jquery_vars,
        init_all,
        init_map;

 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
 	init_jquery_vars = function(){
             
     };
             
    init_map = function(){
	map = new ol.Map({
        layers: [
          new ol.layer.Tile({
            source: new ol.source.OSM()
          })
        ],
        target: 'map',
        view: new ol.View({
          center: [0, 0],
          zoom: 2
        })
      });
    };
            
    init_events = function(){
            
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
