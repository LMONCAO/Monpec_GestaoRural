# -*- coding: utf-8 -*-
"""
Forms do módulo de Vendas
"""

from django import forms
from django.db.models import Q
from decimal import Decimal
from .models import ParametrosVendaPorCategoria
from .models_compras_financeiro import NotaFiscal, ItemNotaFiscal
from .models_cadastros import Cliente


class VendaForm(forms.ModelForm):
    """Formulário simplificado para cadastro de venda"""
    
    class Meta:
        model = NotaFiscal
        fields = ['cliente', 'data_emissao', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'data_emissao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre a venda (opcional)'
            }),
        }
    
    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriedade:
            # Filtrar clientes da propriedade ou globais
            self.fields['cliente'].queryset = Cliente.objects.filter(
                Q(propriedade=propriedade) | Q(propriedade__isnull=True),
                ativo=True
            ).order_by('nome')


class ItemVendaForm(forms.ModelForm):
    """Formulário para itens da venda"""
    
    class Meta:
        model = ItemNotaFiscal
        fields = ['descricao', 'quantidade', 'valor_unitario', 'unidade_medida', 'ncm', 'cfop']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Descrição do produto/serviço'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'required': True
            }),
            'valor_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'unidade_medida': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('UN', 'Unidade (UN)'),
                ('KG', 'Quilograma (KG)'),
                ('TON', 'Tonelada (TON)'),
                ('L', 'Litro (L)'),
                ('M', 'Metro (M)'),
                ('M2', 'Metro Quadrado (M²)'),
                ('M3', 'Metro Cúbico (M³)'),
                ('SC', 'Saca (SC)'),
                ('CX', 'Caixa (CX)'),
                ('PC', 'Peça (PC)'),
                ('FD', 'Fardo (FD)'),
                ('RL', 'Rolo (RL)'),
            ]),
            'ncm': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'NCM (ex: 0102.29.00)'
            }),
            'cfop': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CFOP (ex: 5102)'
            }),
        }


class ParametrosVendaPorCategoriaForm(forms.ModelForm):
    """Formulário para parâmetros de venda por categoria"""
    
    class Meta:
        model = ParametrosVendaPorCategoria
        fields = ['categoria', 'preco_medio_kg', 'preco_minimo_kg', 'preco_maximo_kg', 'ativo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'preco_medio_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_minimo_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_maximo_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        if propriedade:
            from .models import CategoriaAnimal
            self.fields['categoria'].queryset = CategoriaAnimal.objects.all().order_by('nome')


class BulkVendaPorCategoriaForm(forms.Form):
    """Formulário para atualização em lote de parâmetros de venda"""
    pass  # Implementar conforme necessário


class ConfigurarSerieNFeForm(forms.Form):
    """Formulário para configurar série de NF-e"""
    serie = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 1, 2, TESTE, etc.',
            'required': True
        }),
        label="Série",
        help_text="Número ou código da série (ex: '1' para série normal, 'TESTE' para testes)"
    )
    proximo_numero = forms.IntegerField(
        required=True,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'required': True
        }),
        label="Próximo Número",
        help_text="Próximo número sequencial a ser usado nesta série"
    )
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações sobre esta série (opcional)'
        }),
        label="Observações",
        help_text="Ex: 'Série normal', 'Série de teste', 'Série para exportação', etc."
    )
