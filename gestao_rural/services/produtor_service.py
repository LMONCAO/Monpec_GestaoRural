"""
Serviço para lógica de negócio relacionada a Produtores Rurais
Separa a lógica de negócio das views, facilitando testes e reutilização
"""
import logging
from typing import Optional, List
from django.contrib.auth.models import User
from django.db import transaction, ProgrammingError, DatabaseError, OperationalError
from django.db.models import Count, Q
from decimal import Decimal

from ..models import ProdutorRural, Propriedade
from ..helpers_acesso import is_usuario_assinante, is_usuario_demo

logger = logging.getLogger(__name__)


class ProdutorService:
    """Serviço para operações com Produtores Rurais"""
    
    @staticmethod
    def obter_produtores_do_usuario(user: User) -> List[ProdutorRural]:
        """
        Retorna lista de produtores disponíveis para o usuário.
        
        Regras:
        - Admin/Staff: todos os produtores
        - Assinante ativo: produtores da equipe (mesma assinatura)
        - Usuário normal: apenas produtores que ele cadastrou
        """
        try:
            if user.is_superuser or user.is_staff:
                # Admin: todos os produtores
                return ProdutorRural.objects.select_related(
                    'usuario_responsavel'
                ).annotate(
                    propriedades_count=Count('propriedade')
                ).order_by('nome')
            
            # Verificar se é assinante
            from ..models import AssinaturaCliente, TenantUsuario
            
            # Sempre usar defer() para evitar campos do Stripe removidos
            assinatura = AssinaturaCliente.objects.defer('stripe_customer_id', 'stripe_subscription_id').filter(usuario=user).first()
            
            if assinatura and assinatura.status == 'ATIVA':
                # Assinante: buscar todos os usuários da mesma assinatura (equipe)
                usuarios_tenant = TenantUsuario.objects.filter(
                    assinatura=assinatura,
                    ativo=True
                ).select_related('usuario')
                
                usuarios_ids = [tu.usuario.id for tu in usuarios_tenant]
                usuarios_ids.append(user.id)
                
                return ProdutorRural.objects.filter(
                    usuario_responsavel__id__in=usuarios_ids
                ).select_related(
                    'usuario_responsavel'
                ).annotate(
                    propriedades_count=Count('propriedade')
                ).order_by('nome')
            else:
                # Usuário normal: apenas os produtores que ele cadastrou
                return ProdutorRural.objects.filter(
                    usuario_responsavel=user
                ).select_related(
                    'usuario_responsavel'
                ).annotate(
                    propriedades_count=Count('propriedade')
                ).order_by('nome')
                
        except (ProgrammingError, DatabaseError, OperationalError) as e:
            logger.warning(f'Erro ao buscar produtores com annotate: {e}. Tentando query simplificada.')
            try:
                if user.is_superuser or user.is_staff:
                    return ProdutorRural.objects.select_related(
                        'usuario_responsavel'
                    ).order_by('nome')
                else:
                    return ProdutorRural.objects.filter(
                        usuario_responsavel=user
                    ).select_related(
                        'usuario_responsavel'
                    ).order_by('nome')
            except Exception as e2:
                logger.error(f'Erro ao buscar produtores mesmo com query simplificada: {e2}')
                return []
        except Exception as e:
            logger.error(f'Erro inesperado ao buscar produtores: {e}', exc_info=True)
            return []
    
    @staticmethod
    def pode_acessar_produtor(user: User, produtor: ProdutorRural) -> bool:
        """
        Verifica se o usuário tem permissão para acessar o produtor.
        
        Retorna True se:
        - É admin/staff
        - É assinante ativo (pode acessar produtores da equipe)
        - É o responsável pelo produtor
        """
        if user.is_superuser or user.is_staff:
            return True
        
        if is_usuario_assinante(user):
            # Assinante pode acessar produtores da equipe
            from ..models import AssinaturaCliente, TenantUsuario
            
            # Sempre usar defer() para evitar campos do Stripe removidos
            assinatura = AssinaturaCliente.objects.defer('stripe_customer_id', 'stripe_subscription_id').filter(usuario=user).first()
            
            if assinatura and assinatura.status == 'ATIVA':
                # Verificar se o produtor pertence a algum usuário da equipe
                usuarios_tenant = TenantUsuario.objects.filter(
                    assinatura=assinatura,
                    ativo=True
                ).values_list('usuario_id', flat=True)
                
                return produtor.usuario_responsavel_id in list(usuarios_tenant) + [user.id]
        
        # Usuário normal: apenas se for o responsável
        return produtor.usuario_responsavel_id == user.id
    
    @staticmethod
    @transaction.atomic
    def criar_produtor_com_propriedade_demo(
        user: User, 
        dados_produtor: dict,
        nome_propriedade: str = 'Monpec1'
    ) -> tuple[ProdutorRural, Propriedade]:
        """
        Cria um produtor e uma propriedade padrão para usuários demo.
        
        Retorna tupla (produtor, propriedade)
        """
        import re
        
        # Criar produtor
        produtor = ProdutorRural.objects.create(
            usuario_responsavel=user,
            **dados_produtor
        )
        
        # Verificar se já existe propriedade com nome "Monpec" para este produtor
        propriedades_existentes = Propriedade.objects.filter(
            produtor=produtor,
            nome_propriedade__iregex=r'^Monpec\d+$'
        ).order_by('nome_propriedade')
        
        # Determinar o próximo número disponível
        if propriedades_existentes.exists():
            numeros_usados = []
            for prop in propriedades_existentes:
                match = re.search(r'Monpec(\d+)', prop.nome_propriedade, re.IGNORECASE)
                if match:
                    numeros_usados.append(int(match.group(1)))
            
            if numeros_usados:
                proximo_numero = max(numeros_usados) + 1
            else:
                proximo_numero = 2
            
            nome_propriedade = f'Monpec{proximo_numero}'
            logger.info(f'Propriedade Monpec1 já existe. Usando {nome_propriedade}')
        
        # Criar propriedade padrão
        propriedade = Propriedade.objects.create(
            produtor=produtor,
            nome_propriedade=nome_propriedade,
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=Decimal('1000.00'),
            tipo_operacao='PECUARIA',
            tipo_ciclo_pecuario=['CICLO_COMPLETO'],
            tipo_propriedade='PROPRIA',
            valor_hectare_proprio=Decimal('10000.00'),
        )
        
        logger.info(
            f'Produtor {produtor.nome} e propriedade {propriedade.nome_propriedade} '
            f'criados para usuário demo {user.username}'
        )
        
        return produtor, propriedade
    
    @staticmethod
    def obter_dados_iniciais_demo(user: User) -> dict:
        """
        Retorna dados iniciais para pré-preencher formulário de demo.
        
        Busca dados do UsuarioAtivo se disponível.
        """
        try:
            from ..models_auditoria import UsuarioAtivo
            usuario_ativo = UsuarioAtivo.objects.get(usuario=user)
            return {
                'nome': usuario_ativo.nome_completo,
                'email': usuario_ativo.email,
                'telefone': usuario_ativo.telefone,
            }
        except Exception:
            return {}


