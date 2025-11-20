# -*- coding: utf-8 -*-
"""
API BovTrace - Embrapa
Integração com sistema de rastreabilidade bovina
"""

import requests
import json
from typing import Dict, Optional, List
from django.conf import settings


class BovTraceAPI:
    """Classe para integração com API BovTrace da Embrapa"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a API BovTrace
        
        Args:
            api_key: Chave de API (se None, tenta obter de settings)
        """
        self.api_key = api_key or getattr(settings, 'BOVTRACE_API_KEY', '')
        self.base_url = getattr(
            settings, 
            'BOVTRACE_BASE_URL', 
            'https://api.agroapi.cnptia.embrapa.br/bovtrace'
        )
        self.timeout = getattr(settings, 'BOVTRACE_TIMEOUT', 30)
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
        }
    
    def enviar_animal(self, animal_data: Dict) -> Dict:
        """
        Envia dados de animal para BovTrace
        
        Args:
            animal_data: Dicionário com dados do animal
                {
                    'numero_brinco': str,
                    'data_nascimento': str (YYYY-MM-DD),
                    'sexo': str ('M' ou 'F'),
                    'raca': str,
                    'propriedade_origem': str,
                    'categoria': str,
                }
        
        Returns:
            Dict com resposta da API
        """
        try:
            url = f"{self.base_url}/animais"
            response = requests.post(
                url,
                json=animal_data,
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
    
    def consultar_animal(self, numero_brinco: str) -> Dict:
        """
        Consulta dados de animal no BovTrace
        
        Args:
            numero_brinco: Número do brinco do animal
        
        Returns:
            Dict com dados do animal ou erro
        """
        try:
            url = f"{self.base_url}/animais/{numero_brinco}"
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
    
    def validar_brinco(self, numero_brinco: str) -> bool:
        """
        Valida se brinco existe no sistema BovTrace
        
        Args:
            numero_brinco: Número do brinco
        
        Returns:
            True se existe, False caso contrário
        """
        resultado = self.consultar_animal(numero_brinco)
        return resultado.get('success', False)
    
    def registrar_movimentacao(self, movimentacao_data: Dict) -> Dict:
        """
        Registra movimentação de animal
        
        Args:
            movimentacao_data: Dicionário com dados da movimentação
                {
                    'numero_brinco': str,
                    'tipo_movimentacao': str,
                    'data_movimentacao': str (YYYY-MM-DD),
                    'propriedade_origem': str,
                    'propriedade_destino': str,
                    'numero_documento': str,
                }
        
        Returns:
            Dict com resposta da API
        """
        try:
            url = f"{self.base_url}/movimentacoes"
            response = requests.post(
                url,
                json=movimentacao_data,
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
    
    def obter_historico_animal(self, numero_brinco: str) -> Dict:
        """
        Obtém histórico completo de movimentações de um animal
        
        Args:
            numero_brinco: Número do brinco
        
        Returns:
            Dict com histórico ou erro
        """
        try:
            url = f"{self.base_url}/animais/{numero_brinco}/historico"
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


