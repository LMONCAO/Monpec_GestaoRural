# -*- coding: utf-8 -*-
"""
Serviço de Emissão de NF-e Direta com SEFAZ
Permite emitir NF-e diretamente sem usar APIs terceiras
Requer certificado digital A1 ou A3

NOTA: Esta é uma implementação básica. Para produção, recomenda-se usar:
- PyNFe (pip install pynfe) - Biblioteca completa e testada
- PyTrustNFe (pip install pytrustnfe) - Alternativa focada em SEFAZ

Veja: gestao_rural/services_nfe_sefaz_pynfe.py para exemplo com PyNFe
"""

import os
import logging
from decimal import Decimal
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Tentar importar bibliotecas opcionais
try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    logger.warning('lxml não instalado. Instale com: pip install lxml')

try:
    from zeep import Client
    from zeep.transports import Transport
    from requests import Session
    ZEEP_AVAILABLE = True
except ImportError:
    ZEEP_AVAILABLE = False
    logger.warning('zeep não instalado. Instale com: pip install zeep')


def emitir_nfe_direta_sefaz(nota_fiscal):
    """
    Emite NF-e diretamente com a SEFAZ usando certificado digital
    
    Tenta usar PyNFe se disponível, caso contrário usa implementação básica
    
    Args:
        nota_fiscal: Instância do modelo NotaFiscal
        
    Returns:
        dict: {
            'sucesso': bool,
            'chave_acesso': str,
            'protocolo': str,
            'xml': bytes,
            'erro': str (se houver erro)
        }
    """
    # Tentar usar PyNFe primeiro (recomendado)
    try:
        from .services_nfe_sefaz_pynfe import emitir_nfe_com_pynfe
        resultado = emitir_nfe_com_pynfe(nota_fiscal)
        if resultado.get('sucesso') or 'PyNFe não instalado' not in resultado.get('erro', ''):
            return resultado
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f'Erro ao usar PyNFe, tentando implementação básica: {str(e)}')
    
    # Se PyNFe não estiver disponível, usar implementação básica
    try:
        # Buscar certificado do produtor da propriedade
        produtor = nota_fiscal.propriedade.produtor
        certificado_path = None
        senha_certificado = None
        
        if produtor.certificado_digital and produtor.tem_certificado_valido():
            # Certificado do produtor (prioridade)
            certificado_path = produtor.certificado_digital.path
            senha_certificado = produtor.senha_certificado
        else:
            # Fallback: verificar configuração nas settings (para compatibilidade)
            config = getattr(settings, 'NFE_SEFAZ', None)
            if config:
                certificado_path = config.get('CERTIFICADO_PATH')
                senha_certificado = config.get('SENHA_CERTIFICADO')
        
        if not certificado_path or not os.path.exists(certificado_path):
            return {
                'sucesso': False,
                'erro': 'Certificado digital não encontrado ou não configurado. Configure o certificado digital no cadastro do produtor.'
            }
        
        if not senha_certificado:
            return {
                'sucesso': False,
                'erro': 'Senha do certificado digital não configurada. Configure no cadastro do produtor.'
            }
        
        # Usar configuração das settings para outros parâmetros
        config = getattr(settings, 'NFE_SEFAZ', {})
        
        # Verificar bibliotecas necessárias
        if not LXML_AVAILABLE:
            return {
                'sucesso': False,
                'erro': 'Biblioteca lxml não instalada. Execute: pip install lxml. Para implementação completa, recomenda-se: pip install pynfe'
            }
        
        # Gerar XML da NF-e
        xml_nfe = _gerar_xml_nfe(nota_fiscal, config)
        
        if not xml_nfe:
            return {
                'sucesso': False,
                'erro': 'Erro ao gerar XML da NF-e'
            }
        
        # Assinar XML
        xml_assinado = _assinar_xml_nfe(xml_nfe, certificado_path, senha_certificado)
        
        if not xml_assinado:
            return {
                'sucesso': False,
                'erro': 'Erro ao assinar XML da NF-e. Para implementação completa, instale PyNFe: pip install pynfe'
            }
        
        # Enviar para SEFAZ
        ambiente = config.get('AMBIENTE', 'homologacao')
        uf = config.get('UF', 'SP')
        
        resultado = _enviar_para_sefaz(xml_assinado, ambiente, uf, certificado_path, senha_certificado)
        
        return resultado
        
    except Exception as e:
        logger.error(f'Erro ao emitir NF-e diretamente com SEFAZ: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro ao emitir NF-e: {str(e)}. Para implementação completa, instale PyNFe: pip install pynfe'
        }


