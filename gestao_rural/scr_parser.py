# -*- coding: utf-8 -*-
"""
Parser para SCR (Sistema de Informações de Crédito Rural) do Banco Central
Extrai dados de dívidas por banco e status automaticamente de PDFs
"""

import re
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import PyPDF2
import pdfplumber
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)

class SCRParser:
    """Parser para extrair dados do SCR do Banco Central"""
    
    def __init__(self):
        self.dados_extraidos = {
            'dividas_por_banco': [],
            'resumo_total': {},
            'data_referencia': None,
            'cnpj_produtor': None,
            'nome_produtor': None
        }
        
        # Padrões regex para identificar informações
        self.padroes = {
            'banco': r'(?i)(banco|sicredi|sicoob|banco do brasil|caixa|bradesco|itau|santander|hsbc|banrisul)',
            'valor': r'R\$\s*([\d.,]+)',
            'data': r'(\d{2}/\d{2}/\d{4})',
            'cnpj': r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
            'status_a_vencer': r'(?i)(a\s+vencer|vencimento|futuro)',
            'status_vencido': r'(?i)(vencido|atrasado|em\s+atraso)',
            'quantidade_contratos': r'(\d+)\s*(?:contrato|operação)',
        }
    
    def extrair_dados_pdf(self, arquivo_pdf: UploadedFile) -> Dict:
        """
        Extrai dados do PDF do SCR
        
        Args:
            arquivo_pdf: Arquivo PDF do SCR
            
        Returns:
            Dict com dados extraídos
        """
        try:
            # Tentar extrair texto usando pdfplumber (mais preciso)
            texto = self._extrair_texto_pdfplumber(arquivo_pdf)
            
            if not texto:
                # Fallback para PyPDF2
                texto = self._extrair_texto_pypdf2(arquivo_pdf)
            
            if not texto:
                raise Exception("Não foi possível extrair texto do PDF")
            
            # Processar o texto extraído
            self._processar_texto(texto)
            
            logger.info(f"Dados extraídos com sucesso: {len(self.dados_extraidos['dividas_por_banco'])} dívidas encontradas")
            
            return self.dados_extraidos
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do PDF: {str(e)}")
            raise Exception(f"Erro ao processar PDF: {str(e)}")
    
    def _extrair_texto_pdfplumber(self, arquivo_pdf: UploadedFile) -> str:
        """Extrai texto usando pdfplumber (mais preciso para tabelas)"""
        try:
            texto_completo = ""
            
            # Resetar posição do arquivo
            arquivo_pdf.seek(0)
            
            with pdfplumber.open(arquivo_pdf) as pdf:
                for pagina_num, pagina in enumerate(pdf.pages):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += f"\n--- PÁGINA {pagina_num + 1} ---\n"
                        texto_completo += texto_pagina
                        
                        # Tentar extrair tabelas também
                        tabelas = pagina.extract_tables()
                        if tabelas:
                            for tabela in tabelas:
                                texto_completo += "\n--- TABELA ---\n"
                                for linha in tabela:
                                    if linha:
                                        texto_completo += " | ".join([str(celula) for celula in linha if celula]) + "\n"
            
            return texto_completo
            
        except Exception as e:
            logger.warning(f"Erro com pdfplumber: {str(e)}")
            return ""
    
    def _extrair_texto_pypdf2(self, arquivo_pdf: UploadedFile) -> str:
        """Fallback: extrai texto usando PyPDF2"""
        try:
            arquivo_pdf.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(arquivo_pdf)
            texto_completo = ""
            
            for pagina_num, pagina in enumerate(pdf_reader.pages):
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += f"\n--- PÁGINA {pagina_num + 1} ---\n"
                    texto_completo += texto_pagina
            
            return texto_completo
            
        except Exception as e:
            logger.warning(f"Erro com PyPDF2: {str(e)}")
            return ""
    
    def _processar_texto(self, texto: str):
        """Processa o texto extraído para identificar dados"""
        linhas = texto.split('\n')
        
        # Identificar informações básicas
        self._extrair_informacoes_basicas(linhas)
        
        # Identificar dívidas por banco
        self._extrair_dividas_por_banco(linhas)
        
        # Calcular resumo total
        self._calcular_resumo_total()
    
    def _extrair_informacoes_basicas(self, linhas: List[str]):
        """Extrai informações básicas do SCR"""
        texto_completo = ' '.join(linhas)
        
        # Extrair CNPJ
        cnpj_match = re.search(self.padroes['cnpj'], texto_completo)
        if cnpj_match:
            self.dados_extraidos['cnpj_produtor'] = cnpj_match.group(1)
        
        # Extrair data de referência
        datas_encontradas = re.findall(self.padroes['data'], texto_completo)
        if datas_encontradas:
            # Usar a data mais recente encontrada
            try:
                data_str = datas_encontradas[-1]
                self.dados_extraidos['data_referencia'] = datetime.strptime(data_str, '%d/%m/%Y').date()
            except ValueError:
                pass
        
        # Extrair nome do produtor (procurar por padrões comuns)
        nome_patterns = [
            r'(?:Nome|Razão Social|Produtor):\s*([A-Za-zÀ-ÿ\s]+)',
            r'([A-Za-zÀ-ÿ\s]+)\s*(?:LTDA|S\.A\.|EIRELI)',
        ]
        
        for pattern in nome_patterns:
            nome_match = re.search(pattern, texto_completo, re.IGNORECASE)
            if nome_match:
                nome = nome_match.group(1).strip()
                if len(nome) > 3:  # Evitar nomes muito curtos
                    self.dados_extraidos['nome_produtor'] = nome
                    break
    
    def _extrair_dividas_por_banco(self, linhas: List[str]):
        """Extrai dívidas organizadas por banco"""
        dividas = []
        
        # Procurar por seções de dívidas
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            
            # Verificar se a linha contém nome de banco
            banco_match = re.search(self.padroes['banco'], linha, re.IGNORECASE)
            
            if banco_match:
                banco_nome = banco_match.group(1).title()
                
                # Procurar valores e status nas próximas linhas
                divida_info = self._extrair_info_divida(linhas, i, banco_nome)
                
                if divida_info:
                    dividas.append(divida_info)
            
            i += 1
        
        self.dados_extraidos['dividas_por_banco'] = dividas
    
    def _extrair_info_divida(self, linhas: List[str], inicio_idx: int, banco_nome: str) -> Optional[Dict]:
        """Extrai informações de uma dívida específica"""
        divida_info = {
            'banco': banco_nome,
            'a_vencer': Decimal('0'),
            'vencido': Decimal('0'),
            'quantidade_contratos': 0,
            'linhas_processadas': []
        }
        
        # Analisar próximas 10 linhas após encontrar o banco
        for i in range(inicio_idx, min(inicio_idx + 10, len(linhas))):
            linha = linhas[i].strip()
            divida_info['linhas_processadas'].append(linha)
            
            # Procurar por valores
            valores = re.findall(self.padroes['valor'], linha)
            
            # Procurar por status
            if re.search(self.padroes['status_a_vencer'], linha, re.IGNORECASE):
                for valor_str in valores:
                    try:
                        valor = self._converter_valor(valor_str)
                        divida_info['a_vencer'] += valor
                    except (ValueError, InvalidOperation):
                        pass
            
            elif re.search(self.padroes['status_vencido'], linha, re.IGNORECASE):
                for valor_str in valores:
                    try:
                        valor = self._converter_valor(valor_str)
                        divida_info['vencido'] += valor
                    except (ValueError, InvalidOperation):
                        pass
            
            # Procurar quantidade de contratos
            contratos_match = re.search(self.padroes['quantidade_contratos'], linha, re.IGNORECASE)
            if contratos_match:
                divida_info['quantidade_contratos'] = int(contratos_match.group(1))
        
        # Se encontrou pelo menos um valor, retorna a dívida
        if divida_info['a_vencer'] > 0 or divida_info['vencido'] > 0:
            return divida_info
        
        return None
    
    def _converter_valor(self, valor_str: str) -> Decimal:
        """Converte string de valor para Decimal"""
        # Remover R$ e espaços
        valor_limpo = re.sub(r'[R$\s]', '', valor_str)
        
        # Verificar se tem vírgula (formato brasileiro)
        if ',' in valor_limpo and '.' in valor_limpo:
            # Formato: 1.234,56
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        elif ',' in valor_limpo:
            # Formato: 1234,56
            valor_limpo = valor_limpo.replace(',', '.')
        
        return Decimal(valor_limpo)
    
    def _calcular_resumo_total(self):
        """Calcula resumo total das dívidas"""
        total_a_vencer = Decimal('0')
        total_vencido = Decimal('0')
        total_contratos = 0
        
        for divida in self.dados_extraidos['dividas_por_banco']:
            total_a_vencer += divida['a_vencer']
            total_vencido += divida['vencido']
            total_contratos += divida['quantidade_contratos']
        
        self.dados_extraidos['resumo_total'] = {
            'total_a_vencer': total_a_vencer,
            'total_vencido': total_vencido,
            'total_geral': total_a_vencer + total_vencido,
            'total_contratos': total_contratos,
            'quantidade_bancos': len(self.dados_extraidos['dividas_por_banco'])
        }
    
    def gerar_relatorio_extracao(self) -> str:
        """Gera relatório da extração realizada"""
        relatorio = []
        relatorio.append("=== RELATÓRIO DE EXTRAÇÃO SCR ===")
        relatorio.append(f"Data de Referência: {self.dados_extraidos.get('data_referencia', 'Não identificada')}")
        relatorio.append(f"CNPJ: {self.dados_extraidos.get('cnpj_produtor', 'Não identificado')}")
        relatorio.append(f"Nome: {self.dados_extraidos.get('nome_produtor', 'Não identificado')}")
        relatorio.append("")
        
        relatorio.append("=== DÍVIDAS POR BANCO ===")
        for divida in self.dados_extraidos['dividas_por_banco']:
            relatorio.append(f"Banco: {divida['banco']}")
            relatorio.append(f"  A Vencer: R$ {divida['a_vencer']:,.2f}")
            relatorio.append(f"  Vencido: R$ {divida['vencido']:,.2f}")
            relatorio.append(f"  Contratos: {divida['quantidade_contratos']}")
            relatorio.append("")
        
        resumo = self.dados_extraidos['resumo_total']
        relatorio.append("=== RESUMO TOTAL ===")
        relatorio.append(f"Total A Vencer: R$ {resumo['total_a_vencer']:,.2f}")
        relatorio.append(f"Total Vencido: R$ {resumo['total_vencido']:,.2f}")
        relatorio.append(f"Total Geral: R$ {resumo['total_geral']:,.2f}")
        relatorio.append(f"Total Contratos: {resumo['total_contratos']}")
        relatorio.append(f"Quantidade Bancos: {resumo['quantidade_bancos']}")
        
        return "\n".join(relatorio)


