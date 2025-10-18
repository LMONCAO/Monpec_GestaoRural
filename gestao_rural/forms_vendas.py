from django import forms
from django.core.exceptions import ValidationError
from .models import ParametrosVendaPorCategoria, CategoriaAnimal


class ParametrosVendaPorCategoriaForm(forms.ModelForm):
    """Formulário para configurar parâmetros de venda por categoria"""
    
    class Meta:
        model = ParametrosVendaPorCategoria
        fields = ['categoria', 'percentual_venda_anual', 'ativo']
        widgets = {
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'percentual_venda_anual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop('propriedade', None)
        super().__init__(*args, **kwargs)
        
        if propriedade:
            # Filtra categorias que ainda não têm parâmetro configurado
            categorias_existentes = ParametrosVendaPorCategoria.objects.filter(
                propriedade=propriedade,
                ativo=True
            ).values_list('categoria_id', flat=True)
            
            self.fields['categoria'].queryset = CategoriaAnimal.objects.exclude(
                id__in=categorias_existentes
            )
    
    def clean_percentual_venda_anual(self):
        percentual = self.cleaned_data.get('percentual_venda_anual')
        if percentual is not None and (percentual < 0 or percentual > 100):
            raise ValidationError('O percentual deve estar entre 0 e 100.')
        return percentual


class BulkVendaPorCategoriaForm(forms.Form):
    """Formulário para configurar vendas em massa por categoria"""
    
    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop('propriedade', None)
        super().__init__(*args, **kwargs)
        
        if propriedade:
            # Busca todas as categorias disponíveis
            categorias = CategoriaAnimal.objects.all().order_by('nome')
            
            for categoria in categorias:
                field_name = f'percentual_{categoria.id}'
                self.fields[field_name] = forms.DecimalField(
                    label=f'{categoria.nome} (%)',
                    max_digits=5,
                    decimal_places=2,
                    required=False,
                    initial=0.00,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'step': '0.01',
                        'min': '0',
                        'max': '100',
                        'placeholder': '0.00'
                    })
                )
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

