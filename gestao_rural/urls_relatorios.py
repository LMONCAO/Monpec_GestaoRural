from django.urls import path
from . import views_relatorios

urlpatterns = [
    # URLs para relatórios
    path('propriedade/<int:propriedade_id>/relatorios/', 
         views_relatorios.relatorios_dashboard, 
         name='relatorios_dashboard'),
    
    path('propriedade/<int:propriedade_id>/relatorios/inventario/', 
         views_relatorios.relatorio_inventario, 
         name='relatorio_inventario'),
    
    path('propriedade/<int:propriedade_id>/relatorios/financeiro/', 
         views_relatorios.relatorio_financeiro, 
         name='relatorio_financeiro'),
    
    path('propriedade/<int:propriedade_id>/relatorios/custos/', 
         views_relatorios.relatorio_custos, 
         name='relatorio_custos'),
    
    path('propriedade/<int:propriedade_id>/relatorios/endividamento/', 
         views_relatorios.relatorio_endividamento, 
         name='relatorio_endividamento'),
    
    path('propriedade/<int:propriedade_id>/relatorios/consolidado/', 
         views_relatorios.relatorio_consolidado, 
         name='relatorio_consolidado'),
]

