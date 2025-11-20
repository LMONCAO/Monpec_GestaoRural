from django.urls import path
from . import views

urlpatterns = [
    # URLs principais
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs de produtores
    path('produtor/novo/', views.produtor_novo, name='produtor_novo'),
    path('produtor/<int:produtor_id>/editar/', views.produtor_editar, name='produtor_editar'),
    path('produtor/<int:produtor_id>/propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('produtor/<int:produtor_id>/propriedade/nova/', views.produtor_nova, name='propriedade_nova'),
    
    # URLs de propriedades
    path('propriedade/<int:propriedade_id>/editar/', views.propriedade_editar, name='propriedade_editar'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard'),
    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard'),
    
    # URLs gerais
    path('propriedades/', views.propriedades_lista, name='propriedades_lista_sem_id'),
    path('categorias/', views.categorias_lista, name='categorias_lista'),
]
