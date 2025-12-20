# -*- coding: utf-8 -*-
"""
Serviço para consulta de dados por CPF/CNPJ
Integração com APIs públicas (ReceitaWS, ViaCEP)
"""

import logging
import requests
import re
from typing import Optional, Dict
from django.conf import settings
from .validacao_cpf_cnpj import validar_cpf_cnpj as validar_cpf_cnpj_local

logger = logging.getLogger(__name__)


class ConsultaCPFCNPJ:
    """
    Serviço para consultar dados de CPF/CNPJ usando APIs públicas
    """
    
    def __init__(self):
        self.receitaws_url = "https://www.receitaws.com.br/v1"
        self.viacep_url = "https://viacep.com.br/ws"
        self.timeout = 10  # segundos
    
    def limpar_cpf_cnpj(self, cpf_cnpj: str) -> str:
        """
        Remove formatação do CPF/CNPJ (pontos, barras, hífens)
        
        Args:
            cpf_cnpj: CPF/CNPJ formatado
            
        Returns:
            CPF/CNPJ apenas com números
        """
        if not cpf_cnpj:
            return ''
        return re.sub(r'[^0-9]', '', cpf_cnpj)
    
    def validar_cpf_cnpj(self, cpf_cnpj: str) -> tuple[bool, str]:
        """
        Valida se é CPF ou CNPJ baseado no tamanho
        
        Args:
            cpf_cnpj: CPF/CNPJ sem formatação
            
        Returns:
            (valido, tipo) - tipo pode ser 'CPF', 'CNPJ' ou 'INVALIDO'
        """
        cpf_cnpj_limpo = self.limpar_cpf_cnpj(cpf_cnpj)
        
        if len(cpf_cnpj_limpo) == 11:
            return True, 'CPF'
        elif len(cpf_cnpj_limpo) == 14:
            return True, 'CNPJ'
        else:
            return False, 'INVALIDO'
    
    def consultar_cnpj(self, cnpj: str) -> Optional[Dict]:
        """
        Consulta dados de CNPJ
        
        Prioridade:
        1. Buscar cliente existente no banco de dados (cache local)
        2. Consultar ReceitaWS (API pública)
        
        Args:
            cnpj: CNPJ sem formatação
            
        Returns:
            Dict com dados da empresa ou None em caso de erro
        """
        cnpj_limpo = self.limpar_cpf_cnpj(cnpj)
        
        if len(cnpj_limpo) != 14:
            logger.warning(f"CNPJ inválido: {cnpj}")
            return None
        
        # 1. PRIMEIRO: Buscar cliente existente no banco (cache local)
        cliente_existente = self.buscar_cliente_existente_por_cpf_cnpj(cnpj)
        if cliente_existente:
            cliente_existente['fonte_cache_local'] = True
            return cliente_existente
        
        # 2. SEGUNDO: Consultar ReceitaWS
        try:
            url = f"{self.receitaws_url}/{cnpj_limpo}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se a consulta foi bem-sucedida
                if data.get('status') == 'ERROR':
                    logger.warning(f"Erro na consulta CNPJ: {data.get('message', 'Erro desconhecido')}")
                    return None
                
                # Retornar dados formatados
                return {
                    'nome': data.get('nome', ''),
                    'nome_fantasia': data.get('fantasia', ''),
                    'tipo_pessoa': 'JURIDICA',
                    'cpf_cnpj': cnpj_limpo,
                    'inscricao_estadual': data.get('inscricao_estadual', ''),
                    'telefone': data.get('telefone', ''),
                    'email': data.get('email', ''),
                    'endereco': data.get('logradouro', ''),
                    'numero': data.get('numero', ''),
                    'complemento': data.get('complemento', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('municipio', ''),
                    'estado': data.get('uf', ''),
                    'cep': data.get('cep', '').replace('-', ''),
                    'situacao': data.get('situacao', ''),
                    'abertura': data.get('abertura', ''),
                    'fonte_receitaws': True,
                }
            else:
                logger.warning(f"Erro ao consultar CNPJ: Status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao consultar CNPJ: {cnpj}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar CNPJ: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar CNPJ: {e}")
            return None
    
    def consultar_cpf_com_api_paga(self, cpf: str) -> Optional[Dict]:
        """
        Consulta CPF usando API paga (quando configurada)
        
        Implemente este método conforme a API escolhida:
        - Brasil API Fácil: https://brasilapifacil.com.br/docs/cpf
        - Serpro: https://loja.serpro.gov.br/en/consultacpf
        - SimpleData: https://simpledata.com.br/
        
        Args:
            cpf: CPF sem formatação
            
        Returns:
            Dict com dados do CPF ou None se não configurado
        """
        from django.conf import settings
        
        # Verificar se alguma API paga está configurada
        # Exemplo para Brasil API Fácil:
        token = getattr(settings, 'BRASIL_API_FACIL_TOKEN', None)
        if not token:
            return None  # API não configurada
        
        cpf_limpo = self.limpar_cpf_cnpj(cpf)
        
        # TODO: Implementar chamada à API paga escolhida
        # Exemplo de implementação para Brasil API Fácil:
        # try:
        #     url = "https://brasilapifacil.com.br/api/cpf/consulta"
        #     headers = {
        #         'Authorization': f'Bearer {token}',
        #         'Content-Type': 'application/json'
        #     }
        #     data = {'cpf': cpf_limpo}
        #     response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
        #     if response.status_code == 200:
        #         dados = response.json()
        #         return {
        #             'nome': dados.get('nome', ''),
        #             'data_nascimento': dados.get('data_nascimento', ''),
        #             'situacao_cadastral': dados.get('situacao', ''),
        #             'tipo_pessoa': 'FISICA',
        #             'cpf_cnpj': cpf_limpo,
        #         }
        # except Exception as e:
        #     logger.error(f"Erro ao consultar CPF via API paga: {e}")
        
        return None
    
    def buscar_cliente_existente_por_cpf_cnpj(self, cpf_cnpj: str) -> Optional[Dict]:
        """
        Busca cliente já cadastrado no sistema pelo CPF/CNPJ
        
        Args:
            cpf_cnpj: CPF ou CNPJ sem formatação
            
        Returns:
            Dict com dados do cliente ou None se não encontrado
        """
        try:
            from gestao_rural.models_cadastros import Cliente
            
            cpf_cnpj_limpo = self.limpar_cpf_cnpj(cpf_cnpj)
            
            # Buscar cliente existente (pode estar em qualquer propriedade)
            cliente = Cliente.objects.filter(cpf_cnpj=cpf_cnpj_limpo).first()
            
            if cliente:
                # Retornar dados do cliente encontrado
                return {
                    'nome': cliente.nome or '',
                    'nome_fantasia': cliente.nome_fantasia or '',
                    'tipo_pessoa': cliente.tipo_pessoa or 'FISICA',
                    'cpf_cnpj': cliente.cpf_cnpj or cpf_cnpj_limpo,
                    'inscricao_estadual': cliente.inscricao_estadual or '',
                    'tipo_cliente': cliente.tipo_cliente or 'OUTROS',
                    'telefone': cliente.telefone or '',
                    'celular': cliente.celular or '',
                    'email': cliente.email or '',
                    'website': cliente.website or '',
                    'endereco': cliente.endereco or '',
                    'numero': cliente.numero or '',
                    'complemento': cliente.complemento or '',
                    'bairro': cliente.bairro or '',
                    'cidade': cliente.cidade or '',
                    'estado': cliente.estado or '',
                    'cep': cliente.cep or '',
                    'banco': cliente.banco or '',
                    'agencia': cliente.agencia or '',
                    'conta': cliente.conta or '',
                    'tipo_conta': cliente.tipo_conta or '',
                    'pix': cliente.pix or '',
                    'cliente_existente': True,  # Flag indicando que veio do banco
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente existente: {e}")
            return None
    
    def consultar_cpf(self, cpf: str) -> Optional[Dict]:
        """
        Consulta dados de CPF
        
        Prioridade:
        1. Buscar cliente existente no banco de dados (cache local)
        2. Tentar API paga (se configurada)
        3. Retornar apenas validação
        
        Args:
            cpf: CPF sem formatação
            
        Returns:
            Dict com dados básicos ou None
        """
        cpf_limpo = self.limpar_cpf_cnpj(cpf)
        
        if len(cpf_limpo) != 11:
            logger.warning(f"CPF inválido: {cpf}")
            return None
        
        # Validar CPF antes de retornar
        valido, tipo, mensagem = validar_cpf_cnpj_local(cpf)
        if not valido:
            logger.warning(f"CPF inválido: {mensagem}")
            return {
                'eh_cpf': True,
                'cpf_invalido': True,
                'mensagem': f'CPF inválido: {mensagem}',
            }
        
        # 1. PRIMEIRO: Buscar cliente existente no banco (cache local)
        cliente_existente = self.buscar_cliente_existente_por_cpf_cnpj(cpf)
        if cliente_existente:
            cliente_existente['eh_cpf'] = True
            cliente_existente['fonte_cache_local'] = True
            return cliente_existente
        
        # 2. SEGUNDO: Tentar API paga (se configurada)
        dados_api_paga = self.consultar_cpf_com_api_paga(cpf)
        if dados_api_paga:
            dados_api_paga['eh_cpf'] = True
            dados_api_paga['fonte_api_paga'] = True
            return dados_api_paga
        
        # 3. FALLBACK: retornar apenas validação (sem dados completos)
        return {
            'tipo_pessoa': 'FISICA',
            'cpf_cnpj': cpf_limpo,
            'eh_cpf': True,  # Flag para indicar que é CPF
            'cpf_valido': True,
            'mensagem': 'CPF válido detectado. Cliente não encontrado no sistema. Por favor, preencha os dados.',
        }
    
    def consultar_cep(self, cep: str) -> Optional[Dict]:
        """
        Consulta endereço por CEP usando ViaCEP
        
        Args:
            cep: CEP com ou sem formatação
            
        Returns:
            Dict com dados do endereço ou None
        """
        cep_limpo = self.limpar_cpf_cnpj(cep)
        
        if len(cep_limpo) != 8:
            logger.warning(f"CEP inválido: {cep}")
            return None
        
        try:
            url = f"{self.viacep_url}/{cep_limpo}/json/"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se CEP foi encontrado
                if data.get('erro'):
                    logger.warning(f"CEP não encontrado: {cep}")
                    return None
                
                return {
                    'endereco': data.get('logradouro', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('localidade', ''),
                    'estado': data.get('uf', ''),
                    'cep': cep_limpo,
                }
            else:
                logger.warning(f"Erro ao consultar CEP: Status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao consultar CEP: {cep}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar CEP: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar CEP: {e}")
            return None
    
    def consultar(self, cpf_cnpj: str) -> Optional[Dict]:
        """
        Consulta dados por CPF ou CNPJ
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
            
        Returns:
            Dict com dados encontrados ou None
        """
        valido, tipo = self.validar_cpf_cnpj(cpf_cnpj)
        
        if not valido:
            return None
        
        if tipo == 'CNPJ':
            return self.consultar_cnpj(cpf_cnpj)
        elif tipo == 'CPF':
            return self.consultar_cpf(cpf_cnpj)
        
        return None


def consultar_dados_cpf_cnpj(cpf_cnpj: str) -> Optional[Dict]:
    """
    Função helper para consultar dados por CPF/CNPJ
    
    Args:
        cpf_cnpj: CPF ou CNPJ
        
    Returns:
        Dict com dados ou None
    """
    service = ConsultaCPFCNPJ()
    return service.consultar(cpf_cnpj)

