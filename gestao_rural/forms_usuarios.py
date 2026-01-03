from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from .models import PlanoAssinatura, TenantUsuario
from .validators import SenhaAssinanteValidator


class TenantUsuarioForm(forms.Form):
    nome = forms.CharField(label="Nome completo", max_length=150)
    username = forms.CharField(
        label="Nome de usuário (Login)", 
        max_length=150,
        required=False,
        help_text="Deixe em branco para gerar automaticamente a partir do nome"
    )
    email = forms.EmailField(label="E-mail de acesso")
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Digite a senha do usuário (mínimo 8 caracteres, 1 maiúscula, 1 minúscula). Se deixar em branco, o sistema gerará uma senha temporária.",
    )
    
    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        if senha:
            # Validar senha usando o validador customizado para assinantes
            validator = SenhaAssinanteValidator()
            try:
                validator.validate(senha)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return senha
    perfil = forms.ChoiceField(
        label="Perfil",
        choices=TenantUsuario.Perfil.choices,
    )
    modulos = forms.MultipleChoiceField(
        label="Módulos liberados",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[(mod, mod.title()) for mod in PlanoAssinatura.MODULOS_PADRAO],
    )

    def __init__(self, *args, modulos_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Atualizar choices dos módulos se fornecido
        if modulos_choices is not None:
            self.fields['modulos'].choices = modulos_choices
        
        for field_name, field in self.fields.items():
            if field_name == "modulos":
                field.widget.attrs.update({"class": "form-check-input"})
                continue
            css_class = "form-control"
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                css_class = ""
            field.widget.attrs.setdefault("class", css_class)


class TenantUsuarioUpdateForm(TenantUsuarioForm):
    usuario_id = forms.IntegerField(widget=forms.HiddenInput)


