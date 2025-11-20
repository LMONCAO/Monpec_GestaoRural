from django import forms
from django.utils import timezone

from .models import AnimalPesagem, AnimalIndividual


class AnimalPesagemForm(forms.ModelForm):
    class Meta:
        model = AnimalPesagem
        fields = [
            'animal',
            'data_pesagem',
            'peso_kg',
            'local',
            'tipo_racao',
            'consumo_racao_kg_dia',
            'observacoes',
        ]
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-select'}),
            'data_pesagem': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Balança 1'}),
            'tipo_racao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Confinamento 18% PB'}),
            'consumo_racao_kg_dia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'consumo_racao_kg_dia': 'Consumo diário de ração (kg)',
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        self.propriedade = propriedade
        super().__init__(*args, **kwargs)

        if propriedade:
            self.fields['animal'].queryset = (
                AnimalIndividual.objects.filter(propriedade=propriedade)
                .select_related('categoria')
                .order_by('numero_brinco', 'apelido')
            )

        if not self.initial.get('data_pesagem'):
            self.fields['data_pesagem'].initial = timezone.localdate()

        self.fields['observacoes'].required = False
        self.fields['local'].required = False
        self.fields['tipo_racao'].required = False
        self.fields['consumo_racao_kg_dia'].required = False












