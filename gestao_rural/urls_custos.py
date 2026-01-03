from django.urls import path
from . import views_custos

urlpatterns = [
    path('propriedade/<int:propriedade_id>/custos/', views_custos.custos_dashboard, name='custos_dashboard'),
    path('propriedade/<int:propriedade_id>/custos/fixos/', views_custos.custos_fixos_lista, name='custos_fixos_lista'),
    path('propriedade/<int:propriedade_id>/custos/fixos/novo/', views_custos.custos_fixos_novo, name='custos_fixos_novo'),
    path('propriedade/<int:propriedade_id>/custos/variaveis/', views_custos.custos_variaveis_lista, name='custos_variaveis_lista'),
    path('propriedade/<int:propriedade_id>/custos/fixos/<int:custo_id>/editar/', views_custos.custos_fixos_editar, name='custos_fixos_editar'),
    path('propriedade/<int:propriedade_id>/custos/fixos/<int:custo_id>/excluir/', views_custos.custos_fixos_excluir, name='custos_fixos_excluir'),
    path('propriedade/<int:propriedade_id>/custos/variaveis/novo/', views_custos.custos_variaveis_novo, name='custos_variaveis_novo'),
    path('propriedade/<int:propriedade_id>/custos/variaveis/<int:custo_id>/editar/', views_custos.custos_variaveis_editar, name='custos_variaveis_editar'),
    path('propriedade/<int:propriedade_id>/custos/variaveis/<int:custo_id>/excluir/', views_custos.custos_variaveis_excluir, name='custos_variaveis_excluir'),
    path('propriedade/<int:propriedade_id>/custos/calcular-fluxo/', views_custos.calcular_fluxo_caixa, name='calcular_fluxo_caixa'),
]

