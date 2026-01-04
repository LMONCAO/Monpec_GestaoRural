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
            'anos_experiencia', 'telefone', 'email', 'endereco',
            'vai_emitir_nfe',
            'certificado_digital', 'senha_certificado', 'certificado_valido_ate', 'certificado_tipo'
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
            'vai_emitir_nfe': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_vai_emitir_nfe'}),
            'certificado_digital': forms.FileInput(attrs={'class': 'form-control', 'accept': '.p12,.pfx'}),
            'senha_certificado': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'Senha do certificado digital'}),
            'certificado_valido_ate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'certificado_tipo': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campos de certificado não obrigatórios
        self.fields['senha_certificado'].required = False
        self.fields['certificado_digital'].required = False
        self.fields['certificado_valido_ate'].required = False
        self.fields['certificado_tipo'].required = False
        self.fields['vai_emitir_nfe'].required = False
    
    def save(self, commit=True):
        # Se a senha estiver vazia e já existir uma senha, manter a senha existente
        instance = super().save(commit=False)
        if not self.cleaned_data.get('senha_certificado') and self.instance.pk:
            if hasattr(self.instance, 'senha_certificado') and self.instance.senha_certificado:
                instance.senha_certificado = self.instance.senha_certificado
        if commit:
            instance.save()
        return instance


class PropriedadeForm(forms.ModelForm):
    tipo_ciclo_pecuario = forms.MultipleChoiceField(
        choices=Propriedade.TIPO_CICLO_PECUARIO_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Tipos de Ciclo Pecuário"
    )
    produtor = forms.ModelChoiceField(
        queryset=ProdutorRural.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Produtor",
        empty_label="Selecione o produtor"
    )

    class Meta:
        model = Propriedade
        fields = [
            'produtor', 'nome_propriedade', 'municipio', 'uf', 'endereco', 'cep', 'bairro', 
            'latitude', 'longitude', 'ponto_referencia', 'area_total_ha', 'tipo_operacao',
            'tipo_ciclo_pecuario', 'tipo_propriedade', 'valor_hectare_proprio', 
            'valor_mensal_hectare_arrendamento', 'nirf', 'incra', 'car', 'inscricao_estadual'
        ]
        widgets = {
            'nome_propriedade': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.Select(attrs={'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'ponto_referencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'area_total_ha': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'tipo_operacao': forms.Select(attrs={'class': 'form-control'}),
            'tipo_propriedade': forms.Select(attrs={'class': 'form-control'}),
            'valor_hectare_proprio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'valor_mensal_hectare_arrendamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'nirf': forms.TextInput(attrs={'class': 'form-control'}),
            'incra': forms.TextInput(attrs={'class': 'form-control'}),
            'car': forms.TextInput(attrs={'class': 'form-control'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        produtor_initial = kwargs.pop('produtor_initial', None)
        super().__init__(*args, **kwargs)
        
        # Configurar queryset do campo produtor baseado no usuário
        if user:
            # Verificar se é admin (superusuário ou staff) - pode ver TODOS os produtores
            if user.is_superuser or user.is_staff:
                # Admin pode ver todos os produtores
                self.fields['produtor'].queryset = ProdutorRural.objects.all().order_by('nome')
            else:
                # Verificar se é assinante usando função segura
                try:
                    from .helpers_db import obter_assinatura_usuario_seguro, obter_usuarios_tenant_seguro
                    
                    assinatura = obter_assinatura_usuario_seguro(user)
                    
                    if assinatura and hasattr(assinatura, 'ativa') and assinatura.ativa:
                        # Assinante: buscar todos os usuários da mesma assinatura (equipe)
                        usuarios_tenant = obter_usuarios_tenant_seguro(assinatura)
                        
                        # Obter IDs dos usuários da equipe
                        usuarios_ids = [tu.usuario.id for tu in usuarios_tenant]
                        
                        # Também incluir o próprio usuário (pode não estar em TenantUsuario se for o dono da assinatura)
                        usuarios_ids.append(user.id)
                        
                        # Filtrar produtores cadastrados por esses usuários (equipe do assinante)
                        self.fields['produtor'].queryset = ProdutorRural.objects.filter(
                            usuario_responsavel__id__in=usuarios_ids
                        ).order_by('nome')
                    else:
                        # Usuário normal ou assinante inativo: só vê seus próprios produtores
                        self.fields['produtor'].queryset = ProdutorRural.objects.filter(
                            usuario_responsavel=user
                        ).order_by('nome')
                except Exception:
                    # Em caso de erro, comportamento seguro: apenas seus próprios produtores
                    self.fields['produtor'].queryset = ProdutorRural.objects.filter(
                        usuario_responsavel=user
                    ).order_by('nome')
        
        # Se já existe uma instância (edição), definir o produtor inicial
        if self.instance and self.instance.pk:
            self.fields['produtor'].initial = self.instance.produtor
            # Não desabilitar o campo, apenas torná-lo readonly visualmente
            # Desabilitar impede o envio do valor no POST
            self.fields['produtor'].widget.attrs['readonly'] = True
            self.fields['produtor'].widget.attrs['style'] = 'background-color: #e9ecef; cursor: not-allowed;'
        elif produtor_initial:
            # Se foi passado um produtor inicial (via URL), pré-selecionar mas SEMPRE mostrar o campo
            # Permitir que o usuário possa alterar a seleção
            self.fields['produtor'].initial = produtor_initial
            # NÃO ocultar o campo - sempre permitir seleção
            # self.fields['produtor'].widget.attrs['style'] = 'display: none;'  # REMOVIDO
        
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
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Se o campo produtor não foi enviado (por estar readonly), usar o produtor da instância existente
        if self.instance and self.instance.pk and 'produtor' not in self.cleaned_data:
            instance.produtor = self.instance.produtor
        if commit:
            instance.save()
        return instance


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
