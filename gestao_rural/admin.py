from django.contrib import admin
from .models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho, 
    ParametrosProjecaoRebanho, MovimentacaoProjetada, Cultura, CicloProducaoAgricola,
    RegraPromocaoCategoria, TransferenciaPropriedade, ConfiguracaoVenda,
    ParametrosVendaPorCategoria,
    CustoFixo, CustoVariavel, FluxoCaixa
)


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
    list_display = ['nome_propriedade', 'produtor', 'municipio', 'uf', 'area_total_ha', 'tipo_operacao', 'tipo_ciclo_pecuario', 'tipo_propriedade', 'valor_total_propriedade']
    list_filter = ['tipo_operacao', 'tipo_ciclo_pecuario', 'tipo_propriedade', 'uf', 'municipio']
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


@admin.register(Cultura)
class CulturaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']


@admin.register(RegraPromocaoCategoria)
class RegraPromocaoCategoriaAdmin(admin.ModelAdmin):
    list_display = ['categoria_origem', 'categoria_destino', 'idade_minima_meses', 'idade_maxima_meses', 'ativo']
    list_filter = ['ativo', 'categoria_origem', 'categoria_destino']
    search_fields = ['categoria_origem__nome', 'categoria_destino__nome']


@admin.register(CicloProducaoAgricola)
class CicloProducaoAgricolaAdmin(admin.ModelAdmin):
    list_display = [
        'propriedade', 'cultura', 'safra', 'area_plantada_ha', 
        'producao_total_esperada_sc', 'receita_esperada_total', 'lucro_esperado'
    ]
    list_filter = ['cultura', 'safra', 'data_inicio_plantio']
    search_fields = ['propriedade__nome_propriedade', 'cultura__nome', 'safra']
    readonly_fields = ['data_cadastro']


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


