from django.urls import path
from . import views_proprietario

urlpatterns = [
    # Dashboard consolidado do proprietário
    path('produtor/<int:produtor_id>/dashboard/', 
         views_proprietario.proprietario_dashboard, 
         name='proprietario_dashboard'),
    
    # Módulos consolidados
    path('produtor/<int:produtor_id>/dividas-consolidadas/', 
         views_proprietario.proprietario_dividas_consolidadas, 
         name='proprietario_dividas_consolidadas'),
    
    path('produtor/<int:produtor_id>/capacidade-consolidada/', 
         views_proprietario.proprietario_capacidade_consolidada, 
         name='proprietario_capacidade_consolidada'),
    
    path('produtor/<int:produtor_id>/imobilizado-consolidado/', 
         views_proprietario.proprietario_imobilizado_consolidado, 
         name='proprietario_imobilizado_consolidado'),
    
    path('produtor/<int:produtor_id>/analise-consolidada/', 
         views_proprietario.proprietario_analise_consolidada, 
         name='proprietario_analise_consolidada'),
    
    path('produtor/<int:produtor_id>/relatorios-consolidados/', 
         views_proprietario.proprietario_relatorios_consolidados, 
         name='proprietario_relatorios_consolidados'),
]

