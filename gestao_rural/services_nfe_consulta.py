# -*- coding: utf-8 -*-
"""
Serviço de Consulta de Notas Fiscais Eletrônicas Recebidas
Permite consultar e baixar NF-e recebidas através de APIs
"""

import requests
import logging
from datetime import date, datetime
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def consultar_nfe_recebidas(propriedade, data_inicio, data_fim, limite=100):
    """
    Consulta NF-e recebidas (entrada) para uma propriedade
    
    Args:
        propriedade: Instância do modelo Propriedade
        data_inicio: Data inicial para consulta
        data_fim: Data final para consulta
        limite: Número máximo de notas a retornar
        
    Returns:
        dict: {
            'sucesso': bool,
            'notas': list,
            'total_encontrado': int,
            'erro': str (se houver erro)
        }
    """
    api_nfe = getattr(settings, 'API_NFE', None)
    
    if not api_nfe:
        return {
            'sucesso': False,
            'erro': 'API de NF-e não configurada'
        }
    
    # Obter CPF/CNPJ da propriedade
    cpf_cnpj = None
    if hasattr(propriedade, 'produtor') and propriedade.produtor:
        cpf_cnpj = propriedade.produtor.cpf_cnpj
    
    if not cpf_cnpj:
        return {
            'sucesso': False,
            'erro': 'CPF/CNPJ não configurado para a propriedade'
        }
    
    api_type = api_nfe.get('TIPO', 'FOCUS_NFE')
    
    if api_type == 'FOCUS_NFE':
        return _consultar_focus_nfe_recebidas(cpf_cnpj, data_inicio, data_fim, limite, api_nfe)
    elif api_type == 'NFE_IO':
        return _consultar_nfe_io_recebidas(cpf_cnpj, data_inicio, data_fim, limite, api_nfe)
    else:
        return {
            'sucesso': False,
            'erro': f'Tipo de API não suportado: {api_type}'
        }


def _consultar_focus_nfe_recebidas(cpf_cnpj, data_inicio, data_fim, limite, config):
    """
    Consulta NF-e recebidas usando Focus NFe API
    """
    token = config.get('TOKEN')
    ambiente = config.get('AMBIENTE', 'homologacao')
    
    if not token:
        return {
            'sucesso': False,
            'erro': 'Token da API Focus NFe não configurado'
        }
    
    base_url = 'https://api.focusnfe.com.br' if ambiente == 'producao' else 'https://homologacao.focusnfe.com.br'
    
    # Focus NFe usa endpoint de consulta por CNPJ
    url = f'{base_url}/v2/nfe_recebidas'
    
    params = {
        'cnpj': cpf_cnpj.replace('.', '').replace('/', '').replace('-', ''),
        'data_inicial': data_inicio.strftime('%Y-%m-%d'),
        'data_final': data_fim.strftime('%Y-%m-%d'),
        'limit': limite
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            auth=(token, ''),
            timeout=30
        )
        
        if response.status_code == 200:
            dados = response.json()
            notas = dados.get('notas', [])
            
            return {
                'sucesso': True,
                'notas': notas,
                'total_encontrado': len(notas)
            }
        else:
            erro = response.json().get('mensagem', 'Erro desconhecido')
            logger.error(f'Erro ao consultar NF-e recebidas Focus NFe: {erro}')
            return {
                'sucesso': False,
                'erro': erro
            }
    except Exception as e:
        logger.error(f'Exceção ao consultar NF-e recebidas Focus NFe: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro de conexão: {str(e)}'
        }


