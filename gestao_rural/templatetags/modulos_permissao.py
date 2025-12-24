from django import template
from django.contrib.auth.models import User
from gestao_rural.models import TenantUsuario

register = template.Library()


@register.filter
def tem_acesso_modulo(usuario, modulo):
    """
    Template filter para verificar se o usuário tem acesso a um módulo específico.
    
    Uso: {% if user|tem_acesso_modulo:'pecuaria' %}
    """
    if not usuario or not usuario.is_authenticated:
        return False
    
    # Se o usuário tem perfil de tenant, verifica os módulos
    if hasattr(usuario, 'tenant_profile'):
        tenant_profile = usuario.tenant_profile
        return tenant_profile.tem_acesso_modulo(modulo)
    
    # Se não tem perfil de tenant, assume que é admin e tem acesso a tudo
    # Ou pode ser um superuser
    return usuario.is_superuser or not hasattr(usuario, 'tenant_profile')


@register.simple_tag
def usuario_pode_acessar_modulo(usuario, modulo):
    """
    Template tag para verificar se o usuário tem acesso a um módulo específico.
    
    Uso: {% usuario_pode_acessar_modulo user 'pecuaria' as pode_acessar %}
    """
    if not usuario or not usuario.is_authenticated:
        return False
    
    # Se o usuário tem perfil de tenant, verifica os módulos
    if hasattr(usuario, 'tenant_profile'):
        tenant_profile = usuario.tenant_profile
        return tenant_profile.tem_acesso_modulo(modulo)
    
    # Se não tem perfil de tenant, assume que tem acesso
    return True


@register.simple_tag
def obter_modulos_usuario(usuario):
    """
    Retorna lista de módulos que o usuário pode acessar.
    
    Uso: {% obter_modulos_usuario user as modulos %}
    """
    if not usuario or not usuario.is_authenticated:
        return []
    
    if hasattr(usuario, 'tenant_profile'):
        tenant_profile = usuario.tenant_profile
        return tenant_profile.modulos_autorizados
    
    return []


@register.filter
def eh_admin(usuario):
    """
    Template filter para verificar se o usuário é administrador.
    
    Uso: {% if user|eh_admin %}
    """
    if not usuario or not usuario.is_authenticated:
        return False
    
    # Superuser sempre é admin
    if usuario.is_superuser:
        return True
    
    # Verificar se tem assinatura (usuário master)
    if hasattr(usuario, 'assinatura'):
        return True
    
    # Verificar perfil de tenant
    if hasattr(usuario, 'tenant_profile'):
        return usuario.tenant_profile.perfil == TenantUsuario.Perfil.ADMIN
    
    return False