def _gerar_xml_nfe(nota_fiscal, config):
    """
    Gera o XML da NF-e conforme layout oficial da SEFAZ
    """
    if not LXML_AVAILABLE:
        logger.error('lxml não disponível para gerar XML')
        return None
    
    try:
        # Namespace NFe
        ns = {
            'nfe': 'http://www.portalfiscal.inf.br/nfe',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        # Criar elemento raiz
        root = etree.Element('{http://www.portalfiscal.inf.br/nfe}NFe', nsmap=ns)
        
        # infNFe
        inf_nfe = etree.SubElement(root, '{http://www.portalfiscal.inf.br/nfe}infNFe')
        inf_nfe.set('Id', f'NFe{nota_fiscal.chave_acesso or _gerar_chave_acesso(nota_fiscal, config)}')
        inf_nfe.set('versao', '4.00')
        
        # ide (Identificação)
        ide = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}ide')
        
        # Código da UF do emitente
        uf_emitente = config.get('UF_EMITENTE', '35')  # SP = 35
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}cUF').text = uf_emitente
        
        # Código numérico aleatório (8 dígitos)
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}cNF').text = nota_fiscal.numero.zfill(8)[-8:]
        
        # Natureza da operação
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}natOp').text = 'VENDA'
        
        # Modelo (55 = NF-e)
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}mod').text = '55'
        
        # Série
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}serie').text = nota_fiscal.serie
        
        # Número da NF-e
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}nNF').text = nota_fiscal.numero
        
        # Data e hora de emissão
        dh_emissao = datetime.combine(nota_fiscal.data_emissao, datetime.min.time())
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}dhEmi').text = dh_emissao.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        # Data de saída/entrada
        if nota_fiscal.data_entrada:
            dh_saida = datetime.combine(nota_fiscal.data_entrada, datetime.min.time())
            etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}dhSaiEnt').text = dh_saida.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        # Tipo de operação (1 = Saída)
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}tpNF').text = '1'
        
        # Identificador de local de destino da operação
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}idDest').text = '1'  # 1 = Operação interna
        
        # Código do município
        cod_mun = config.get('CODIGO_MUNICIPIO', '3550308')  # São Paulo
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}cMunFG').text = cod_mun
        
        # Formato de impressão do DANFE
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}tpImp').text = '1'  # 1 = Retrato
        
        # Forma de emissão (1 = Normal)
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}tpEmis').text = '1'
        
        # DV do código numérico
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}cDV').text = '0'  # Será calculado
        
        # Tipo de ambiente (1 = Produção, 2 = Homologação)
        ambiente = config.get('AMBIENTE', 'homologacao')
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}tpAmb').text = '2' if ambiente == 'homologacao' else '1'
        
        # Finalidade da emissão (1 = Normal)
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}finNFe').text = '1'
        
        # Indicador de operação com consumidor final
        cliente = nota_fiscal.cliente
        if cliente and cliente.tipo_pessoa == 'FISICA':
            etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}indFinal').text = '1'  # 1 = Sim
        else:
            etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}indFinal').text = '0'  # 0 = Não
        
        # Indicador de presença do comprador
        etree.SubElement(ide, '{http://www.portalfiscal.inf.br/nfe}indPres').text = '1'  # 1 = Operação presencial
        
        # Emitente
        emit = _gerar_emitente(inf_nfe, nota_fiscal.propriedade, config)
        
        # Destinatário
        dest = _gerar_destinatario(inf_nfe, nota_fiscal.cliente)
        
        # Itens
        _gerar_itens(inf_nfe, nota_fiscal)
        
        # Totais
        _gerar_totais(inf_nfe, nota_fiscal)
        
        # Transporte (opcional)
        transp = _gerar_transporte(inf_nfe, nota_fiscal)
        
        # Pagamento (opcional)
        pag = _gerar_pagamento(inf_nfe, nota_fiscal)
        
        # Informações adicionais
        if nota_fiscal.observacoes:
            inf_adic = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}infAdic')
            etree.SubElement(inf_adic, '{http://www.portalfiscal.inf.br/nfe}infCpl').text = nota_fiscal.observacoes[:5000]
        
        # Converter para string XML
        xml_string = etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
        return xml_string
        
    except Exception as e:
        logger.error(f'Erro ao gerar XML da NF-e: {str(e)}', exc_info=True)
        return None


