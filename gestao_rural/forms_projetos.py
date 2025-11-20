from django import forms
from .models import ProjetoBancario


class ProjetoBancarioForm(forms.ModelForm):
    class Meta:
        model = ProjetoBancario
        fields = [
            'nome_projeto', 'tipo_projeto', 'banco_solicitado', 'valor_solicitado',
            'prazo_pagamento', 'taxa_juros', 'data_solicitacao', 'data_aprovacao',
            'valor_aprovado', 'status', 'observacoes', 'arquivo_projeto'
        ]
        widgets = {
            'nome_projeto': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'tipo_projeto': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'banco_solicitado': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'valor_solicitado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'required': True}),
            'prazo_pagamento': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'required': True}),
            'taxa_juros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'data_solicitacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'data_aprovacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor_aprovado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo_projeto': forms.FileInput(attrs={'class': 'form-control'}),
        }














