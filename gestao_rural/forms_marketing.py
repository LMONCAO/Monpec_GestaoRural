"""
Forms para o módulo de Marketing
"""
from django import forms
from .models_marketing import (
    TemplatePost, PostGerado, LeadInteressado, CampanhaMarketing, ConfiguracaoMarketing
)


class TemplatePostForm(forms.ModelForm):
    """Form para criar/editar template de post"""
    
    class Meta:
        model = TemplatePost
        fields = [
            'nome', 'tipo_post', 'rede_social', 'conteudo', 'hashtags',
            'variaveis_disponiveis', 'ativo'
        ]
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'rows': 15,
                'class': 'form-control',
                'placeholder': 'Use {variavel} para incluir variáveis que serão substituídas'
            }),
            'hashtags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: #MONPEC, #GestãoRural, #Agronegócio'
            }),
            'variaveis_disponiveis': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'JSON com variáveis disponíveis. Ex: {"variavel1": "valor1"}'
            }),
        }
        help_texts = {
            'conteudo': 'Use variáveis entre chaves: {nome_produto}, {beneficio_1}, {cta_padrao}, etc.',
            'hashtags': 'Separe as hashtags por vírgula',
            'variaveis_disponiveis': 'Variáveis adicionais em formato JSON (opcional)',
        }


class PostGeradoForm(forms.ModelForm):
    """Form para editar post gerado"""
    
    class Meta:
        model = PostGerado
        fields = [
            'titulo', 'conteudo_final', 'hashtags_final', 'rede_social',
            'tipo_post', 'status', 'agendar_para'
        ]
        widgets = {
            'conteudo_final': forms.Textarea(attrs={
                'rows': 15,
                'class': 'form-control'
            }),
            'hashtags_final': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'agendar_para': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }


class LeadForm(forms.ModelForm):
    """Form para criar/editar lead"""
    
    class Meta:
        model = LeadInteressado
        fields = [
            'nome', 'email', 'telefone', 'propriedade_nome',
            'tipo_atividade', 'status', 'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'propriedade_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da sua propriedade/fazenda'
            }),
            'tipo_atividade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observacoes': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control'
            }),
        }


class CampanhaForm(forms.ModelForm):
    """Form para criar/editar campanha"""
    
    class Meta:
        model = CampanhaMarketing
        fields = [
            'nome', 'descricao', 'data_inicio', 'data_fim',
            'objetivo_principal', 'publico_alvo', 'meta_leads',
            'meta_conversoes', 'ativa'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'data_fim': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'objetivo_principal': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'publico_alvo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'meta_leads': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_conversoes': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ConfiguracaoMarketingForm(forms.ModelForm):
    """Form para configurações de marketing"""
    
    class Meta:
        model = ConfiguracaoMarketing
        fields = [
            'url_site', 'url_whatsapp', 'email_contato',
            'mensagem_cta_padrao', 'variaveis_padrao',
            'ativar_acesso_gratuito', 'mensagem_acesso_gratuito'
        ]
        widgets = {
            'url_site': forms.URLInput(attrs={'class': 'form-control'}),
            'url_whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '5511999999999'
            }),
            'email_contato': forms.EmailInput(attrs={'class': 'form-control'}),
            'mensagem_cta_padrao': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'variaveis_padrao': forms.Textarea(attrs={
                'rows': 10,
                'class': 'form-control',
                'placeholder': 'JSON com variáveis padrão. Ex: {"variavel": "valor"}'
            }),
            'mensagem_acesso_gratuito': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }


class GerarPostForm(forms.Form):
    """Form para gerar novo post"""
    
    template = forms.ModelChoiceField(
        queryset=TemplatePost.objects.filter(ativo=True),
        required=False,
        label='Template',
        help_text='Escolha um template específico ou deixe em branco para gerar aleatório',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tipo_post = forms.ChoiceField(
        choices=[('', 'Qualquer tipo')] + TemplatePost.TIPO_POST_CHOICES,
        required=False,
        label='Tipo de Post',
        help_text='Obrigatório se não escolher template',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    rede_social = forms.ChoiceField(
        choices=TemplatePost.REDE_SOCIAL_CHOICES,
        initial='geral',
        label='Rede Social',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    variaveis_extras = forms.CharField(
        required=False,
        label='Variáveis Extras (JSON)',
        help_text='Variáveis adicionais em formato JSON. Ex: {"variavel": "valor"}',
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': '{"variavel1": "valor1", "variavel2": "valor2"}'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        template = cleaned_data.get('template')
        tipo_post = cleaned_data.get('tipo_post')
        
        if not template and not tipo_post:
            raise forms.ValidationError(
                'Escolha um template ou um tipo de post para gerar.'
            )
        
        # Validar JSON das variáveis extras
        variaveis_extras = cleaned_data.get('variaveis_extras')
        if variaveis_extras:
            try:
                import json
                json.loads(variaveis_extras)
            except json.JSONDecodeError:
                raise forms.ValidationError(
                    'Variáveis extras devem estar em formato JSON válido.'
                )
        
        return cleaned_data
    
    def clean_variaveis_extras(self):
        variaveis_extras = self.cleaned_data.get('variaveis_extras')
        if variaveis_extras:
            import json
            try:
                return json.loads(variaveis_extras)
            except json.JSONDecodeError:
                raise forms.ValidationError('JSON inválido')
        return {}






























