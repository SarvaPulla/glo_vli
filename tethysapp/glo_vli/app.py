from tethys_sdk.base import TethysAppBase, url_map_maker


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
        )

        return url_maps
