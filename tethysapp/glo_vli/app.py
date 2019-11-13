from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, PersistentStoreConnectionSetting


class GloVli(TethysAppBase):
    """
    Tethys app class for Vulnerability of Life and Infrastructure.
    """

    name = 'Vulnerability of Life and Infrastructure'
    index = 'glo_vli:home'
    icon = 'glo_vli/images/logo.jpg'
    package = 'glo_vli'
    root_url = 'glo-vli'
    color = '#16a085'
    description = 'Vulnerability of Life and Infrastructure'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='glo-vli',
                controller='glo_vli.controllers.home'
            ),
            UrlMap(
                name='popup-info',
                url='glo-vli/popup-info',
                controller='glo_vli.controllers_ajax.get_popup_info'
            ),
            UrlMap(
                name='get-meta-file',
                url='glo-vli/get-meta-file',
                controller='glo_vli.controllers_ajax.get_meta_file'
            ),
            UrlMap(
                name='add-point',
                url='glo-vli/add-point',
                controller='glo_vli.controllers.add_point'
            ),
            UrlMap(
                name='delete-layer',
                url='glo-vli/delete-layer',
                controller='glo_vli.controllers.delete_layer'
            ),
            UrlMap(
                name='submit-delete-layer',
                url='glo-vli/delete-layer/submit',
                controller='glo_vli.controllers_ajax.layer_delete'
            ),
            UrlMap(
                name='add-point-ajax',
                url='glo-vli/add-point/submit',
                controller='glo_vli.controllers_ajax.point_add'
            ),
            UrlMap(
                name='approve-points',
                url='glo-vli/approve-points',
                controller='glo_vli.controllers.approve_points'
            ),
            UrlMap(
                name='approve-points_tabulator',
                url='glo-vli/approve-points/tabulator',
                controller='glo_vli.controllers_ajax.points_tabulator'
            ),
            UrlMap(
                name='update-points-ajax',
                url='glo-vli/approve-points/submit',
                controller='glo_vli.controllers_ajax.point_update'
            ),
            UrlMap(
                name='delete-points-ajax',
                url='glo-vli/approve-points/delete',
                controller='glo_vli.controllers_ajax.point_delete'
            ),
            UrlMap(
                name='add-polygon',
                url='glo-vli/add-polygon',
                controller='glo_vli.controllers.add_polygon'
            ),
            UrlMap(
                name='add-polygon-ajax',
                url='glo-vli/add-polygon/submit',
                controller='glo_vli.controllers_ajax.polygon_add'
            ),
            UrlMap(
                name='approve-polygons',
                url='glo-vli/approve-polygons',
                controller='glo_vli.controllers.approve_polygons'
            ),
            UrlMap(
                name='approve-polygons-tabulator',
                url='glo-vli/approve-polygons/tabulator',
                controller='glo_vli.controllers_ajax.polygons_tabulator'
            ),
            UrlMap(
                name='update-polygons-ajax',
                url='glo-vli/approve-polygons/submit',
                controller='glo_vli.controllers_ajax.polygon_update'
            ),
            UrlMap(
                name='delete-polygons-ajax',
                url='glo-vli/approve-polygons/delete',
                controller='glo_vli.controllers_ajax.polygon_delete'
            ),
            UrlMap(
                name='add-new-layer',
                url='glo-vli/add-new-layer',
                controller='glo_vli.controllers.add_new_layer'
            ),
            UrlMap(
                name='get-new-layer-attributes',
                url='glo-vli/add-new-layer/get-attributes',
                controller='glo_vli.controllers_ajax.get_shp_attributes'
            ),
            UrlMap(
                name='add-new-layer-ajax',
                url='glo-vli/add-new-layer/submit',
                controller='glo_vli.controllers_ajax.new_layer_add'
            ),
            UrlMap(
                name='set-layer-style',
                url='glo-vli/set-layer-style',
                controller='glo_vli.controllers.set_layer_style'
            ),
            UrlMap(
                name='set-layer-style-ajax',
                url='glo-vli/set-layer-style/submit',
                controller='glo_vli.controllers_ajax.layer_style_set'
            ),
            UrlMap(
                name='add-endpoint',
                url='glo-vli/add-endpoint',
                controller='glo_vli.controllers.add_endpoint'
            ),
            UrlMap(
                name='add-endpoint-submit',
                url='glo-vli/add-endpoint/submit',
                controller='glo_vli.controllers_ajax.endpoint_add'
            ),
            UrlMap(
                name='delete-endpoint',
                url='glo-vli/delete-endpoint',
                controller='glo_vli.controllers.delete_endpoint'
            ),
            UrlMap(
                name='delete-endpoint-submit',
                url='glo-vli/delete-endpoint/submit',
                controller='glo_vli.controllers_ajax.endpoint_delete'
            ),
            UrlMap(
                name='get-layers-info',
                url='glo-vli/api/get-layers-info',
                controller='glo_vli.api.get_layers_info'
            ),
            UrlMap(
                name='get-layers-by-county',
                url='glo-vli/api/get-layers-by-county',
                controller='glo_vli.api.get_layers_by_county'
            ),
            UrlMap(
                name='get-points-by-county',
                url='glo-vli/api/get-points-by-county',
                controller='glo_vli.api.get_points_by_county'
            ),
            UrlMap(
                name='get-polygons-by-county',
                url='glo-vli/api/get-polygons-by-county',
                controller='glo_vli.api.get_polygons_by_county'
            ),
            UrlMap(
                name='get-points-by-layer',
                url='glo-vli/api/get-points-by-layer',
                controller='glo_vli.api.get_points_by_layer'
            ),
            UrlMap(
                name='get-polygons-by-layer',
                url='glo-vli/api/get-polygons-by-layer',
                controller='glo_vli.api.get_polygons_by_layer'
            ),
        )

        return url_maps

    def persistent_store_settings(self):
        """
        Define Persistent Store Settings.
        """
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='layers',
                description='layers database',
                initializer='glo_vli.model.init_layer_db',
                required=True,
                spatial=True
            ),
            PersistentStoreConnectionSetting(
                name='primary',
                description='Connection to Layers DB',
                required=True
            ),
        )

        return ps_settings