def _gerar_emitente(inf_nfe, propriedade, config):
    """Gera dados do emitente (propriedade)"""
    emit = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}emit')
    
    # CNPJ
    cnpj = propriedade.cnpj or config.get('CNPJ_EMITENTE', '')
    if len(cnpj) == 14:
        etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}CNPJ').text = cnpj
    else:
        # Se não tiver CNPJ, usar CPF (11 dígitos)
        cpf = propriedade.produtor.cpf_cnpj if hasattr(propriedade, 'produtor') and propriedade.produtor else ''
        if len(cpf) == 11:
            etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}CPF').text = cpf
    
    # Razão Social
    etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}xNome').text = propriedade.nome_propriedade[:60]
    
    # Nome Fantasia (se houver)
    if hasattr(propriedade, 'nome_fantasia') and propriedade.nome_fantasia:
        etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}xFant').text = propriedade.nome_fantasia[:60]
    
    # Endereço
    ender_emit = etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}enderEmit')
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}xLgr').text = (propriedade.endereco or '')[:60]
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}nro').text = (propriedade.numero or 'S/N')[:60]
    if propriedade.complemento:
        etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}xCpl').text = propriedade.complemento[:60]
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}xBairro').text = (propriedade.bairro or '')[:60]
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}cMun').text = config.get('CODIGO_MUNICIPIO', '3550308')
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}xMun').text = (propriedade.cidade or 'São Paulo')[:60]
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}UF').text = (propriedade.estado or 'SP')[:2]
    if propriedade.cep:
        etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}CEP').text = propriedade.cep.replace('-', '')[:8]
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}cPais').text = '1058'  # Brasil
    etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}xPais').text = 'BRASIL'
    if propriedade.telefone:
        etree.SubElement(ender_emit, '{http://www.portalfiscal.inf.br/nfe}fone').text = propriedade.telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')[:14]
    
    # Inscrição Estadual
    if propriedade.inscricao_estadual:
        etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}IE').text = propriedade.inscricao_estadual[:14]
    else:
        etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}IE').text = 'ISENTO'
    
    # Inscrição Municipal (se houver)
    if hasattr(propriedade, 'inscricao_municipal') and propriedade.inscricao_municipal:
        etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}IM').text = propriedade.inscricao_municipal[:15]
    
    # CNAE Fiscal (se houver)
    cnae = config.get('CNAE_FISCAL', '')
    if cnae:
        etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}CNAE').text = cnae
    
    # CRT (Código de Regime Tributário)
    # 1 = Simples Nacional, 2 = Simples Nacional - excesso de sublimite, 3 = Regime Normal
    crt = config.get('CRT', '3')
    etree.SubElement(emit, '{http://www.portalfiscal.inf.br/nfe}CRT').text = crt
    
    return emit


