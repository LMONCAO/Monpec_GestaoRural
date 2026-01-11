"""
URL configuration for sistema_rural project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from gestao_rural import views as gestao_views
from gestao_rural import views_curral
from gestao_rural import views_sitemap
from gestao_rural import views_password_reset
from gestao_rural import views_static
from gestao_rural import views_media
from gestao_rural import views_diagnostico_imagens
from gestao_rural import views_animais_offline

urlpatterns = [
    # Health check endpoint (deve vir primeiro para ser encontrado rapidamente)
    path('health/', gestao_views.health_check, name='health_check'),

    # Página offline para PWA
    path('offline/', gestao_views.offline_page, name='offline'),

    # LANDING PAGE COM VÍDEO - DEVE VIR PRIMEIRO (página inicial)
    path('', gestao_views.landing_page, name='landing_page'),
    
    # Curral Dashboard v3 e v4 - DEVE VIR PRIMEIRO para garantir que seja encontrado
    path('propriedade/<int:propriedade_id>/curral/', views_curral.curral_tela_unica, name='curral_tela_unica'),
    path('propriedade/<int:propriedade_id>/curral/v4/', views_curral.curral_dashboard_v4, name='curral_dashboard_v4'),
    path('propriedade/<int:propriedade_id>/curral/v3/', views_curral.curral_dashboard_v3, name='curral_dashboard_v3'),
    
    # Logout deve vir antes do admin para garantir que use nossa view personalizada
    path('logout/', gestao_views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('contato/', gestao_views.contato_submit, name='contato_submit'),
    
    # Google Search Console Verification
    path('google40933139f3b0d469.html', gestao_views.google_search_console_verification, name='google_search_console_verification'),

    # Robots.txt
    path('robots.txt', gestao_views.robots_txt, name='robots_txt'),

    # Sitemap (view customizada para garantir acesso público)
    path('sitemap.xml', views_sitemap.sitemap_view, name='sitemap'),
    
    # Recuperação de senha (customizada para bloquear usuários demo)
    path('recuperar-senha/', views_password_reset.CustomPasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/recuperar-senha/enviado/',
    ), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('recuperar-senha/confirmar/<uidb64>/<token>/', views_password_reset.CustomPasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/recuperar-senha/concluido/',
    ), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
    
    # Rota customizada para servir arquivos estáticos (FALLBACK)
    # IMPORTANTE: Esta rota funciona como fallback se WhiteNoise não servir o arquivo
    # WhiteNoise tem prioridade (middleware), mas se falhar, esta view serve o arquivo
    # A ordem importa: esta rota deve vir ANTES do include('gestao_rural.urls')
    path('static/<path:path>', views_static.serve_static_file, name='serve_static'),
    
    # Rota para servir arquivos media (fotos, uploads) em produção
    path('media/<path:path>', views_media.serve_media, name='serve_media'),
    
    # Diagnóstico de imagens (útil para debug)
    path('diagnostico-imagens/', views_diagnostico_imagens.diagnostico_imagens, name='diagnostico_imagens'),
    
    path('', include('gestao_rural.urls')),
]

# Servir arquivos estáticos e media files
# Em desenvolvimento (DEBUG=True): usar static() do Django
# Em produção: WhiteNoise serve static files automaticamente
# Media files serão servidos via WhiteNoise também (se configurado) ou via view customizada

# Importar serve para produção
from django.views.static import serve

# Servir arquivos estáticos - SEMPRE em desenvolvimento
# O helper static() do Django já cria a rota correta
if settings.STATICFILES_DIRS:
    static_root = settings.STATICFILES_DIRS[0]
    urlpatterns += static(settings.STATIC_URL, document_root=static_root)
    
if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Modo produção: servir media files manualmente (WhiteNoise já serve static files)
    # IMPORTANTE: Media files precisam ser servidos manualmente em produção
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
        # Adicionar rota para servir media files
        # Usar path completo para evitar conflitos
        media_url = settings.MEDIA_URL.rstrip('/')
        if media_url:
            # Adicionar antes do include('gestao_rural.urls') mas depois das rotas principais
            # Usar função lambda para servir arquivos de media
            urlpatterns.insert(-1, path(
                f'{media_url}/<path:path>',
                lambda request, path: serve(request, path, document_root=settings.MEDIA_ROOT),
                name='serve_media'
            ))

