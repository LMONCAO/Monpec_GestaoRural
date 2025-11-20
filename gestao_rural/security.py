"""
Módulo de segurança do sistema MONPEC
Implementa validações de senha forte, bloqueio de contas e outras medidas de segurança
"""
import re
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Senhas comuns que devem ser bloqueadas
SENHAS_FRACAS = [
    '123456', '123456789', '12345678', '1234567890',
    'password', 'senha', 'admin', 'administrador',
    '1234', '12345', 'qwerty', 'abc123',
    'monpec', 'monpec123', 'admin123',
    'senha123', 'password123', '12345678901',
    'root', 'toor', 'pass', 'pass123',
    'teste', 'teste123', 'demo', 'demo123',
]

# Usuários padrão que devem ser desabilitados ou removidos
USUARIOS_PADRAO_PERIGOSOS = [
    'admin', 'administrator', 'root', 'test', 'teste',
    'demo', 'guest', 'user', 'usuario', 'default',
]


def validar_senha_forte(senha):
    """
    Valida se a senha atende aos critérios de segurança:
    - Mínimo 12 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial
    - Não pode ser uma senha comum
    """
    if len(senha) < 12:
        raise ValidationError(
            'A senha deve ter no mínimo 12 caracteres.',
            code='senha_curta'
        )
    
    if senha.lower() in [s.lower() for s in SENHAS_FRACAS]:
        raise ValidationError(
            'Esta senha é muito comum e não é permitida. Use uma senha mais segura.',
            code='senha_fraca'
        )
    
    if not re.search(r'[A-Z]', senha):
        raise ValidationError(
            'A senha deve conter pelo menos uma letra maiúscula.',
            code='sem_maiuscula'
        )
    
    if not re.search(r'[a-z]', senha):
        raise ValidationError(
            'A senha deve conter pelo menos uma letra minúscula.',
            code='sem_minuscula'
        )
    
    if not re.search(r'\d', senha):
        raise ValidationError(
            'A senha deve conter pelo menos um número.',
            code='sem_numero'
        )
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', senha):
        raise ValidationError(
            'A senha deve conter pelo menos um caractere especial (!@#$%^&*...).',
            code='sem_especial'
        )
    
    # Verifica se a senha não é uma sequência simples
    if re.search(r'(.)\1{3,}', senha):
        raise ValidationError(
            'A senha não pode conter caracteres repetidos em sequência.',
            code='sequencia_repetida'
        )
    
    # Verifica sequências comuns (123, abc, etc)
    sequencias_comuns = ['123', 'abc', 'qwe', 'asd', 'zxc']
    senha_lower = senha.lower()
    for seq in sequencias_comuns:
        if seq in senha_lower or seq[::-1] in senha_lower:
            raise ValidationError(
                'A senha não pode conter sequências comuns (123, abc, etc).',
                code='sequencia_comum'
            )
    
    return True


def verificar_tentativas_login(username, ip_address):
    """
    Verifica se o usuário/IP excedeu o limite de tentativas de login.
    Retorna (bloqueado, tempo_restante_segundos)
    """
    # Limite: 5 tentativas em 15 minutos
    MAX_TENTATIVAS = 5
    TEMPO_BLOQUEIO_MINUTOS = 15
    
    chave_usuario = f'login_attempts_user_{username}'
    chave_ip = f'login_attempts_ip_{ip_address}'
    
    tentativas_usuario = cache.get(chave_usuario, 0)
    tentativas_ip = cache.get(chave_ip, 0)
    
    if tentativas_usuario >= MAX_TENTATIVAS:
        tempo_restante = cache.ttl(chave_usuario)
        if tempo_restante is None:
            tempo_restante = TEMPO_BLOQUEIO_MINUTOS * 60
        return True, tempo_restante
    
    if tentativas_ip >= MAX_TENTATIVAS:
        tempo_restante = cache.ttl(chave_ip)
        if tempo_restante is None:
            tempo_restante = TEMPO_BLOQUEIO_MINUTOS * 60
        return True, tempo_restante
    
    return False, 0


def registrar_tentativa_login_falha(username, ip_address):
    """
    Registra uma tentativa de login falha
    """
    chave_usuario = f'login_attempts_user_{username}'
    chave_ip = f'login_attempts_ip_{ip_address}'
    
    TEMPO_BLOQUEIO_SEGUNDOS = 15 * 60  # 15 minutos
    
    # Incrementa tentativas do usuário
    tentativas_usuario = cache.get(chave_usuario, 0) + 1
    cache.set(chave_usuario, tentativas_usuario, TEMPO_BLOQUEIO_SEGUNDOS)
    
    # Incrementa tentativas do IP
    tentativas_ip = cache.get(chave_ip, 0) + 1
    cache.set(chave_ip, tentativas_ip, TEMPO_BLOQUEIO_SEGUNDOS)
    
    logger.warning(
        f'Tentativa de login falha - Usuário: {username}, IP: {ip_address}, '
        f'Tentativas usuário: {tentativas_usuario}, Tentativas IP: {tentativas_ip}'
    )


def limpar_tentativas_login(username=None, ip_address=None):
    """
    Limpa as tentativas de login (chamado após login bem-sucedido)
    """
    if username:
        cache.delete(f'login_attempts_user_{username}')
    if ip_address:
        cache.delete(f'login_attempts_ip_{ip_address}')


def verificar_usuarios_inseguros():
    """
    Verifica e retorna lista de usuários com problemas de segurança:
    - Usuários padrão perigosos
    - Usuários com senhas fracas
    - Usuários sem senha definida
    """
    problemas = []
    
    usuarios = User.objects.all()
    for usuario in usuarios:
        problemas_usuario = []
        
        # Verifica se é um usuário padrão perigoso
        if usuario.username.lower() in [u.lower() for u in USUARIOS_PADRAO_PERIGOSOS]:
            problemas_usuario.append('Usuário padrão perigoso')
        
        # Verifica se o usuário está ativo mas tem senha vazia ou muito simples
        if usuario.is_active:
            if not usuario.has_usable_password():
                problemas_usuario.append('Usuário sem senha definida')
            elif usuario.check_password('123456') or usuario.check_password('admin'):
                problemas_usuario.append('Senha muito fraca detectada')
        
        # Verifica se é superusuário com nome padrão
        if usuario.is_superuser and usuario.username.lower() in ['admin', 'administrator', 'root']:
            problemas_usuario.append('Superusuário com nome padrão')
        
        if problemas_usuario:
            problemas.append({
                'usuario': usuario,
                'problemas': problemas_usuario
            })
    
    return problemas


def desabilitar_usuarios_padrao():
    """
    Desabilita usuários padrão perigosos que não devem estar ativos
    """
    usuarios_desabilitados = []
    
    for username in USUARIOS_PADRAO_PERIGOSOS:
        try:
            usuario = User.objects.get(username__iexact=username)
            if usuario.is_active:
                usuario.is_active = False
                usuario.save()
                usuarios_desabilitados.append(username)
                logger.warning(f'Usuário padrão desabilitado: {username}')
        except User.DoesNotExist:
            pass
    
    return usuarios_desabilitados


def verificar_senha_nao_alterada(usuario, dias_maximo=90):
    """
    Verifica se o usuário não alterou a senha há muito tempo
    """
    if not hasattr(usuario, 'last_password_change'):
        return False, None
    
    if usuario.last_password_change:
        dias_sem_alterar = (timezone.now() - usuario.last_password_change).days
        if dias_sem_alterar > dias_maximo:
            return True, dias_sem_alterar
    
    return False, None