def _gerar_destinatario(inf_nfe, cliente):
    """Gera dados do destinatário (cliente)"""
    if not cliente:
        return None
    
    dest = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}dest')
    
    # CPF ou CNPJ
    cpf_cnpj = cliente.cpf_cnpj.replace('.', '').replace('/', '').replace('-', '')
    if len(cpf_cnpj) == 14:
        etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}CNPJ').text = cpf_cnpj
    elif len(cpf_cnpj) == 11:
        etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}CPF').text = cpf_cnpj
    else:
        # Consumidor não identificado
        etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}CPF').text = '00000000000'
    
    # Razão Social ou Nome
    etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}xNome').text = cliente.nome[:60]
    
    # Endereço
    ender_dest = etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}enderDest')
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}xLgr').text = (cliente.endereco or '')[:60]
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}nro').text = (cliente.numero or 'S/N')[:60]
    if cliente.complemento:
        etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}xCpl').text = cliente.complemento[:60]
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}xBairro').text = (cliente.bairro or '')[:60]
    
    # Código do município (buscar por nome ou usar padrão)
    cod_mun = _buscar_codigo_municipio(cliente.cidade, cliente.estado)
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}cMun').text = cod_mun
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}xMun').text = (cliente.cidade or '')[:60]
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}UF').text = (cliente.estado or 'SP')[:2]
    if cliente.cep:
        etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}CEP').text = cliente.cep.replace('-', '')[:8]
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}cPais').text = '1058'
    etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}xPais').text = 'BRASIL'
    if cliente.telefone:
        etree.SubElement(ender_dest, '{http://www.portalfiscal.inf.br/nfe}fone').text = cliente.telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')[:14]
    
    # Inscrição Estadual (se houver)
    if cliente.inscricao_estadual:
        etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}IE').text = cliente.inscricao_estadual[:14]
    elif cliente.tipo_pessoa == 'JURIDICA':
        etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}IE').text = 'ISENTO'
    
    # Email (se houver)
    if hasattr(cliente, 'email') and cliente.email:
        etree.SubElement(dest, '{http://www.portalfiscal.inf.br/nfe}email').text = cliente.email[:60]
    
    return dest


