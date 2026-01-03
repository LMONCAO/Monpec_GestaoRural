# Adicionar ao arquivo admin.py existente ou criar novo

from django.contrib import admin
from .models_compras_financeiro import NumeroSequencialNFE


@admin.register(NumeroSequencialNFE)
class NumeroSequencialNFEAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'serie', 'proximo_numero', 'data_atualizacao']
    list_filter = ['propriedade', 'serie']
    search_fields = ['propriedade__nome_propriedade', 'serie']
    readonly_fields = ['data_atualizacao']
    ordering = ['propriedade', 'serie']
