# -*- coding: utf-8 -*-
"""
API InfoDAP - MAPA
Consulta de Declaração de Aptidão ao Pronaf
"""

import requests
from typing import Dict, Optional
from django.conf import settings


class InfoDAPAPI:
    """Classe para integração com API InfoDAP do MAPA"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a API InfoDAP
        
        Args:
            api_key: Chave de API (se None, tenta obter de settings)
        """
        self.api_key = api_key or getattr(settings, 'INFODAP_API_KEY', '')
        self.base_url = getattr(
            settings,
            'INFODAP_BASE_URL',
            'https://api.conecta.gov.br/infodap'
        )
        self.timeout = getattr(settings, 'INFODAP_TIMEOUT', 30)
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
        }
    
    def consultar_dap(self, cpf_cnpj: str) -> Dict:
        """
        Consulta DAP por CPF/CNPJ
        
        Args:
            cpf_cnpj: CPF ou CNPJ do produtor
        
        Returns:
            Dict com dados da DAP ou erro
        """
        try:
            url = f"{self.base_url}/dap/{cpf_cnpj}"
            response = requests.get(
                url,
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
    
    def validar_propriedade_familiar(self, cpf_cnpj: str) -> bool:
        """
        Valida se propriedade é familiar (possui DAP)
        
        Args:
            cpf_cnpj: CPF ou CNPJ do produtor
        
        Returns:
            True se possui DAP válida, False caso contrário
        """
        resultado = self.consultar_dap(cpf_cnpj)
        if resultado.get('success'):
            dados = resultado.get('data', {})
            # Verificar se DAP está válida
            return dados.get('situacao') == 'VIGENTE'
        return False


