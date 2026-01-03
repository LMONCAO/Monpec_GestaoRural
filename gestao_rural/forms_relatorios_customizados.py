# -*- coding: utf-8 -*-
"""
Formulários para Sistema de Relatórios Customizados
"""

from django import forms
from django.forms import ModelForm
from .models_relatorios_customizados import RelatorioCustomizado, TemplateRelatorio


class RelatorioCustomizadoForm(ModelForm):
    """Formulário para criar/editar relatórios customizados"""
    
    class Meta:
        model = RelatorioCustomizado
        fields = [
            'nome', 'descricao', 'modulo', 'tipo_exportacao',
            'campos_selecionados', 'filtros', 'agrupamentos',
            'ordenacao', 'formatacao', 'template_personalizado',
            'compartilhado', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do relatório'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do relatório (opcional)'
            }),
            'modulo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_modulo'
            }),
            'tipo_exportacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'campos_selecionados': forms.HiddenInput(),
            'filtros': forms.HiddenInput(),
            'agrupamentos': forms.HiddenInput(),
            'ordenacao': forms.HiddenInput(),
            'formatacao': forms.HiddenInput(),
            'template_personalizado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'HTML customizado (opcional)'
            }),
            'compartilhado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class FiltroRelatorioForm(forms.Form):
    """Formulário dinâmico para configurar filtros do relatório"""
    
    campo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    operador = forms.ChoiceField(
        choices=[
            ('igual', 'Igual a'),
            ('diferente', 'Diferente de'),
            ('maior', 'Maior que'),
            ('menor', 'Menor que'),
            ('maior_igual', 'Maior ou igual a'),
            ('menor_igual', 'Menor ou igual a'),
            ('contem', 'Contém'),
            ('nao_contem', 'Não contém'),
            ('inicio', 'Começa com'),
            ('fim', 'Termina com'),
            ('entre', 'Entre'),
            ('vazio', 'É vazio'),
            ('nao_vazio', 'Não é vazio'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    valor = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    valor2 = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Segundo valor (para operador 'Entre')"
    )


class ExecutarRelatorioForm(forms.Form):
    """Formulário para executar um relatório com filtros adicionais"""
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    formato = forms.ChoiceField(
        choices=[
            ('html', 'Visualizar no navegador'),
            ('pdf', 'Baixar PDF'),
            ('excel', 'Baixar Excel'),
        ],
        initial='html',
        widget=forms.Select(attrs={'class': 'form-select'})
    )







