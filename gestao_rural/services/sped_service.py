# -*- coding: utf-8 -*-
"""
Serviço para geração de arquivos SPED (Sistema Público de Escrituração Digital)
Integração com Receita Federal
"""

import logging
from decimal import Decimal
from datetime import date
from typing import Optional, List

logger = logging.getLogger(__name__)


class SPEDService:
    """
    Serviço para geração de arquivos SPED Fiscal (EFD-ICMS/IPI)
    
    Nota: Este é um exemplo base. Para produção, recomenda-se usar bibliotecas
    especializadas como erpbrasil.sped ou pysped
    """
    
    def __init__(self, propriedade):
        """
        Inicializa o serviço com uma propriedade
        
        Args:
            propriedade: Instância de Propriedade
        """
        self.propriedade = propriedade
        self.produtor = propriedade.produtor
    
    def validar_dados_obrigatorios(self) -> tuple[bool, List[str]]:
        """
        Valida se todos os dados obrigatórios estão preenchidos
        
        Returns:
            (valido, lista_erros)
        """
        erros = []
        
        if not self.produtor.cpf_cnpj:
            erros.append("CPF/CNPJ do produtor não cadastrado")
        
        if not self.propriedade.inscricao_estadual:
            erros.append("Inscrição Estadual da propriedade não cadastrada")
        
        if not self.propriedade.municipio or not self.propriedade.uf:
            erros.append("Município e UF da propriedade são obrigatórios")
        
        return len(erros) == 0, erros
    
    def formatar_cnpj_cpf(self, cnpj_cpf: str) -> str:
        """Remove formatação do CNPJ/CPF"""
        if not cnpj_cpf:
            return ''
        return cnpj_cpf.replace('.', '').replace('/', '').replace('-', '').strip()
    
    def obter_codigo_municipio_ibge(self) -> str:
        """
        Obtém código IBGE do município
        
        Nota: Em produção, usar tabela IBGE ou API
        """
        # Exemplo: retornar código padrão
        # Em produção, buscar na tabela de municípios IBGE
        return '0000000'  # Substituir por código real
    
    def gerar_registro_0000(self, periodo_inicio: date, periodo_fim: date) -> str:
        """
        Gera registro 0000 - Abertura do Arquivo Digital
        
        Layout conforme Manual de Orientação do SPED Fiscal
        """
        cnpj = self.formatar_cnpj_cpf(self.produtor.cpf_cnpj)
        ie = self.propriedade.inscricao_estadual or ''
        razao_social = self.produtor.nome[:60]
        cod_municipio = self.obter_codigo_municipio_ibge()
        uf = self.propriedade.uf
        
        # Formato: |0000|versao|cod_fin|dt_ini|dt_fim|nome|cnpj|cpf|uf|ie|...
        registro = (
            f"|0000|008|0|{periodo_inicio.strftime('%d%m%Y')}|"
            f"{periodo_fim.strftime('%d%m%Y')}|{razao_social}|{cnpj}||{uf}|"
            f"{ie}|{cod_municipio}|||"
        )
        
        return registro
    
    def gerar_registro_0001(self) -> str:
        """
        Gera registro 0001 - Abertura do Bloco 0
        """
        return "|0001|0|"
    
    def gerar_registro_0005(self) -> str:
        """
        Gera registro 0005 - Dados Complementares da Entidade
        """
        cep = (self.propriedade.cep or '').replace('-', '').replace('.', '')
        endereco = (self.propriedade.endereco or '')[:60]
        numero = ''  # Adicionar campo número em Propriedade se necessário
        complemento = ''  # Adicionar campo complemento se necessário
        bairro = (self.propriedade.bairro or '')[:60]
        municipio = self.propriedade.municipio[:60]
        uf = self.propriedade.uf
        telefone = (self.produtor.telefone or '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        email = (self.produtor.email or '')[:60]
        
        fantasia = ''  # Adicionar campo nome_fantasia em ProdutorRural se necessário
        
        registro = (
            f"|0005|{fantasia}|{cep}|{endereco}|{numero}|{complemento}|"
            f"{bairro}|{municipio}|{uf}|{telefone}|{email}|"
        )
        
        return registro
    
    def gerar_registro_c100(self, nota) -> str:
        """
        Gera registro C100 - Documento - Nota Fiscal (Entrada/Saída)
        
        Args:
            nota: Instância de NotaFiscal
        """
        ind_oper = '0' if nota.tipo == 'ENTRADA' else '1'
        ind_emit = '0'  # 0=Emissão própria, 1=Terceiros
        cod_part = ''  # Código do participante (fornecedor/cliente)
        cod_mod = '55'  # 55=NF-e
        cod_sit = '00'  # 00=Documento regular
        ser = nota.serie
        num_doc = nota.numero
        chv_nfe = nota.chave_acesso or ''
        dt_doc = nota.data_emissao.strftime('%d%m%Y')
        dt_e_s = (nota.data_entrada or nota.data_emissao).strftime('%d%m%Y')
        vl_doc = f"{float(nota.valor_total):.2f}"
        ind_pgto = '0'  # 0=À vista, 1=À prazo
        vl_desc = f"{float(nota.valor_desconto):.2f}"
        vl_abat_nt = '0.00'
        vl_merc = f"{float(nota.valor_produtos):.2f}"
        ind_frt = '0'  # 0=Por conta do emitente
        vl_frt = f"{float(nota.valor_frete):.2f}"
        vl_seg = f"{float(nota.valor_seguro):.2f}"
        vl_out_da = f"{float(nota.valor_outros):.2f}"
        vl_bc_icms = f"{float(nota.valor_produtos):.2f}"  # Ajustar conforme cálculo real
        vl_icms = '0.00'  # Calcular conforme alíquota
        vl_bc_icms_st = '0.00'
        vl_icms_st = '0.00'
        vl_ipi = '0.00'
        vl_pis = '0.00'
        vl_cofins = '0.00'
        vl_pis_st = '0.00'
        vl_cofins_st = '0.00'
        
        registro = (
            f"|C100|{ind_oper}|{ind_emit}|{cod_part}|{cod_mod}|{cod_sit}|"
            f"{ser}|{num_doc}|{chv_nfe}|{dt_doc}|{dt_e_s}|{vl_doc}|"
            f"{ind_pgto}|{vl_desc}|{vl_abat_nt}|{vl_merc}|{ind_frt}|{vl_frt}|"
            f"{vl_seg}|{vl_out_da}|{vl_bc_icms}|{vl_icms}|{vl_bc_icms_st}|"
            f"{vl_icms_st}|{vl_ipi}|{vl_pis}|{vl_cofins}|{vl_pis_st}|{vl_cofins_st}|"
        )
        
        return registro
    
    def gerar_registro_c170(self, item_nota, nota) -> str:
        """
        Gera registro C170 - Itens do Documento
        
        Args:
            item_nota: Instância de ItemNotaFiscal
            nota: Instância de NotaFiscal (pai do item)
        """
        num_item = str(item_nota.ordem or 1).zfill(3)
        cod_item = item_nota.codigo_produto or ''
        descr_compl = item_nota.descricao[:60]
        qtd = f"{float(item_nota.quantidade):.3f}"
        unid = item_nota.unidade_medida or 'UN'
        vl_item = f"{float(item_nota.valor_total):.2f}"
        vl_desc = '0.00'
        ind_mov = '0'  # 0=Sim, 1=Não
        cst_icms = '000'  # Código de Situação Tributária
        cfop = item_nota.cfop or ''
        cod_nat = '01'  # Natureza da operação
        vl_bc_icms = f"{float(item_nota.valor_total):.2f}"
        aliq_icms = '0.00'
        vl_icms = '0.00'
        vl_bc_icms_st = '0.00'
        aliq_st = '0.00'
        vl_icms_st = '0.00'
        ind_apur = '0'
        cst_ipi = '00'
        cod_enq = ''
        vl_bc_ipi = '0.00'
        aliq_ipi = '0.00'
        vl_ipi = '0.00'
        cst_pis = '01'
        vl_bc_pis = '0.00'
        aliq_pis = '0.00'
        quant_bc_pis = '0.00'
        vl_pis = '0.00'
        cst_cofins = '01'
        vl_bc_cofins = '0.00'
        aliq_cofins = '0.00'
        quant_bc_cofins = '0.00'
        vl_cofins = '0.00'
        cod_cta = ''
        
        registro = (
            f"|C170|{num_item}|{cod_item}|{descr_compl}|{qtd}|{unid}|"
            f"{vl_item}|{vl_desc}|{ind_mov}|{cst_icms}|{cfop}|{cod_nat}|"
            f"{vl_bc_icms}|{aliq_icms}|{vl_icms}|{vl_bc_icms_st}|{aliq_st}|"
            f"{vl_icms_st}|{ind_apur}|{cst_ipi}|{cod_enq}|{vl_bc_ipi}|"
            f"{aliq_ipi}|{vl_ipi}|{cst_pis}|{vl_bc_pis}|{aliq_pis}|"
            f"{quant_bc_pis}|{vl_pis}|{cst_cofins}|{vl_bc_cofins}|"
            f"{aliq_cofins}|{quant_bc_cofins}|{vl_cofins}|{cod_cta}|"
        )
        
        return registro
    
    def gerar_registro_9999(self, total_linhas: int) -> str:
        """
        Gera registro 9999 - Encerramento do Arquivo Digital
        
        Args:
            total_linhas: Total de linhas do arquivo (incluindo este registro)
        """
        return f"|9999|{total_linhas}|"
    
    def gerar_arquivo_efd_icms_ipi(
        self,
        periodo_inicio: date,
        periodo_fim: date
    ) -> str:
        """
        Gera arquivo completo EFD-ICMS/IPI
        
        Args:
            periodo_inicio: Data inicial do período
            periodo_fim: Data final do período
            
        Returns:
            Conteúdo do arquivo como string
            
        Raises:
            ValueError: Se dados obrigatórios estiverem faltando
        """
        # Validar dados
        valido, erros = self.validar_dados_obrigatorios()
        if not valido:
            raise ValueError(f"Dados obrigatórios faltando: {', '.join(erros)}")
        
        linhas = []
        
        # Registro 0000 - Abertura
        linhas.append(self.gerar_registro_0000(periodo_inicio, periodo_fim))
        
        # Registro 0001 - Abertura Bloco 0
        linhas.append(self.gerar_registro_0001())
        
        # Registro 0005 - Dados Complementares
        linhas.append(self.gerar_registro_0005())
        
        # Registro 0990 - Encerramento Bloco 0
        linhas.append("|0990|3|")  # 3 registros no bloco 0 (0001, 0005, 0990)
        
        # Bloco C - Documentos Fiscais I - Mercadorias (ICMS/IPI)
        linhas.append("|C001|0|")  # Abertura Bloco C
        
        # Buscar notas fiscais
        from gestao_rural.models_compras_financeiro import NotaFiscal
        
        notas = NotaFiscal.objects.filter(
            propriedade=self.propriedade,
            data_emissao__gte=periodo_inicio,
            data_emissao__lte=periodo_fim
        ).select_related('fornecedor').prefetch_related('itens')
        
        # Registros C100 - Documentos
        for nota in notas:
            try:
                linhas.append(self.gerar_registro_c100(nota))
                
                # Registros C170 - Itens
                for item in nota.itens.all():
                    linhas.append(self.gerar_registro_c170(item, nota))
                    
            except Exception as e:
                logger.error(f"Erro ao processar nota {nota.id}: {e}")
                continue
        
        # Registro C990 - Encerramento Bloco C
        total_c = len([l for l in linhas if l.startswith('|C')]) + 2  # +2 para C001 e C990
        linhas.append(f"|C990|{total_c}|")
        
        # Registro 9999 - Encerramento
        total_linhas = len(linhas) + 1  # +1 para incluir este registro
        linhas.append(self.gerar_registro_9999(total_linhas))
        
        # Juntar todas as linhas
        arquivo = '\n'.join(linhas)
        
        return arquivo


def gerar_arquivo_sped(
    propriedade_id: int,
    periodo_inicio: date,
    periodo_fim: date
) -> str:
    """
    Função helper para gerar arquivo SPED
    
    Args:
        propriedade_id: ID da propriedade
        periodo_inicio: Data inicial
        periodo_fim: Data final
        
    Returns:
        Conteúdo do arquivo como string
    """
    from gestao_rural.models import Propriedade
    
    propriedade = Propriedade.objects.get(id=propriedade_id)
    service = SPEDService(propriedade)
    
    return service.gerar_arquivo_efd_icms_ipi(periodo_inicio, periodo_fim)

