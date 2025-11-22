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

urlpatterns = [
    # Logout deve vir antes do admin para garantir que use nossa view personalizada
    path('logout/', gestao_views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('', gestao_views.landing_page, name='landing_page'),
    path('contato/', gestao_views.contato_submit, name='contato_submit'),
    
    # Curral Dashboard v3 - Adicionado diretamente para garantir que funcione
    path('propriedade/<int:propriedade_id>/curral/v3/', views_curral.curral_dashboard_v3, name='curral_dashboard_v3'),
    
    # Recuperação de senha
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/recuperar-senha/enviado/',
    ), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),
    path('recuperar-senha/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/recuperar-senha/concluido/',
    ), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
    
    path('', include('gestao_rural.urls')),
]

# Servir arquivos estáticos em modo desenvolvimento (DEBUG=True)
if settings.DEBUG:
    # Servir arquivos estáticos (CSS, JS, imagens)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Servir arquivos de mídia se existir MEDIA_URL e MEDIA_ROOT
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