def _gerar_itens(inf_nfe, nota_fiscal):
    """Gera os itens da NF-e"""
    itens = nota_fiscal.itens.all()
    
    for idx, item in enumerate(itens, start=1):
        det = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}det')
        det.set('nItem', str(idx))
        
        prod = etree.SubElement(det, '{http://www.portalfiscal.inf.br/nfe}prod')
        
        # Código do produto
        if item.codigo_produto:
            etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}cProd').text = item.codigo_produto[:60]
        else:
            etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}cProd').text = str(item.id)
        
        # Descrição
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}xProd').text = item.descricao[:120]
        
        # NCM
        ncm = item.ncm or '0101.29.00'  # NCM padrão para gado bovino
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}NCM').text = ncm.replace('.', '')
        
        # CFOP
        cfop = item.cfop or '5102'  # CFOP padrão para venda
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}CFOP').text = cfop
        
        # Unidade Comercial
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}uCom').text = item.unidade_medida[:6]
        
        # Quantidade Comercial
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}qCom').text = f'{item.quantidade:.4f}'.replace('.', ',')
        
        # Valor Unitário Comercial
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}vUnCom').text = f'{item.valor_unitario:.2f}'.replace('.', ',')
        
        # Valor Total do Produto
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}vProd').text = f'{item.valor_total:.2f}'.replace('.', ',')
        
        # Unidade Tributável (mesma da comercial)
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}uTrib').text = item.unidade_medida[:6]
        
        # Quantidade Tributável
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}qTrib').text = f'{item.quantidade:.4f}'.replace('.', ',')
        
        # Valor Unitário Tributável
        etree.SubElement(prod, '{http://www.portalfiscal.inf.br/nfe}vUnTrib').text = f'{item.valor_unitario:.2f}'.replace('.', ',')
        
        # Impostos
        imposto = etree.SubElement(det, '{http://www.portalfiscal.inf.br/nfe}imposto')
        
        # ICMS
        icms = etree.SubElement(imposto, '{http://www.portalfiscal.inf.br/nfe}ICMS')
        icms00 = etree.SubElement(icms, '{http://www.portalfiscal.inf.br/nfe}ICMS00')
        etree.SubElement(icms00, '{http://www.portalfiscal.inf.br/nfe}orig').text = '0'  # 0 = Nacional
        etree.SubElement(icms00, '{http://www.portalfiscal.inf.br/nfe}CST').text = '000'  # Tributada integralmente
        etree.SubElement(icms00, '{http://www.portalfiscal.inf.br/nfe}modBC').text = '0'  # Margem de valor agregado
        etree.SubElement(icms00, '{http://www.portalfiscal.inf.br/nfe}vBC').text = f'{item.valor_total:.2f}'.replace('.', ',')
        etree.SubElement(icms00, '{http://www.portalfiscal.inf.br/nfe}pICMS').text = '0,00'  # Alíquota (ajustar conforme necessário)
        etree.SubElement(icms00, '{http://www.portalfiscal.inf.br/nfe}vICMS').text = '0,00'
        
        # IPI (se aplicável)
        ipi = etree.SubElement(imposto, '{http://www.portalfiscal.inf.br/nfe}IPI')
        ipint = etree.SubElement(ipi, '{http://www.portalfiscal.inf.br/nfe}IPINT')
        etree.SubElement(ipint, '{http://www.portalfiscal.inf.br/nfe}CST').text = '03'  # Isento
        
        # PIS
        pis = etree.SubElement(imposto, '{http://www.portalfiscal.inf.br/nfe}PIS')
        pis_aliq = etree.SubElement(pis, '{http://www.portalfiscal.inf.br/nfe}PISAliq')
        etree.SubElement(pis_aliq, '{http://www.portalfiscal.inf.br/nfe}CST').text = '01'  # Operação tributável
        etree.SubElement(pis_aliq, '{http://www.portalfiscal.inf.br/nfe}vBC').text = f'{item.valor_total:.2f}'.replace('.', ',')
        etree.SubElement(pis_aliq, '{http://www.portalfiscal.inf.br/nfe}pPIS').text = '1,65'  # Alíquota padrão
        v_pis = item.valor_total * Decimal('0.0165')
        etree.SubElement(pis_aliq, '{http://www.portalfiscal.inf.br/nfe}vPIS').text = f'{v_pis:.2f}'.replace('.', ',')
        
        # COFINS
        cofins = etree.SubElement(imposto, '{http://www.portalfiscal.inf.br/nfe}COFINS')
        cofins_aliq = etree.SubElement(cofins, '{http://www.portalfiscal.inf.br/nfe}COFINSAliq')
        etree.SubElement(cofins_aliq, '{http://www.portalfiscal.inf.br/nfe}CST').text = '01'  # Operação tributável
        etree.SubElement(cofins_aliq, '{http://www.portalfiscal.inf.br/nfe}vBC').text = f'{item.valor_total:.2f}'.replace('.', ',')
        etree.SubElement(cofins_aliq, '{http://www.portalfiscal.inf.br/nfe}pCOFINS').text = '7,60'  # Alíquota padrão
        v_cofins = item.valor_total * Decimal('0.076')
        etree.SubElement(cofins_aliq, '{http://www.portalfiscal.inf.br/nfe}vCOFINS').text = f'{v_cofins:.2f}'.replace('.', ',')


def _gerar_totais(inf_nfe, nota_fiscal):
    """Gera os totais da NF-e"""
    total = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}total')
    icms_tot = etree.SubElement(total, '{http://www.portalfiscal.inf.br/nfe}ICMSTot')
    
    # Valor dos produtos
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vBC').text = f'{nota_fiscal.valor_produtos:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vICMS').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vICMSDeson').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vFCP').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vBCST').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vST').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vFCPST').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vFCPSTRet').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vProd').text = f'{nota_fiscal.valor_produtos:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vFrete').text = f'{nota_fiscal.valor_frete:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vSeg').text = f'{nota_fiscal.valor_seguro:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vDesc').text = f'{nota_fiscal.valor_desconto:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vII').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vIPI').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vIPIDevol').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vPIS').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vCOFINS').text = '0,00'
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vOutro').text = f'{nota_fiscal.valor_outros:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vNF').text = f'{nota_fiscal.valor_total:.2f}'.replace('.', ',')
    etree.SubElement(icms_tot, '{http://www.portalfiscal.inf.br/nfe}vTotTrib').text = '0,00'


def _gerar_transporte(inf_nfe, nota_fiscal):
    """Gera dados de transporte (opcional)"""
    if nota_fiscal.valor_frete == 0:
        return None
    
    transp = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}transp')
    
    # Modalidade do frete
    # 0 = Por conta do emitente, 1 = Por conta do destinatário, 2 = Por conta de terceiros, 9 = Sem frete
    etree.SubElement(transp, '{http://www.portalfiscal.inf.br/nfe}modFrete').text = '0'  # Por conta do emitente
    
    # Transportadora (se houver)
    # transporta = etree.SubElement(transp, '{http://www.portalfiscal.inf.br/nfe}transporta')
    # vol = etree.SubElement(transp, '{http://www.portalfiscal.inf.br/nfe}vol')
    
    return transp


