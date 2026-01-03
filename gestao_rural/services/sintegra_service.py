# -*- coding: utf-8 -*-
"""
Serviço para geração de arquivos Sintegra
Integração com Sistema Integrado de Informações sobre Operações Interestaduais
"""

import logging
from decimal import Decimal
from datetime import date
from typing import Optional, List
from django.db.models import Q

logger = logging.getLogger(__name__)


class SintegraService:
    """
    Serviço para geração de arquivos Sintegra
    
    Nota: Este é um exemplo base. Para produção, recomenda-se usar bibliotecas
    especializadas como pysintegra ou erpbrasil.edoc
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
        
        # Validar CNPJ/CPF
        if not self.produtor.cpf_cnpj:
            erros.append("CPF/CNPJ do produtor não cadastrado")
        
        # Validar Inscrição Estadual
        if not self.propriedade.inscricao_estadual:
            erros.append("Inscrição Estadual da propriedade não cadastrada")
        
        # Validar endereço
        if not self.propriedade.municipio or not self.propriedade.uf:
            erros.append("Município e UF da propriedade são obrigatórios")
        
        return len(erros) == 0, erros
    
    def formatar_cnpj_cpf(self, cnpj_cpf: str) -> str:
        """
        Remove formatação do CNPJ/CPF (pontos, barras, hífens)
        
        Args:
            cnpj_cpf: CNPJ/CPF formatado
            
        Returns:
            CNPJ/CPF apenas com números
        """
        if not cnpj_cpf:
            return ''
        return cnpj_cpf.replace('.', '').replace('/', '').replace('-', '').strip()
    
    def formatar_cep(self, cep: str) -> str:
        """
        Remove formatação do CEP
        
        Args:
            cep: CEP formatado
            
        Returns:
            CEP apenas com números
        """
        if not cep:
            return ''
        return cep.replace('-', '').replace('.', '').strip()
    
    def obter_notas_fiscais_periodo(
        self,
        periodo_inicio: date,
        periodo_fim: date,
        tipo: Optional[str] = None
    ):
        """
        Obtém notas fiscais do período
        
        Args:
            periodo_inicio: Data inicial
            periodo_fim: Data final
            tipo: 'ENTRADA', 'SAIDA' ou None para ambos
            
        Returns:
            QuerySet de NotaFiscal
        """
        from gestao_rural.models_compras_financeiro import NotaFiscal
        
        filtros = Q(
            propriedade=self.propriedade,
            data_emissao__gte=periodo_inicio,
            data_emissao__lte=periodo_fim
        )
        
        if tipo:
            filtros &= Q(tipo=tipo)
        
        return NotaFiscal.objects.filter(filtros).select_related(
            'fornecedor'
        ).prefetch_related('itens')
    
    def calcular_icms_nota(self, nota) -> dict:
        """
        Calcula valores de ICMS da nota fiscal
        
        Nota: Este é um exemplo simplificado. Em produção, o cálculo
        deve considerar alíquotas, CST, regime tributário, etc.
        
        Args:
            nota: Instância de NotaFiscal
            
        Returns:
            Dict com valores calculados
        """
        # Valores padrão (ajustar conforme regras fiscais)
        base_calculo = float(nota.valor_produtos)
        
        # Exemplo: alíquota de 12% (ajustar conforme estado e produto)
        aliquota_icms = 0.12
        valor_icms = base_calculo * aliquota_icms
        
        return {
            'base_calculo': base_calculo,
            'aliquota': aliquota_icms,
            'valor_icms': valor_icms,
        }
    
    def gerar_registro_tipo_0(self, uf: str) -> str:
        """
        Gera registro tipo 0 - Identificação do Arquivo
        
        Formato varia por estado. Este é um exemplo genérico.
        """
        # Exemplo de formato (ajustar conforme estado)
        registro = f"0|SINTEGRA|{uf}|{date.today().strftime('%Y%m%d')}|"
        return registro
    
    def gerar_registro_tipo_1(self) -> str:
        """
        Gera registro tipo 1 - Identificação da Empresa
        """
        cnpj = self.formatar_cnpj_cpf(self.produtor.cpf_cnpj)
        ie = self.propriedade.inscricao_estadual or ''
        razao_social = self.produtor.nome[:60]  # Limitar tamanho
        municipio = self.propriedade.municipio[:30]
        uf = self.propriedade.uf
        cep = self.formatar_cep(self.propriedade.cep or '')
        endereco = (self.propriedade.endereco or '')[:60]
        
        # Formato exemplo (ajustar conforme estado)
        registro = f"1|{cnpj}|{ie}|{razao_social}|{municipio}|{uf}|{cep}|{endereco}|"
        return registro
    
    def gerar_registro_tipo_3_entrada(self, nota) -> str:
        """
        Gera registro tipo 3 - Entrada (Compra)
        
        Args:
            nota: Instância de NotaFiscal tipo ENTRADA
        """
        fornecedor = nota.fornecedor
        cnpj_fornecedor = self.formatar_cnpj_cpf(fornecedor.cpf_cnpj or '')
        ie_fornecedor = fornecedor.inscricao_estadual or ''
        uf_fornecedor = fornecedor.estado or ''
        
        # Obter CFOP do primeiro item (ou padrão)
        cfop = '5101'  # Padrão para compra
        if nota.itens.exists():
            primeiro_item = nota.itens.first()
            if primeiro_item.cfop:
                cfop = primeiro_item.cfop
        
        # Calcular ICMS
        icms = self.calcular_icms_nota(nota)
        
        data_entrada = (nota.data_entrada or nota.data_emissao).strftime('%Y%m%d')
        
        # Formato exemplo (ajustar conforme estado)
        registro = (
            f"3|E|{data_entrada}|{uf_fornecedor}|{cnpj_fornecedor}|"
            f"{ie_fornecedor}|55|{nota.serie}|{nota.numero}|{cfop}|"
            f"{nota.valor_total:.2f}|{icms['base_calculo']:.2f}|"
            f"{icms['valor_icms']:.2f}|"
        )
        
        return registro
    
    def gerar_registro_tipo_3_saida(self, nota) -> str:
        """
        Gera registro tipo 3 - Saída (Venda)
        
        Args:
            nota: Instância de NotaFiscal tipo SAIDA
        """
        # Nota: Precisa adicionar campo 'cliente' em NotaFiscal
        # Por enquanto, usar valores padrão
        cnpj_cliente = ''
        ie_cliente = ''
        uf_cliente = ''
        
        cfop = '5102'  # Padrão para venda
        if nota.itens.exists():
            primeiro_item = nota.itens.first()
            if primeiro_item.cfop:
                cfop = primeiro_item.cfop
        
        icms = self.calcular_icms_nota(nota)
        data_saida = (nota.data_entrada or nota.data_emissao).strftime('%Y%m%d')
        
        registro = (
            f"3|S|{data_saida}|{uf_cliente}|{cnpj_cliente}|"
            f"{ie_cliente}|55|{nota.serie}|{nota.numero}|{cfop}|"
            f"{nota.valor_total:.2f}|{icms['base_calculo']:.2f}|"
            f"{icms['valor_icms']:.2f}|"
        )
        
        return registro
    
    def gerar_registro_tipo_5(self, total_registros: int) -> str:
        """
        Gera registro tipo 5 - Encerramento
        
        Args:
            total_registros: Total de registros tipo 3
        """
        registro = f"5|{total_registros}|"
        return registro
    
    def gerar_arquivo(
        self,
        periodo_inicio: date,
        periodo_fim: date,
        uf: Optional[str] = None
    ) -> str:
        """
        Gera arquivo completo do Sintegra
        
        Args:
            periodo_inicio: Data inicial do período
            periodo_fim: Data final do período
            uf: UF do estado (usa da propriedade se não informado)
            
        Returns:
            Conteúdo do arquivo como string
            
        Raises:
            ValueError: Se dados obrigatórios estiverem faltando
        """
        # Validar dados
        valido, erros = self.validar_dados_obrigatorios()
        if not valido:
            raise ValueError(f"Dados obrigatórios faltando: {', '.join(erros)}")
        
        uf = uf or self.propriedade.uf
        
        # Iniciar arquivo
        linhas = []
        
        # Registro tipo 0 - Cabeçalho
        linhas.append(self.gerar_registro_tipo_0(uf))
        
        # Registro tipo 1 - Empresa
        linhas.append(self.gerar_registro_tipo_1())
        
        # Registros tipo 3 - Entradas
        notas_entrada = self.obter_notas_fiscais_periodo(
            periodo_inicio, periodo_fim, tipo='ENTRADA'
        )
        
        for nota in notas_entrada:
            try:
                registro = self.gerar_registro_tipo_3_entrada(nota)
                linhas.append(registro)
            except Exception as e:
                logger.error(f"Erro ao processar nota entrada {nota.id}: {e}")
                continue
        
        # Registros tipo 3 - Saídas
        notas_saida = self.obter_notas_fiscais_periodo(
            periodo_inicio, periodo_fim, tipo='SAIDA'
        )
        
        for nota in notas_saida:
            try:
                registro = self.gerar_registro_tipo_3_saida(nota)
                linhas.append(registro)
            except Exception as e:
                logger.error(f"Erro ao processar nota saída {nota.id}: {e}")
                continue
        
        # Contar registros tipo 3
        total_registros_3 = len(linhas) - 2  # Excluir registros 0 e 1
        
        # Registro tipo 5 - Encerramento
        linhas.append(self.gerar_registro_tipo_5(total_registros_3))
        
        # Juntar todas as linhas
        arquivo = '\n'.join(linhas)
        
        return arquivo


def gerar_arquivo_sintegra(
    propriedade_id: int,
    periodo_inicio: date,
    periodo_fim: date,
    uf: Optional[str] = None
) -> str:
    """
    Função helper para gerar arquivo Sintegra
    
    Args:
        propriedade_id: ID da propriedade
        periodo_inicio: Data inicial
        periodo_fim: Data final
        uf: UF do estado (opcional)
        
    Returns:
        Conteúdo do arquivo como string
    """
    from gestao_rural.models import Propriedade
    
    propriedade = Propriedade.objects.get(id=propriedade_id)
    service = SintegraService(propriedade)
    
    return service.gerar_arquivo(periodo_inicio, periodo_fim, uf)

