from __future__ import annotations

from django import forms

from .models import PlanoAssinatura, TenantUsuario


class TenantUsuarioForm(forms.Form):
    nome = forms.CharField(label="Nome completo", max_length=150)
    email = forms.EmailField(label="E-mail de acesso")
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
    senha_temporaria = forms.CharField(
        label="Definir senha (opcional)",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Caso deixe em branco, o sistema criará uma senha temporária automaticamente.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


