# -*- coding: utf-8 -*-
"""
Parser para BND (Base Nacional de Dados) SISBOV
Extrai dados de animais de PDFs exportados do Portal SISBOV
"""

import re
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class BNDSisbovParser:
    """Parser para extrair dados de animais do PDF BND SISBOV"""
    
    def __init__(self):
        self.animais_extraidos = []
        self.informacoes_propriedade = {
            'nome_propriedade': None,
            'cnpj_cpf': None,
            'inscricao_estadual': None,
            'data_emissao': None,
        }
        
        # Padrões regex para identificar informações
        self.padroes = {
            'codigo_sisbov': r'(BR\d{13}|\d{15})',  # Código SISBOV: BR + 13 dígitos ou 15 dígitos
            'numero_manejo': r'(\d{6})',  # Número de manejo: 6 dígitos
            'numero_brinco': r'(\d{12,15})',  # Número do brinco: 12-15 dígitos
            'data': r'(\d{2}/\d{2}/\d{4})',  # Data formato DD/MM/YYYY
            'cnpj_cpf': r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})',  # CNPJ ou CPF
            'peso': r'(\d+[.,]\d+|\d+)\s*(?:kg|KG)',  # Peso em kg
            'sexo': r'(?i)(macho|fêmea|femea|m|f|macho|fêmea)',  # Sexo do animal
            'raca': r'(?i)(nelore|angus|brahman|brangus|hereford|simmental|limousin|charolês|charoles|canchim|tabapuã|tabapua|guzerá|guzera|gir|holandês|holandes)',  # Raças comuns
        }
    
    def extrair_dados_pdf(self, arquivo_pdf: UploadedFile) -> Dict:
        """
        Extrai dados do PDF BND SISBOV
        
        Args:
            arquivo_pdf: Arquivo PDF do BND SISBOV
            
        Returns:
            Dict com animais extraídos e informações da propriedade
        """
        try:
            # Estratégia 1: Tentar extrair diretamente de tabelas (mais preciso)
            animais_tabela = self._extrair_animais_de_tabela_pdfplumber(arquivo_pdf)
            
            if animais_tabela:
                self.animais_extraidos = animais_tabela
                # Também extrair informações da propriedade do texto
                texto = self._extrair_texto_pdfplumber(arquivo_pdf)
                if texto:
                    linhas = texto.split('\n')
                    self._extrair_informacoes_propriedade(linhas)
                logger.info(f"Dados extraídos de tabelas: {len(self.animais_extraidos)} animais encontrados")
            else:
                # Estratégia 2: Tentar extrair texto usando pdfplumber
                texto = self._extrair_texto_pdfplumber(arquivo_pdf)
                
                if not texto:
                    # Fallback para PyPDF2
                    texto = self._extrair_texto_pypdf2(arquivo_pdf)
                
                if not texto:
                    raise Exception("Não foi possível extrair texto do PDF")
                
                # Processar o texto extraído
                self._processar_texto(texto)
                
                logger.info(f"Dados extraídos do texto: {len(self.animais_extraidos)} animais encontrados")
            
            return {
                'animais': self.animais_extraidos,
                'informacoes_propriedade': self.informacoes_propriedade,
                'total_animais': len(self.animais_extraidos)
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do PDF: {str(e)}")
            raise Exception(f"Erro ao processar PDF BND SISBOV: {str(e)}")
    
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
                        
                        # Tentar extrair tabelas também (importante para dados estruturados)
                        tabelas = pagina.extract_tables()
                        if tabelas:
                            texto_completo += "\n--- TABELAS ---\n"
                            for idx_tabela, tabela in enumerate(tabelas):
                                texto_completo += f"\n--- TABELA {idx_tabela + 1} ---\n"
                                for linha in tabela:
                                    if linha:
                                        linha_texto = " | ".join([str(celula) if celula else "" for celula in linha])
                                        texto_completo += linha_texto + "\n"
            
            return texto_completo
            
        except Exception as e:
            logger.warning(f"Erro com pdfplumber: {str(e)}")
            return ""
    
    def _extrair_animais_de_tabela_pdfplumber(self, arquivo_pdf: UploadedFile) -> List[Dict]:
        """Extrai animais diretamente de tabelas usando pdfplumber"""
        animais = []
        codigos_vistos = set()  # Para evitar duplicatas
        
        try:
            arquivo_pdf.seek(0)
            
            # Primeiro, tentar extrair de tabelas estruturadas
            with pdfplumber.open(arquivo_pdf) as pdf:
                indices_globais = None  # Reutilizar índices entre páginas
                
                for pagina_num, pagina in enumerate(pdf.pages):
                    tabelas = pagina.extract_tables()
                    
                    for tabela in tabelas:
                        if not tabela or len(tabela) < 2:
                            continue
                        
                        # Procurar cabeçalho (apenas na primeira tabela ou se não tiver índices)
                        if indices_globais is None:
                            cabecalho = None
                            linha_cabecalho_idx = 0
                            
                            for idx, linha in enumerate(tabela):
                                if not linha:
                                    continue
                                
                                linha_str = ' '.join([str(c) if c else '' for c in linha]).lower()
                                
                                # Verificar se é cabeçalho
                                if any(palavra in linha_str for palavra in ['sisbov', 'código', 'codigo', 'brinco', 'raça', 'raca', 'sexo', 'nascimento']):
                                    cabecalho = linha
                                    linha_cabecalho_idx = idx
                                    break
                            
                            if cabecalho:
                                # Mapear índices das colunas
                                indices_globais = {}
                                for idx, coluna in enumerate(cabecalho):
                                    if not coluna:
                                        continue
                                    
                                    coluna_lower = str(coluna).lower()
                                    
                                    if 'sisbov' in coluna_lower or 'código' in coluna_lower or 'codigo' in coluna_lower:
                                        indices_globais['sisbov'] = idx
                                    elif 'manejo' in coluna_lower:
                                        indices_globais['manejo'] = idx
                                    elif 'brinco' in coluna_lower:
                                        indices_globais['brinco'] = idx
                                    elif 'raça' in coluna_lower or 'raca' in coluna_lower:
                                        indices_globais['raca'] = idx
                                    elif 'sexo' in coluna_lower:
                                        indices_globais['sexo'] = idx
                                    elif 'nasc' in coluna_lower or 'data' in coluna_lower:
                                        indices_globais['nascimento'] = idx
                                    elif 'peso' in coluna_lower:
                                        indices_globais['peso'] = idx
                            
                            if indices_globais:
                                linha_cabecalho_idx = 0
                            else:
                                continue
                        
                        # Processar todas as linhas (pode ser continuação de tabela de outra página)
                        inicio_linhas = linha_cabecalho_idx + 1 if indices_globais else 0
                        for linha_idx in range(inicio_linhas, len(tabela)):
                            linha = tabela[linha_idx]
                            if not linha:
                                continue
                            
                            animal_info = {}
                            
                            # Extrair código SISBOV
                            codigo_encontrado = None
                            if 'sisbov' in indices_globais and indices_globais['sisbov'] < len(linha):
                                codigo = str(linha[indices_globais['sisbov']]) if linha[indices_globais['sisbov']] else ''
                                codigo_limpo = re.sub(r'\D', '', codigo)
                                
                                if len(codigo_limpo) == 13:
                                    codigo_encontrado = f"BR{codigo_limpo}"
                                elif len(codigo_limpo) == 15:
                                    if codigo_limpo.startswith('BR'):
                                        codigo_encontrado = codigo
                                    else:
                                        codigo_encontrado = f"BR{codigo_limpo[2:]}"
                            
                            # Se não encontrou na coluna, buscar na linha inteira
                            if not codigo_encontrado:
                                linha_texto = ' '.join([str(c) if c else '' for c in linha])
                                codigo_match = re.search(self.padroes['codigo_sisbov'], linha_texto)
                                if codigo_match:
                                    codigo = codigo_match.group(1)
                                    codigo_limpo = re.sub(r'\D', '', codigo)
                                    if len(codigo_limpo) == 13:
                                        codigo_encontrado = f"BR{codigo_limpo}"
                                    elif len(codigo_limpo) == 15:
                                        codigo_encontrado = f"BR{codigo_limpo[2:]}" if not codigo_limpo.startswith('BR') else codigo
                            
                            if not codigo_encontrado:
                                continue  # Sem código SISBOV, pular linha
                            
                            # Evitar duplicatas
                            if codigo_encontrado in codigos_vistos:
                                continue
                            codigos_vistos.add(codigo_encontrado)
                            animal_info['codigo_sisbov'] = codigo_encontrado
                            
                            # Extrair outros campos usando índices
                            if indices_globais:
                                if 'manejo' in indices_globais and indices_globais['manejo'] < len(linha):
                                    animal_info['numero_manejo'] = str(linha[indices_globais['manejo']]) if linha[indices_globais['manejo']] else None
                                
                                if 'brinco' in indices_globais and indices_globais['brinco'] < len(linha):
                                    animal_info['numero_brinco'] = str(linha[indices_globais['brinco']]) if linha[indices_globais['brinco']] else None
                                
                                if 'raca' in indices_globais and indices_globais['raca'] < len(linha):
                                    animal_info['raca'] = str(linha[indices_globais['raca']]) if linha[indices_globais['raca']] else None
                                
                                if 'sexo' in indices_globais and indices_globais['sexo'] < len(linha):
                                    sexo_str = str(linha[indices_globais['sexo']]).strip().upper() if linha[indices_globais['sexo']] else ''
                                    if sexo_str in ['M', 'MACHO', 'MALE']:
                                        animal_info['sexo'] = 'M'
                                    elif sexo_str in ['F', 'FÊMEA', 'FEMEA', 'FEMALE']:
                                        animal_info['sexo'] = 'F'
                                
                                if 'nascimento' in indices_globais and indices_globais['nascimento'] < len(linha):
                                    data_str = str(linha[indices_globais['nascimento']]) if linha[indices_globais['nascimento']] else ''
                                    if data_str:
                                        data_match = re.search(self.padroes['data'], data_str)
                                        if data_match:
                                            try:
                                                animal_info['data_nascimento'] = datetime.strptime(data_match.group(1), '%d/%m/%Y').date()
                                            except ValueError:
                                                pass
                                
                                if 'peso' in indices_globais and indices_globais['peso'] < len(linha):
                                    peso_str = str(linha[indices_globais['peso']]) if linha[indices_globais['peso']] else ''
                                    if peso_str:
                                        peso_match = re.search(r'(\d+[.,]?\d*)', peso_str.replace(',', '.'))
                                        if peso_match:
                                            try:
                                                animal_info['peso_kg'] = Decimal(peso_match.group(1))
                                            except (ValueError, InvalidOperation):
                                                pass
                            
                            # Adicionar animal
                            animais.append(animal_info)
            
            # Se extraiu poucos animais de tabelas, tentar método alternativo mais agressivo
            if len(animais) < 50:
                logger.info(f"Apenas {len(animais)} animais extraídos de tabelas, tentando método alternativo...")
                animais_alternativos = self._extrair_animais_agressivo(arquivo_pdf)
                
                # Adicionar apenas animais não encontrados
                for animal in animais_alternativos:
                    codigo = animal.get('codigo_sisbov')
                    if codigo and codigo not in codigos_vistos:
                        animais.append(animal)
                        codigos_vistos.add(codigo)
            
            logger.info(f"Extraídos {len(animais)} animais de tabelas PDF")
            return animais
            
        except Exception as e:
            logger.warning(f"Erro ao extrair animais de tabelas: {str(e)}")
            return []
    
    def _extrair_animais_agressivo(self, arquivo_pdf: UploadedFile) -> List[Dict]:
        """Método agressivo: busca todos os códigos SISBOV no texto completo"""
        animais = []
        
        try:
            arquivo_pdf.seek(0)
            texto_completo = ""
            
            # Extrair todo o texto de todas as páginas
            with pdfplumber.open(arquivo_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
            
            # Buscar todos os códigos SISBOV no texto
            codigos_sisbov = re.findall(self.padroes['codigo_sisbov'], texto_completo)
            
            # Remover duplicatas mantendo ordem
            codigos_unicos = []
            codigos_vistos = set()
            for codigo in codigos_sisbov:
                codigo_limpo = re.sub(r'\D', '', codigo)
                if codigo_limpo not in codigos_vistos and (len(codigo_limpo) == 13 or len(codigo_limpo) == 15):
                    codigos_vistos.add(codigo_limpo)
                    codigos_unicos.append(codigo)
            
            # Para cada código, extrair informações do contexto
            for codigo in codigos_unicos:
                # Normalizar código
                codigo_limpo = re.sub(r'\D', '', codigo)
                if len(codigo_limpo) == 13:
                    codigo_formatado = f"BR{codigo_limpo}"
                elif len(codigo_limpo) == 15:
                    codigo_formatado = f"BR{codigo_limpo[2:]}" if not codigo_limpo.startswith('BR') else codigo
                else:
                    continue
                
                animal_info = self._extrair_info_animal(texto_completo, codigo_formatado)
                if animal_info:
                    animais.append(animal_info)
            
            logger.info(f"Método agressivo encontrou {len(animais)} animais")
            return animais
            
        except Exception as e:
            logger.warning(f"Erro no método agressivo: {str(e)}")
            return []
    
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
        """Processa o texto extraído para identificar animais e informações"""
        linhas = texto.split('\n')
        
        # Identificar informações da propriedade
        self._extrair_informacoes_propriedade(linhas)
        
        # Identificar animais (pode estar em tabela ou texto livre)
        self._extrair_animais(linhas, texto)
    
    def _extrair_informacoes_propriedade(self, linhas: List[str]):
        """Extrai informações da propriedade do PDF"""
        texto_completo = ' '.join(linhas)
        
        # Extrair CNPJ/CPF
        cnpj_cpf_match = re.search(self.padroes['cnpj_cpf'], texto_completo)
        if cnpj_cpf_match:
            self.informacoes_propriedade['cnpj_cpf'] = cnpj_cpf_match.group(1)
        
        # Extrair data de emissão
        datas_encontradas = re.findall(self.padroes['data'], texto_completo)
        if datas_encontradas:
            try:
                # Usar a primeira data encontrada (geralmente é a data de emissão)
                data_str = datas_encontradas[0]
                self.informacoes_propriedade['data_emissao'] = datetime.strptime(data_str, '%d/%m/%Y').date()
            except ValueError:
                pass
        
        # Extrair nome da propriedade (procurar por padrões comuns)
        nome_patterns = [
            r'(?:Propriedade|Estabelecimento|Fazenda|Nome):\s*([A-Za-zÀ-ÿ\s]+)',
            r'([A-Za-zÀ-ÿ\s]+)\s*(?:LTDA|S\.A\.|EIRELI|Fazenda)',
        ]
        
        for pattern in nome_patterns:
            nome_match = re.search(pattern, texto_completo, re.IGNORECASE)
            if nome_match:
                nome = nome_match.group(1).strip()
                if len(nome) > 3:  # Evitar nomes muito curtos
                    self.informacoes_propriedade['nome_propriedade'] = nome
                    break
    
    def _extrair_animais(self, linhas: List[str], texto_completo: str):
        """Extrai dados dos animais do PDF"""
        animais_encontrados = []
        
        # Estratégia 1: Tentar extrair de tabelas estruturadas primeiro (mais confiável)
        # Isso será chamado antes, mas precisamos do arquivo original
        # Por enquanto, vamos processar o texto
        
        # Estratégia 2: Procurar por códigos SISBOV no texto
        codigos_sisbov = re.findall(self.padroes['codigo_sisbov'], texto_completo)
        
        # Remover duplicatas mantendo ordem
        codigos_unicos = []
        codigos_vistos = set()
        for codigo in codigos_sisbov:
            codigo_limpo = re.sub(r'\D', '', codigo)
            if codigo_limpo not in codigos_vistos:
                codigos_vistos.add(codigo_limpo)
                codigos_unicos.append(codigo)
        
        for codigo_sisbov in codigos_unicos:
            # Normalizar código SISBOV (remover espaços, garantir formato BR + 13 dígitos)
            codigo_limpo = re.sub(r'\D', '', codigo_sisbov)
            if len(codigo_limpo) == 13:
                codigo_sisbov_formatado = f"BR{codigo_limpo}"
            elif len(codigo_limpo) == 15 and codigo_limpo.startswith('BR'):
                codigo_sisbov_formatado = codigo_sisbov
            elif len(codigo_limpo) == 15:
                codigo_sisbov_formatado = f"BR{codigo_limpo[2:]}"
            else:
                continue  # Código inválido
            
            # Procurar informações do animal próximo ao código SISBOV
            animal_info = self._extrair_info_animal(texto_completo, codigo_sisbov_formatado)
            
            if animal_info:
                # Verificar se já não foi adicionado (evitar duplicatas)
                if not any(a.get('codigo_sisbov') == codigo_sisbov_formatado for a in animais_encontrados):
                    animais_encontrados.append(animal_info)
        
        # Estratégia 3: Processar linhas sequencialmente procurando por padrões de tabela
        if len(animais_encontrados) < 10:  # Se encontrou poucos animais, tentar método alternativo
            animais_tabela = self._processar_linhas_como_tabela(linhas)
            # Adicionar apenas animais que não foram encontrados antes
            for animal in animais_tabela:
                codigo = animal.get('codigo_sisbov')
                if codigo and not any(a.get('codigo_sisbov') == codigo for a in animais_encontrados):
                    animais_encontrados.append(animal)
        
        self.animais_extraidos = animais_encontrados
    
    def _extrair_info_animal(self, texto: str, codigo_sisbov: str) -> Optional[Dict]:
        """Extrai informações de um animal específico baseado no código SISBOV"""
        # Encontrar posição do código SISBOV no texto
        posicao = texto.find(codigo_sisbov)
        if posicao == -1:
            return None
        
        # Extrair contexto ao redor do código (próximos 500 caracteres)
        contexto = texto[max(0, posicao - 100):posicao + 500]
        
        animal_info = {
            'codigo_sisbov': codigo_sisbov,
            'numero_manejo': None,
            'numero_brinco': None,
            'raca': None,
            'sexo': None,
            'data_nascimento': None,
            'peso_kg': None,
            'categoria': None,
        }
        
        # Extrair número de manejo (6 dígitos, geralmente próximo ao SISBOV)
        manejo_match = re.search(self.padroes['numero_manejo'], contexto)
        if manejo_match:
            animal_info['numero_manejo'] = manejo_match.group(1)
        
        # Extrair número do brinco
        brinco_match = re.search(self.padroes['numero_brinco'], contexto)
        if brinco_match:
            brinco = brinco_match.group(1)
            # Normalizar para 15 dígitos se necessário
            if len(brinco) == 12:
                brinco = '000' + brinco
            animal_info['numero_brinco'] = brinco
        
        # Extrair raça
        raca_match = re.search(self.padroes['raca'], contexto, re.IGNORECASE)
        if raca_match:
            animal_info['raca'] = raca_match.group(1).title()
        
        # Extrair sexo
        sexo_match = re.search(self.padroes['sexo'], contexto, re.IGNORECASE)
        if sexo_match:
            sexo_str = sexo_match.group(1).upper()
            if sexo_str in ['M', 'MACHO', 'MALE']:
                animal_info['sexo'] = 'M'
            elif sexo_str in ['F', 'FÊMEA', 'FEMEA', 'FEMALE']:
                animal_info['sexo'] = 'F'
        
        # Extrair data de nascimento
        data_match = re.search(self.padroes['data'], contexto)
        if data_match:
            try:
                data_str = data_match.group(1)
                animal_info['data_nascimento'] = datetime.strptime(data_str, '%d/%m/%Y').date()
            except ValueError:
                pass
        
        # Extrair peso
        peso_match = re.search(self.padroes['peso'], contexto)
        if peso_match:
            try:
                peso_str = peso_match.group(1).replace(',', '.')
                animal_info['peso_kg'] = Decimal(peso_str)
            except (ValueError, InvalidOperation):
                pass
        
        # Se encontrou pelo menos o código SISBOV, retorna o animal
        if animal_info['codigo_sisbov']:
            return animal_info
        
        return None
    
    def _processar_linhas_como_tabela(self, linhas: List[str]) -> List[Dict]:
        """Processa linhas como se fossem uma tabela estruturada"""
        animais = []
        
        # Procurar por cabeçalho de tabela
        cabecalho_encontrado = False
        indices_colunas = {}
        
        for i, linha in enumerate(linhas):
            linha_lower = linha.lower()
            
            # Detectar cabeçalho
            if not cabecalho_encontrado:
                if any(palavra in linha_lower for palavra in ['sisbov', 'brinco', 'código', 'codigo', 'animal']):
                    # Identificar colunas
                    if 'sisbov' in linha_lower:
                        indices_colunas['sisbov'] = linha_lower.find('sisbov')
                    if 'brinco' in linha_lower:
                        indices_colunas['brinco'] = linha_lower.find('brinco')
                    if 'raça' in linha_lower or 'raca' in linha_lower:
                        indices_colunas['raca'] = linha_lower.find('raça') if 'raça' in linha_lower else linha_lower.find('raca')
                    if 'sexo' in linha_lower:
                        indices_colunas['sexo'] = linha_lower.find('sexo')
                    if 'nascimento' in linha_lower:
                        indices_colunas['nascimento'] = linha_lower.find('nascimento')
                    
                    cabecalho_encontrado = True
                    continue
            
            # Processar linhas de dados após encontrar cabeçalho
            if cabecalho_encontrado:
                # Verificar se a linha contém código SISBOV
                codigo_match = re.search(self.padroes['codigo_sisbov'], linha)
                if codigo_match:
                    animal_info = self._extrair_animal_da_linha(linha, indices_colunas)
                    if animal_info:
                        animais.append(animal_info)
        
        return animais
    
    def _extrair_animal_da_linha(self, linha: str, indices_colunas: Dict) -> Optional[Dict]:
        """Extrai informações de um animal de uma linha de tabela"""
        animal_info = {
            'codigo_sisbov': None,
            'numero_manejo': None,
            'numero_brinco': None,
            'raca': None,
            'sexo': None,
            'data_nascimento': None,
            'peso_kg': None,
        }
        
        # Extrair código SISBOV
        codigo_match = re.search(self.padroes['codigo_sisbov'], linha)
        if codigo_match:
            codigo = codigo_match.group(1)
            codigo_limpo = re.sub(r'\D', '', codigo)
            if len(codigo_limpo) == 13:
                animal_info['codigo_sisbov'] = f"BR{codigo_limpo}"
            elif len(codigo_limpo) == 15:
                if codigo_limpo.startswith('BR'):
                    animal_info['codigo_sisbov'] = codigo
                else:
                    animal_info['codigo_sisbov'] = f"BR{codigo_limpo[2:]}"
        
        if not animal_info['codigo_sisbov']:
            return None
        
        # Extrair outros campos usando índices de colunas se disponíveis
        # Ou usar regex como fallback
        
        # Número de manejo
        manejo_match = re.search(self.padroes['numero_manejo'], linha)
        if manejo_match:
            animal_info['numero_manejo'] = manejo_match.group(1)
        
        # Número do brinco
        brinco_match = re.search(self.padroes['numero_brinco'], linha)
        if brinco_match:
            brinco = brinco_match.group(1)
            if len(brinco) == 12:
                brinco = '000' + brinco
            animal_info['numero_brinco'] = brinco
        
        # Raça
        raca_match = re.search(self.padroes['raca'], linha, re.IGNORECASE)
        if raca_match:
            animal_info['raca'] = raca_match.group(1).title()
        
        # Sexo
        sexo_match = re.search(self.padroes['sexo'], linha, re.IGNORECASE)
        if sexo_match:
            sexo_str = sexo_match.group(1).upper()
            if sexo_str in ['M', 'MACHO', 'MALE']:
                animal_info['sexo'] = 'M'
            elif sexo_str in ['F', 'FÊMEA', 'FEMEA', 'FEMALE']:
                animal_info['sexo'] = 'F'
        
        # Data de nascimento
        data_match = re.search(self.padroes['data'], linha)
        if data_match:
            try:
                data_str = data_match.group(1)
                animal_info['data_nascimento'] = datetime.strptime(data_str, '%d/%m/%Y').date()
            except ValueError:
                pass
        
        # Peso
        peso_match = re.search(self.padroes['peso'], linha)
        if peso_match:
            try:
                peso_str = peso_match.group(1).replace(',', '.')
                animal_info['peso_kg'] = Decimal(peso_str)
            except (ValueError, InvalidOperation):
                pass
        
        return animal_info
    
    def gerar_relatorio_extracao(self) -> str:
        """Gera relatório da extração realizada"""
        relatorio = []
        relatorio.append("=== RELATÓRIO DE EXTRAÇÃO BND SISBOV ===")
        relatorio.append(f"Data de Emissão: {self.informacoes_propriedade.get('data_emissao', 'Não identificada')}")
        relatorio.append(f"CNPJ/CPF: {self.informacoes_propriedade.get('cnpj_cpf', 'Não identificado')}")
        relatorio.append(f"Propriedade: {self.informacoes_propriedade.get('nome_propriedade', 'Não identificada')}")
        relatorio.append("")
        relatorio.append(f"Total de Animais Extraídos: {len(self.animais_extraidos)}")
        relatorio.append("")
        
        if self.animais_extraidos:
            relatorio.append("=== ANIMAIS EXTRAÍDOS ===")
            for idx, animal in enumerate(self.animais_extraidos[:10], 1):  # Mostrar apenas os 10 primeiros
                relatorio.append(f"{idx}. SISBOV: {animal.get('codigo_sisbov', 'N/A')}")
                relatorio.append(f"   Brinco: {animal.get('numero_brinco', 'N/A')}")
                relatorio.append(f"   Raça: {animal.get('raca', 'N/A')}")
                relatorio.append(f"   Sexo: {animal.get('sexo', 'N/A')}")
                relatorio.append("")
            
            if len(self.animais_extraidos) > 10:
                relatorio.append(f"... e mais {len(self.animais_extraidos) - 10} animais")
        
        return "\n".join(relatorio)


