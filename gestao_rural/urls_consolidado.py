# -*- coding: utf-8 -*-
"""
URLs Consolidadas - Estrutura Otimizada
Agrupa módulos conforme análise de agrupamento
"""

from django.urls import path, include
from . import views
from . import views_pecuaria_completa
from . import views_nutricao
from . import views_operacoes
from . import views_compras
from . import views_financeiro
from . import views_funcionarios
from . import views_exportacao
from . import views_cenarios
from . import views_rastreabilidade
from . import views_relatorios_rastreabilidade

urlpatterns = [
    # ========== AUTENTICAÇÃO ==========
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    
    # ========== MÓDULO 1: PROPRIEDADES ==========
    path('produtor/novo/', views.produtor_novo, name='produtor_novo'),
    path('produtor/<int:produtor_id>/editar/', views.produtor_editar, name='produtor_editar'),
    path('produtor/<int:produtor_id>/excluir/', views.produtor_excluir, name='produtor_excluir'),
    path('produtor/<int:produtor_id>/propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('produtor/<int:produtor_id>/propriedade/nova/', views.propriedade_nova, name='propriedade_nova'),
    path('propriedade/<int:propriedade_id>/editar/', views.propriedade_editar, name='propriedade_editar'),
    path('propriedade/<int:propriedade_id>/excluir/', views.propriedade_excluir, name='propriedade_excluir'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    
    # ========== MÓDULO 2: PECUÁRIA COMPLETA ==========
    # Dashboard consolidado
    path('propriedade/<int:propriedade_id>/pecuaria/', views_pecuaria_completa.pecuaria_completa_dashboard, name='pecuaria_completa_dashboard'),
    
    # Inventário (mantém compatibilidade)
    path('propriedade/<int:propriedade_id>/pecuaria/inventario/', views.pecuaria_inventario, name='pecuaria_inventario'),
    path('propriedade/<int:propriedade_id>/pecuaria/parametros/', views.pecuaria_parametros, name='pecuaria_parametros'),
    path('propriedade/<int:propriedade_id>/pecuaria/projecao/', views.pecuaria_projecao, name='pecuaria_projecao'),
    path('propriedade/<int:propriedade_id>/pecuaria/planejamento/', views_pecuaria_completa.pecuaria_planejamento_dashboard, name='pecuaria_planejamento_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/planejamento/api/', views_pecuaria_completa.pecuaria_planejamentos_api, name='pecuaria_planejamentos_api'),
    path('propriedade/<int:propriedade_id>/pecuaria/planejamento/<int:planejamento_id>/resumo/', views_pecuaria_completa.pecuaria_planejamento_resumo_api, name='pecuaria_planejamento_resumo_api'),
    path('propriedade/<int:propriedade_id>/pecuaria/cenarios/', views_cenarios.analise_cenarios, name='analise_cenarios'),
    
    # Rastreabilidade (PNIB)
    path('propriedade/<int:propriedade_id>/pecuaria/rastreabilidade/animais/', views_pecuaria_completa.animais_individuais_lista, name='animais_individuais_lista'),
    path('propriedade/<int:propriedade_id>/pecuaria/rastreabilidade/animal/novo/', views_pecuaria_completa.animal_individual_novo, name='animal_individual_novo'),
    path('propriedade/<int:propriedade_id>/pecuaria/rastreabilidade/animal/<int:animal_id>/', views_pecuaria_completa.animal_individual_detalhes, name='animal_individual_detalhes'),
    
    # Reprodução
    path('propriedade/<int:propriedade_id>/pecuaria/reproducao/', views_pecuaria_completa.reproducao_dashboard, name='reproducao_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/reproducao/touros/', views_pecuaria_completa.touros_lista, name='touros_lista'),
    path('propriedade/<int:propriedade_id>/pecuaria/reproducao/touro/novo/', views_pecuaria_completa.touro_novo, name='touro_novo'),
    path('propriedade/<int:propriedade_id>/pecuaria/reproducao/estacao-monta/nova/', views_pecuaria_completa.estacao_monta_nova, name='estacao_monta_nova'),
    path('propriedade/<int:propriedade_id>/pecuaria/reproducao/iatf/nova/', views_pecuaria_completa.iatf_nova, name='iatf_nova'),
    
    # ========== MÓDULO 3: NUTRIÇÃO ==========
    path('propriedade/<int:propriedade_id>/nutricao/', views_nutricao.nutricao_dashboard, name='nutricao_dashboard'),
    path('propriedade/<int:propriedade_id>/nutricao/suplementacao/estoques/', views_nutricao.estoque_suplementacao_lista, name='estoque_suplementacao_lista'),
    path('propriedade/<int:propriedade_id>/nutricao/suplementacao/compra/nova/', views_nutricao.compra_suplementacao_nova, name='compra_suplementacao_nova'),
    path('propriedade/<int:propriedade_id>/nutricao/suplementacao/distribuicao/nova/', views_nutricao.distribuicao_suplementacao_nova, name='distribuicao_suplementacao_nova'),
    path('propriedade/<int:propriedade_id>/nutricao/cochos/', views_nutricao.cochos_lista, name='cochos_lista'),
    path('propriedade/<int:propriedade_id>/nutricao/cochos/controle/novo/', views_nutricao.controle_cocho_novo, name='controle_cocho_novo'),
    
    # ========== MÓDULO 4: PASTAGENS ==========
    # (Manter views existentes de rastreabilidade para pastagens)
    path('propriedade/<int:propriedade_id>/pastagens/', views_rastreabilidade.rastreabilidade_dashboard, name='pastagens_dashboard'),
    
    # ========== MÓDULO 5: SAÚDE ==========
    # (Manter views existentes de sanitário)
    
    # ========== MÓDULO 6: OPERAÇÕES ==========
    path('propriedade/<int:propriedade_id>/operacoes/', views_operacoes.operacoes_dashboard, name='operacoes_dashboard'),
    path('propriedade/<int:propriedade_id>/operacoes/combustivel/', views_operacoes.combustivel_lista, name='combustivel_lista'),
    path('propriedade/<int:propriedade_id>/operacoes/combustivel/consumo/novo/', views_operacoes.consumo_combustivel_novo, name='consumo_combustivel_novo'),
    path('propriedade/<int:propriedade_id>/operacoes/equipamentos/', views_operacoes.equipamentos_lista, name='equipamentos_lista'),
    path('propriedade/<int:propriedade_id>/operacoes/manutencao/nova/', views_operacoes.manutencao_nova, name='manutencao_nova'),
    
    # Funcionários
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/', views_funcionarios.funcionarios_dashboard, name='funcionarios_dashboard'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/lista/', views_funcionarios.funcionarios_lista, name='funcionarios_lista'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/novo/', views_funcionarios.funcionario_novo, name='funcionario_novo'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/folha/processar/', views_funcionarios.folha_pagamento_processar, name='folha_pagamento_processar'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/folha/<int:folha_id>/', views_funcionarios.folha_pagamento_detalhes, name='folha_pagamento_detalhes'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/holerite/<int:holerite_id>/pdf/', views_funcionarios.holerite_pdf, name='holerite_pdf'),
    
    # ========== MÓDULO 7: COMPRAS ==========
    path('propriedade/<int:propriedade_id>/compras/', views_compras.compras_dashboard, name='compras_dashboard'),
    path('propriedade/<int:propriedade_id>/compras/fornecedores/', views_compras.fornecedores_lista, name='fornecedores_lista'),
    path('propriedade/<int:propriedade_id>/compras/fornecedor/novo/', views_compras.fornecedor_novo, name='fornecedor_novo'),
    path('propriedade/<int:propriedade_id>/compras/ordens/', views_compras.ordens_compra_lista, name='ordens_compra_lista'),
    path('propriedade/<int:propriedade_id>/compras/ordem/nova/', views_compras.ordem_compra_nova, name='ordem_compra_nova'),
    path('propriedade/<int:propriedade_id>/compras/notas-fiscais/', views_compras.notas_fiscais_lista, name='notas_fiscais_lista'),
    path('propriedade/<int:propriedade_id>/compras/nota-fiscal/upload/', views_compras.nota_fiscal_upload, name='nota_fiscal_upload'),
    path('propriedade/<int:propriedade_id>/compras/nota-fiscal/<int:nota_id>/', views_compras.nota_fiscal_detalhes, name='nota_fiscal_detalhes'),
    
    # ========== MÓDULO 8: FINANCEIRO ==========
    path('propriedade/<int:propriedade_id>/financeiro/', views_financeiro.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/', views_financeiro.contas_pagar_lista, name='contas_pagar_lista'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/nova/', views_financeiro.conta_pagar_nova, name='conta_pagar_nova'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/<int:parcela_id>/pagar/', views_financeiro.conta_pagar_pagar, name='conta_pagar_pagar'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/', views_financeiro.contas_receber_lista, name='contas_receber_lista'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/nova/', views_financeiro.conta_receber_nova, name='conta_receber_nova'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/<int:parcela_id>/receber/', views_financeiro.conta_receber_receber, name='conta_receber_receber'),
    
    # ========== MÓDULO 11: PROJETOS BANCÁRIOS ==========
    # (Manter URLs existentes de projetos bancários)
    
    # ========== MÓDULO 12: RELATÓRIOS ==========
    # (Manter URLs existentes de relatórios)
    
    # ========== EXPORTAÇÃO ==========
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/inventario/excel/', views_exportacao.exportar_inventario_excel, name='exportar_inventario_excel'),
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/inventario/pdf/', views_exportacao.exportar_inventario_pdf, name='exportar_inventario_pdf'),
]


