from django import forms
from django.core.exceptions import ValidationError
from .models import CategoriaImobilizado, BemImobilizado


class CategoriaImobilizadoForm(forms.ModelForm):
    """Formulário para categorias de imobilizado"""
    
    class Meta:
        model = CategoriaImobilizado
        fields = ['nome', 'descricao', 'vida_util_anos', 'taxa_depreciacao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Máquinas, Veículos, Construções...'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição da categoria...'
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
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona eventos JavaScript para cálculos automáticos
        self.fields['vida_util_anos'].widget.attrs['onchange'] = 'calcularTaxaDepreciacao()'
    
    def clean_vida_util_anos(self):
        anos = self.cleaned_data.get('vida_util_anos')
        if anos is not None and anos <= 0:
            raise ValidationError('A vida útil deve ser maior que zero.')
        return anos
    
    def clean_taxa_depreciacao(self):
        taxa = self.cleaned_data.get('taxa_depreciacao')
        if taxa is not None and (taxa <= 0 or taxa > 100):
            raise ValidationError('A taxa de depreciação deve estar entre 0 e 100%.')
        return taxa


class BemImobilizadoForm(forms.ModelForm):
    """Formulário para bens imobilizados"""
    
    class Meta:
        model = BemImobilizado
        fields = [
            'categoria', 'nome', 'descricao', 'marca', 'modelo', 'numero_serie',
            'valor_aquisicao', 'valor_residual', 'data_aquisicao', 'data_inicio_depreciacao',
            'tipo_aquisicao', 'ativo'
        ]
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do bem...'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do bem...'
            }),
            'valor_aquisicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca do bem...'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo do bem...'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de série...'
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
            'data_aquisicao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_inicio_depreciacao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tipo_aquisicao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configura data padrão de aquisição para hoje
        if not self.instance.pk:
            from datetime import date
            self.fields['data_aquisicao'].initial = date.today()
            self.fields['data_inicio_depreciacao'].initial = date.today()
    
    def clean_valor_aquisicao(self):
        valor = self.cleaned_data.get('valor_aquisicao')
        if valor is not None and valor <= 0:
            raise ValidationError('O valor de aquisição deve ser maior que zero.')
        return valor
    
    def clean_valor_residual(self):
        valor = self.cleaned_data.get('valor_residual')
        if valor is not None and valor < 0:
            raise ValidationError('O valor residual não pode ser negativo.')
        return valor
    
    def clean(self):
        cleaned_data = super().clean()
        data_aquisicao = cleaned_data.get('data_aquisicao')
        data_inicio_depreciacao = cleaned_data.get('data_inicio_depreciacao')
        valor_aquisicao = cleaned_data.get('valor_aquisicao')
        valor_residual = cleaned_data.get('valor_residual')
        
        if data_aquisicao and data_inicio_depreciacao:
            if data_inicio_depreciacao < data_aquisicao:
                raise ValidationError('A data de início da depreciação não pode ser anterior à data de aquisição.')
        
        if valor_aquisicao and valor_residual:
            if valor_residual > valor_aquisicao:
                raise ValidationError('O valor residual não pode ser maior que o valor de aquisição.')
        
        return cleaned_data
