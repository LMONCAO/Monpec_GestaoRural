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


def get_propriedade_atual(request):
    """
    Obtém a propriedade atual baseada na requisição.
    Primeiro tenta obter da sessão, depois da primeira propriedade do usuário.
    """
    if not request.user or not request.user.is_authenticated:
        return None

    try:
        from .models import Propriedade

        # Tentar obter da sessão
        propriedade_id = request.session.get('propriedade_atual_id')
        if propriedade_id:
            try:
                propriedade = Propriedade.objects.get(
                    id=propriedade_id,
                    produtor__usuario_responsavel=request.user
                )
                return propriedade
            except Propriedade.DoesNotExist:
                pass

        # Se não encontrou na sessão, pegar a primeira propriedade do usuário
        propriedade = Propriedade.objects.filter(
            produtor__usuario_responsavel=request.user
        ).first()

        # Salvar na sessão para próximos acessos
        if propriedade:
            request.session['propriedade_atual_id'] = propriedade.id

        return propriedade

    except Exception as e:
        # Em caso de erro, retornar None silenciosamente
        return None


def is_usuario_assinante(user):
    """
    Verifica se o usuário é assinante (superusuário ou tem assinatura ativa).
    Retorna True se:
    - É superusuário ou staff
    - Tem assinatura ativa com acesso liberado

    NOTA: Usuários com assinatura ativa são considerados assinantes independente do status demo.
    """
    if not user or not user.is_authenticated:
        return False

    # Superusuários e staff sempre são assinantes
    if user.is_superuser or user.is_staff:
        return True

    try:
        # Usar ORM do Django ao invés de SQL puro para compatibilidade com SQLite
        from .models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.filter(
            usuario=user,
            status='ATIVA'
        ).first()

        if assinatura:
            from datetime import date
            data_liberacao = getattr(assinatura, 'data_liberacao', None)
            acesso_liberado = data_liberacao is None or data_liberacao <= date.today()
            if acesso_liberado:
                return True
    except Exception as e:
        # Se a tabela não existir ou houver erro, retorna False silenciosamente
        logger.warning(f"Erro ao verificar assinatura para usuário {user.username}: {e}")
        pass

    return False



















