from django import forms
from django.core.exceptions import ValidationError
from .models import TipoFinanciamento, Financiamento


class TipoFinanciamentoForm(forms.ModelForm):
    """Formulário para tipos de financiamento"""
    
    class Meta:
        model = TipoFinanciamento
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Financiamento Rural, Empréstimo Pessoal...'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do tipo de financiamento...'
            })
        }


class FinanciamentoForm(forms.ModelForm):
    """Formulário para financiamentos"""
    
    class Meta:
        model = Financiamento
        fields = [
            'tipo', 'nome', 'descricao', 'valor_principal', 'taxa_juros_anual',
            'tipo_taxa', 'data_contratacao', 'data_primeiro_vencimento',
            'data_ultimo_vencimento', 'numero_parcelas', 'valor_parcela'
        ]
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do financiamento...'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do financiamento...'
            }),
            'valor_principal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'taxa_juros_anual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'tipo_taxa': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_contratacao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_primeiro_vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_ultimo_vencimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numero_parcelas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '1'
            }),
            'valor_parcela': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona eventos JavaScript para cálculos automáticos
        self.fields['valor_principal'].widget.attrs['onchange'] = 'calcularParcelas()'
        self.fields['taxa_juros_anual'].widget.attrs['onchange'] = 'calcularParcelas()'
        self.fields['numero_parcelas'].widget.attrs['onchange'] = 'calcularParcelas()'
        self.fields['data_primeiro_vencimento'].widget.attrs['onchange'] = 'calcularDataFinal()'
        self.fields['numero_parcelas'].widget.attrs['onchange'] = 'calcularDataFinal()'
    
    def clean_valor_principal(self):
        valor = self.cleaned_data.get('valor_principal')
        if valor is not None and valor <= 0:
            raise ValidationError('O valor principal deve ser maior que zero.')
        return valor
    
    def clean_taxa_juros_anual(self):
        taxa = self.cleaned_data.get('taxa_juros_anual')
        if taxa is not None and (taxa < 0 or taxa > 100):
            raise ValidationError('A taxa de juros deve estar entre 0 e 100%.')
        return taxa
    
    def clean_numero_parcelas(self):
        parcelas = self.cleaned_data.get('numero_parcelas')
        if parcelas is not None and parcelas <= 0:
            raise ValidationError('O número de parcelas deve ser maior que zero.')
        return parcelas
    
    def clean_valor_parcela(self):
        valor = self.cleaned_data.get('valor_parcela')
        if valor is not None and valor <= 0:
            raise ValidationError('O valor da parcela deve ser maior que zero.')
        return valor
    
    def clean(self):
        cleaned_data = super().clean()
        data_contratacao = cleaned_data.get('data_contratacao')
        data_primeiro = cleaned_data.get('data_primeiro_vencimento')
        data_ultimo = cleaned_data.get('data_ultimo_vencimento')
        
        if data_contratacao and data_primeiro:
            if data_primeiro <= data_contratacao:
                raise ValidationError('A data do primeiro vencimento deve ser posterior à data de contratação.')
        
        if data_primeiro and data_ultimo:
            if data_ultimo <= data_primeiro:
                raise ValidationError('A data do último vencimento deve ser posterior à data do primeiro vencimento.')
        
        return cleaned_data

