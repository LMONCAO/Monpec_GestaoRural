from django.urls import path, include
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Gestão de produtores
    path('produtor/novo/', views.produtor_novo, name='produtor_novo'),
    path('produtor/<int:produtor_id>/editar/', views.produtor_editar, name='produtor_editar'),
    path('produtor/<int:produtor_id>/excluir/', views.produtor_excluir, name='produtor_excluir'),
    
    # Gestão de propriedades
    path('produtor/<int:produtor_id>/propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('produtor/<int:produtor_id>/propriedade/nova/', views.propriedade_nova, name='propriedade_nova'),
    path('propriedade/<int:propriedade_id>/editar/', views.propriedade_editar, name='propriedade_editar'),
    path('propriedade/<int:propriedade_id>/excluir/', views.propriedade_excluir, name='propriedade_excluir'),
    
    # Módulo Pecuária
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/inventario/', views.pecuaria_inventario, name='pecuaria_inventario'),
    path('propriedade/<int:propriedade_id>/pecuaria/parametros/', views.pecuaria_parametros, name='pecuaria_parametros'),
    path('propriedade/<int:propriedade_id>/pecuaria/parametros-avancados/', views.pecuaria_parametros_avancados, name='pecuaria_parametros_avancados'),
    path('propriedade/<int:propriedade_id>/pecuaria/testar-transferencias/', views.testar_transferencias, name='testar_transferencias'),
    path('api/saldo-fazenda/<int:fazenda_id>/<int:categoria_id>/', views.obter_saldo_fazenda_ajax, name='obter_saldo_fazenda_ajax'),
    path('propriedade/<int:propriedade_id>/inventario/saldo/<int:categoria_id>/', views.buscar_saldo_inventario, name='buscar_saldo_inventario'),
    path('propriedade/<int:propriedade_id>/pecuaria/projecao/', views.pecuaria_projecao, name='pecuaria_projecao'),
    path('propriedade/<int:propriedade_id>/pecuaria/inventario/dados/', views.pecuaria_inventario_dados, name='pecuaria_inventario_dados'),
    
    # Módulo Agricultura
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/ciclo/novo/', views.agricultura_ciclo_novo, name='agricultura_ciclo_novo'),
    
    # Relatório Final
    path('propriedade/<int:propriedade_id>/relatorio-final/', views.relatorio_final, name='relatorio_final'),
    
    # Transferências entre Propriedades
    path('transferencias/', views.transferencias_lista, name='transferencias_lista'),
    path('transferencias/nova/', views.transferencia_nova, name='transferencia_nova'),
    path('transferencias/<int:transferencia_id>/editar/', views.transferencia_editar, name='transferencia_editar'),
    path('transferencias/<int:transferencia_id>/excluir/', views.transferencia_excluir, name='transferencia_excluir'),
    
    # Gestão de Categorias de Animais
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('categorias/nova/', views.categoria_nova, name='categoria_nova'),
    path('categorias/<int:categoria_id>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:categoria_id>/excluir/', views.categoria_excluir, name='categoria_excluir'),
    
    # Gestão de Custos
    path('custos/', include('gestao_rural.urls_custos')),
    
    # Gestão de Vendas por Categoria
    path('vendas/', include('gestao_rural.urls_vendas')),
    
    # Gestão de Endividamento
    path('endividamento/', include('gestao_rural.urls_endividamento')),
    
    # Gestão de Análise
    path('analise/', include('gestao_rural.urls_analise')),
    
    # Gestão de Relatórios
    path('relatorios/', include('gestao_rural.urls_relatorios')),
    
    # Gestão de Projetos Bancários
    path('projetos-bancarios/', include('gestao_rural.urls_projetos_bancarios')),
    
    # Gestão de Imobilizado
    path('imobilizado/', include('gestao_rural.urls_imobilizado')),
    
    # Gestão de Capacidade de Pagamento
    path('capacidade-pagamento/', include('gestao_rural.urls_capacidade_pagamento')),
    
    # Gestão Consolidada do Proprietário
    path('proprietario/', include('gestao_rural.urls_proprietario')),
]
