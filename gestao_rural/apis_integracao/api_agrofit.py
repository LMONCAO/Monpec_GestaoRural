# -*- coding: utf-8 -*-
"""
API Agrofit - Embrapa
Consulta de produtos fitossanitários
"""

import requests
from typing import Dict, Optional, List
from django.conf import settings


class AgrofitAPI:
    """Classe para integração com API Agrofit da Embrapa"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a API Agrofit
        
        Args:
            api_key: Chave de API (se None, tenta obter de settings)
        """
        self.api_key = api_key or getattr(settings, 'AGROFIT_API_KEY', '')
        self.base_url = getattr(
            settings,
            'AGROFIT_BASE_URL',
            'https://api.agroapi.cnptia.embrapa.br/agrofit'
        )
        self.timeout = getattr(settings, 'AGROFIT_TIMEOUT', 30)
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
        }
    
    def buscar_produtos_por_cultura(self, cultura: str) -> Dict:
        """
        Busca produtos fitossanitários permitidos para uma cultura
        
        Args:
            cultura: Nome da cultura (ex: 'Soja', 'Milho')
        
        Returns:
            Dict com lista de produtos ou erro
        """
        try:
            url = f"{self.base_url}/produtos"
            params = {'cultura': cultura}
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def buscar_produto_por_nome(self, nome: str) -> Dict:
        """
        Busca produto fitossanitário por nome
        
        Args:
            nome: Nome do produto
        
        Returns:
            Dict com dados do produto ou erro
        """
        try:
            url = f"{self.base_url}/produtos/buscar"
            params = {'nome': nome}
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def validar_produto_para_cultura(self, produto: str, cultura: str) -> bool:
        """
        Valida se produto pode ser usado em determinada cultura
        
        Args:
            produto: Nome do produto
            cultura: Nome da cultura
        
        Returns:
            True se permitido, False caso contrário
        """
        resultado = self.buscar_produtos_por_cultura(cultura)
        if resultado.get('success'):
            produtos = resultado.get('data', {}).get('produtos', [])
            return any(p.get('nome') == produto for p in produtos)
        return False


