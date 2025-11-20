from django import forms
from .models import (
    ProdutorRural, Propriedade, InventarioRebanho, ParametrosProjecaoRebanho,
    MovimentacaoProjetada, TransferenciaPropriedade, CategoriaAnimal
)


class ProdutorRuralForm(forms.ModelForm):
    class Meta:
        model = ProdutorRural
        fields = [
            'nome', 'cpf_cnpj', 'documento_identidade', 'data_nascimento', 
            'anos_experiencia', 'telefone', 'email', 'endereco'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identidade': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'anos_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PropriedadeForm(forms.ModelForm):
    tipo_ciclo_pecuario = forms.MultipleChoiceField(
        choices=Propriedade.TIPO_CICLO_PECUARIO_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Tipos de Ciclo Pecuário"
    )

    class Meta:
        model = Propriedade
        fields = [
            'nome_propriedade', 'municipio', 'uf', 'area_total_ha', 'tipo_operacao',
            'tipo_ciclo_pecuario', 'tipo_propriedade', 'valor_hectare_proprio', 
            'valor_mensal_hectare_arrendamento', 'nirf', 'incra', 'car'
        ]
        widgets = {
            'nome_propriedade': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.Select(attrs={'class': 'form-control'}),
            'area_total_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'tipo_operacao': forms.Select(attrs={'class': 'form-control'}),
            'tipo_propriedade': forms.Select(attrs={'class': 'form-control'}),
            'valor_hectare_proprio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'valor_mensal_hectare_arrendamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'nirf': forms.TextInput(attrs={'class': 'form-control'}),
            'incra': forms.TextInput(attrs={'class': 'form-control'}),
            'car': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar opções de UF
        self.fields['uf'].widget.choices = [
            ('', 'Selecione o Estado'),
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
            ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ]
        if self.instance and getattr(self.instance, 'ciclos_pecuarios_list', None) and self.instance.pk:
            self.fields['tipo_ciclo_pecuario'].initial = self.instance.ciclos_pecuarios_list()
        elif not self.initial.get('tipo_ciclo_pecuario'):
            self.fields['tipo_ciclo_pecuario'].initial = ['CICLO_COMPLETO']


class InventarioRebanhoForm(forms.ModelForm):
    class Meta:
        model = InventarioRebanho
        fields = ['categoria', 'quantidade', 'valor_por_cabeca', 'data_inventario']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valor_por_cabeca': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'data_inventario': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ParametrosProjecaoForm(forms.ModelForm):
    class Meta:
        model = ParametrosProjecaoRebanho
        fields = [
            'taxa_natalidade_anual', 'taxa_mortalidade_bezerros_anual', 
            'taxa_mortalidade_adultos_anual', 'percentual_venda_machos_anual',
            'percentual_venda_femeas_anual', 'periodicidade'
        ]
        widgets = {
            'taxa_natalidade_anual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'taxa_mortalidade_bezerros_anual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'taxa_mortalidade_adultos_anual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'percentual_venda_machos_anual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'percentual_venda_femeas_anual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'max': '100',
                'required': True
            }),
            'periodicidade': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
        help_texts = {
            'taxa_natalidade_anual': 'Percentual de fêmeas que parirão por ano (0-100%)',
            'taxa_mortalidade_bezerros_anual': 'Percentual de bezerros que morrerão por ano (0-100%)',
            'taxa_mortalidade_adultos_anual': 'Percentual de adultos que morrerão por ano (0-100%)',
            'percentual_venda_machos_anual': 'Percentual de machos vendidos por ano (0-100%)',
            'percentual_venda_femeas_anual': 'Percentual de fêmeas vendidas por ano (0-100%)',
            'periodicidade': 'Periodicidade da projeção',
        }
    
    def clean_taxa_natalidade_anual(self):
        taxa = self.cleaned_data.get('taxa_natalidade_anual')
        if taxa is not None and (taxa < 0 or taxa > 100):
            raise forms.ValidationError('Taxa de natalidade deve estar entre 0 e 100.')
        return taxa
    
    def clean_taxa_mortalidade_bezerros_anual(self):
        taxa = self.cleaned_data.get('taxa_mortalidade_bezerros_anual')
        if taxa is not None and (taxa < 0 or taxa > 100):
            raise forms.ValidationError('Taxa de mortalidade de bezerros deve estar entre 0 e 100.')
        return taxa
    
    def clean_taxa_mortalidade_adultos_anual(self):
        taxa = self.cleaned_data.get('taxa_mortalidade_adultos_anual')
        if taxa is not None and (taxa < 0 or taxa > 100):
            raise forms.ValidationError('Taxa de mortalidade de adultos deve estar entre 0 e 100.')
        return taxa
    
    def clean_percentual_venda_machos_anual(self):
        taxa = self.cleaned_data.get('percentual_venda_machos_anual')
        if taxa is not None and (taxa < 0 or taxa > 100):
            raise forms.ValidationError('Percentual de venda de machos deve estar entre 0 e 100.')
        return taxa
    
    def clean_percentual_venda_femeas_anual(self):
        taxa = self.cleaned_data.get('percentual_venda_femeas_anual')
        if taxa is not None and (taxa < 0 or taxa > 100):
            raise forms.ValidationError('Percentual de venda de fêmeas deve estar entre 0 e 100.')
        return taxa
    
    def clean(self):
        cleaned_data = super().clean()
        natalidade = cleaned_data.get('taxa_natalidade_anual')
        mortalidade = cleaned_data.get('taxa_mortalidade_bezerros_anual')
        
        if natalidade and mortalidade and natalidade <= mortalidade:
            raise forms.ValidationError(
                'A taxa de natalidade deve ser maior que a taxa de mortalidade de bezerros.'
            )
        
        return cleaned_data


class MovimentacaoProjetadaForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoProjetada
        fields = ['data_movimentacao', 'tipo_movimentacao', 'categoria', 'quantidade', 'observacao']
        widgets = {
            'data_movimentacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_movimentacao': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TransferenciaPropriedadeForm(forms.ModelForm):
    class Meta:
        model = TransferenciaPropriedade
        fields = [
            'propriedade_origem', 'propriedade_destino', 'categoria', 'quantidade',
            'data_transferencia', 'tipo_transferencia', 'status', 'observacao'
        ]
        widgets = {
            'propriedade_origem': forms.Select(attrs={'class': 'form-control'}),
            'propriedade_destino': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'data_transferencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_transferencia': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar propriedades do usuário
            propriedades_usuario = Propriedade.objects.filter(produtor__usuario_responsavel=user)
            self.fields['propriedade_origem'].queryset = propriedades_usuario
            self.fields['propriedade_destino'].queryset = propriedades_usuario


class CategoriaAnimalForm(forms.ModelForm):
    class Meta:
        model = CategoriaAnimal
        fields = ['nome', 'idade_minima_meses', 'idade_maxima_meses', 'sexo', 'raca', 'peso_medio_kg', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Bezerro 0-12 meses (SISBOV)'}),
            'idade_minima_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '1200'}),
            'idade_maxima_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '1200'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'raca': forms.Select(attrs={'class': 'form-select'}),
            'peso_medio_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ex: 150.50'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informe o texto padrão SISBOV para esta categoria'}),
        }
        labels = {
            'nome': 'Categoria SISBOV',
            'idade_minima_meses': 'Idade Mínima (meses)',
            'idade_maxima_meses': 'Idade Máxima (meses)',
            'sexo': 'Sexo',
            'raca': 'Raça',
            'peso_medio_kg': 'Peso Médio (kg)',
            'descricao': 'Descrição padrão SISBOV',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        idade_minima = cleaned_data.get('idade_minima_meses')
        idade_maxima = cleaned_data.get('idade_maxima_meses')
        
        if idade_minima is not None and idade_maxima is not None:
            if idade_minima >= idade_maxima:
                raise forms.ValidationError('A idade mínima deve ser menor que a idade máxima.')
        
        return cleaned_data
