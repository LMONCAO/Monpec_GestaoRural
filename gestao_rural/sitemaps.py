from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """
    Sitemap para páginas estáticas e públicas do site MONPEC.
    """
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Lista de nomes de URLs públicas acessíveis sem login
        return [
            'landing_page',
            'pre_lancamento',  # Página de pré-lançamento
        ]

    def location(self, item):
        return reverse(item)


class PublicContentSitemap(Sitemap):
    """
    Sitemap para conteúdo público adicional.
    """
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        # URLs públicas adicionais que podem ser indexadas
        return [
            'assinaturas_dashboard',  # Página de planos (pode ser acessada publicamente)
        ]

    def location(self, item):
        return reverse(item)


















