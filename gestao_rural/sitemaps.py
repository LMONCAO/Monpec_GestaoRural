from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """
    Sitemap para páginas estáticas do site.
    """
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Lista de nomes de URLs estáticas
        return [
            'landing_page',
            # Adicione outras URLs públicas aqui
        ]

    def location(self, item):
        return reverse(item)


















