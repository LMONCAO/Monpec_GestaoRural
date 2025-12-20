# -*- coding: utf-8 -*-
"""
Serviço de Emissão de NF-e Direta com SEFAZ usando PyNFe
Requer: pip install pynfe
"""

import os
import logging
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def emitir_nfe_com_pynfe(nota_fiscal):
    """
    Emite NF-e usando PyNFe (biblioteca especializada)
    
    Requisitos:
    - pip install pynfe
    - Certificado digital A1 ou A3
    - Configuração NFE_SEFAZ nas settings
    
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
    try:
        # Verificar se PyNFe está instalado
        try:
            from pynfe.processamento.comunicacao import ComunicacaoSefaz
            from pynfe.processamento.serializacao import SerializacaoXML
            from pynfe.entidades.cliente import Cliente
            from pynfe.entidades.emitente import Emitente
            from pynfe.entidades.produto import Produto
            from pynfe.entidades.nota_fiscal import NotaFiscal as PyNFeNota
        except ImportError:
            return {
                'sucesso': False,
                'erro': 'PyNFe não instalado. Execute: pip install pynfe'
            }
        
        # Verificar configuração
        config = getattr(settings, 'NFE_SEFAZ', None)
        if not config:
            return {
                'sucesso': False,
                'erro': 'Configuração NFE_SEFAZ não encontrada nas settings'
            }
        
        certificado_path = config.get('CERTIFICADO_PATH')
        senha_certificado = config.get('SENHA_CERTIFICADO')
        ambiente = config.get('AMBIENTE', 'homologacao')
        uf = config.get('UF', 'SP')
        
        if not certificado_path or not os.path.exists(certificado_path):
            return {
                'sucesso': False,
                'erro': 'Certificado digital não encontrado'
            }
        
        # Criar emitente
        emitente = _criar_emitente_pynfe(nota_fiscal.propriedade, config)
        
        # Criar cliente
        cliente = _criar_cliente_pynfe(nota_fiscal.cliente)
        
        # Criar produtos
        produtos = _criar_produtos_pynfe(nota_fiscal)
        
        # Criar nota fiscal PyNFe
        nfe = PyNFeNota(
            emitente=emitente,
            cliente=cliente,
            uf=uf,
            natureza_operacao='VENDA',
            forma_pagamento='99',  # Outros
            tipo_pagamento='0',  # À vista
            modelo='55',  # NF-e
            serie=nota_fiscal.serie,
            numero_nf=nota_fiscal.numero,
            data_emissao=datetime.combine(nota_fiscal.data_emissao, datetime.min.time()),
            data_saida_entrada=datetime.combine(nota_fiscal.data_entrada or nota_fiscal.data_emissao, datetime.min.time()),
            tipo_documento='1',  # Saída
            local_destino='1',  # Operação interna
            finalidade_emissao='1',  # Normal
            consumidor_final='1' if cliente.tipo_pessoa == 'FISICA' else '0',
            presenca_comprador='1',  # Operação presencial
            processo_emissao='0',  # Emissão de NF-e com aplicativo do contribuinte
            produtos=produtos,
            valor_icms=Decimal('0.00'),
            valor_ipi=Decimal('0.00'),
            valor_pis=Decimal('0.00'),
            valor_cofins=Decimal('0.00'),
            valor_desconto=nota_fiscal.valor_desconto,
            valor_total=nota_fiscal.valor_total,
            valor_frete=nota_fiscal.valor_frete,
            valor_seguro=nota_fiscal.valor_seguro,
            valor_outros=nota_fiscal.valor_outros,
        )
        
        # Serializar e assinar
        serializador = SerializacaoXML(certificado_path, senha_certificado)
        xml_assinado = serializador.gerar_nfe(nfe)
        
        # Enviar para SEFAZ
        comunicacao = ComunicacaoSefaz(
            uf=uf,
            certificado=certificado_path,
            senha=senha_certificado,
            homologacao=(ambiente == 'homologacao')
        )
        
        resultado = comunicacao.autorizar(
            modelo='nfe',
            versao='4.00',
            xml=xml_assinado
        )
        
        if resultado['status'] == 'autorizado':
            return {
                'sucesso': True,
                'chave_acesso': resultado.get('chave', ''),
                'protocolo': resultado.get('protocolo', ''),
                'xml': xml_assinado.encode('utf-8') if isinstance(xml_assinado, str) else xml_assinado
            }
        else:
            return {
                'sucesso': False,
                'erro': resultado.get('mensagem', 'Erro ao autorizar NF-e')
            }
            
    except Exception as e:
        logger.error(f'Erro ao emitir NF-e com PyNFe: {str(e)}', exc_info=True)
        return {
            'sucesso': False,
            'erro': f'Erro ao emitir NF-e: {str(e)}'
        }


def _criar_emitente_pynfe(propriedade, config):
    """Cria objeto Emitente para PyNFe"""
    from pynfe.entidades.emitente import Emitente
    
    cnpj = propriedade.cnpj or config.get('CNPJ_EMITENTE', '')
    if not cnpj and hasattr(propriedade, 'produtor') and propriedade.produtor:
        cnpj = propriedade.produtor.cpf_cnpj
    
    emitente = Emitente(
        razao_social=propriedade.nome_propriedade,
        nome_fantasia=getattr(propriedade, 'nome_fantasia', None) or propriedade.nome_propriedade,
        cnpj=cnpj.replace('.', '').replace('/', '').replace('-', ''),
        codigo_de_regime_tributario=config.get('CRT', '3'),
        inscricao_estadual=propriedade.inscricao_estadual or 'ISENTO',
        inscricao_municipal=getattr(propriedade, 'inscricao_municipal', None) or '',
        cnae_fiscal=config.get('CNAE_FISCAL', ''),
        endereco_logradouro=propriedade.endereco or '',
        endereco_numero=propriedade.numero or 'S/N',
        endereco_complemento=propriedade.complemento or '',
        endereco_bairro=propriedade.bairro or '',
        endereco_municipio=propriedade.cidade or '',
        endereco_uf=propriedade.estado or 'SP',
        endereco_cep=propriedade.cep.replace('-', '') if propriedade.cep else '',
        endereco_pais='1058',  # Brasil
        endereco_telefone=propriedade.telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '') if propriedade.telefone else '',
    )
    
    return emitente


def _criar_cliente_pynfe(cliente):
    """Cria objeto Cliente para PyNFe"""
    from pynfe.entidades.cliente import Cliente
    
    if not cliente:
        # Cliente não identificado
        return Cliente(
            razao_social='CONSUMIDOR NAO IDENTIFICADO',
            tipo_documento='CPF',
            numero_documento='00000000000',
            indicador_ie='9',  # Não contribuinte
        )
    
    cpf_cnpj = cliente.cpf_cnpj.replace('.', '').replace('/', '').replace('-', '')
    
    return Cliente(
        razao_social=cliente.nome,
        tipo_documento='CNPJ' if len(cpf_cnpj) == 14 else 'CPF',
        numero_documento=cpf_cnpj,
        indicador_ie='1' if cliente.inscricao_estadual else '9',
        inscricao_estadual=cliente.inscricao_estadual or '',
        endereco_logradouro=cliente.endereco or '',
        endereco_numero=cliente.numero or 'S/N',
        endereco_complemento=cliente.complemento or '',
        endereco_bairro=cliente.bairro or '',
        endereco_municipio=cliente.cidade or '',
        endereco_uf=cliente.estado or 'SP',
        endereco_cep=cliente.cep.replace('-', '') if cliente.cep else '',
        endereco_pais='1058',
        endereco_telefone=cliente.telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '') if cliente.telefone else '',
        email=cliente.email if hasattr(cliente, 'email') and cliente.email else '',
    )


def _criar_produtos_pynfe(nota_fiscal):
    """Cria lista de produtos para PyNFe"""
    from pynfe.entidades.produto import Produto
    
    produtos = []
    
    for item in nota_fiscal.itens.all():
        produto = Produto(
            codigo=item.codigo_produto or str(item.id),
            descricao=item.descricao,
            ncm=item.ncm.replace('.', '') if item.ncm else '01012900',
            cfop=item.cfop or '5102',
            unidade_comercial=item.unidade_medida,
            quantidade_comercial=item.quantidade,
            valor_unitario_comercial=item.valor_unitario,
            valor_total_bruto=item.valor_total,
            unidade_tributavel=item.unidade_medida,
            quantidade_tributavel=item.quantidade,
            valor_unitario_tributavel=item.valor_unitario,
            origem='0',  # Nacional
            tributacao_icms='00',  # Tributada integralmente
            icms_situacao_tributaria='00',
            icms_aliquota=Decimal('0.00'),
            icms_base_calculo=item.valor_total,
            icms_valor=Decimal('0.00'),
            ipi_situacao_tributaria='03',  # Isento
            ipi_aliquota=Decimal('0.00'),
            pis_situacao_tributaria='01',  # Operação tributável
            pis_aliquota=Decimal('1.65'),
            cofins_situacao_tributaria='01',  # Operação tributável
            cofins_aliquota=Decimal('7.60'),
        )
        
        produtos.append(produto)
    
    return produtos

