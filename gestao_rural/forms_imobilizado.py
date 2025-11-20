from django import forms
from django.core.exceptions import ValidationError
from .models import Propriedade
from .models_patrimonio import TipoBem, BemPatrimonial


class TipoBemForm(forms.ModelForm):
    """Formulário para tipos de bem"""
    
    class Meta:
        model = TipoBem
        fields = ['nome', 'categoria', 'descricao', 'vida_util_anos', 'taxa_depreciacao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Trator, Implemento, Veículo...'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do tipo de bem...'
            }),
            'vida_util_anos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '10'
            }),
            'taxa_depreciacao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '10.00'
            }),
        }
    
    def clean_taxa_depreciacao(self):
        taxa = self.cleaned_data.get('taxa_depreciacao')
        if taxa and (taxa < 0 or taxa > 100):
            raise ValidationError('A taxa de depreciação deve estar entre 0 e 100%.')
        return taxa


class BemPatrimonialForm(forms.ModelForm):
    """Formulário para bens patrimoniais"""
    
    class Meta:
        model = BemPatrimonial
        fields = ['tipo_bem', 'descricao', 'data_aquisicao', 'valor_aquisicao', 
                 'valor_residual', 'quantidade', 'estado_conservacao', 'observacoes']
        widgets = {
            'tipo_bem': forms.Select(attrs={
                'class': 'form-control'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Trator John Deere 6110J'
            }),
            'data_aquisicao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_aquisicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'valor_residual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '1'
            }),
            'estado_conservacao': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais...'
            }),
        }
    
    def clean_valor_aquisicao(self):
        valor = self.cleaned_data.get('valor_aquisicao')
        if valor and valor <= 0:
            raise ValidationError('O valor de aquisição deve ser maior que zero.')
        return valor
    
    def clean_valor_residual(self):
        valor_residual = self.cleaned_data.get('valor_residual')
        valor_aquisicao = self.cleaned_data.get('valor_aquisicao')
        
        if valor_residual and valor_aquisicao and valor_residual >= valor_aquisicao:
            raise ValidationError('O valor residual deve ser menor que o valor de aquisição.')
        return valor_residual