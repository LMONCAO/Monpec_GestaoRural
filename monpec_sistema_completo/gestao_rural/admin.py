from django.contrib import admin
from .models import *

@admin.register(ProdutorRural)
class ProdutorAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf_cnpj', 'telefone']
    search_fields = ['nome_completo', 'cpf_cnpj']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome_propriedade', 'produtor', 'municipio', 'uf']
    list_filter = ['uf', 'tipo']

@admin.register(InventarioRebanho)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'categoria', 'quantidade', 'valor_total']

@admin.register(CicloProducaoAgricola)
class CicloAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'cultura', 'safra', 'receita_esperada_total']

@admin.register(BemImobilizado)
class BemAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'descricao', 'valor_aquisicao']

@admin.register(Financiamento)
class FinanciamentoAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'banco', 'valor_total', 'ativo']

admin.site.register(CategoriaAnimal)
admin.site.register(CustoFixo)
admin.site.register(CustoVariavel)
