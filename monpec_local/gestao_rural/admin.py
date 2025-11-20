from django.contrib import admin
from .models import Proprietario, Propriedade, ProjetoCredito

@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cidade', 'estado', 'created_at']
    search_fields = ['nome', 'cpf', 'cidade', 'email']
    list_filter = ['estado', 'cidade', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprietario', 'area', 'municipio', 'estado', 'created_at']
    search_fields = ['nome', 'proprietario__nome', 'municipio', 'matricula']
    list_filter = ['estado', 'municipio', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']

@admin.register(ProjetoCredito)
class ProjetoCreditoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'propriedade', 'tipo', 'valor_solicitado', 'status', 'data_inicio']
    search_fields = ['titulo', 'propriedade__nome', 'propriedade__proprietario__nome']
    list_filter = ['tipo', 'status', 'data_inicio', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