def _gerar_pagamento(inf_nfe, nota_fiscal):
    """Gera dados de pagamento"""
    pag = etree.SubElement(inf_nfe, '{http://www.portalfiscal.inf.br/nfe}pag')
    
    det_pag = etree.SubElement(pag, '{http://www.portalfiscal.inf.br/nfe}detPag')
    etree.SubElement(det_pag, '{http://www.portalfiscal.inf.br/nfe}indPag').text = '0'  # 0 = Pagamento à vista
    etree.SubElement(det_pag, '{http://www.portalfiscal.inf.br/nfe}tPag').text = '99'  # 99 = Outros
    etree.SubElement(det_pag, '{http://www.portalfiscal.inf.br/nfe}vPag').text = f'{nota_fiscal.valor_total:.2f}'.replace('.', ',')
    
    etree.SubElement(pag, '{http://www.portalfiscal.inf.br/nfe}vTroco').text = '0,00'
    
    return pag


def _assinar_xml_nfe(xml_content, certificado_path, senha_certificado):
    """
    Assina o XML da NF-e com certificado digital
    
    NOTA: Esta é uma implementação básica. Para produção, use PyNFe ou PyTrustNFe
    que implementam a assinatura XML-DSig corretamente.
    """
    try:
        from OpenSSL import crypto
        if not LXML_AVAILABLE:
            logger.error('lxml não disponível para assinar XML')
            return None
        
        # Carregar certificado
        with open(certificado_path, 'rb') as f:
            cert_data = f.read()
        
        # Tentar carregar como PKCS12
        try:
            p12 = crypto.load_pkcs12(cert_data, senha_certificado.encode() if senha_certificado else None)
            certificado = p12.get_certificate()
            chave_privada = p12.get_privatekey()
        except:
            # Tentar carregar como PEM
            certificado = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            # Carregar chave privada separadamente
            chave_path = certificado_path.replace('.p12', '.key').replace('.pfx', '.key')
            if os.path.exists(chave_path):
                with open(chave_path, 'rb') as kf:
                    chave_data = kf.read()
                chave_privada = crypto.load_privatekey(crypto.FILETYPE_PEM, chave_data, senha_certificado.encode() if senha_certificado else None)
            else:
                logger.error('Chave privada não encontrada')
                return None
        
        # Parse do XML
        root = etree.fromstring(xml_content)
        
        # Assinar usando xmlsec
        # Nota: Esta é uma implementação simplificada
        # Em produção, use uma biblioteca especializada como PyNFe ou PyTrustNFe
        
        # Por enquanto, retornar XML sem assinatura (será necessário implementar assinatura completa)
        logger.warning('Assinatura digital não implementada completamente. Use biblioteca especializada.')
        return xml_content
        
    except Exception as e:
        logger.error(f'Erro ao assinar XML: {str(e)}', exc_info=True)
        return None


