from django.urls import path
from . import views_endividamento

urlpatterns = [
    # URLs para endividamento
    path('propriedade/<int:propriedade_id>/endividamento/', 
         views_endividamento.dividas_financeiras_dashboard, 
         name='endividamento_dashboard'),
    
    path('propriedade/<int:propriedade_id>/endividamento/financiamentos/', 
         views_endividamento.financiamentos_lista, 
         name='financiamentos_lista'),
    
    path('propriedade/<int:propriedade_id>/endividamento/financiamento/novo/', 
         views_endividamento.financiamento_novo, 
         name='financiamento_novo'),
    
    path('propriedade/<int:propriedade_id>/endividamento/financiamento/<int:financiamento_id>/editar/', 
         views_endividamento.financiamento_editar, 
         name='financiamento_editar'),
    
    path('propriedade/<int:propriedade_id>/endividamento/financiamento/<int:financiamento_id>/excluir/', 
         views_endividamento.financiamento_excluir, 
         name='financiamento_excluir'),
    
    path('propriedade/<int:propriedade_id>/endividamento/financiamento/<int:financiamento_id>/amortizacao/', 
         views_endividamento.calcular_amortizacao, 
         name='calcular_amortizacao'),
    
    # URLs para tipos de financiamento
    path('endividamento/tipos/', 
         views_endividamento.tipos_financiamento_lista, 
         name='tipos_financiamento_lista'),
    
    path('endividamento/tipo/novo/', 
         views_endividamento.tipo_financiamento_novo, 
         name='tipo_financiamento_novo'),
]
