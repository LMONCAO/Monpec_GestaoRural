from django.contrib import admin
from .models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    ParametrosProjecaoRebanho, MovimentacaoProjetada,
    RegraPromocaoCategoria, TransferenciaPropriedade, ConfiguracaoVenda,
    ParametrosVendaPorCategoria,
    CustoFixo, CustoVariavel, FluxoCaixa, AnimalIndividual,
    AnimalPesagem, AnimalVacinaAplicada, AnimalTratamento,
    AnimalReproducaoEvento, AnimalHistoricoEvento, AnimalDocumento,
    PlanoAssinatura, AssinaturaCliente, CurralLote, TenantWorkspace, TenantUsuario
)
from .models_auditoria import LogAuditoria, VerificacaoEmail, SessaoSegura
from .models_compras_financeiro import (
    SetorPropriedade,
    ConviteCotacaoFornecedor,
    Fornecedor,
    RequisicaoCompra,
    OrcamentoCompraMensal, AjusteOrcamentoCompra,
    Produto, CategoriaProduto,
)

# Importar modelos IATF se existirem
try:
    from .models_iatf_completo import (
        ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF, EtapaLoteIATF,
        IATFIndividual, AplicacaoMedicamentoIATF, CalendarioIATF
    )
    IATF_DISPONIVEL = True
except ImportError:
    IATF_DISPONIVEL = False

# Importar modelos de relatórios customizados
try:
    from .models_relatorios_customizados import RelatorioCustomizado, TemplateRelatorio
    RELATORIOS_CUSTOMIZADOS_DISPONIVEL = True
except ImportError:
    RELATORIOS_CUSTOMIZADOS_DISPONIVEL = False

# Importar modelos de marketing
try:
    from .models_marketing import (
        TemplatePost, PostGerado, LeadInteressado, CampanhaMarketing, ConfiguracaoMarketing
    )
    MARKETING_DISPONIVEL = True
except ImportError:
    MARKETING_DISPONIVEL = False


@admin.register(ProdutorRural)
class ProdutorRuralAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'documento_identidade', 'idade', 'anos_experiencia', 'usuario_responsavel', 'telefone', 'data_cadastro']
    list_filter = ['usuario_responsavel', 'data_cadastro', 'anos_experiencia']
    search_fields = ['nome', 'cpf_cnpj', 'documento_identidade', 'telefone', 'email']
    readonly_fields = ['data_cadastro', 'idade']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'cpf_cnpj', 'documento_identidade', 'data_nascimento', 'idade')
        }),
        ('Experiência', {
            'fields': ('anos_experiencia',)
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'endereco')
        }),
        ('Sistema', {
            'fields': ('usuario_responsavel', 'data_cadastro'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome_propriedade', 'produtor', 'municipio', 'uf', 'area_total_ha', 'tipo_operacao', 'display_ciclos_pecuarios', 'tipo_propriedade', 'valor_total_propriedade']
    list_filter = ['tipo_operacao', 'tipo_propriedade', 'uf', 'municipio']
    search_fields = ['nome_propriedade', 'produtor__nome', 'municipio', 'nirf', 'incra', 'car']
    readonly_fields = ['data_cadastro', 'valor_total_propriedade', 'valor_mensal_total_arrendamento']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_propriedade', 'produtor', 'municipio', 'uf', 'area_total_ha', 'tipo_operacao', 'tipo_ciclo_pecuario')
        }),
        ('Tipo de Propriedade', {
            'fields': ('tipo_propriedade', 'valor_hectare_proprio', 'valor_total_propriedade', 'valor_mensal_hectare_arrendamento', 'valor_mensal_total_arrendamento')
        }),
        ('Documentação', {
            'fields': ('nirf', 'incra', 'car')
        }),
        ('Sistema', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )

    def display_ciclos_pecuarios(self, obj):
        return obj.get_ciclos_pecuarios_display()
    display_ciclos_pecuarios.short_description = "Ciclos Pecuários"


@admin.register(CategoriaAnimal)
class CategoriaAnimalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sexo', 'raca', 'idade_minima_meses', 'idade_maxima_meses', 'peso_medio_kg', 'ativo']
    list_filter = ['sexo', 'raca', 'ativo']
    search_fields = ['nome', 'descricao']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Características', {
            'fields': ('sexo', 'raca', 'idade_minima_meses', 'idade_maxima_meses', 'peso_medio_kg')
        }),
    )


