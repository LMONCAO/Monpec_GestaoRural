from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from gestao_rural import views as gestao_views
from gestao_rural import views_curral
from gestao_rural import views_sitemap
from gestao_rural import views_password_reset
from gestao_rural import views_static
from gestao_rural import views_media
from gestao_rural import views_diagnostico_imagens
from gestao_rural import views_animais_offline
from gestao_rural import views_assinaturas

urlpatterns = [
    # APENAS nossa URL de teste
    path('teste-usuarios/', views_assinaturas.usuarios_assinantes, name='teste_usuarios'),
]