"""
Context processors para templates
"""
from django.conf import settings


def demo_mode(request):
    """
    Adiciona DEMO_MODE ao contexto de todos os templates
    """
    try:
        # Verificar se o usuário está autenticado de forma segura
        if hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            from .helpers_acesso import is_usuario_demo
            is_demo_user = is_usuario_demo(request.user)
        else:
            is_demo_user = False
    except Exception:
        is_demo_user = False
    
    return {
        'DEMO_MODE': getattr(settings, 'DEMO_MODE', False),
        'DEMO_LINK_PAGAMENTO': getattr(settings, 'DEMO_LINK_PAGAMENTO', '/assinaturas/'),
        'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'IS_DEMO_USER': is_demo_user,  # Indica se o usuário atual é demo
    }


def assinatura_info(request):
    """
    Adiciona informações de assinatura ao contexto de todos os templates.
    Usado para mostrar o botão "Garanta sua assinatura agora" quando necessário.
    """
    # Verificar se o usuário está autenticado de forma segura
    try:
        if not hasattr(request, 'user') or not hasattr(request.user, 'is_authenticated') or not request.user.is_authenticated:
            return {
                'acesso_liberado': True,  # Usuários não autenticados não precisam de verificação
                'assinatura': None,
                'IS_DEMO_USER': False,
                'IS_ASSINANTE': False,  # Usuários não autenticados não são assinantes
            }
        
        user = request.user
        
        # Superusuários e staff sempre têm acesso
        if user.is_superuser or user.is_staff:
            return {
                'acesso_liberado': True,
                'assinatura': None,
                'IS_DEMO_USER': False,
                'IS_ASSINANTE': True,  # Superusuários são tratados como assinantes
            }
        
        # Verificar se é usuário demo (usuários criados pelo botão demonstração ou demo padrão)
        from .helpers_acesso import is_usuario_demo
        is_demo_user = is_usuario_demo(user)

        # Verificar se tem assinatura ativa PRIMEIRO
        from .helpers_acesso import is_usuario_assinante
        is_assinante = is_usuario_assinante(user)

        # Se for assinante ativo, priorizar isso sobre ser demo
        if is_assinante:
            # Mesmo que seja demo, se tem assinatura ativa, é tratado como assinante
            request.IS_DEMO_USER = False  # Não mostrar como demo se é assinante
            return {
                'acesso_liberado': True,
                'assinatura': None,  # Poderia buscar a assinatura aqui se necessário
                'IS_DEMO_USER': False,
                'IS_ASSINANTE': True,
            }

        # Se for usuário demo (mas não assinante), acesso restrito
        if is_demo_user:
            request.IS_DEMO_USER = is_demo_user  # Adiciona ao request para uso em outros middlewares/views
            return {
                'acesso_liberado': False,  # Usuários demo têm acesso restrito (pré-lançamento)
                'assinatura': None,
                'IS_DEMO_USER': True,
                'IS_ASSINANTE': False,  # Demo nunca é assinante
            }
        
        # Verificar se o middleware já adicionou as informações
        if hasattr(request, 'acesso_liberado') and hasattr(request, 'assinatura'):
            is_assinante_middleware = not is_demo_user and request.acesso_liberado
            return {
                'acesso_liberado': request.acesso_liberado,
                'assinatura': request.assinatura,
                'IS_DEMO_USER': False,
                'IS_ASSINANTE': is_assinante_middleware,
            }
        
        # Se o middleware não executou, buscar diretamente usando função segura
        try:
            from .helpers_db import obter_assinatura_usuario_seguro
            assinatura = obter_assinatura_usuario_seguro(user)
            if assinatura:
                try:
                    acesso_liberado = assinatura.acesso_liberado if hasattr(assinatura, 'acesso_liberado') else False
                except Exception:
                    acesso_liberado = False
            else:
                acesso_liberado = False
                assinatura = None
        except Exception:
            acesso_liberado = True  # Em caso de erro, permitir acesso
            assinatura = None
        
        # Verificar se é assinante (não demo e com acesso liberado)
        is_assinante = not is_demo_user and acesso_liberado
        
        return {
            'acesso_liberado': acesso_liberado,
            'assinatura': assinatura,
            'IS_DEMO_USER': False,
            'IS_ASSINANTE': is_assinante,  # True apenas para assinantes (não demo)
        }
    except Exception:
        # Em caso de qualquer erro, retornar valores padrão seguros
        return {
            'acesso_liberado': True,  # Em caso de erro, permitir acesso
            'assinatura': None,
            'IS_DEMO_USER': False,
            'IS_ASSINANTE': False,
        }


