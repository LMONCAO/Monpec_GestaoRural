from django.urls import path
from . import views

urlpatterns = [
    # URLs principais
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs de proprietários
    path('proprietarios/', views.proprietarios_lista, name='proprietarios_lista'),
    path('proprietarios/novo/', views.proprietario_novo, name='proprietario_novo'),
    
    # URLs de propriedades
    path('propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    
    # URLs de módulos
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard'),
    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard'),
    
    # URLs de categorias e inventário
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('propriedade/<int:propriedade_id>/inventario/', views.inventario_lista, name='inventario_lista'),
]
