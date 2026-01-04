"""
Helpers para verificação e tratamento de erros de banco de dados
"""
import logging
from django.db import connection, ProgrammingError, OperationalError

logger = logging.getLogger(__name__)


def tabela_existe(nome_tabela):
    """
    Verifica se uma tabela existe no banco de dados.
    Retorna True se existe, False caso contrário.
    """
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [nome_tabela])
            elif connection.vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?;
                """, [nome_tabela])
            else:
                # MySQL ou outros
                cursor.execute("SHOW TABLES LIKE %s", [nome_tabela])
            
            return cursor.fetchone() is not None
    except (ProgrammingError, OperationalError) as e:
        logger.warning(f'Erro ao verificar se tabela {nome_tabela} existe: {e}')
        return False
    except Exception as e:
        logger.error(f'Erro inesperado ao verificar tabela {nome_tabela}: {e}')
        return False


def obter_assinatura_usuario_seguro(user):
    """
    Obtém a assinatura do usuário de forma segura, tratando erros de tabela não existente.
    Retorna None se não houver assinatura ou se houver erro.
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        # Verificar se as tabelas existem antes de acessar
        if not tabela_existe('gestao_rural_assinaturacliente'):
            logger.debug('Tabela AssinaturaCliente não existe ainda')
            return None
        
        from .models import AssinaturaCliente
        
        # Tentar acessar assinatura de diferentes formas
        try:
            if hasattr(user, 'assinatura'):
                return user.assinatura
        except Exception:
            pass
        
        # Verificar se tem tenant_profile (e se a tabela existe)
        if tabela_existe('gestao_rural_tenantusuario'):
            try:
                if hasattr(user, 'tenant_profile'):
                    tenant_profile = user.tenant_profile
                    if hasattr(tenant_profile, 'assinatura'):
                        return tenant_profile.assinatura
            except Exception:
                pass
        
        # Tentar buscar diretamente
        try:
            assinatura = AssinaturaCliente.objects.filter(usuario=user).first()
            if assinatura:
                return assinatura
        except (ProgrammingError, OperationalError):
            logger.debug(f'Tabela AssinaturaCliente não acessível para usuário {user.id}')
            return None
        except Exception as e:
            logger.warning(f'Erro ao buscar assinatura para usuário {user.id}: {e}')
            return None
        
        return None
    except ImportError:
        logger.debug('Modelo AssinaturaCliente não importável')
        return None
    except Exception as e:
        logger.warning(f'Erro inesperado ao obter assinatura: {e}')
        return None


def obter_usuarios_tenant_seguro(assinatura):
    """
    Obtém os usuários do tenant de forma segura.
    Retorna lista vazia se não houver usuários ou se houver erro.
    """
    if not assinatura:
        return []
    
    try:
        # Verificar se a tabela existe
        if not tabela_existe('gestao_rural_tenantusuario'):
            logger.debug('Tabela TenantUsuario não existe ainda')
            return []
        
        from .models import TenantUsuario
        
        try:
            usuarios_tenant = TenantUsuario.objects.filter(
                assinatura=assinatura,
                ativo=True
            ).select_related('usuario')
            return list(usuarios_tenant)
        except (ProgrammingError, OperationalError) as e:
            logger.debug(f'Tabela TenantUsuario não acessível: {e}')
            return []
        except Exception as e:
            logger.warning(f'Erro ao buscar usuários do tenant: {e}')
            return []
    except ImportError:
        logger.debug('Modelo TenantUsuario não importável')
        return []
    except Exception as e:
        logger.warning(f'Erro inesperado ao obter usuários do tenant: {e}')
        return []


def obter_usuario_ativo_seguro(user):
    """
    Obtém o registro UsuarioAtivo de forma segura.
    Retorna None se não existir ou se houver erro.
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        # Verificar se a tabela existe
        if not tabela_existe('gestao_rural_usuarioativo'):
            return None
        
        from .models_auditoria import UsuarioAtivo
        
        try:
            return UsuarioAtivo.objects.get(usuario=user)
        except UsuarioAtivo.DoesNotExist:
            return None
        except (ProgrammingError, OperationalError):
            return None
        except Exception as e:
            logger.warning(f'Erro ao buscar UsuarioAtivo: {e}')
            return None
    except ImportError:
        return None
    except Exception as e:
        logger.warning(f'Erro inesperado ao obter UsuarioAtivo: {e}')
        return None