def _enviar_para_sefaz(xml_assinado, ambiente, uf, certificado_path, senha_certificado):
    """
    Envia XML assinado para a SEFAZ
    
    NOTA: Esta é uma estrutura básica. Para produção, use PyNFe ou PyTrustNFe
    que implementam a comunicação SOAP com SEFAZ corretamente.
    """
    if not ZEEP_AVAILABLE:
        return {
            'sucesso': False,
            'erro': 'Biblioteca zeep não instalada. Execute: pip install zeep. Para implementação completa, recomenda-se: pip install pynfe'
        }
    
    try:
        # URLs dos webservices da SEFAZ por UF e ambiente
        urls_sefaz = {
            'SP': {
                'homologacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx',
                'producao': 'https://nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx'
            },
            # Adicionar outras UFs conforme necessário
        }
        
        url = urls_sefaz.get(uf, {}).get(ambiente)
        if not url:
            return {
                'sucesso': False,
                'erro': f'URL da SEFAZ não configurada para UF {uf} e ambiente {ambiente}'
            }
        
        # Criar sessão com certificado
        session = Session()
        session.cert = (certificado_path, senha_certificado) if senha_certificado else certificado_path
        
        # Criar cliente SOAP
        transport = Transport(session=session)
        client = Client(url, transport=transport)
        
        # Enviar para autorização
        # Nota: Esta é uma estrutura básica. A implementação completa requer
        # conhecimento detalhado do protocolo NFeAutorizacao4 da SEFAZ
        
        logger.warning('Envio direto para SEFAZ requer implementação completa do protocolo SOAP. Use PyNFe para implementação completa.')
        
        return {
            'sucesso': False,
            'erro': 'Envio direto para SEFAZ requer biblioteca especializada. Instale PyNFe: pip install pynfe'
        }
        
    except Exception as e:
        logger.error(f'Erro ao enviar para SEFAZ: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro ao enviar para SEFAZ: {str(e)}. Para implementação completa, instale PyNFe: pip install pynfe'
        }


def _gerar_chave_acesso(nota_fiscal, config):
    """
    Gera chave de acesso da NF-e (44 dígitos)
    """
    # Formato: UF (2) + AAMM (4) + CNPJ (14) + mod (2) + serie (3) + nNF (9) + tpEmis (1) + cNF (8) + cDV (1)
    uf = config.get('UF_EMITENTE', '35')
    ano_mes = nota_fiscal.data_emissao.strftime('%y%m')
    
    cnpj = nota_fiscal.propriedade.cnpj or ''
    if not cnpj and hasattr(nota_fiscal.propriedade, 'produtor') and nota_fiscal.propriedade.produtor:
        cnpj = nota_fiscal.propriedade.produtor.cpf_cnpj
    cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')[:14].zfill(14)
    
    modelo = '55'  # NF-e
    serie = nota_fiscal.serie.zfill(3)
    numero = nota_fiscal.numero.zfill(9)
    tp_emis = '1'  # Normal
    c_nf = nota_fiscal.numero.zfill(8)[-8:]
    
    # Montar chave (sem DV)
    chave_sem_dv = f'{uf}{ano_mes}{cnpj}{modelo}{serie}{numero}{tp_emis}{c_nf}'
    
    # Calcular DV (dígito verificador)
    dv = _calcular_dv_chave_acesso(chave_sem_dv)
    
    return f'{chave_sem_dv}{dv}'


def _calcular_dv_chave_acesso(chave):
    """Calcula o dígito verificador da chave de acesso"""
    multiplicadores = [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(chave[i]) * multiplicadores[i] for i in range(len(chave)))
    resto = soma % 11
    if resto < 2:
        return '0'
    else:
        return str(11 - resto)


def _buscar_codigo_municipio(cidade, uf):
    """Busca código do município (simplificado - usar tabela IBGE completa)"""
    # Tabela simplificada de códigos de municípios
    codigos_municipios = {
        'SP': {
            'SAO PAULO': '3550308',
            'CAMPINAS': '3509502',
            'SANTOS': '3548500',
        },
        'MG': {
            'BELO HORIZONTE': '3106200',
            'UBERLANDIA': '3170206',
        },
        # Adicionar mais conforme necessário
    }
    
    cidade_upper = (cidade or '').upper()
    uf_upper = (uf or 'SP').upper()
    
    if uf_upper in codigos_municipios:
        if cidade_upper in codigos_municipios[uf_upper]:
            return codigos_municipios[uf_upper][cidade_upper]
    
    # Retornar código padrão (São Paulo)
    return '3550308'

