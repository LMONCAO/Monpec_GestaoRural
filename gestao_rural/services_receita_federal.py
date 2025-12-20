# -*- coding: utf-8 -*-
"""
Serviço de Integração com Receita Federal
- Consulta e validação de NCM
- Consulta de CFOP
- Sincronização de dados fiscais
"""

import requests
import logging
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class ReceitaFederalService:
    """Serviço para consultas na Receita Federal"""
    
    # Base URL para APIs públicas de consulta fiscal
    NCM_API_URL = "https://brasilapi.com.br/api/ncm/v1"
    SEFAZ_API_URL = "https://www.sefaz.ce.gov.br/nfce/consulta"
    
    @staticmethod
    def consultar_ncm(codigo_ncm):
        """
        Consulta informações sobre um NCM na Receita Federal
        
        Args:
            codigo_ncm: Código NCM (formato: 0102.29.00 ou 01022900)
            
        Returns:
            dict: {
                'sucesso': bool,
                'codigo': str,
                'descricao': str,
                'data_atualizacao': str,
                'erro': str (se houver)
            }
        """
        try:
            # Limpar e formatar NCM
            ncm_limpo = codigo_ncm.replace('.', '').replace('-', '')
            if len(ncm_limpo) != 8 or not ncm_limpo.isdigit():
                return {
                    'sucesso': False,
                    'erro': 'NCM inválido. Deve ter 8 dígitos numéricos.'
                }
            
            # Formatar NCM para consulta (0102.29.00)
            ncm_formatado = f"{ncm_limpo[:4]}.{ncm_limpo[4:6]}.{ncm_limpo[6:]}"
            
            # Tentar consultar via BrasilAPI (gratuita e pública)
            try:
                response = requests.get(
                    f"{ReceitaFederalService.NCM_API_URL}/{ncm_formatado}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'sucesso': True,
                        'codigo': ncm_formatado,
                        'descricao': data.get('descricao', ''),
                        'data_atualizacao': data.get('data_atualizacao', ''),
                        'fonte': 'BrasilAPI'
                    }
                elif response.status_code == 404:
                    # NCM não encontrado, mas pode ser válido
                    # Retornar sucesso parcial
                    return {
                        'sucesso': True,
                        'codigo': ncm_formatado,
                        'descricao': '',
                        'data_atualizacao': None,
                        'fonte': 'BrasilAPI (não encontrado)',
                        'aviso': 'NCM não encontrado na base pública. Verifique se está correto.'
                    }
            except requests.RequestException as e:
                logger.warning(f"Erro ao consultar NCM via BrasilAPI: {str(e)}")
            
            # Fallback: Validar formato e retornar estrutura básica
            return {
                'sucesso': True,
                'codigo': ncm_formatado,
                'descricao': '',
                'data_atualizacao': None,
                'fonte': 'Validação local',
                'aviso': 'NCM validado localmente. Consulte a Receita Federal para descrição completa.'
            }
            
        except Exception as e:
            logger.error(f"Erro ao consultar NCM {codigo_ncm}: {str(e)}", exc_info=True)
            return {
                'sucesso': False,
                'erro': f'Erro ao consultar NCM: {str(e)}'
            }
    
    @staticmethod
    def validar_cfop(codigo_cfop, tipo_operacao='SAIDA', uf_origem='', uf_destino=''):
        """
        Valida e retorna informações sobre um CFOP
        
        Args:
            codigo_cfop: Código CFOP (ex: 5102)
            tipo_operacao: 'ENTRADA' ou 'SAIDA'
            uf_origem: UF de origem (para operações interestaduais)
            uf_destino: UF de destino (para operações interestaduais)
            
        Returns:
            dict: {
                'sucesso': bool,
                'codigo': str,
                'descricao': str,
                'tipo': str,
                'erro': str (se houver)
            }
        """
        try:
            # Limpar CFOP
            cfop_limpo = codigo_cfop.strip()
            if not cfop_limpo.isdigit() or len(cfop_limpo) != 4:
                return {
                    'sucesso': False,
                    'erro': 'CFOP inválido. Deve ter 4 dígitos numéricos.'
                }
            
            # Tabela básica de CFOPs mais comuns
            cfop_tabela = {
                # Entrada
                '1102': {'descricao': 'Compra para comercialização', 'tipo': 'ENTRADA'},
                '1101': {'descricao': 'Compra para industrialização', 'tipo': 'ENTRADA'},
                '1403': {'descricao': 'Compra para comercialização em operação com produto sujeito ao regime de substituição tributária', 'tipo': 'ENTRADA'},
                '1551': {'descricao': 'Compra de bem para o ativo imobilizado', 'tipo': 'ENTRADA'},
                '1556': {'descricao': 'Compra de material para uso ou consumo', 'tipo': 'ENTRADA'},
                
                # Saída Estadual
                '5102': {'descricao': 'Venda de produção do estabelecimento', 'tipo': 'SAIDA'},
                '5101': {'descricao': 'Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária', 'tipo': 'SAIDA'},
                '5104': {'descricao': 'Venda de produção do estabelecimento que não deva por ele transitar', 'tipo': 'SAIDA'},
                '5105': {'descricao': 'Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária, na condição de contribuinte substituto', 'tipo': 'SAIDA'},
                '5109': {'descricao': 'Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária, na condição de contribuinte substituído', 'tipo': 'SAIDA'},
                
                # Saída Interestadual
                '6102': {'descricao': 'Venda de produção do estabelecimento', 'tipo': 'SAIDA'},
                '6101': {'descricao': 'Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária', 'tipo': 'SAIDA'},
                '6104': {'descricao': 'Venda de produção do estabelecimento que não deva por ele transitar', 'tipo': 'SAIDA'},
                '6105': {'descricao': 'Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária, na condição de contribuinte substituto', 'tipo': 'SAIDA'},
                '6109': {'descricao': 'Venda de produção do estabelecimento em operação com produto sujeito ao regime de substituição tributária, na condição de contribuinte substituído', 'tipo': 'SAIDA'},
            }
            
            if cfop_limpo in cfop_tabela:
                info = cfop_tabela[cfop_limpo]
                return {
                    'sucesso': True,
                    'codigo': cfop_limpo,
                    'descricao': info['descricao'],
                    'tipo': info['tipo'],
                    'fonte': 'Tabela local'
                }
            else:
                # CFOP não está na tabela local, mas pode ser válido
                # Validar estrutura básica
                primeiro_digito = cfop_limpo[0]
                if tipo_operacao == 'ENTRADA' and primeiro_digito in ['1', '2', '3']:
                    return {
                        'sucesso': True,
                        'codigo': cfop_limpo,
                        'descricao': 'CFOP de entrada (consulte tabela oficial)',
                        'tipo': 'ENTRADA',
                        'fonte': 'Validação local',
                        'aviso': 'CFOP validado localmente. Consulte a tabela oficial da Receita Federal.'
                    }
                elif tipo_operacao == 'SAIDA' and primeiro_digito in ['5', '6', '7']:
                    return {
                        'sucesso': True,
                        'codigo': cfop_limpo,
                        'descricao': 'CFOP de saída (consulte tabela oficial)',
                        'tipo': 'SAIDA',
                        'fonte': 'Validação local',
                        'aviso': 'CFOP validado localmente. Consulte a tabela oficial da Receita Federal.'
                    }
                else:
                    return {
                        'sucesso': False,
                        'erro': f'CFOP {cfop_limpo} não é compatível com operação {tipo_operacao}. CFOPs de entrada começam com 1-3, saída com 5-7.'
                    }
                    
        except Exception as e:
            logger.error(f"Erro ao validar CFOP {codigo_cfop}: {str(e)}", exc_info=True)
            return {
                'sucesso': False,
                'erro': f'Erro ao validar CFOP: {str(e)}'
            }
    
    @staticmethod
    def sincronizar_produto(produto):
        """
        Sincroniza um produto com a Receita Federal
        Atualiza NCM, CFOP e outros dados fiscais
        
        Args:
            produto: Instância do modelo Produto
            
        Returns:
            dict: {
                'sucesso': bool,
                'dados_atualizados': dict,
                'erro': str (se houver)
            }
        """
        try:
            dados_atualizados = {}
            
            # Consultar NCM
            if produto.ncm:
                resultado_ncm = ReceitaFederalService.consultar_ncm(produto.ncm)
                if resultado_ncm.get('sucesso'):
                    if resultado_ncm.get('descricao'):
                        produto.ncm_descricao = resultado_ncm['descricao']
                        dados_atualizados['ncm_descricao'] = resultado_ncm['descricao']
                    produto.ncm_validado = True
                    produto.ncm_data_validacao = timezone.now()
                    dados_atualizados['ncm_validado'] = True
            
            # Validar CFOPs
            cfops_validados = []
            if produto.cfop_entrada:
                resultado = ReceitaFederalService.validar_cfop(produto.cfop_entrada, 'ENTRADA')
                if resultado.get('sucesso'):
                    cfops_validados.append('cfop_entrada')
            
            if produto.cfop_saida_estadual:
                resultado = ReceitaFederalService.validar_cfop(produto.cfop_saida_estadual, 'SAIDA')
                if resultado.get('sucesso'):
                    cfops_validados.append('cfop_saida_estadual')
            
            if produto.cfop_saida_interestadual:
                resultado = ReceitaFederalService.validar_cfop(produto.cfop_saida_interestadual, 'SAIDA')
                if resultado.get('sucesso'):
                    cfops_validados.append('cfop_saida_interestadual')
            
            # Atualizar produto
            produto.sincronizado_receita = True
            produto.data_sincronizacao = timezone.now()
            produto.save()
            
            return {
                'sucesso': True,
                'dados_atualizados': dados_atualizados,
                'cfops_validados': cfops_validados
            }
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar produto {produto.codigo}: {str(e)}", exc_info=True)
            return {
                'sucesso': False,
                'erro': f'Erro ao sincronizar produto: {str(e)}'
            }


def consultar_ncm(codigo_ncm):
    """Função auxiliar para consultar NCM"""
    return ReceitaFederalService.consultar_ncm(codigo_ncm)


def validar_cfop(codigo_cfop, tipo_operacao='SAIDA', uf_origem='', uf_destino=''):
    """Função auxiliar para validar CFOP"""
    return ReceitaFederalService.validar_cfop(codigo_cfop, tipo_operacao, uf_origem, uf_destino)


def sincronizar_produto(produto):
    """Função auxiliar para sincronizar produto"""
    return ReceitaFederalService.sincronizar_produto(produto)

