"""
Helpers para verificação de acesso e permissões de usuários.
Centraliza a lógica para evitar importação circular.
"""


def is_usuario_demo(user):
    """
    Verifica se o usuário é demo.
    Retorna True se:
    - username está em ['demo', 'demo_monpec']
    - ou tem registro UsuarioAtivo (criado pelo botão demonstração)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar se é usuário demo padrão
    if user.username in ['demo', 'demo_monpec']:
        return True
    
    # Verificar se tem UsuarioAtivo (usuário criado pelo popup)
    try:
        from .models_auditoria import UsuarioAtivo
        UsuarioAtivo.objects.get(usuario=user)
        return True
    except:
        return False


def is_usuario_assinante(user):
    """
    Verifica se o usuário é assinante (superusuário ou tem assinatura ativa).
    Retorna True se:
    - É superusuário ou staff
    - Tem assinatura ativa com acesso liberado
    
    IMPORTANTE: Usuários demo NUNCA são assinantes, mesmo que tenham assinatura no banco.
    """
    if not user or not user.is_authenticated:
        return False
    
    # IMPORTANTE: Verificar se é demo PRIMEIRO - usuários demo nunca são assinantes
    if is_usuario_demo(user):
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



















