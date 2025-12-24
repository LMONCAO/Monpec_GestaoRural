"""
Middleware para versão de demonstração restrita
Bloqueia acesso a todas as rotas exceto as permitidas
"""
from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve
import re


class DemoRestrictionMiddleware:
    """
    Middleware que restringe acesso em modo demo
    Permite apenas:
    - /propriedade/2/pecuaria/dashboard/
    - /propriedade/2/curral/painel/
    - /login/
    - /comprar-sistema/ (página de compra)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rotas permitidas em modo demo
        self.allowed_paths = [
            r'^/login/',
            r'^/logout/',
            r'^/comprar-sistema/',
            r'^/assinaturas/',  # Página de assinaturas/compra
            r'^/propriedade/\d+/modulos/',  # Página de módulos de qualquer propriedade
            r'^/propriedade/\d+/pecuaria/',  # Módulo de pecuária de qualquer propriedade
            r'^/propriedade/\d+/curral/',  # Módulo de curral de qualquer propriedade
            r'^/propriedade/\d+/nutricao/',  # Módulo de nutrição de qualquer propriedade
            r'^/propriedade/\d+/financeiro/',  # Módulo financeiro de qualquer propriedade
            r'^/propriedade/\d+/compras/',  # Módulo de compras de qualquer propriedade
            r'^/propriedade/\d+/imobilizado/',  # Módulo de bens e patrimônio de qualquer propriedade
            r'^/propriedade/\d+/planejamento/',  # Módulo de planejamento de qualquer propriedade
            r'^/dashboard/',  # Dashboard principal
            r'^/$',  # Página inicial
            r'^/static/',
            r'^/media/',
            r'^/admin/',
            r'^/sitemap\.xml$',  # Sitemap para SEO
            r'^/google.*\.html$',  # Arquivos de verificação Google
        ]
        
        # Rotas de API permitidas (se necessário)
        self.allowed_api_paths = [
            r'^/propriedade/2/pecuaria/dashboard/consulta/',
        ]
        
        # Permitir também rotas que começam com as permitidas (para sub-rotas)
        self.allowed_paths_regex = [
            r'^/propriedade/\d+/pecuaria',
            r'^/propriedade/\d+/curral',
            r'^/propriedade/\d+/nutricao',
            r'^/propriedade/\d+/financeiro',
            r'^/propriedade/\d+/compras',
            r'^/propriedade/\d+/imobilizado',
            r'^/propriedade/\d+/planejamento',
            r'^/propriedade/\d+/modulos',
        ]
    
    def __call__(self, request):
        # Verificar se está em modo demo
        if not getattr(settings, 'DEMO_MODE', False):
            return self.get_response(request)
        
        # Se o usuário for demo_monpec ou demo, permitir acesso completo (não bloquear)
        if request.user.is_authenticated:
            if request.user.username == 'demo_monpec' or request.user.username == 'demo':
                return self.get_response(request)
        
        # Verificar se a rota é permitida
        path = request.path
        
        # Permitir rotas estáticas e de mídia
        if any(re.match(pattern, path) for pattern in self.allowed_paths):
            return self.get_response(request)
        
        # Permitir rotas que começam com os padrões permitidos (para sub-rotas)
        if any(re.match(pattern, path) for pattern in self.allowed_paths_regex):
            return self.get_response(request)
        
        # Bloquear todas as outras rotas
        # Redirecionar para página de compra
        return redirect('comprar_sistema')


