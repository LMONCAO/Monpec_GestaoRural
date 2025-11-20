from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proprietarios/', views.proprietarios_lista, name='proprietarios_lista'),
    path('proprietarios/novo/', views.proprietario_novo, name='proprietario_novo'),
    path('propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard'),
    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard'),
    path('propriedade/<int:propriedade_id>/relatorio/', views.relatorio_final, name='relatorio_final'),
]
