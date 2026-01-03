from django.urls import path
from . import views_vendas

urlpatterns = [
    # URLs para parâmetros de venda por categoria
    path('propriedade/<int:propriedade_id>/vendas-por-categoria/', 
         views_vendas.vendas_por_categoria_lista, 
         name='vendas_por_categoria_lista'),
    
    path('propriedade/<int:propriedade_id>/vendas-por-categoria/novo/', 
         views_vendas.vendas_por_categoria_novo, 
         name='vendas_por_categoria_novo'),
    
    path('propriedade/<int:propriedade_id>/vendas-por-categoria/<int:parametro_id>/editar/', 
         views_vendas.vendas_por_categoria_editar, 
         name='vendas_por_categoria_editar'),
    
    path('propriedade/<int:propriedade_id>/vendas-por-categoria/bulk/', 
         views_vendas.vendas_por_categoria_bulk, 
         name='vendas_por_categoria_bulk'),
    
    path('propriedade/<int:propriedade_id>/vendas-por-categoria/<int:parametro_id>/excluir/', 
         views_vendas.vendas_por_categoria_excluir, 
         name='vendas_por_categoria_excluir'),
    
    path('propriedade/<int:propriedade_id>/vendas-por-categoria/<int:parametro_id>/toggle-status/', 
         views_vendas.vendas_por_categoria_toggle_status, 
         name='vendas_por_categoria_toggle_status'),
]

