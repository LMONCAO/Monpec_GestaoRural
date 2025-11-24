from django.urls import path, include
from . import views
from . import views_exportacao
from . import views_cenarios
from . import views_rastreabilidade
from . import views_relatorios_rastreabilidade
from . import views_pecuaria_completa
from . import views_nutricao
from . import views_operacoes
from . import views_compras
from . import views_financeiro
from . import views_financeiro_avancado
from . import views_funcionarios
from . import views_iatf_completo
from . import views_curral
from . import views_pesagem
from . import views_assinaturas
from . import views_usuarios_tenant
from . import views_seguranca
from . import views_relatorios_customizados
from . import views_demo
from . import views_whatsapp

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    # Logout está definido no urls.py principal para garantir redirecionamento correto
    
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),

    # Assinaturas e Stripe
    path('assinaturas/', views_assinaturas.assinaturas_dashboard, name='assinaturas_dashboard'),
    path('assinaturas/plano/<slug:plano_slug>/checkout/', views_assinaturas.iniciar_checkout, name='assinaturas_checkout'),
    path('assinaturas/sucesso/', views_assinaturas.checkout_sucesso, name='assinaturas_sucesso'),
    path('assinaturas/cancelado/', views_assinaturas.checkout_cancelado, name='assinaturas_cancelado'),
    path('assinaturas/webhook/', views_assinaturas.stripe_webhook, name='stripe_webhook'),
    
    # Gestão de usuários do tenant
    path('usuarios/', views_usuarios_tenant.tenant_usuarios_dashboard, name='tenant_usuarios_dashboard'),
    path('usuarios/<int:usuario_id>/<str:acao>/', views_usuarios_tenant.tenant_usuario_toggle, name='tenant_usuario_toggle'),
    
    # Segurança
    path('verificar-email/<str:token>/', views_seguranca.verificar_email, name='verificar_email'),
    path('reenviar-email-verificacao/', views_seguranca.reenviar_email_verificacao, name='reenviar_email_verificacao'),
    path('logs-auditoria/', views_seguranca.logs_auditoria, name='logs_auditoria'),
    path('seguranca/', views_seguranca.informacoes_seguranca, name='informacoes_seguranca'),
    
    # Gestão de produtores
    path('produtor/novo/', views.produtor_novo, name='produtor_novo'),
    path('produtor/<int:produtor_id>/editar/', views.produtor_editar, name='produtor_editar'),
    path('produtor/<int:produtor_id>/excluir/', views.produtor_excluir, name='produtor_excluir'),
    
    # Gestão de propriedades
    path('produtor/<int:produtor_id>/propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('produtor/<int:produtor_id>/propriedade/nova/', views.propriedade_nova, name='propriedade_nova'),
    path('propriedade/<int:propriedade_id>/editar/', views.propriedade_editar, name='propriedade_editar'),
    path('propriedade/<int:propriedade_id>/excluir/', views.propriedade_excluir, name='propriedade_excluir'),
    
    # Dashboard de Módulos
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    
    # Módulo Pecuária Completa (Consolidado)
    path('propriedade/<int:propriedade_id>/pecuaria/', views_pecuaria_completa.pecuaria_completa_dashboard, name='pecuaria_completa_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/dashboard/', views_pecuaria_completa.pecuaria_completa_dashboard, name='pecuaria_dashboard'),  # Alias para compatibilidade
    path('propriedade/<int:propriedade_id>/pecuaria/dashboard/consulta/', views_pecuaria_completa.dashboard_consulta_api, name='dashboard_consulta_api'),
    path('propriedade/<int:propriedade_id>/pecuaria/inventario/', views.pecuaria_inventario, name='pecuaria_inventario'),
    path('propriedade/<int:propriedade_id>/pecuaria/parametros/', views.pecuaria_parametros, name='pecuaria_parametros'),
    path('propriedade/<int:propriedade_id>/pecuaria/parametros-avancados/', views.pecuaria_parametros_avancados, name='pecuaria_parametros_avancados'),
    path('propriedade/<int:propriedade_id>/pecuaria/testar-transferencias/', views.testar_transferencias, name='testar_transferencias'),
    path('api/saldo-fazenda/<int:fazenda_id>/<int:categoria_id>/', views.obter_saldo_fazenda_ajax, name='obter_saldo_fazenda_ajax'),
    path('propriedade/<int:propriedade_id>/inventario/saldo/<int:categoria_id>/', views.buscar_saldo_inventario, name='buscar_saldo_inventario'),
    path('propriedade/<int:propriedade_id>/pecuaria/projecao/', views.pecuaria_projecao, name='pecuaria_projecao'),
    path('propriedade/<int:propriedade_id>/pecuaria/planejamento/', views_pecuaria_completa.pecuaria_planejamento_dashboard, name='pecuaria_planejamento_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/planejamento/api/', views_pecuaria_completa.pecuaria_planejamentos_api, name='pecuaria_planejamentos_api'),
    path('propriedade/<int:propriedade_id>/pecuaria/planejamento/<int:planejamento_id>/resumo/', views_pecuaria_completa.pecuaria_planejamento_resumo_api, name='pecuaria_planejamento_resumo_api'),
    path('propriedade/<int:propriedade_id>/pecuaria/cenarios/', views_cenarios.analise_cenarios, name='analise_cenarios'),
    path('propriedade/<int:propriedade_id>/pecuaria/cenarios/criar/', views_cenarios.criar_cenario, name='criar_cenario'),
    path('propriedade/<int:propriedade_id>/pecuaria/cenarios/<int:cenario_id>/editar/', views_cenarios.editar_cenario, name='editar_cenario'),
    path('propriedade/<int:propriedade_id>/pecuaria/cenarios/<int:cenario_id>/excluir/', views_cenarios.excluir_cenario, name='excluir_cenario'),
    path('propriedade/<int:propriedade_id>/pecuaria/cenarios/api/comparar/', views_cenarios.comparar_cenarios_api, name='comparar_cenarios_api'),
    path('propriedade/<int:propriedade_id>/pecuaria/inventario/dados/', views.pecuaria_inventario_dados, name='pecuaria_inventario_dados'),
    
    # Rastreabilidade (dentro de Pecuária) - Comentado pois as funções estão em views_rastreabilidade
    # path('propriedade/<int:propriedade_id>/pecuaria/rastreabilidade/animais/', views_pecuaria_completa.animais_individuais_lista, name='animais_individuais_lista'),
    # path('propriedade/<int:propriedade_id>/pecuaria/rastreabilidade/animal/novo/', views_pecuaria_completa.animal_individual_novo, name='animal_individual_novo'),
    # path('propriedade/<int:propriedade_id>/pecuaria/rastreabilidade/animal/<int:animal_id>/', views_pecuaria_completa.animal_individual_detalhes, name='animal_individual_detalhes'),
    
    # Reprodução (dentro de Pecuária)
    path('propriedade/<int:propriedade_id>/pecuaria/reproducao/', views_pecuaria_completa.reproducao_dashboard, name='reproducao_dashboard'),
    # path('propriedade/<int:propriedade_id>/pecuaria/reproducao/touros/', views_pecuaria_completa.touros_lista, name='touros_lista'),
    # path('propriedade/<int:propriedade_id>/pecuaria/reproducao/touro/novo/', views_pecuaria_completa.touro_novo, name='touro_novo'),
    # path('propriedade/<int:propriedade_id>/pecuaria/reproducao/estacao-monta/nova/', views_pecuaria_completa.estacao_monta_nova, name='estacao_monta_nova'),
    # path('propriedade/<int:propriedade_id>/pecuaria/reproducao/iatf/nova/', views_pecuaria_completa.iatf_nova, name='iatf_nova'),
    path('propriedade/<int:propriedade_id>/pecuaria/pesagens/', views_pesagem.pesagem_dashboard, name='pesagem_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/pesagens/nova/', views_pesagem.pesagem_nova, name='pesagem_nova'),
    
    # IATF Completo (Sistema Avançado)
    path('propriedade/<int:propriedade_id>/iatf/', views_iatf_completo.iatf_dashboard, name='iatf_dashboard'),
    path('propriedade/<int:propriedade_id>/iatf/lotes/', views_iatf_completo.lotes_iatf_lista, name='lotes_iatf_lista'),
    path('propriedade/<int:propriedade_id>/iatf/lote/novo/', views_iatf_completo.lote_iatf_novo, name='lote_iatf_novo'),
    path('propriedade/<int:propriedade_id>/iatf/lote/<int:lote_id>/', views_iatf_completo.lote_iatf_detalhes, name='lote_iatf_detalhes'),
    path('propriedade/<int:propriedade_id>/iatf/individual/novo/', views_iatf_completo.iatf_individual_novo, name='iatf_individual_novo'),
    path('propriedade/<int:propriedade_id>/iatf/individual/<int:iatf_id>/', views_iatf_completo.iatf_individual_detalhes, name='iatf_individual_detalhes'),
    path('propriedade/<int:propriedade_id>/iatf/individual/<int:iatf_id>/aplicacao/', views_iatf_completo.iatf_registrar_aplicacao, name='iatf_registrar_aplicacao'),
    path('propriedade/<int:propriedade_id>/iatf/individual/<int:iatf_id>/inseminacao/', views_iatf_completo.iatf_registrar_inseminacao, name='iatf_registrar_inseminacao'),
    path('propriedade/<int:propriedade_id>/iatf/individual/<int:iatf_id>/diagnostico/', views_iatf_completo.iatf_registrar_diagnostico, name='iatf_registrar_diagnostico'),
    path('propriedade/<int:propriedade_id>/iatf/lista/', views_iatf_completo.iatfs_lista, name='iatfs_lista'),
    path('propriedade/<int:propriedade_id>/iatf/relatorio/', views_iatf_completo.iatf_relatorio, name='iatf_relatorio'),
    path('propriedade/<int:propriedade_id>/iatf/relatorio/etapas/', views_iatf_completo.iatf_relatorio_etapas, name='iatf_relatorio_etapas'),
    path('propriedade/<int:propriedade_id>/iatf/relatorio/etapas/pdf/', views_iatf_completo.iatf_relatorio_etapas_pdf, name='iatf_relatorio_etapas_pdf'),
    path('propriedade/<int:propriedade_id>/iatf/protocolos/', views_iatf_completo.protocolos_iatf_lista, name='protocolos_iatf_lista'),
    path('propriedade/<int:propriedade_id>/iatf/touros-semen/', views_iatf_completo.touros_semen_lista, name='touros_semen_lista'),
    path('propriedade/<int:propriedade_id>/iatf/lotes-semen/', views_iatf_completo.lotes_semen_lista, name='lotes_semen_lista'),

    # Super Tela de Curral / Manejo
    # Rotas específicas devem vir ANTES da rota genérica
    path('propriedade/<int:propriedade_id>/curral/v3/', views_curral.curral_dashboard_v3, name='curral_dashboard_v3'),
    path('propriedade/<int:propriedade_id>/curral/painel/', views_curral.curral_painel, name='curral_painel'),
    path('propriedade/<int:propriedade_id>/curral/tela-unica/', views_curral.curral_tela_unica, name='curral_tela_unica'),
    path('propriedade/<int:propriedade_id>/curral/', views_curral.curral_dashboard, name='curral_dashboard'),
    path('propriedade/<int:propriedade_id>/curral/sessao/<int:sessao_id>/', views_curral.curral_sessao, name='curral_sessao'),
    path('propriedade/<int:propriedade_id>/curral/sessao/<int:sessao_id>/evento/', views_curral.curral_registrar_evento, name='curral_registrar_evento'),
    path('propriedade/<int:propriedade_id>/curral/sessao/<int:sessao_id>/lote/', views_curral.curral_criar_lote, name='curral_criar_lote'),
    path('propriedade/<int:propriedade_id>/curral/sessao/<int:sessao_id>/encerrar/', views_curral.curral_encerrar_sessao, name='curral_encerrar_sessao'),
    path('propriedade/<int:propriedade_id>/curral/sessao/<int:sessao_id>/relatorio/', views_curral.curral_relatorio, name='curral_relatorio'),
    path('propriedade/<int:propriedade_id>/curral/relatorio/reprodutivo/', views_curral.curral_relatorio_reprodutivo, name='curral_relatorio_reprodutivo'),
    path('propriedade/<int:propriedade_id>/curral/relatorio/iatf/', views_curral.curral_relatorio_iatf, name='curral_relatorio_iatf'),
    path('propriedade/<int:propriedade_id>/curral/api/identificar/', views_curral.curral_identificar_codigo, name='curral_identificar_codigo'),
    path('propriedade/<int:propriedade_id>/curral/api/dados-simulacao/', views_curral.curral_dados_simulacao, name='curral_dados_simulacao'),
    path('propriedade/<int:propriedade_id>/curral/api/animal/atualizar/', views_curral.curral_atualizar_animal_api, name='curral_atualizar_animal_api'),
    path('propriedade/<int:propriedade_id>/curral/api/registrar/', views_curral.curral_registrar_manejo, name='curral_registrar_manejo'),
    path('propriedade/<int:propriedade_id>/curral/api/animal/<int:animal_id>/registros/', views_curral.curral_registros_animal, name='curral_registros_animal'),
    path('propriedade/<int:propriedade_id>/curral/api/animal/<int:animal_id>/pesagens/', views_curral.curral_historico_pesagens, name='curral_historico_pesagens'),
    path('propriedade/<int:propriedade_id>/curral/api/animal/<int:animal_id>/manejos/', views_curral.curral_historico_manejos, name='curral_historico_manejos'),
    path('propriedade/<int:propriedade_id>/curral/api/balanca/peso/', views_curral.curral_receber_peso_balanca, name='curral_receber_peso_balanca'),
    path('propriedade/<int:propriedade_id>/curral/api/sincronizar/', views_curral.curral_sincronizar_offline, name='curral_sincronizar_offline'),
    path('propriedade/<int:propriedade_id>/curral/api/sessao/criar/', views_curral.curral_criar_sessao_api, name='curral_criar_sessao_api'),
    path('propriedade/<int:propriedade_id>/curral/api/sessao/encerrar/', views_curral.curral_encerrar_sessao_api, name='curral_encerrar_sessao_api'),
    path('propriedade/<int:propriedade_id>/curral/api/sessao/stats/', views_curral.curral_stats_sessao_api, name='curral_stats_sessao_api'),
    path('propriedade/<int:propriedade_id>/curral/api/stats/', views_curral.curral_stats_api, name='curral_stats_api'),
    path('propriedade/<int:propriedade_id>/curral/api/pesagem/', views_curral.curral_salvar_pesagem_api, name='curral_salvar_pesagem_api'),
    path('propriedade/<int:propriedade_id>/curral/api/pesagem/editar/', views_curral.curral_editar_pesagem_api, name='curral_editar_pesagem_api'),
    path('propriedade/<int:propriedade_id>/curral/api/manejos/registrar/', views_curral.curral_registrar_manejos_api, name='curral_registrar_manejos_api'),
    
    # Módulo Nutrição
    path('propriedade/<int:propriedade_id>/nutricao/', views_nutricao.nutricao_dashboard, name='nutricao_dashboard'),
    path('propriedade/<int:propriedade_id>/nutricao/suplementacao/estoques/', views_nutricao.estoque_suplementacao_lista, name='estoque_suplementacao_lista'),
    path('propriedade/<int:propriedade_id>/nutricao/suplementacao/compra/nova/', views_nutricao.compra_suplementacao_nova, name='compra_suplementacao_nova'),
    path('propriedade/<int:propriedade_id>/nutricao/suplementacao/distribuicao/nova/', views_nutricao.distribuicao_suplementacao_nova, name='distribuicao_suplementacao_nova'),
    path('propriedade/<int:propriedade_id>/nutricao/cochos/', views_nutricao.cochos_lista, name='cochos_lista'),
    path('propriedade/<int:propriedade_id>/nutricao/cochos/controle/novo/', views_nutricao.controle_cocho_novo, name='controle_cocho_novo'),
    
    # Módulo Operações
    path('propriedade/<int:propriedade_id>/operacoes/', views_operacoes.operacoes_dashboard, name='operacoes_dashboard'),
    path('propriedade/<int:propriedade_id>/operacoes/combustivel/', views_operacoes.combustivel_lista, name='combustivel_lista'),
    path('propriedade/<int:propriedade_id>/operacoes/combustivel/consumo/novo/', views_operacoes.consumo_combustivel_novo, name='consumo_combustivel_novo'),
    path('propriedade/<int:propriedade_id>/operacoes/equipamentos/', views_operacoes.equipamentos_lista, name='equipamentos_lista'),
    path('propriedade/<int:propriedade_id>/operacoes/manutencao/nova/', views_operacoes.manutencao_nova, name='manutencao_nova'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/', views_funcionarios.funcionarios_dashboard, name='funcionarios_dashboard'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/lista/', views_funcionarios.funcionarios_lista, name='funcionarios_lista'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/novo/', views_funcionarios.funcionario_novo, name='funcionario_novo'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/folha/processar/', views_funcionarios.folha_pagamento_processar, name='folha_pagamento_processar'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/folha/<int:folha_id>/', views_funcionarios.folha_pagamento_detalhes, name='folha_pagamento_detalhes'),
    path('propriedade/<int:propriedade_id>/operacoes/funcionarios/holerite/<int:holerite_id>/pdf/', views_funcionarios.holerite_pdf, name='holerite_pdf'),
    
    # Módulo Compras
    path('propriedade/<int:propriedade_id>/compras/', views_compras.compras_dashboard, name='compras_dashboard'),
    path('propriedade/<int:propriedade_id>/compras/setores/', views_compras.setores_compra_lista, name='setores_compra_lista'),
    path('propriedade/<int:propriedade_id>/compras/setores/novo/', views_compras.setor_compra_novo, name='setor_compra_novo'),
    path('propriedade/<int:propriedade_id>/compras/setores/<int:setor_id>/editar/', views_compras.setor_compra_editar, name='setor_compra_editar'),
    path('propriedade/<int:propriedade_id>/compras/setores/<int:setor_id>/status/', views_compras.setor_compra_alterar_status, name='setor_compra_alterar_status'),
    path('propriedade/<int:propriedade_id>/compras/requisicoes/', views_compras.requisicoes_compra_lista, name='requisicoes_compra_lista'),
    path('propriedade/<int:propriedade_id>/compras/requisicao/nova/', views_compras.requisicao_compra_nova, name='requisicao_compra_nova'),
    path('propriedade/<int:propriedade_id>/compras/requisicao/<int:requisicao_id>/', views_compras.requisicao_compra_detalhes, name='requisicao_compra_detalhes'),
    path('propriedade/<int:propriedade_id>/compras/requisicao/<int:requisicao_id>/cotacao/nova/', views_compras.cotacao_fornecedor_nova, name='cotacao_fornecedor_nova'),
    path('propriedade/<int:propriedade_id>/compras/orcamentos/', views_compras.orcamentos_compra_lista, name='orcamentos_compra_lista'),
    path('propriedade/<int:propriedade_id>/compras/fornecedores/', views_compras.fornecedores_lista, name='fornecedores_lista'),
    path('propriedade/<int:propriedade_id>/compras/fornecedor/novo/', views_compras.fornecedor_novo, name='fornecedor_novo'),
    path('propriedade/<int:propriedade_id>/compras/ordens/', views_compras.ordens_compra_lista, name='ordens_compra_lista'),
    path('propriedade/<int:propriedade_id>/compras/ordem/nova/', views_compras.ordem_compra_nova, name='ordem_compra_nova'),
    path('propriedade/<int:propriedade_id>/compras/ordem/<int:ordem_id>/', views_compras.ordem_compra_detalhes, name='ordem_compra_detalhes'),
    path('propriedade/<int:propriedade_id>/compras/ordem/<int:ordem_id>/recebimento/', views_compras.recebimento_compra_novo, name='recebimento_compra_novo'),
    path('propriedade/<int:propriedade_id>/compras/notas-fiscais/', views_compras.notas_fiscais_lista, name='notas_fiscais_lista'),
    path('propriedade/<int:propriedade_id>/compras/nota-fiscal/upload/', views_compras.nota_fiscal_upload, name='nota_fiscal_upload'),
    path('propriedade/<int:propriedade_id>/compras/nota-fiscal/<int:nota_id>/', views_compras.nota_fiscal_detalhes, name='nota_fiscal_detalhes'),
    
    # Módulo Financeiro (novo)
    path('propriedade/<int:propriedade_id>/financeiro/', views_financeiro.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/lancamentos/', views_financeiro.lancamentos_lista, name='financeiro_lancamentos'),
    path('propriedade/<int:propriedade_id>/financeiro/lancamentos/novo/', views_financeiro.lancamento_novo, name='financeiro_lancamento_novo'),
    path('propriedade/<int:propriedade_id>/financeiro/lancamentos/<int:lancamento_id>/editar/', views_financeiro.lancamento_editar, name='financeiro_lancamento_editar'),
    path('propriedade/<int:propriedade_id>/financeiro/lancamentos/<int:lancamento_id>/quitar/', views_financeiro.lancamento_quitar, name='financeiro_lancamento_quitar'),
    path('propriedade/<int:propriedade_id>/financeiro/lancamentos/<int:lancamento_id>/cancelar/', views_financeiro.lancamento_cancelar, name='financeiro_lancamento_cancelar'),
    path('propriedade/<int:propriedade_id>/financeiro/contas/', views_financeiro.contas_financeiras_lista, name='financeiro_contas'),
    path('propriedade/<int:propriedade_id>/financeiro/contas/nova/', views_financeiro.conta_financeira_nova, name='financeiro_conta_nova'),
    path('propriedade/<int:propriedade_id>/financeiro/contas/<int:conta_id>/editar/', views_financeiro.conta_financeira_editar, name='financeiro_conta_editar'),
    path('propriedade/<int:propriedade_id>/financeiro/categorias/', views_financeiro.categorias_lista, name='financeiro_categorias'),
    path('propriedade/<int:propriedade_id>/financeiro/categorias/nova/', views_financeiro.categoria_nova, name='financeiro_categoria_nova'),
    path('propriedade/<int:propriedade_id>/financeiro/categorias/<int:categoria_id>/editar/', views_financeiro.categoria_editar, name='financeiro_categoria_editar'),
    path('propriedade/<int:propriedade_id>/financeiro/centros-custo/', views_financeiro.centros_custo_lista, name='financeiro_centros_custo'),
    path('propriedade/<int:propriedade_id>/financeiro/centros-custo/nova/', views_financeiro.centro_custo_novo, name='financeiro_centro_custo_novo'),
    path('propriedade/<int:propriedade_id>/financeiro/centros-custo/<int:centro_id>/editar/', views_financeiro.centro_custo_editar, name='financeiro_centro_custo_editar'),
    
    # Contas a Pagar
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/', views_financeiro.contas_pagar_lista, name='financeiro_contas_pagar'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/nova/', views_financeiro.conta_pagar_nova, name='financeiro_conta_pagar_nova'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/<int:conta_id>/editar/', views_financeiro.conta_pagar_editar, name='financeiro_conta_pagar_editar'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-pagar/<int:conta_id>/pagar/', views_financeiro.conta_pagar_pagar, name='financeiro_conta_pagar_pagar'),
    
    # Contas a Receber
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/', views_financeiro.contas_receber_lista, name='financeiro_contas_receber'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/nova/', views_financeiro.conta_receber_nova, name='financeiro_conta_receber_nova'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/<int:conta_id>/editar/', views_financeiro.conta_receber_editar, name='financeiro_conta_receber_editar'),
    path('propriedade/<int:propriedade_id>/financeiro/contas-receber/<int:conta_id>/receber/', views_financeiro.conta_receber_receber, name='financeiro_conta_receber_receber'),
    
    # Conciliação Bancária
    path('propriedade/<int:propriedade_id>/financeiro/conciliacao/', views_financeiro_avancado.conciliacao_bancaria, name='financeiro_conciliacao'),
    path('propriedade/<int:propriedade_id>/financeiro/conciliacao/marcar/', views_financeiro_avancado.conciliacao_marcar_conciliado, name='financeiro_conciliacao_marcar'),
    
    # Boletos
    path('propriedade/<int:propriedade_id>/financeiro/boletos/', views_financeiro_avancado.boletos_lista, name='financeiro_boletos'),
    path('propriedade/<int:propriedade_id>/financeiro/boletos/<int:conta_receber_id>/gerar/', views_financeiro_avancado.boleto_gerar, name='financeiro_boleto_gerar'),
    
    # Fluxo de Caixa Detalhado
    path('propriedade/<int:propriedade_id>/financeiro/fluxo-caixa/', views_financeiro_avancado.fluxo_caixa_detalhado, name='financeiro_fluxo_caixa'),
    
    # DRE - Demonstração do Resultado do Exercício
    path('propriedade/<int:propriedade_id>/financeiro/dre/', views_financeiro_avancado.dre, name='financeiro_dre'),
    
    # LCDPR - Livro Caixa e Demonstração de Pagamentos e Recebimentos
    path('propriedade/<int:propriedade_id>/financeiro/lcdpr/', views_financeiro_avancado.lcdpr, name='financeiro_lcdpr'),
    path('propriedade/<int:propriedade_id>/financeiro/lcdpr/exportar/pdf/', views_financeiro_avancado.lcdpr_exportar_pdf, name='financeiro_lcdpr_exportar_pdf'),
    path('propriedade/<int:propriedade_id>/financeiro/lcdpr/exportar/excel/', views_financeiro_avancado.lcdpr_exportar_excel, name='financeiro_lcdpr_exportar_excel'),
    
    # Exportações DRE
    path('propriedade/<int:propriedade_id>/financeiro/dre/exportar/pdf/', views_financeiro_avancado.dre_exportar_pdf, name='financeiro_dre_exportar_pdf'),
    path('propriedade/<int:propriedade_id>/financeiro/dre/exportar/excel/', views_financeiro_avancado.dre_exportar_excel, name='financeiro_dre_exportar_excel'),
    
    # Exportação
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/inventario/excel/', views_exportacao.exportar_inventario_excel, name='exportar_inventario_excel'),
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/inventario/pdf/', views_exportacao.exportar_inventario_pdf, name='exportar_inventario_pdf'),
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/projecao/excel/', views_exportacao.exportar_projecao_excel, name='exportar_projecao_excel'),
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/projecao/pdf/', views_exportacao.exportar_projecao_pdf, name='exportar_projecao_pdf'),
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/iatf/excel/', views_exportacao.exportar_iatf_excel, name='exportar_iatf_excel'),
    path('propriedade/<int:propriedade_id>/pecuaria/exportar/iatf/pdf/', views_exportacao.exportar_iatf_pdf, name='exportar_iatf_pdf'),
    
    # Módulo Dívidas Financeiras
    path('propriedade/<int:propriedade_id>/dividas/', views.dividas_dashboard, name='dividas_dashboard'),
    path('propriedade/<int:propriedade_id>/dividas/importar-scr/', views.importar_scr, name='importar_scr'),
    path('propriedade/<int:propriedade_id>/dividas/reprocessar-scr/<int:scr_id>/', views.reprocessar_scr, name='reprocessar_scr'),
    path('propriedade/<int:propriedade_id>/dividas/distribuir/<int:scr_id>/', views.distribuir_dividas_por_fazenda, name='distribuir_dividas'),
    path('propriedade/<int:propriedade_id>/dividas/contratos/', views.dividas_contratos, name='dividas_contratos'),
    path('propriedade/<int:propriedade_id>/dividas/amortizacao/', views.dividas_amortizacao, name='dividas_amortizacao'),
    
    # Módulo Projeto Bancário
    path('propriedade/<int:propriedade_id>/projeto-bancario/', views.projeto_bancario_dashboard, name='projeto_bancario_dashboard'),
    path('propriedade/<int:propriedade_id>/projeto-bancario/novo/', views.projeto_bancario_novo, name='projeto_bancario_novo'),
    path('propriedade/<int:propriedade_id>/projeto-bancario/<int:projeto_id>/', views.projeto_bancario_detalhes, name='projeto_bancario_detalhes'),
    path('propriedade/<int:propriedade_id>/projeto-bancario/<int:projeto_id>/editar/', views.projeto_bancario_editar, name='projeto_bancario_editar'),
    
    # Relatório Final
    path('propriedade/<int:propriedade_id>/relatorio-final/', views.relatorio_final, name='relatorio_final'),
    
    # Transferências entre Propriedades
    path('transferencias/', views.transferencias_lista, name='transferencias_lista'),
    
    # API para valor do inventário
    path('api/valor-inventario/<int:propriedade_id>/<int:categoria_id>/', views.api_valor_inventario, name='api_valor_inventario'),
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
    
    # Sistema de Rastreabilidade Bovina - PNIB
    path('propriedade/<int:propriedade_id>/rastreabilidade/', views_rastreabilidade.rastreabilidade_dashboard, name='rastreabilidade_dashboard'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/importar-bnd/', views_rastreabilidade.importar_bnd_sisbov, name='importar_bnd_sisbov'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/animais/', views_rastreabilidade.animais_individuais_lista, name='animais_individuais_lista'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/animal/novo/', views_rastreabilidade.animal_individual_novo, name='animal_individual_novo'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/animal/<int:animal_id>/', views_rastreabilidade.animal_individual_detalhes, name='animal_individual_detalhes'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/animal/<int:animal_id>/editar/', views_rastreabilidade.animal_individual_editar, name='animal_individual_editar'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/animal/<int:animal_id>/movimentacao/nova/', views_rastreabilidade.movimentacao_individual_nova, name='movimentacao_individual_nova'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/brincos/', views_rastreabilidade.brincos_lista, name='brincos_lista'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/brinco/lote/excluir/', views_rastreabilidade.brinco_excluir_lote, name='brinco_excluir_lote'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/brinco/lote/', views_rastreabilidade.brinco_cadastrar_lote, name='brinco_cadastrar_lote'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/brinco/importar/', views_rastreabilidade.brinco_importar_lista, name='brinco_importar_lista'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/', views_rastreabilidade.relatorio_rastreabilidade, name='relatorio_rastreabilidade'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/dia/', views_rastreabilidade.relatorio_dia_barcodes, name='relatorio_dia_barcodes'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/inventario/', views_rastreabilidade.relatorio_inventario_sisbov, name='relatorio_inventario_sisbov'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/movimentacoes/', views_rastreabilidade.relatorio_movimentacoes_sisbov, name='relatorio_movimentacoes_sisbov'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/entradas/', views_rastreabilidade.relatorio_entradas_sisbov, name='relatorio_entradas_sisbov'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/saidas/', views_rastreabilidade.relatorio_saidas_sisbov, name='relatorio_saidas_sisbov'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/saidas/pdf/', views_relatorios_rastreabilidade.exportar_saidas_sisbov_pdf, name='exportar_saidas_sisbov_pdf'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/sanitario/', views_rastreabilidade.relatorio_sanitario_sisbov, name='relatorio_sanitario_sisbov'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/api/proximo-brinco/', views_rastreabilidade.api_gerar_numero_brinco, name='api_gerar_numero_brinco'),
    
    # Relatórios Obrigatórios de Rastreabilidade - PNIB
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/identificacao-individual/', views_relatorios_rastreabilidade.relatorio_identificacao_individual, name='relatorio_identificacao_individual'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/movimentacao-animais/', views_relatorios_rastreabilidade.relatorio_movimentacao_animais, name='relatorio_movimentacao_animais'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/sanitario/', views_relatorios_rastreabilidade.relatorio_sanitario, name='relatorio_sanitario'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/gta/', views_relatorios_rastreabilidade.relatorio_gta, name='relatorio_gta'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/gta/<int:movimentacao_id>/', views_relatorios_rastreabilidade.relatorio_gta, name='relatorio_gta_detalhe'),
    
    # Exportação de Relatórios PNIB
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/identificacao-individual/pdf/', views_relatorios_rastreabilidade.exportar_identificacao_individual_pdf, name='exportar_identificacao_individual_pdf'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios/movimentacao-animais/pdf/', views_relatorios_rastreabilidade.exportar_movimentacao_animais_pdf, name='exportar_movimentacao_animais_pdf'),
    
    # Exportação de Anexos IN 51/MAPA - PDF
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-i/pdf/', views_relatorios_rastreabilidade.exportar_anexo_i_pdf, name='exportar_anexo_i_pdf'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-ii/pdf/', views_relatorios_rastreabilidade.exportar_anexo_ii_pdf, name='exportar_anexo_ii_pdf'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-iii/pdf/', views_relatorios_rastreabilidade.exportar_anexo_iii_pdf, name='exportar_anexo_iii_pdf'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-iv/pdf/', views_relatorios_rastreabilidade.exportar_anexo_iv_pdf, name='exportar_anexo_iv_pdf'),
    
    # Exportação de Anexos IN 51/MAPA - Excel
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-i/excel/', views_relatorios_rastreabilidade.exportar_anexo_i_excel, name='exportar_anexo_i_excel'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-ii/excel/', views_relatorios_rastreabilidade.exportar_anexo_ii_excel, name='exportar_anexo_ii_excel'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-iii/excel/', views_relatorios_rastreabilidade.exportar_anexo_iii_excel, name='exportar_anexo_iii_excel'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorio/anexo-iv/excel/', views_relatorios_rastreabilidade.exportar_anexo_iv_excel, name='exportar_anexo_iv_excel'),
    path('propriedade/<int:propriedade_id>/compras/convites/', views_compras.convites_cotacao_lista, name='convites_cotacao_lista'),
    path('propriedade/<int:propriedade_id>/compras/convites/nova/', views_compras.convite_cotacao_novo, name='convite_cotacao_novo'),
    path('propriedade/<int:propriedade_id>/compras/convites/<int:convite_id>/cancelar/', views_compras.convite_cotacao_cancelar, name='convite_cotacao_cancelar'),
    path('compras/cotacao/responder/<str:token>/', views_compras.cotacao_fornecedor_responder_token, name='cotacao_fornecedor_responder_token'),
    
    # Relatórios Customizados (Criador de Relatórios)
    path('propriedade/<int:propriedade_id>/relatorios-customizados/', views_relatorios_customizados.relatorios_customizados_lista, name='relatorios_customizados_lista'),
    path('propriedade/<int:propriedade_id>/relatorios-customizados/criar/', views_relatorios_customizados.relatorio_customizado_criar, name='relatorio_customizado_criar'),
    path('propriedade/<int:propriedade_id>/relatorios-customizados/<int:relatorio_id>/editar/', views_relatorios_customizados.relatorio_customizado_editar, name='relatorio_customizado_editar'),
    path('propriedade/<int:propriedade_id>/relatorios-customizados/<int:relatorio_id>/executar/', views_relatorios_customizados.relatorio_customizado_executar, name='relatorio_customizado_executar'),
    path('propriedade/<int:propriedade_id>/relatorios-customizados/<int:relatorio_id>/excluir/', views_relatorios_customizados.relatorio_customizado_excluir, name='relatorio_customizado_excluir'),
    path('propriedade/<int:propriedade_id>/relatorios-customizados/<int:relatorio_id>/duplicar/', views_relatorios_customizados.relatorio_customizado_duplicar, name='relatorio_customizado_duplicar'),
    path('propriedade/<int:propriedade_id>/relatorios-customizados/api/campos/', views_relatorios_customizados.api_campos_disponiveis, name='api_campos_disponiveis'),
    
    # Demo - Página de compra
    path('comprar-sistema/', views_demo.comprar_sistema, name='comprar_sistema'),
    
    # Integração WhatsApp - Registro de Nascimentos
    path('whatsapp/webhook/', views_whatsapp.whatsapp_webhook, name='whatsapp_webhook'),
    path('whatsapp/processar-audio/', views_whatsapp.whatsapp_processar_audio, name='whatsapp_processar_audio'),
    path('propriedade/<int:propriedade_id>/whatsapp/mensagens/', views_whatsapp.whatsapp_mensagens_lista, name='whatsapp_mensagens_lista'),
    path('whatsapp/mensagem/<int:mensagem_id>/reprocessar/', views_whatsapp.whatsapp_reprocessar, name='whatsapp_reprocessar'),
]
