from django import forms
from django.core.exceptions import ValidationError
from .models import IndicadorFinanceiro


class IndicadorFinanceiroForm(forms.ModelForm):
    """Formulário para indicadores financeiros"""
    
    class Meta:
        model = IndicadorFinanceiro
        fields = [
            'nome', 'tipo', 'valor', 'unidade', 'data_referencia', 'descricao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do indicador...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'placeholder': '0.0000'
            }),
            'unidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: %, R$, kg...'
            }),
            'data_referencia': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do indicador...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configura data padrão para hoje
        if not self.instance.pk:
            self.fields['data_referencia'].initial = forms.fields.DateField().to_python(None)
            self.fields['unidade'].initial = '%'
    
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor < 0:
            raise ValidationError('O valor do indicador deve ser maior ou igual a zero.')
        return valor
    
    def clean_data_referencia(self):
        data = self.cleaned_data.get('data_referencia')
        if data and data > forms.fields.DateField().to_python(None):
            raise ValidationError('A data de referência não pode ser futura.')
        return data

