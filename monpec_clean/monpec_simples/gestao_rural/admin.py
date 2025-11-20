from django.contrib import admin
from .models import Proprietario, Propriedade

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
