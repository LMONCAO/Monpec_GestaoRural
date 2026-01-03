from django import forms
from .models import CustoFixo, CustoVariavel


class CustoFixoForm(forms.ModelForm):
    """Formulário para custos fixos"""
    
    class Meta:
        model = CustoFixo
        fields = ['nome_custo', 'tipo_custo', 'valor_mensal', 'tipo_periodo', 'meses_aplicaveis', 'data_inicio', 'data_fim', 'descricao', 'ativo']
        widgets = {
            'nome_custo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Manutenção de trator'
            }),
            'tipo_custo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'valor_mensal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tipo_periodo': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'togglePeriodoFields()'
            }),
            'meses_aplicaveis': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do custo...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome_custo': 'Nome do Custo',
            'tipo_custo': 'Tipo de Custo',
            'valor_mensal': 'Valor Mensal (R$)',
            'tipo_periodo': 'Tipo de Período',
            'meses_aplicaveis': 'Meses Aplicáveis',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim',
            'descricao': 'Descrição',
            'ativo': 'Custo ativo'
        }


class CustoVariavelForm(forms.ModelForm):
    """Formulário para custos variáveis"""
    
    class Meta:
        model = CustoVariavel
        fields = ['nome_custo', 'tipo_custo', 'valor_por_cabeca', 'tipo_periodo', 'meses_aplicaveis', 'data_inicio', 'data_fim', 'descricao', 'ativo']
        widgets = {
            'nome_custo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Ração para engorda'
            }),
            'tipo_custo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'valor_por_cabeca': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tipo_periodo': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'togglePeriodoFields()'
            }),
            'meses_aplicaveis': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do custo...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nome_custo': 'Nome do Custo',
            'tipo_custo': 'Tipo de Custo',
            'valor_por_cabeca': 'Valor por Cabeça (R$)',
            'tipo_periodo': 'Tipo de Período',
            'meses_aplicaveis': 'Meses Aplicáveis',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim',
            'descricao': 'Descrição',
            'ativo': 'Custo ativo'
        }
