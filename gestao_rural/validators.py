# -*- coding: utf-8 -*-
"""
Validadores customizados para senhas
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SenhaAssinanteValidator:
    """
    Validador de senha para assinantes:
    - Mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    """
    
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("A senha deve ter no mínimo 8 caracteres."),
                code='password_too_short',
            )
        
        if not any(c.isupper() for c in password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra maiúscula."),
                code='password_no_uppercase',
            )
        
        if not any(c.islower() for c in password):
            raise ValidationError(
                _("A senha deve conter pelo menos uma letra minúscula."),
                code='password_no_lowercase',
            )
    
    def get_help_text(self):
        return _("A senha deve ter no mínimo 8 caracteres, incluindo pelo menos uma letra maiúscula e uma minúscula.")












