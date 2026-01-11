from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods


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


@require_http_methods(["GET"])
@cache_page(3600)  # Cache por 1 hora
def sitemap_view(request):
    """
    View customizada para servir o sitemap.
    Garante acesso público sem autenticação.
    """
    from django.contrib.sitemaps.views import sitemap as django_sitemap
    
    sitemaps = {
        'static': StaticViewSitemap,
        'public': PublicContentSitemap,
    }
    
    return django_sitemap(request, sitemaps)

