def produtores_menu(request):
    """
    Adiciona lista de produtores ao contexto para uso no menu lateral.
    - Se for admin (superusuário): mostra TODOS os produtores cadastrados
    - Se for assinante: mostra apenas os produtores que ele cadastrou (usuario_responsavel=user)
    - Se for usuário normal: mostra apenas os produtores que ele cadastrou
    """
    # Sempre retornar uma lista vazia por padrão
    default_return = {'produtores_menu': []}
    
    # Verificar se o usuário está autenticado de forma segura
    try:
        if not hasattr(request, 'user'):
            return default_return
        
        user = request.user
        
        # Verificar se o usuário está autenticado de forma segura
        if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return default_return
    except Exception:
        # Se houver qualquer erro ao acessar request.user, retornar lista vazia
        return default_return
    
    try:
        from .models import ProdutorRural
        from django.db import DatabaseError, OperationalError, ProgrammingError
        
        # Verificar se a tabela existe antes de fazer a query
        try:
            # Verificar se é admin (superusuário ou staff)
            if user.is_superuser or user.is_staff:
                # Admin: mostrar TODOS os produtores cadastrados
                produtores = ProdutorRural.objects.all().order_by('nome')
            else:
                # Verificar se é assinante usando função segura
                try:
                    from .helpers_db import obter_assinatura_usuario_seguro, obter_usuarios_tenant_seguro
                    
                    assinatura = obter_assinatura_usuario_seguro(user)
                    
                    if assinatura and hasattr(assinatura, 'status') and assinatura.status == 'ATIVA':
                        # Assinante: buscar todos os usuários da mesma assinatura (equipe)
                        usuarios_tenant = obter_usuarios_tenant_seguro(assinatura)
                        
                        # Obter IDs dos usuários da equipe
                        usuarios_ids = [tu.usuario.id for tu in usuarios_tenant]
                        
                        # Também incluir o próprio usuário (pode não estar em TenantUsuario se for o dono da assinatura)
                        usuarios_ids.append(user.id)
                        
                        # Filtrar produtores cadastrados por esses usuários (equipe do assinante)
                        produtores = ProdutorRural.objects.filter(
                            usuario_responsavel__id__in=usuarios_ids
                        ).order_by('nome')
                    else:
                        # Usuário normal ou assinante inativo: mostrar apenas os produtores que ele cadastrou
                        produtores = ProdutorRural.objects.filter(
                            usuario_responsavel=user
                        ).order_by('nome')
                except Exception:
                    # Em caso de erro, comportamento seguro: apenas seus próprios produtores
                    produtores = ProdutorRural.objects.filter(
                        usuario_responsavel=user
                    ).order_by('nome')
            
            # Converter para lista para evitar problemas de lazy evaluation
            produtores_list = list(produtores)
            
            return {
                'produtores_menu': produtores_list,
            }
        except (DatabaseError, OperationalError, ProgrammingError) as e:
            # Erro de banco de dados - retornar lista vazia
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Erro ao buscar produtores no context processor: {e}')
            return default_return
        except Exception as e:
            # Qualquer outro erro na query - retornar lista vazia
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Erro inesperado ao buscar produtores no context processor: {e}')
            return default_return
    except ImportError:
        # Modelo não existe ainda - retornar lista vazia
        return default_return
    except Exception:
        # Qualquer outro erro - retornar lista vazia silenciosamente
        return default_return