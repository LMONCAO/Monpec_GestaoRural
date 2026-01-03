from django.urls import path
from . import views_analise

urlpatterns = [
    # URLs para análise
    path('propriedade/<int:propriedade_id>/analise/', 
         views_analise.analise_dashboard, 
         name='analise_dashboard'),
    
    path('propriedade/<int:propriedade_id>/analise/indicadores/', 
         views_analise.indicadores_lista, 
         name='indicadores_lista'),
    
    path('propriedade/<int:propriedade_id>/analise/indicador/novo/', 
         views_analise.indicador_novo, 
         name='indicador_novo'),
    
    path('propriedade/<int:propriedade_id>/analise/indicador/<int:indicador_id>/editar/', 
         views_analise.indicador_editar, 
         name='indicador_editar'),
    
    path('propriedade/<int:propriedade_id>/analise/calcular-automaticos/', 
         views_analise.calcular_indicadores_automaticos, 
         name='calcular_indicadores_automaticos'),
    
    path('propriedade/<int:propriedade_id>/analise/relatorio/', 
         views_analise.relatorio_analise, 
         name='relatorio_analise'),
]

