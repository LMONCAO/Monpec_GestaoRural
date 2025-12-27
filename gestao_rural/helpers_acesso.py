"""
Helpers para verificação de acesso e permissões de usuários.
Centraliza a lógica para evitar importação circular.
"""


def is_usuario_assinante(user):
    """
    Verifica se o usuário é assinante (superusuário ou tem assinatura ativa).
    Retorna True se:
    - É superusuário ou staff
    - Tem assinatura ativa com acesso liberado
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser or user.is_staff:
        return True
    
    try:
        from .models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.filter(usuario=user).first()
        if assinatura and assinatura.acesso_liberado:
            return True
    except:
        pass
    
    return False









