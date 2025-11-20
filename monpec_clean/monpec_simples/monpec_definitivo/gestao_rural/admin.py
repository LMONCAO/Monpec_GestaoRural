from django.contrib import admin
from .models import Proprietario, Propriedade, Categoria, ItemInventario

@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cidade', 'estado', 'created_at']
    search_fields = ['nome', 'cpf', 'cidade', 'email']
    list_filter = ['estado', 'cidade', 'created_at']
    ordering = ['nome']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprietario', 'area', 'municipio', 'estado', 'created_at']
    search_fields = ['nome', 'proprietario__nome', 'municipio']
    list_filter = ['estado', 'municipio', 'created_at']
    ordering = ['nome']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor', 'created_at']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']

@admin.register(ItemInventario)
class ItemInventarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'propriedade', 'categoria', 'quantidade', 'valor_total', 'created_at']
    search_fields = ['nome', 'propriedade__nome', 'categoria__nome']
    list_filter = ['categoria', 'propriedade', 'created_at']
    ordering = ['categoria', 'nome']
