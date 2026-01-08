# -*- coding: utf-8 -*-
"""
Serviço de Integração com APIs de Nota Fiscal Eletrônica
Suporta integração com:
- Focus NFe (https://doc.focusnfe.com.br/)
- NFe.io (https://nfe.io/)
- Outras APIs compatíveis
"""

import requests
import json
import os
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Importar validação de CPF/CNPJ
try:
    from ..services.validacao_cpf_cnpj import validar_cpf_cnpj
except ImportError:
    try:
        from gestao_rural.services.validacao_cpf_cnpj import validar_cpf_cnpj
    except ImportError:
        # Fallback se módulo não estiver disponível
        def validar_cpf_cnpj(cpf_cnpj):
            """Validação básica de CPF/CNPJ"""
            import re
            if not cpf_cnpj:
                return False, "INVALIDO", "CPF/CNPJ não informado"
            # Remove caracteres não numéricos
            cpf_cnpj_limpo = re.sub(r'[^0-9]', '', str(cpf_cnpj))
            if len(cpf_cnpj_limpo) == 11:
                return True, "CPF", "CPF válido"
            elif len(cpf_cnpj_limpo) == 14:
                return True, "CNPJ", "CNPJ válido"
            else:
                return False, "INVALIDO", f"CPF/CNPJ inválido: deve ter 11 ou 14 dígitos, encontrado {len(cpf_cnpj_limpo)}"


def emitir_nfe(nota_fiscal):
    """
    Emite uma NF-e através da API configurada ou diretamente com SEFAZ
    
    Args:
        nota_fiscal: Instância do modelo NotaFiscal
        
    Returns:
        dict: {
            'sucesso': bool,
            'chave_acesso': str,
            'protocolo': str,
            'xml': bytes (opcional),
            'erro': str (se houver erro)
        }
    """
    # Verificar se há certificado configurado no produtor ou configuração nas settings
    produtor = nota_fiscal.propriedade.produtor
    tem_certificado_produtor = produtor.certificado_digital and produtor.tem_certificado_valido()
    nfe_sefaz = getattr(settings, 'NFE_SEFAZ', None)
    tem_certificado_settings = nfe_sefaz and nfe_sefaz.get('CERTIFICADO_PATH') and os.path.exists(nfe_sefaz.get('CERTIFICADO_PATH'))
    
    # Priorizar emissão direta se houver certificado configurado
    if (tem_certificado_produtor or (nfe_sefaz and nfe_sefaz.get('USAR_DIRETO', False) and tem_certificado_settings)):
        try:
            from .services_nfe_sefaz import emitir_nfe_direta_sefaz
            resultado = emitir_nfe_direta_sefaz(nota_fiscal)
            # Se PyNFe não estiver instalado, resultado terá erro específico
            # Mas ainda tentamos, pois pode ser que a implementação básica funcione
            if resultado.get('sucesso') or 'PyNFe não instalado' not in resultado.get('erro', ''):
                return resultado
            # Se falhou por falta de PyNFe, continuar para tentar API terceira
            logger.info('Emissão direta SEFAZ requer PyNFe. Tentando API terceira se configurada...')
        except ImportError as e:
            logger.warning(f'Serviço de emissão direta SEFAZ não disponível: {e}')
    
    # Verificar qual API está configurada
    api_nfe = getattr(settings, 'API_NFE', None)
    
    if not api_nfe:
        logger.warning('API de NF-e não configurada. Configure API_NFE ou NFE_SEFAZ nas settings.')
        return {
            'sucesso': False,
            'erro': 'API de NF-e não configurada. Configure API_NFE ou NFE_SEFAZ nas settings.'
        }
    
    api_type = api_nfe.get('TIPO', 'FOCUS_NFE')
    
    if api_type == 'FOCUS_NFE':
        return _emitir_focus_nfe(nota_fiscal, api_nfe)
    elif api_type == 'NFE_IO':
        return _emitir_nfe_io(nota_fiscal, api_nfe)
    else:
        return {
            'sucesso': False,
            'erro': f'Tipo de API não suportado: {api_type}'
        }