def _consultar_nfe_io_recebidas(cpf_cnpj, data_inicio, data_fim, limite, config):
    """
    Consulta NF-e recebidas usando NFe.io API
    """
    token = config.get('TOKEN')
    ambiente = config.get('AMBIENTE', 'homologacao')
    company_id = config.get('COMPANY_ID')
    
    if not token or not company_id:
        return {
            'sucesso': False,
            'erro': 'Token ou Company ID da API NFe.io não configurado'
        }
    
    base_url = 'https://api.nfe.io' if ambiente == 'producao' else 'https://api.nfe.io'
    url = f'{base_url}/v1/companies/{company_id}/serviceinvoices/received'
    
    params = {
        'start_date': data_inicio.strftime('%Y-%m-%d'),
        'end_date': data_fim.strftime('%Y-%m-%d'),
        'limit': limite
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            dados = response.json()
            notas = dados.get('data', [])
            
            # Converter formato NFe.io para formato padrão
            notas_formatadas = []
            for nota in notas:
                notas_formatadas.append({
                    'chave_acesso': nota.get('accessKey', ''),
                    'numero': nota.get('number', ''),
                    'serie': nota.get('series', '1'),
                    'data_emissao': nota.get('issuedOn', ''),
                    'valor_total': nota.get('totalAmount', 0),
                    'emitente_cnpj': nota.get('issuer', {}).get('federalTaxNumber', ''),
                    'emitente_nome': nota.get('issuer', {}).get('name', ''),
                })
            
            return {
                'sucesso': True,
                'notas': notas_formatadas,
                'total_encontrado': len(notas_formatadas)
            }
        else:
            erro = response.json().get('message', 'Erro desconhecido')
            logger.error(f'Erro ao consultar NF-e recebidas NFe.io: {erro}')
            return {
                'sucesso': False,
                'erro': erro
            }
    except Exception as e:
        logger.error(f'Exceção ao consultar NF-e recebidas NFe.io: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro de conexão: {str(e)}'
        }


def baixar_xml_nfe(chave_acesso, config):
    """
    Baixa o XML de uma NF-e pela chave de acesso
    
    Args:
        chave_acesso: Chave de acesso da NF-e (44 dígitos)
        config: Configuração da API
        
    Returns:
        dict: {
            'sucesso': bool,
            'xml': bytes (se sucesso),
            'erro': str (se houver erro)
        }
    """
    api_type = config.get('TIPO', 'FOCUS_NFE')
    token = config.get('TOKEN')
    ambiente = config.get('AMBIENTE', 'homologacao')
    
    if api_type == 'FOCUS_NFE':
        base_url = 'https://api.focusnfe.com.br' if ambiente == 'producao' else 'https://homologacao.focusnfe.com.br'
        url = f'{base_url}/v2/nfe/{chave_acesso}.xml'
        
        try:
            response = requests.get(
                url,
                auth=(token, ''),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'xml': response.content
                }
            else:
                return {
                    'sucesso': False,
                    'erro': f'Erro HTTP {response.status_code}'
                }
        except Exception as e:
            logger.error(f'Erro ao baixar XML NF-e: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    return {
        'sucesso': False,
        'erro': 'Tipo de API não suportado para download de XML'
    }


def baixar_pdf_nfe(chave_acesso, config):
    """
    Baixa o PDF (DANFE) de uma NF-e pela chave de acesso
    
    Args:
        chave_acesso: Chave de acesso da NF-e (44 dígitos)
        config: Configuração da API
        
    Returns:
        dict: {
            'sucesso': bool,
            'pdf': bytes (se sucesso),
            'erro': str (se houver erro)
        }
    """
    api_type = config.get('TIPO', 'FOCUS_NFE')
    token = config.get('TOKEN')
    ambiente = config.get('AMBIENTE', 'homologacao')
    
    if api_type == 'FOCUS_NFE':
        base_url = 'https://api.focusnfe.com.br' if ambiente == 'producao' else 'https://homologacao.focusnfe.com.br'
        url = f'{base_url}/v2/nfe/{chave_acesso}.pdf'
        
        try:
            response = requests.get(
                url,
                auth=(token, ''),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'pdf': response.content
                }
            else:
                return {
                    'sucesso': False,
                    'erro': f'Erro HTTP {response.status_code}'
                }
        except Exception as e:
            logger.error(f'Erro ao baixar PDF NF-e: {str(e)}')
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    return {
        'sucesso': False,
        'erro': 'Tipo de API não suportado para download de PDF'
    }


def importar_nfe_do_xml(xml_content, propriedade, usuario):
    """
    Importa uma NF-e a partir do conteúdo XML
    
    Args:
        xml_content: Conteúdo XML da NF-e (bytes ou string)
        propriedade: Instância do modelo Propriedade
        usuario: Usuário que está importando
        
    Returns:
        dict: {
            'sucesso': bool,
            'nota_fiscal': NotaFiscal (se sucesso),
            'erro': str (se houver erro)
        }
    """
    try:
        import xml.etree.ElementTree as ET
        from io import BytesIO
        from django.core.files.base import ContentFile
        from .models_compras_financeiro import NotaFiscal, ItemNotaFiscal, Fornecedor
        
        # Converter para bytes se necessário
        if isinstance(xml_content, str):
            xml_content = xml_content.encode('utf-8')
        
        # Parse do XML
        tree = ET.parse(BytesIO(xml_content))
        root = tree.getroot()
        
        # Namespace NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Extrair dados da NF-e
        inf_nfe = root.find('.//nfe:infNFe', ns)
        if inf_nfe is None:
            return {
                'sucesso': False,
                'erro': 'Arquivo XML inválido ou não é uma NF-e'
            }
        
        # Chave de acesso
        chave_acesso = inf_nfe.get('Id', '').replace('NFe', '')
        
        # Verificar se já existe
        if NotaFiscal.objects.filter(chave_acesso=chave_acesso).exists():
            nota_existente = NotaFiscal.objects.get(chave_acesso=chave_acesso)
            return {
                'sucesso': True,
                'nota_fiscal': nota_existente,
                'ja_existia': True
            }
        
        # Dados da NF
        ide = inf_nfe.find('.//nfe:ide', ns)
        if ide is None:
            return {
                'sucesso': False,
                'erro': 'Estrutura XML inválida: elemento "ide" não encontrado'
            }
        
        numero_elem = ide.find('nfe:nNF', ns)
        numero = numero_elem.text if numero_elem is not None and numero_elem.text else ''
        
        serie_elem = ide.find('nfe:serie', ns)
        serie = serie_elem.text if serie_elem is not None and serie_elem.text else '1'
        
        dh_emi_elem = ide.find('nfe:dhEmi', ns)
        if dh_emi_elem is not None and dh_emi_elem.text:
            try:
                data_emissao_str = dh_emi_elem.text[:10]
                data_emissao = datetime.strptime(data_emissao_str, '%Y-%m-%d').date()
            except (ValueError, IndexError):
                data_emissao = date.today()
        else:
            data_emissao = date.today()
        
        # Emitente (fornecedor)
        emit = inf_nfe.find('.//nfe:emit', ns)
        if emit is None:
            return {
                'sucesso': False,
                'erro': 'Estrutura XML inválida: elemento "emit" não encontrado'
            }
        
        cnpj_elem = emit.find('nfe:CNPJ', ns)
        cnpj_emitente = cnpj_elem.text if cnpj_elem is not None and cnpj_elem.text else ''
        
        nome_elem = emit.find('nfe:xNome', ns)
        nome_emitente = nome_elem.text if nome_elem is not None and nome_elem.text else ''
        
        if not cnpj_emitente:
            return {
                'sucesso': False,
                'erro': 'CNPJ do emitente não encontrado no XML'
            }
        
        # Buscar ou criar fornecedor
        fornecedor, _ = Fornecedor.objects.get_or_create(
            cpf_cnpj=cnpj_emitente,
            defaults={'nome': nome_emitente, 'propriedade': propriedade}
        )
        
        # Valores
        total = inf_nfe.find('.//nfe:total/nfe:ICMSTot', ns)
        if total is None:
            return {
                'sucesso': False,
                'erro': 'Estrutura XML inválida: valores totais não encontrados'
            }
        
        v_prod_elem = total.find('nfe:vProd', ns)
        valor_produtos = Decimal(v_prod_elem.text) if v_prod_elem is not None and v_prod_elem.text else Decimal('0')
        
        v_nf_elem = total.find('nfe:vNF', ns)
        valor_total = Decimal(v_nf_elem.text) if v_nf_elem is not None and v_nf_elem.text else Decimal('0')
        
        # Criar Nota Fiscal
        nota = NotaFiscal(
            propriedade=propriedade,
            fornecedor=fornecedor,
            tipo='ENTRADA',
            numero=numero,
            serie=serie,
            chave_acesso=chave_acesso,
            data_emissao=data_emissao,
            data_entrada=data_emissao,
            valor_produtos=valor_produtos,
            valor_total=valor_total,
            status='AUTORIZADA',
            importado_por=usuario
        )
        
        # Salvar XML
        nota.arquivo_xml.save(
            f'nfe_{chave_acesso}.xml',
            ContentFile(xml_content),
            save=False
        )
        
        nota.save()
        
        # Processar itens
        dets = inf_nfe.findall('.//nfe:det', ns)
        for det in dets:
            try:
                prod = det.find('nfe:prod', ns)
                if prod is None:
                    continue
                
                c_prod_elem = prod.find('nfe:cProd', ns)
                codigo_produto = c_prod_elem.text if c_prod_elem is not None and c_prod_elem.text else ''
                
                x_prod_elem = prod.find('nfe:xProd', ns)
                descricao = x_prod_elem.text if x_prod_elem is not None and x_prod_elem.text else ''
                
                ncm_elem = prod.find('nfe:NCM', ns)
                ncm = ncm_elem.text if ncm_elem is not None and ncm_elem.text else ''
                
                u_com_elem = prod.find('nfe:uCom', ns)
                unidade_medida = u_com_elem.text if u_com_elem is not None and u_com_elem.text else 'UN'
                
                q_com_elem = prod.find('nfe:qCom', ns)
                quantidade = Decimal(q_com_elem.text) if q_com_elem is not None and q_com_elem.text else Decimal('1')
                
                v_un_com_elem = prod.find('nfe:vUnCom', ns)
                valor_unitario = Decimal(v_un_com_elem.text) if v_un_com_elem is not None and v_un_com_elem.text else Decimal('0')
                
                ItemNotaFiscal(
                    nota_fiscal=nota,
                    codigo_produto=codigo_produto,
                    descricao=descricao,
                    ncm=ncm,
                    unidade_medida=unidade_medida,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                ).save()
            except Exception as e:
                logger.warning(f"Erro ao processar item da NF-e {numero}: {str(e)}")
                continue
        
        return {
            'sucesso': True,
            'nota_fiscal': nota,
            'ja_existia': False
        }
        
    except Exception as e:
        logger.error(f'Erro ao importar NF-e do XML: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro ao processar XML: {str(e)}'
        }

