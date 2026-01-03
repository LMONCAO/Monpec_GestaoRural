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
    
    # URLs para exportação de relatórios
    path('propriedade/<int:propriedade_id>/relatorios/inventario/exportar/pdf/', 
         views_relatorios.exportar_relatorio_inventario_pdf, 
         name='exportar_relatorio_inventario_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/inventario/exportar/excel/', 
         views_relatorios.exportar_relatorio_inventario_excel, 
         name='exportar_relatorio_inventario_excel'),
    
    path('propriedade/<int:propriedade_id>/relatorios/financeiro/exportar/pdf/', 
         views_relatorios.exportar_relatorio_financeiro_pdf, 
         name='exportar_relatorio_financeiro_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/financeiro/exportar/excel/', 
         views_relatorios.exportar_relatorio_financeiro_excel, 
         name='exportar_relatorio_financeiro_excel'),
    
    path('propriedade/<int:propriedade_id>/relatorios/custos/exportar/pdf/', 
         views_relatorios.exportar_relatorio_custos_pdf, 
         name='exportar_relatorio_custos_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/custos/exportar/excel/', 
         views_relatorios.exportar_relatorio_custos_excel, 
         name='exportar_relatorio_custos_excel'),
    
    path('propriedade/<int:propriedade_id>/relatorios/endividamento/exportar/pdf/', 
         views_relatorios.exportar_relatorio_endividamento_pdf, 
         name='exportar_relatorio_endividamento_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/endividamento/exportar/excel/', 
         views_relatorios.exportar_relatorio_endividamento_excel, 
         name='exportar_relatorio_endividamento_excel'),
    
    path('propriedade/<int:propriedade_id>/relatorios/consolidado/exportar/pdf/', 
         views_relatorios.exportar_relatorio_consolidado_pdf, 
         name='exportar_relatorio_consolidado_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/consolidado/exportar/excel/', 
         views_relatorios.exportar_relatorio_consolidado_excel, 
         name='exportar_relatorio_consolidado_excel'),
    
    # Relatórios por Módulo
    path('propriedade/<int:propriedade_id>/relatorios/pecuaria/pdf/', 
         views_relatorios.relatorio_pecuaria_pdf, 
         name='relatorio_pecuaria_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/nutricao/pdf/', 
         views_relatorios.relatorio_nutricao_pdf, 
         name='relatorio_nutricao_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/operacoes/pdf/', 
         views_relatorios.relatorio_operacoes_pdf, 
         name='relatorio_operacoes_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/compras/pdf/', 
         views_relatorios.relatorio_compras_pdf, 
         name='relatorio_compras_pdf'),
    
    path('propriedade/<int:propriedade_id>/relatorios/projetos-bancarios/pdf/', 
         views_relatorios.relatorio_projetos_bancarios_pdf, 
         name='relatorio_projetos_bancarios_pdf'),
]

