"""
Serviço para lógica de negócio do Dashboard
Centraliza a lógica de busca de dados do dashboard
"""
import logging
from typing import List, Tuple, Optional
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from decimal import Decimal

from ..models import ProdutorRural, Propriedade
from ..helpers_acesso import is_usuario_assinante
from .produtor_service import ProdutorService
from .propriedade_service import PropriedadeService

logger = logging.getLogger(__name__)


class DashboardService:
    """Serviço para operações do Dashboard"""
    
    @staticmethod
    def obter_dados_dashboard(user: User) -> dict:
        """
        Retorna todos os dados necessários para o dashboard.
        
        Retorna:
        - produtores: Lista de produtores do usuário
        - propriedades: Lista de propriedades do usuário
        - total_propriedades: Total de propriedades
        - total_area: Área total em hectares
        - propriedade_prioritaria: Propriedade para redirecionamento (se houver)
        """
        # Buscar produtores usando o serviço
        produtores = ProdutorService.obter_produtores_do_usuario(user)
        
        # Buscar propriedades usando o serviço
        propriedades = PropriedadeService.obter_propriedades_do_usuario(user)
        
        # Calcular totais
        total_propriedades = propriedades.count() if hasattr(propriedades, 'count') else len(propriedades)
        
        # Calcular área total
        try:
            if hasattr(propriedades, 'aggregate'):
                total_area = propriedades.aggregate(Sum('area_total_ha'))['area_total_ha__sum'] or Decimal('0.00')
            else:
                total_area = sum(prop.area_total_ha for prop in propriedades if prop.area_total_ha) or Decimal('0.00')
        except Exception as e:
            logger.warning(f'Erro ao calcular área total: {e}')
            total_area = Decimal('0.00')
        
        # Buscar propriedade prioritária (Monpec1, Monpec2, etc.)
        propriedade_prioritaria = DashboardService._obter_propriedade_prioritaria(propriedades)
        
        return {
            'produtores': produtores,
            'propriedades': propriedades,
            'total_propriedades': total_propriedades,
            'total_area': total_area,
            'propriedade_prioritaria': propriedade_prioritaria,
        }
    
    @staticmethod
    def _obter_propriedade_prioritaria(propriedades) -> Optional[Propriedade]:
        """
        Retorna a propriedade prioritária para redirecionamento.
        
        Prioridade:
        1. Propriedades com nome Monpec1, Monpec2, Monpec3...
        2. Primeira propriedade disponível
        """
        import re
        
        # Buscar propriedades Monpec
        propriedades_monpec = []
        for prop in propriedades:
            if re.match(r'^Monpec\d+$', prop.nome_propriedade, re.IGNORECASE):
                propriedades_monpec.append(prop)
        
        if propriedades_monpec:
            # Ordenar por número (Monpec1, Monpec2, etc.)
            propriedades_monpec.sort(key=lambda p: int(re.search(r'(\d+)', p.nome_propriedade).group(1)) if re.search(r'(\d+)', p.nome_propriedade) else 999)
            return propriedades_monpec[0]
        
        # Se não houver Monpec, retornar a primeira propriedade
        if hasattr(propriedades, 'first'):
            return propriedades.first()
        elif propriedades:
            return propriedades[0]
        
        return None