class SCRProcessor:
    """Processador para salvar dados extraídos do SCR no banco de dados"""
    
    def __init__(self, scr_obj, dados_extraidos: Dict):
        self.scr_obj = scr_obj
        self.dados_extraidos = dados_extraidos
    
    def processar_e_salvar(self) -> Dict:
        """
        Processa os dados extraídos e salva no banco de dados
        
        Returns:
            Dict com estatísticas do processamento
        """
        from .models import DividaBanco, ContratoDivida
        
        estatisticas = {
            'dividas_criadas': 0,
            'contratos_criados': 0,
            'erros': []
        }
        
        try:
            # Atualizar status do SCR
            self.scr_obj.status = 'PROCESSADO'
            self.scr_obj.observacoes = self.gerar_relatorio_extracao()
            self.scr_obj.save()
            
            # Criar registros de dívidas por banco
            for divida_data in self.dados_extraidos['dividas_por_banco']:
                # Criar dívida a vencer se houver valor
                if divida_data['a_vencer'] > 0:
                    divida_a_vencer = DividaBanco.objects.create(
                        scr=self.scr_obj,
                        banco=divida_data['banco'],
                        status_divida='A_VENCER',
                        valor_total=divida_data['a_vencer'],
                        quantidade_contratos=divida_data['quantidade_contratos'] or 1
                    )
                    estatisticas['dividas_criadas'] += 1
                
                # Criar dívida vencida se houver valor
                if divida_data['vencido'] > 0:
                    divida_vencida = DividaBanco.objects.create(
                        scr=self.scr_obj,
                        banco=divida_data['banco'],
                        status_divida='VENCIDO',
                        valor_total=divida_data['vencido'],
                        quantidade_contratos=divida_data['quantidade_contratos'] or 1
                    )
                    estatisticas['dividas_criadas'] += 1
            
            # Atualizar status final
            self.scr_obj.status = 'DISTRIBUIDO'
            self.scr_obj.save()
            
            logger.info(f"SCR processado com sucesso: {estatisticas['dividas_criadas']} dívidas criadas")
            
        except Exception as e:
            logger.error(f"Erro ao processar SCR: {str(e)}")
            estatisticas['erros'].append(str(e))
            self.scr_obj.status = 'ERRO'
            self.scr_obj.observacoes = f"Erro no processamento: {str(e)}"
            self.scr_obj.save()
        
        return estatisticas
    
    def gerar_relatorio_extracao(self) -> str:
        """Gera relatório da extração"""
        parser = SCRParser()
        parser.dados_extraidos = self.dados_extraidos
        return parser.gerar_relatorio_extracao()