@admin.register(InventarioRebanho)
class InventarioRebanhoAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'categoria', 'quantidade', 'data_inventario']
    list_filter = ['propriedade', 'categoria', 'data_inventario']
    search_fields = ['propriedade__nome_propriedade', 'categoria__nome']


@admin.register(ParametrosProjecaoRebanho)
class ParametrosProjecaoRebanhoAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'taxa_natalidade_anual', 'periodicidade', 'data_criacao']
    list_filter = ['periodicidade', 'data_criacao']
    search_fields = ['propriedade__nome_propriedade']


@admin.register(MovimentacaoProjetada)
class MovimentacaoProjetadaAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'data_movimentacao', 'tipo_movimentacao', 'categoria', 'quantidade']
    list_filter = ['tipo_movimentacao', 'categoria', 'data_movimentacao']
    search_fields = ['propriedade__nome_propriedade', 'categoria__nome', 'observacao']


@admin.register(RegraPromocaoCategoria)
class RegraPromocaoCategoriaAdmin(admin.ModelAdmin):
    list_display = ['categoria_origem', 'categoria_destino', 'idade_minima_meses', 'idade_maxima_meses', 'ativo']
    list_filter = ['ativo', 'categoria_origem', 'categoria_destino']
    search_fields = ['categoria_origem__nome', 'categoria_destino__nome']


@admin.register(TransferenciaPropriedade)
class TransferenciaPropriedadeAdmin(admin.ModelAdmin):
    list_display = [
        'propriedade_origem', 'propriedade_destino', 'categoria', 'quantidade', 
        'data_transferencia', 'tipo_transferencia', 'status'
    ]
    list_filter = ['tipo_transferencia', 'status', 'categoria', 'data_transferencia']
    search_fields = [
        'propriedade_origem__nome_propriedade', 'propriedade_destino__nome_propriedade',
        'categoria__nome', 'observacao'
    ]
    readonly_fields = ['data_cadastro']
    fieldsets = (
        ('Informações da Transferência', {
            'fields': ('propriedade_origem', 'propriedade_destino', 'categoria', 'quantidade')
        }),
        ('Datas e Status', {
            'fields': ('data_transferencia', 'tipo_transferencia', 'status')
        }),
        ('Observações', {
            'fields': ('observacao',)
        }),
        ('Sistema', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnimalIndividual)
class AnimalIndividualAdmin(admin.ModelAdmin):
    list_display = [
        'numero_brinco', 'apelido', 'propriedade', 'categoria', 'sexo',
        'status', 'status_reprodutivo', 'status_sanitario', 'data_nascimento'
    ]
    list_filter = ['propriedade', 'categoria', 'sexo', 'status', 'status_reprodutivo', 'status_sanitario']
    search_fields = [
        'numero_brinco', 'apelido', 'propriedade__nome_propriedade',
        'categoria__nome', 'codigo_sisbov', 'codigo_eletronico'
    ]
    readonly_fields = ['data_cadastro', 'idade_meses', 'idade_anos']
    autocomplete_fields = ['propriedade', 'categoria', 'mae', 'pai', 'lote_atual', 'responsavel_tecnico']


@admin.register(AnimalPesagem)
class AnimalPesagemAdmin(admin.ModelAdmin):
    list_display = ['animal', 'data_pesagem', 'peso_kg', 'tipo_racao', 'consumo_racao_kg_dia', 'local']
    list_filter = ['data_pesagem', 'local', 'tipo_racao']
    search_fields = ['animal__numero_brinco', 'animal__apelido', 'local']
    autocomplete_fields = ['animal', 'responsavel']
    date_hierarchy = 'data_pesagem'


@admin.register(AnimalVacinaAplicada)
class AnimalVacinaAplicadaAdmin(admin.ModelAdmin):
    list_display = ['animal', 'vacina', 'data_aplicacao', 'responsavel']
    list_filter = ['vacina', 'data_aplicacao']
    search_fields = ['animal__numero_brinco', 'animal__apelido', 'vacina', 'lote_produto']
    autocomplete_fields = ['animal', 'responsavel']
    date_hierarchy = 'data_aplicacao'


@admin.register(AnimalTratamento)
class AnimalTratamentoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'produto', 'data_inicio', 'data_fim', 'responsavel']
    list_filter = ['produto', 'data_inicio', 'data_fim']
    search_fields = ['animal__numero_brinco', 'animal__apelido', 'produto', 'motivo']
    autocomplete_fields = ['animal', 'responsavel']
    date_hierarchy = 'data_inicio'


