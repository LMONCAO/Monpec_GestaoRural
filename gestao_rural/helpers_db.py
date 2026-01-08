"""
Helpers para verificação e tratamento de erros de banco de dados
"""
import logging
from django.db import connection, ProgrammingError, OperationalError

logger = logging.getLogger(__name__)


def tabela_existe(nome_tabela):
    """
    Verifica se uma tabela existe no banco de dados PostgreSQL.
    Retorna True se existe, False caso contrário.
    """
    try:
        with connection.cursor() as cursor:
            # Sistema usa apenas PostgreSQL
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, [nome_tabela])
            
            result = cursor.fetchone()
            return result[0] if result else False
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
        
        # SEMPRE buscar com SQL direto para evitar campos do Stripe removidos
        # Não usar user.assinatura diretamente pois pode tentar buscar todos os campos
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
                    class AssinaturaMock:
                        def __init__(self, row_data):
                            self.id = row_data[0]
                            self.usuario_id = row_data[1]
                            self.produtor_id = row_data[2]
                            self.plano_id = row_data[3]
                            self.status = row_data[4]
                            self.mercadopago_customer_id = row_data[5]
                            self.mercadopago_subscription_id = row_data[6]
                            self.gateway_pagamento = row_data[7]
                            self.ultimo_checkout_id = row_data[8]
                            self.current_period_end = row_data[9]
                            self.cancelamento_agendado = row_data[10]
                            self.metadata = row_data[11]
                            self.data_liberacao = row_data[12]
                            self.criado_em = row_data[13]
                            self.atualizado_em = row_data[14]
                            self.plano = None
                            from datetime import date
                            self.acesso_liberado = row_data[12] is None or row_data[12] <= date.today()
                    assinatura = AssinaturaMock(row)
                    # Carregar plano se necessário
                    if assinatura.plano_id:
                        try:
                            from .models import PlanoAssinatura
                            assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
                        except:
                            pass
                    return assinatura
        except (ProgrammingError, OperationalError) as e:
            logger.debug(f'Tabela AssinaturaCliente não acessível para usuário {user.id}: {e}')
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


