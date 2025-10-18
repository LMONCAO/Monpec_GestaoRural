from django import forms
from .models import (
    ProdutorRural, Propriedade, InventarioRebanho, ParametrosProjecaoRebanho,
    MovimentacaoProjetada, CicloProducaoAgricola, TransferenciaPropriedade, CategoriaAnimal
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
            'tipo_ciclo_pecuario': forms.Select(attrs={'class': 'form-control'}),
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
            'taxa_natalidade_anual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_mortalidade_bezerros_anual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_mortalidade_adultos_anual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'percentual_venda_machos_anual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'percentual_venda_femeas_anual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'periodicidade': forms.Select(attrs={'class': 'form-control'}),
        }


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


class CicloProducaoForm(forms.ModelForm):
    class Meta:
        model = CicloProducaoAgricola
        fields = [
            'cultura', 'safra', 'area_plantada_ha', 'produtividade_esperada_sc_ha',
            'custo_producao_por_ha', 'preco_venda_por_sc', 'data_inicio_plantio', 'data_fim_colheita'
        ]
        widgets = {
            'cultura': forms.Select(attrs={'class': 'form-control'}),
            'safra': forms.TextInput(attrs={'class': 'form-control'}),
            'area_plantada_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'produtividade_esperada_sc_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'custo_producao_por_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_venda_por_sc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_inicio_plantio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim_colheita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
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
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bezerras (0-12m)'}),
            'idade_minima_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '1200'}),
            'idade_maxima_meses': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '1200'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'raca': forms.Select(attrs={'class': 'form-select'}),
            'peso_medio_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ex: 150.50'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição da categoria...'}),
        }
        labels = {
            'nome': 'Nome da Categoria',
            'idade_minima_meses': 'Idade Mínima (meses)',
            'idade_maxima_meses': 'Idade Máxima (meses)',
            'sexo': 'Sexo',
            'raca': 'Raça',
            'peso_medio_kg': 'Peso Médio (kg)',
            'descricao': 'Descrição',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        idade_minima = cleaned_data.get('idade_minima_meses')
        idade_maxima = cleaned_data.get('idade_maxima_meses')
        
        if idade_minima is not None and idade_maxima is not None:
            if idade_minima >= idade_maxima:
                raise forms.ValidationError('A idade mínima deve ser menor que a idade máxima.')
        
        return cleaned_data