@admin.register(AnimalReproducaoEvento)
class AnimalReproducaoEventoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'tipo_evento', 'data_evento', 'resultado']
    list_filter = ['tipo_evento', 'data_evento']
    search_fields = ['animal__numero_brinco', 'animal__apelido', 'resultado', 'touro_reprodutor']
    autocomplete_fields = ['animal', 'responsavel']
    date_hierarchy = 'data_evento'


@admin.register(AnimalHistoricoEvento)
class AnimalHistoricoEventoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'tipo_evento', 'data_evento', 'usuario']
    list_filter = ['tipo_evento', 'data_evento']
    search_fields = ['animal__numero_brinco', 'animal__apelido', 'descricao']
    autocomplete_fields = ['animal', 'usuario']
    date_hierarchy = 'data_evento'


@admin.register(AnimalDocumento)
class AnimalDocumentoAdmin(admin.ModelAdmin):
    list_display = ['animal', 'tipo_documento', 'data_upload', 'usuario']
    list_filter = ['tipo_documento', 'data_upload']
    search_fields = ['animal__numero_brinco', 'animal__apelido', 'descricao']
    autocomplete_fields = ['animal', 'usuario']
    date_hierarchy = 'data_upload'


@admin.register(CurralLote)
class CurralLoteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sessao', 'finalidade', 'ordem_exibicao']
    list_filter = ['finalidade', 'sessao__propriedade']
    search_fields = [
        'nome',
        'sessao__nome',
        'sessao__propriedade__nome_propriedade',
    ]
    raw_id_fields = ['sessao']


@admin.register(PlanoAssinatura)
class PlanoAssinaturaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'mercadopago_preapproval_id', 'preco_mensal_referencia', 'max_usuarios', 'ativo', 'atualizado_em']
    list_filter = ['ativo', 'max_usuarios']
    search_fields = ['nome', 'slug', 'mercadopago_preapproval_id']
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'slug', 'descricao', 'ativo')
        }),
        ('Mercado Pago', {
            'fields': ('mercadopago_preapproval_id', 'preco_mensal_referencia'),
            'description': 'O preapproval_id será criado automaticamente na primeira compra se não estiver configurado.'
        }),
        ('Limites', {
            'fields': ('max_usuarios', 'modulos_disponiveis')
        }),
        ('Sistema', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AssinaturaCliente)
class AssinaturaClienteAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'plano', 'status', 'gateway_pagamento',
        'mercadopago_subscription_id', 'current_period_end', 'cancelamento_agendado'
    ]
    list_filter = ['status', 'cancelamento_agendado', 'plano', 'gateway_pagamento']
    search_fields = ['usuario__username', 'usuario__email', 'mercadopago_customer_id', 'mercadopago_subscription_id']
    autocomplete_fields = ['usuario', 'produtor', 'plano']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(TenantWorkspace)
class TenantWorkspaceAdmin(admin.ModelAdmin):
    list_display = [
        'assinatura', 'alias', 'status', 'provisionado_em', 'ultimo_erro'
    ]
    list_filter = ['status']
    search_fields = ['assinatura__usuario__username', 'alias', 'caminho_banco']
    readonly_fields = ['criado_em', 'atualizado_em', 'ultimo_erro', 'provisionado_em']


