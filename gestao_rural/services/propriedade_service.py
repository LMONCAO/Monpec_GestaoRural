"""
Serviço para lógica de negócio relacionada a Propriedades Rurais
Separa a lógica de negócio das views, facilitando testes e reutilização
"""
import logging
from typing import Optional, List
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal

from ..models import Propriedade, ProdutorRural
from ..helpers_acesso import is_usuario_assinante

logger = logging.getLogger(__name__)


class PropriedadeService:
    """Serviço para operações com Propriedades Rurais"""
    
    @staticmethod
    def obter_propriedades_do_usuario(user: User) -> List[Propriedade]:
        """
        Retorna lista de propriedades disponíveis para o usuário.
        
        Regras:
        - Admin/Staff: todas as propriedades
        - Assinante ativo: propriedades da equipe (mesma assinatura)
        - Usuário normal: apenas propriedades dos seus produtores
        """
        if user.is_superuser or user.is_staff:
            return Propriedade.objects.select_related(
                'produtor', 'produtor__usuario_responsavel'
            ).only(
                'id', 'nome_propriedade', 'produtor_id', 'municipio', 
                'uf', 'area_total_ha', 'tipo_operacao', 'data_cadastro',
                'produtor__nome', 'produtor__usuario_responsavel_id'
            ).all().order_by('produtor__nome', 'nome_propriedade')
        
        if is_usuario_assinante(user):
            # Assinante: propriedades da equipe
            from ..models import AssinaturaCliente, TenantUsuario
            
            # Sempre usar defer() para evitar campos do Stripe removidos
            assinatura = AssinaturaCliente.objects.defer('stripe_customer_id', 'stripe_subscription_id').filter(usuario=user).first()
            
            if assinatura and assinatura.status == 'ATIVA':
                usuarios_tenant = TenantUsuario.objects.filter(
                    assinatura=assinatura,
                    ativo=True
                ).values_list('usuario_id', flat=True)
                
                usuarios_ids = list(usuarios_tenant) + [user.id]
                
                return Propriedade.objects.filter(
                    produtor__usuario_responsavel__id__in=usuarios_ids
                ).select_related(
                    'produtor', 'produtor__usuario_responsavel'
                ).only(
                    'id', 'nome_propriedade', 'produtor_id', 'municipio', 
                    'uf', 'area_total_ha', 'tipo_operacao', 'data_cadastro',
                    'produtor__nome', 'produtor__usuario_responsavel_id'
                ).order_by('produtor__nome', 'nome_propriedade')
        
        # Usuário normal: apenas propriedades dos seus produtores
        return Propriedade.objects.filter(
            produtor__usuario_responsavel=user
        ).select_related(
            'produtor', 'produtor__usuario_responsavel'
        ).only(
            'id', 'nome_propriedade', 'produtor_id', 'municipio', 
            'uf', 'area_total_ha', 'tipo_operacao', 'data_cadastro',
            'produtor__nome', 'produtor__usuario_responsavel_id'
        ).order_by('produtor__nome', 'nome_propriedade')
    
    @staticmethod
    def pode_acessar_propriedade(user: User, propriedade: Propriedade) -> bool:
        """
        Verifica se o usuário tem permissão para acessar a propriedade.
        
        Retorna True se:
        - É admin/staff
        - É assinante ativo (pode acessar propriedades da equipe)
        - É o responsável pelo produtor da propriedade
        """
        if user.is_superuser or user.is_staff:
            return True
        
        if is_usuario_assinante(user):
            # Assinante pode acessar propriedades da equipe
            from ..models import AssinaturaCliente, TenantUsuario
            
            # Sempre usar defer() para evitar campos do Stripe removidos
            assinatura = AssinaturaCliente.objects.defer('stripe_customer_id', 'stripe_subscription_id').filter(usuario=user).first()
            
            if assinatura and assinatura.status == 'ATIVA':
                usuarios_tenant = TenantUsuario.objects.filter(
                    assinatura=assinatura,
                    ativo=True
                ).values_list('usuario_id', flat=True)
                
                return propriedade.produtor.usuario_responsavel_id in list(usuarios_tenant) + [user.id]
        
        # Usuário normal: apenas se for o responsável pelo produtor
        return propriedade.produtor.usuario_responsavel_id == user.id
    
    @staticmethod
    def obter_propriedades_do_produtor(
        user: User, 
        produtor: ProdutorRural
    ) -> List[Propriedade]:
        """
        Retorna lista de propriedades de um produtor específico.
        
        Verifica permissões antes de retornar.
        """
        from .produtor_service import ProdutorService
        
        if not ProdutorService.pode_acessar_produtor(user, produtor):
            return []
        
        return Propriedade.objects.filter(
            produtor=produtor
        ).select_related(
            'produtor', 'produtor__usuario_responsavel'
        ).only(
            'id', 'nome_propriedade', 'produtor_id', 'municipio', 
            'uf', 'area_total_ha', 'tipo_operacao', 'data_cadastro'
        ).order_by('nome_propriedade')
    
    @staticmethod
    @transaction.atomic
    def criar_propriedade_padrao(
        user: User,
        produtor: ProdutorRural,
        nome_propriedade: str = 'Minha Propriedade'
    ) -> Propriedade:
        """
        Cria uma propriedade padrão para o usuário.
        
        Se já existir propriedade com o nome, adiciona número sequencial.
        """
        # Verificar se já existe propriedade com esse nome
        contador = 1
        nome_final = nome_propriedade
        while Propriedade.objects.filter(
            produtor=produtor, 
            nome_propriedade=nome_final
        ).exists():
            nome_final = f'{nome_propriedade} {contador}'
            contador += 1
        
        propriedade = Propriedade.objects.create(
            produtor=produtor,
            nome_propriedade=nome_final,
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=Decimal('100.00'),
            tipo_operacao='PECUARIA',
            tipo_ciclo_pecuario=['CICLO_COMPLETO'],
            tipo_propriedade='PROPRIA',
            valor_hectare_proprio=Decimal('5000.00'),
        )
        
        logger.info(
            f'Propriedade padrão {propriedade.nome_propriedade} criada '
            f'para usuário {user.username}'
        )
        
        return propriedade


