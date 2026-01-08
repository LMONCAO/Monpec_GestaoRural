"""
Helpers para verificação de acesso e permissões de usuários.
Centraliza a lógica para evitar importação circular.
"""


def is_usuario_demo(user):
    """
    Verifica se o usuário é demo.
    Retorna True se:
    - username está em ['demo', 'demo_monpec']
    - ou tem propriedade "Fazenda Demonstracao" (criado pelo formulário demo)
    - ou tem registro UsuarioAtivo (criado pelo botão demonstração)

    IMPORTANTE: Superusuários e staff NUNCA são considerados demo, mesmo que tenham UsuarioAtivo.
    """
    if not user or not user.is_authenticated:
        return False

    # IMPORTANTE: Superusuários e staff nunca são demo
    if user.is_superuser or user.is_staff:
        return False

    # Verificar se é usuário demo padrão
    if user.username in ['demo', 'demo_monpec']:
        return True

    # Verificar se tem propriedade "Fazenda Demonstracao" (formulário demo)
    try:
        from .models import Propriedade
        propriedade_demo = Propriedade.objects.filter(
            produtor__usuario_responsavel=user,
            nome_propriedade='Fazenda Demonstracao'
        ).exists()
        if propriedade_demo:
            return True
    except:
        pass

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
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, usuario_id, produtor_id, plano_id, status,
                       mercadopago_customer_id, mercadopago_subscription_id,
                       gateway_pagamento, ultimo_checkout_id, current_period_end,
                       cancelamento_agendado, metadata, data_liberacao,
                       criado_em, atualizado_em
                FROM gestao_rural_assinaturacliente
                WHERE usuario_id = %s
                LIMIT 1
            """, [user.id])
            row = cursor.fetchone()
            if row:
                from datetime import date
                data_liberacao = row[12]
                acesso_liberado = data_liberacao is None or data_liberacao <= date.today()
                status = row[4]
                if status == 'ATIVA' and acesso_liberado:
                    return True
    except:
        pass
    
    return False



