@admin.register(TenantUsuario)
class TenantUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'nome_exibicao', 'email', 'assinatura', 'perfil', 'ativo', 'ultimo_login', 'criado_em'
    ]
    list_filter = ['perfil', 'ativo', 'assinatura', 'criado_em']
    search_fields = ['nome_exibicao', 'email', 'usuario__username', 'assinatura__usuario__username']
    autocomplete_fields = ['usuario', 'assinatura', 'criado_por']
    readonly_fields = ['criado_em', 'atualizado_em', 'ultimo_login']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'assinatura', 'nome_exibicao', 'email')
        }),
        ('Permissões', {
            'fields': ('perfil', 'modulos', 'ativo')
        }),
        ('Sistema', {
            'fields': ('criado_por', 'ultimo_login', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConviteCotacaoFornecedor)
class ConviteCotacaoFornecedorAdmin(admin.ModelAdmin):
    list_display = ['requisicao', 'fornecedor', 'status', 'enviado_em', 'data_expiracao', 'respondido_em']
    list_filter = ['status', 'data_expiracao', 'requisicao__propriedade']
    search_fields = ['token', 'fornecedor__nome', 'requisicao__titulo']
    autocomplete_fields = ['requisicao', 'fornecedor', 'enviado_por']
    readonly_fields = ['token', 'enviado_em', 'respondido_em', 'criado_em', 'atualizado_em']


@admin.register(OrcamentoCompraMensal)
class OrcamentoCompraMensalAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'setor', 'mes', 'ano', 'valor_limite', 'limite_extra', 'atualizado_em']
    list_filter = ['ano', 'mes', 'propriedade', 'setor']
    search_fields = ['propriedade__nome_propriedade', 'setor__nome']
    autocomplete_fields = ['propriedade', 'setor', 'criado_por', 'atualizado_por']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(AjusteOrcamentoCompra)
class AjusteOrcamentoCompraAdmin(admin.ModelAdmin):
    list_display = ['orcamento', 'valor', 'criado_por', 'criado_em']
    list_filter = ['criado_em', 'orcamento__propriedade', 'orcamento__setor']
    search_fields = ['orcamento__propriedade__nome_propriedade', 'orcamento__setor__nome', 'justificativa']
    autocomplete_fields = ['orcamento', 'criado_por']
    readonly_fields = ['criado_em']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'propriedade', 'cpf_cnpj', 'ativo']
    list_filter = ['tipo', 'ativo', 'propriedade']
    search_fields = ['nome', 'nome_fantasia', 'cpf_cnpj', 'email']
    readonly_fields = ['data_cadastro']


