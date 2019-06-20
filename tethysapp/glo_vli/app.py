from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting

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
                name='add-point',
                url='glo-vli/add-point',
                controller='glo_vli.controllers.add_point'
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
        )

        return ps_settings