from django import forms
from .models import ProjetoBancario, Propriedade, PlanejamentoAnual


class ProjetoBancarioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop('propriedade', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar planejamentos apenas da propriedade selecionada
        if propriedade:
            queryset = PlanejamentoAnual.objects.filter(
                propriedade=propriedade
            ).order_by('-ano')
            
            # Melhorar o label do planejamento para mostrar código
            self.fields['planejamento'].queryset = queryset
            self.fields['planejamento'].empty_label = "-- Selecione uma projeção (opcional) --"
            
            # Customizar as opções para mostrar código + ano
            choices = [('', self.fields['planejamento'].empty_label)]
            for p in queryset:
                codigo_display = f"{p.codigo} - " if p.codigo else ""
                label = f"{codigo_display}{p.ano} - {p.get_status_display}"
                choices.append((p.id, label))
            self.fields['planejamento'].choices = choices
    
    class Meta:
        model = ProjetoBancario
        fields = [
            'planejamento', 'nome_projeto', 'tipo_projeto', 'banco_solicitado', 'valor_solicitado',
            'prazo_pagamento', 'taxa_juros', 'data_solicitacao', 'data_aprovacao',
            'valor_aprovado', 'status', 'observacoes', 'arquivo_projeto'
        ]
        widgets = {
            'planejamento': forms.Select(attrs={
                'class': 'form-select',
                'help_text': 'Selecione um planejamento para avaliar cenários de projeção'
            }),
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