@admin.register(CategoriaProduto)
class CategoriaProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    readonly_fields = []


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descricao', 'categoria', 'ncm', 'origem_mercadoria', 'cest', 'ncm_validado', 'sincronizado_receita', 'ativo']
    list_filter = ['categoria', 'ativo', 'ncm_validado', 'sincronizado_receita', 'unidade_medida', 'origem_mercadoria']
    search_fields = ['codigo', 'descricao', 'ncm', 'cest', 'gtin', 'cfop_entrada', 'cfop_saida_estadual', 'cfop_saida_interestadual']
    readonly_fields = ['data_cadastro', 'data_atualizacao', 'ncm_data_validacao', 'data_sincronizacao']
    fieldsets = (
        ('Dados Básicos', {
            'fields': ('codigo', 'descricao', 'descricao_completa', 'categoria', 'unidade_medida', 'ativo')
        }),
        ('Dados Fiscais - NCM e Origem', {
            'fields': ('ncm', 'ncm_descricao', 'ncm_validado', 'ncm_data_validacao', 'origem_mercadoria')
        }),
        ('Dados Fiscais - CEST e Códigos', {
            'fields': ('cest', 'gtin', 'ex_tipi')
        }),
        ('Dados Fiscais - CFOP', {
            'fields': ('cfop_entrada', 'cfop_saida_estadual', 'cfop_saida_interestadual')
        }),
        ('Dados Fiscais - Impostos', {
            'fields': (
                ('cst_icms', 'aliquota_icms'),
                ('cst_ipi', 'aliquota_ipi'),
                ('cst_pis', 'aliquota_pis'),
                ('cst_cofins', 'aliquota_cofins'),
            )
        }),
        ('Dados Comerciais', {
            'fields': ('preco_venda', 'preco_custo')
        }),
        ('Sincronização', {
            'fields': ('sincronizado_receita', 'data_sincronizacao', 'usuario_cadastro')
        }),
        ('Auditoria', {
            'fields': ('data_cadastro', 'data_atualizacao', 'observacoes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RequisicaoCompra)
class RequisicaoCompraAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titulo', 'propriedade', 'status', 'prioridade', 'solicitante', 'criado_em']
    list_filter = ['status', 'prioridade', 'propriedade', 'setor']
    search_fields = ['numero', 'titulo', 'justificativa', 'solicitante__username', 'propriedade__nome_propriedade']
    readonly_fields = ['numero', 'criado_em', 'atualizado_em', 'enviado_em', 'concluido_em']
    raw_id_fields = ['propriedade', 'solicitante', 'setor', 'equipamento', 'centro_custo', 'plano_conta', 'ordem_compra']


@admin.register(SetorPropriedade)
class SetorPropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'propriedade', 'codigo', 'ativo']
    list_filter = ['ativo', 'propriedade']
    search_fields = ['nome', 'codigo', 'propriedade__nome_propriedade']
    autocomplete_fields = ['propriedade', 'responsavel']


    @admin.register(ProtocoloIATF)
    class ProtocoloIATFAdmin(admin.ModelAdmin):
        list_display = ['nome', 'tipo', 'dia_iatf', 'taxa_prenhez_esperada', 'custo_protocolo', 'ativo']
        list_filter = ['tipo', 'ativo', 'propriedade']
        search_fields = ['nome', 'descricao']

    @admin.register(TouroSemen)
    class TouroSemenAdmin(admin.ModelAdmin):
        list_display = ['numero_touro', 'nome_touro', 'raca', 'tipo_semen', 'preco_dose', 'ativo']
        list_filter = ['raca', 'tipo_semen', 'ativo']
        search_fields = ['numero_touro', 'nome_touro', 'registro']

    @admin.register(LoteSemen)
    class LoteSemenAdmin(admin.ModelAdmin):
        list_display = ['numero_lote', 'propriedade', 'touro', 'numero_doses', 'doses_disponiveis', 'status', 'data_aquisicao']
        list_filter = ['status', 'propriedade', 'data_aquisicao']
        search_fields = ['numero_lote', 'touro__nome_touro']

    @admin.register(LoteIATF)
    class LoteIATFAdmin(admin.ModelAdmin):
        list_display = [
            'nome_lote', 'propriedade', 'protocolo', 'data_inicio',
            'numero_animais', 'taxa_prenhez', 'status', 'score_reprodutivo'
        ]
        list_filter = ['status', 'propriedade', 'protocolo']
        search_fields = ['nome_lote', 'propriedade__nome_propriedade']
        filter_horizontal = ['categoria_animais']
        autocomplete_fields = ['inseminador_padrao', 'touro_semen', 'lote_semen']

    @admin.register(EtapaLoteIATF)
    class EtapaLoteIATFAdmin(admin.ModelAdmin):
        list_display = [
            'lote', 'nome_etapa', 'codigo_etapa', 'dia_relativo',
            'data_prevista', 'status', 'responsavel_planejado'
        ]
        list_filter = ['status', 'dia_relativo', 'data_prevista', 'lote__propriedade']
        search_fields = ['lote__nome_lote', 'nome_etapa', 'codigo_etapa']
        autocomplete_fields = [
            'lote', 'responsavel_planejado', 'responsavel_execucao',
            'inseminador', 'touro_semen'
        ]

    @admin.register(IATFIndividual)
    class IATFIndividualAdmin(admin.ModelAdmin):
        list_display = ['animal_individual', 'lote_iatf', 'protocolo', 'data_inicio_protocolo', 'data_iatf', 'status', 'resultado']
        list_filter = ['status', 'resultado', 'protocolo', 'data_inicio_protocolo']
        search_fields = ['animal_individual__numero_brinco', 'lote_iatf__nome_lote']

    @admin.register(AplicacaoMedicamentoIATF)
    class AplicacaoMedicamentoIATFAdmin(admin.ModelAdmin):
        list_display = ['iatf', 'tipo_medicamento', 'nome_medicamento', 'data_aplicacao', 'dia_protocolo', 'aplicado_por']
        list_filter = ['tipo_medicamento', 'dia_protocolo', 'data_aplicacao']
        search_fields = ['iatf__animal_individual__numero_brinco', 'nome_medicamento']

    @admin.register(CalendarioIATF)
    class CalendarioIATFAdmin(admin.ModelAdmin):
        list_display = ['nome', 'propriedade', 'data_inicio', 'data_fim', 'numero_lotes_planejados', 'ativo']
        list_filter = ['ativo', 'propriedade']
        search_fields = ['nome', 'propriedade__nome_propriedade']

# Registrar modelos de relatórios customizados
if RELATORIOS_CUSTOMIZADOS_DISPONIVEL:
    @admin.register(RelatorioCustomizado)
    class RelatorioCustomizadoAdmin(admin.ModelAdmin):
        list_display = ['nome', 'propriedade', 'modulo', 'tipo_exportacao', 'usuario_criador', 'compartilhado', 'ativo', 'total_execucoes', 'data_atualizacao']
        list_filter = ['modulo', 'tipo_exportacao', 'compartilhado', 'ativo', 'propriedade']
        search_fields = ['nome', 'descricao', 'propriedade__nome_propriedade', 'usuario_criador__username']
        readonly_fields = ['data_criacao', 'data_atualizacao', 'ultima_execucao', 'total_execucoes']
    
    @admin.register(TemplateRelatorio)
    class TemplateRelatorioAdmin(admin.ModelAdmin):
        list_display = ['nome', 'modulo', 'publico', 'ativo', 'data_criacao']
        list_filter = ['modulo', 'publico', 'ativo']
        search_fields = ['nome', 'descricao']


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = [
        'tipo_acao', 'usuario', 'nivel_severidade', 'sucesso', 'ip_address', 'criado_em'
    ]
    list_filter = ['tipo_acao', 'nivel_severidade', 'sucesso', 'criado_em']
    search_fields = ['usuario__username', 'usuario__email', 'ip_address', 'descricao']
    readonly_fields = ['criado_em']
    date_hierarchy = 'criado_em'
    ordering = ['-criado_em']


@admin.register(VerificacaoEmail)
class VerificacaoEmailAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'email_verificado', 'tentativas_verificacao', 'token_expira_em', 'criado_em'
    ]
    list_filter = ['email_verificado', 'criado_em']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['token', 'criado_em', 'verificado_em']


@admin.register(SessaoSegura)
class SessaoSeguraAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'ip_address', 'ativo', 'ultima_atividade', 'criado_em'
    ]
    list_filter = ['ativo', 'ultima_atividade', 'criado_em']
    search_fields = ['usuario__username', 'ip_address']
    readonly_fields = ['session_key', 'criado_em', 'ultima_atividade']


# ========== MARKETING ==========
if MARKETING_DISPONIVEL:
    @admin.register(TemplatePost)
    class TemplatePostAdmin(admin.ModelAdmin):
        list_display = ['nome', 'tipo_post', 'rede_social', 'ativo', 'criado_em']
        list_filter = ['tipo_post', 'rede_social', 'ativo', 'criado_em']
        search_fields = ['nome', 'conteudo']
        readonly_fields = ['criado_em', 'atualizado_em']
    
    @admin.register(PostGerado)
    class PostGeradoAdmin(admin.ModelAdmin):
        list_display = ['titulo', 'tipo_post', 'rede_social', 'status', 'criado_por', 'criado_em']
        list_filter = ['tipo_post', 'rede_social', 'status', 'criado_em']
        search_fields = ['titulo', 'conteudo_final']
        readonly_fields = ['criado_em', 'atualizado_em', 'publicado_em']
    
    @admin.register(LeadInteressado)
    class LeadInteressadoAdmin(admin.ModelAdmin):
        list_display = ['nome', 'email', 'telefone', 'status', 'credenciais_enviadas', 'criado_em']
        list_filter = ['status', 'origem', 'credenciais_enviadas', 'criado_em', 'tipo_atividade']
        search_fields = ['nome', 'email', 'telefone', 'propriedade_nome']
        readonly_fields = ['criado_em', 'atualizado_em', 'ip_address', 'user_agent']
    
    @admin.register(CampanhaMarketing)
    class CampanhaMarketingAdmin(admin.ModelAdmin):
        list_display = ['nome', 'data_inicio', 'data_fim', 'ativa', 'criado_por', 'criado_em']
        list_filter = ['ativa', 'data_inicio', 'criado_em']
        search_fields = ['nome', 'descricao']
        readonly_fields = ['criado_em', 'atualizado_em']
    
    @admin.register(ConfiguracaoMarketing)
    class ConfiguracaoMarketingAdmin(admin.ModelAdmin):
        def has_add_permission(self, request):
            # Permite apenas uma instância
            return not ConfiguracaoMarketing.objects.exists()
        
        def has_delete_permission(self, request, obj=None):
            return False

