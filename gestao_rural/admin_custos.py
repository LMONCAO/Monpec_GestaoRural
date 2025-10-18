from django.contrib import admin
from .models import CustoFixo, CustoVariavel, FluxoCaixa


@admin.register(CustoFixo)
class CustoFixoAdmin(admin.ModelAdmin):
    list_display = ['nome_custo', 'propriedade', 'tipo_custo', 'valor_mensal', 'ativo', 'data_cadastro']
    list_filter = ['tipo_custo', 'ativo', 'propriedade', 'data_cadastro']
    search_fields = ['nome_custo', 'propriedade__nome_propriedade', 'descricao']
    readonly_fields = ['data_cadastro']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('propriedade', 'nome_custo', 'tipo_custo', 'valor_mensal')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'ativo')
        }),
        ('Sistema', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustoVariavel)
class CustoVariavelAdmin(admin.ModelAdmin):
    list_display = ['nome_custo', 'propriedade', 'tipo_custo', 'valor_por_cabeca', 'ativo', 'data_cadastro']
    list_filter = ['tipo_custo', 'ativo', 'propriedade', 'data_cadastro']
    search_fields = ['nome_custo', 'propriedade__nome_propriedade', 'descricao']
    readonly_fields = ['data_cadastro']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('propriedade', 'nome_custo', 'tipo_custo', 'valor_por_cabeca')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'ativo')
        }),
        ('Sistema', {
            'fields': ('data_cadastro',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FluxoCaixa)
class FluxoCaixaAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'data_referencia', 'receita_total', 'custo_fixo_total', 'custo_variavel_total', 'lucro_bruto', 'margem_lucro', 'data_calculo']
    list_filter = ['propriedade', 'data_referencia', 'data_calculo']
    search_fields = ['propriedade__nome_propriedade']
    readonly_fields = ['data_calculo', 'margem_lucro']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('propriedade', 'data_referencia')
        }),
        ('Receitas e Custos', {
            'fields': ('receita_total', 'custo_fixo_total', 'custo_variavel_total')
        }),
        ('Resultado', {
            'fields': ('lucro_bruto', 'margem_lucro')
        }),
        ('Sistema', {
            'fields': ('data_calculo',),
            'classes': ('collapse',)
        }),
    )