def _emitir_focus_nfe(nota_fiscal, config):
    """
    Emite NF-e usando Focus NFe API
    
    Documentação: https://doc.focusnfe.com.br/
    """
    token = config.get('TOKEN')
    ambiente = config.get('AMBIENTE', 'homologacao')  # 'homologacao' ou 'producao'
    
    if not token:
        return {
            'sucesso': False,
            'erro': 'Token da API Focus NFe não configurado'
        }
    
    base_url = 'https://api.focusnfe.com.br' if ambiente == 'producao' else 'https://homologacao.focusnfe.com.br'
    url = f'{base_url}/v2/nfe'
    
    # Preparar dados da NF-e
    dados_nfe = _preparar_dados_nfe(nota_fiscal)
    
    try:
        response = requests.post(
            url,
            json=dados_nfe,
            auth=(token, ''),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 201:
            resultado = response.json()
            return {
                'sucesso': True,
                'chave_acesso': resultado.get('chave_nfe', ''),
                'protocolo': resultado.get('protocolo', ''),
                'xml': None  # Focus NFe retorna XML em endpoint separado
            }
        else:
            erro = response.json().get('mensagem', 'Erro desconhecido')
            logger.error(f'Erro ao emitir NF-e Focus NFe: {erro}')
            return {
                'sucesso': False,
                'erro': erro
            }
    except Exception as e:
        logger.error(f'Exceção ao emitir NF-e Focus NFe: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro de conexão: {str(e)}'
        }


def _emitir_nfe_io(nota_fiscal, config):
    """
    Emite NF-e usando NFe.io API
    
    Documentação: https://nfe.io/
    """
    token = config.get('TOKEN')
    ambiente = config.get('AMBIENTE', 'homologacao')
    
    if not token:
        return {
            'sucesso': False,
            'erro': 'Token da API NFe.io não configurado'
        }
    
    base_url = 'https://api.nfe.io' if ambiente == 'producao' else 'https://api.nfe.io'
    url = f'{base_url}/v1/companies/{config.get("COMPANY_ID")}/serviceinvoices'
    
    dados_nfe = _preparar_dados_nfe(nota_fiscal)
    
    try:
        response = requests.post(
            url,
            json=dados_nfe,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            resultado = response.json()
            return {
                'sucesso': True,
                'chave_acesso': resultado.get('accessKey', ''),
                'protocolo': resultado.get('protocol', ''),
                'xml': None
            }
        else:
            erro = response.json().get('message', 'Erro desconhecido')
            logger.error(f'Erro ao emitir NF-e NFe.io: {erro}')
            return {
                'sucesso': False,
                'erro': erro
            }
    except Exception as e:
        logger.error(f'Exceção ao emitir NF-e NFe.io: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro de conexão: {str(e)}'
        }


def _preparar_dados_nfe(nota_fiscal):
    """
    Prepara os dados da NF-e no formato esperado pela API
    
    Raises:
        ValueError: Se dados obrigatórios estiverem faltando
    """
    # Dados do emitente (propriedade)
    propriedade = nota_fiscal.propriedade
    
    if not propriedade:
        raise ValueError('Propriedade não configurada na nota fiscal')
    
    # Validar propriedade tem CNPJ
    if not propriedade.cnpj:
        raise ValueError('CNPJ da propriedade é obrigatório para emissão de NF-e')
    
    # Validar formato do CNPJ da propriedade
    cnpj_valido, tipo_doc, cnpj_limpo = validar_cpf_cnpj(propriedade.cnpj)
    if not cnpj_valido or tipo_doc != 'CNPJ':
        raise ValueError(f'CNPJ da propriedade inválido: {propriedade.cnpj}')
    
    # Dados do destinatário (cliente)
    cliente = nota_fiscal.cliente
    
    if not cliente and nota_fiscal.tipo == 'SAIDA':
        raise ValueError('Cliente é obrigatório para NF-e de saída')
    
    # Validar dados do cliente se for NF-e de saída
    if nota_fiscal.tipo == 'SAIDA' and cliente:
        if not hasattr(cliente, 'tipo_pessoa') or not cliente.tipo_pessoa:
            raise ValueError('Tipo de pessoa do cliente é obrigatório (FISICA ou JURIDICA)')
        
        if not cliente.cpf_cnpj:
            raise ValueError('CPF/CNPJ do cliente é obrigatório')
        
        # Validar formato do CPF/CNPJ do cliente
        doc_valido, tipo_doc_cliente, doc_limpo = validar_cpf_cnpj(cliente.cpf_cnpj)
        if not doc_valido:
            raise ValueError(f'CPF/CNPJ do cliente inválido: {cliente.cpf_cnpj}')
        
        # Validar consistência: tipo_pessoa deve corresponder ao tipo do documento
        if cliente.tipo_pessoa == 'FISICA' and tipo_doc_cliente != 'CPF':
            raise ValueError(f'Cliente marcado como pessoa física, mas documento informado não é CPF: {cliente.cpf_cnpj}')
        elif cliente.tipo_pessoa == 'JURIDICA' and tipo_doc_cliente != 'CNPJ':
            raise ValueError(f'Cliente marcado como pessoa jurídica, mas documento informado não é CNPJ: {cliente.cpf_cnpj}')
        
        if not cliente.nome:
            raise ValueError('Nome do cliente é obrigatório')
        
        # Validar endereço mínimo
        if not cliente.endereco:
            raise ValueError('Endereço do cliente é obrigatório')
        
        if not cliente.cidade:
            raise ValueError('Cidade do cliente é obrigatória')
        
        if not cliente.estado:
            raise ValueError('Estado (UF) do cliente é obrigatório')
        
        if not cliente.cep:
            raise ValueError('CEP do cliente é obrigatório')
    
    # Preparar itens
    itens = []
    for item in nota_fiscal.itens.all():
        if not item.descricao:
            raise ValueError('Descrição do item é obrigatória')
        
        if not item.quantidade or item.quantidade <= 0:
            raise ValueError('Quantidade do item deve ser maior que zero')
        
        if not item.valor_unitario or item.valor_unitario <= 0:
            raise ValueError('Valor unitário do item deve ser maior que zero')
        
        itens.append({
            'codigo': item.codigo_produto or '',
            'descricao': item.descricao,
            'ncm': item.ncm or '',
            'cfop': item.cfop or '5102',  # CFOP padrão para venda
            'unidade': item.unidade_medida or 'UN',
            'quantidade': float(item.quantidade),
            'valor_unitario': float(item.valor_unitario),
            'valor_total': float(item.valor_total or (item.quantidade * item.valor_unitario))
        })
    
    # Validar que há pelo menos um item
    if not itens:
        raise ValueError('NF-e deve ter pelo menos um item')
    
    # Validar tipo de pessoa do cliente antes de acessar atributos
    tipo_pessoa = getattr(cliente, 'tipo_pessoa', None) if cliente else None
    
    dados = {
        'natureza_operacao': 'VENDA',
        'data_emissao': nota_fiscal.data_emissao.strftime('%Y-%m-%d'),
        'tipo_documento': '1',  # 1 = NF-e
        'local_destino': '1',  # 1 = Operação interna
        'finalidade_emissao': '1',  # 1 = Normal
        'consumidor_final': '1' if (tipo_pessoa == 'FISICA') else '0',
        'presenca_comprador': '1',  # 1 = Operação presencial
        
        # Emitente (propriedade)
        'cnpj_emitente': propriedade.cnpj or '',
        'nome_emitente': propriedade.nome_propriedade or '',
        'inscricao_estadual_emitente': propriedade.inscricao_estadual or '',
        
        # Destinatário (cliente) - apenas se cliente existe
        'cnpj_destinatario': cliente.cpf_cnpj if (cliente and tipo_pessoa == 'JURIDICA') else '',
        'cpf_destinatario': cliente.cpf_cnpj if (cliente and tipo_pessoa == 'FISICA') else '',
        'nome_destinatario': cliente.nome if cliente else '',
        'inscricao_estadual_destinatario': getattr(cliente, 'inscricao_estadual', '') if cliente else '',
        'endereco_destinatario': cliente.endereco if cliente else '',
        'numero_destinatario': getattr(cliente, 'numero', '') if cliente else '',
        'bairro_destinatario': getattr(cliente, 'bairro', '') if cliente else '',
        'municipio_destinatario': cliente.cidade if cliente else '',
        'uf_destinatario': cliente.estado if cliente else '',
        'cep_destinatario': cliente.cep if cliente else '',
        
        # Itens
        'itens': itens,
        
        # Valores
        'valor_produtos': float(nota_fiscal.valor_produtos or 0),
        'valor_frete': float(nota_fiscal.valor_frete or 0),
        'valor_seguro': float(nota_fiscal.valor_seguro or 0),
        'valor_desconto': float(nota_fiscal.valor_desconto or 0),
        'valor_outros': float(nota_fiscal.valor_outros or 0),
        'valor_total': float(nota_fiscal.valor_total or 0),
    }
    
    return dados


def consultar_status_nfe(nota_fiscal):
    """
    Consulta o status de uma NF-e na SEFAZ
    """
    api_nfe = getattr(settings, 'API_NFE', None)
    
    if not api_nfe:
        return {
            'sucesso': False,
            'erro': 'API de NF-e não configurada'
        }
    
    api_type = api_nfe.get('TIPO', 'FOCUS_NFE')
    token = api_nfe.get('TOKEN')
    ambiente = api_nfe.get('AMBIENTE', 'homologacao')
    
    if api_type == 'FOCUS_NFE':
        base_url = 'https://api.focusnfe.com.br' if ambiente == 'producao' else 'https://homologacao.focusnfe.com.br'
        url = f'{base_url}/v2/nfe/{nota_fiscal.chave_acesso}'
        
        try:
            response = requests.get(
                url,
                auth=(token, ''),
                timeout=30
            )
            
            if response.status_code == 200:
                resultado = response.json()
                return {
                    'sucesso': True,
                    'status': resultado.get('status', ''),
                    'dados': resultado
                }
            else:
                return {
                    'sucesso': False,
                    'erro': 'Erro ao consultar status'
                }
        except Exception as e:
            logger.error(f'Erro ao consultar status NF-e: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    return {
        'sucesso': False,
        'erro': 'Tipo de API não suportado para consulta'
    }


def cancelar_nfe(nota_fiscal, justificativa):
    """
    Cancela uma NF-e autorizada
    """
    api_nfe = getattr(settings, 'API_NFE', None)
    
    if not api_nfe:
        return {
            'sucesso': False,
            'erro': 'API de NF-e não configurada'
        }
    
    api_type = api_nfe.get('TIPO', 'FOCUS_NFE')
    token = api_nfe.get('TOKEN')
    ambiente = api_nfe.get('AMBIENTE', 'homologacao')
    
    if api_type == 'FOCUS_NFE':
        base_url = 'https://api.focusnfe.com.br' if ambiente == 'producao' else 'https://homologacao.focusnfe.com.br'
        url = f'{base_url}/v2/nfe/{nota_fiscal.chave_acesso}/cancelamento'
        
        dados = {
            'justificativa': justificativa
        }
        
        try:
            response = requests.post(
                url,
                json=dados,
                auth=(token, ''),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'mensagem': 'NF-e cancelada com sucesso'
                }
            else:
                erro = response.json().get('mensagem', 'Erro desconhecido')
                return {
                    'sucesso': False,
                    'erro': erro
                }
        except Exception as e:
            logger.error(f'Erro ao cancelar NF-e: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    return {
        'sucesso': False,
        'erro': 'Tipo de API não suportado para cancelamento'
    }

