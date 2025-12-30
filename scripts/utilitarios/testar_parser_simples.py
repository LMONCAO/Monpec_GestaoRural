# -*- coding: utf-8 -*-
"""
Script simplificado para testar o parser BND SISBOV sem depender do Django
"""

import os
import sys

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock do UploadedFile do Django
class MockUploadedFile:
    def __init__(self, file_path):
        self.name = os.path.basename(file_path)
        self.file_path = file_path
        self._content = None
    
    def read(self):
        if self._content is None:
            with open(self.file_path, 'rb') as f:
                self._content = f.read()
        return self._content
    
    def seek(self, position):
        # Para este teste, não precisamos implementar seek
        pass

# Importar parser (sem Django)
try:
    # Tentar importar sem Django
    import re
    import logging
    from decimal import Decimal, InvalidOperation
    from datetime import datetime, date
    from typing import Dict, List, Optional
    import PyPDF2
    import pdfplumber
    
    # Copiar a classe do parser (versão simplificada)
    class BNDSisbovParserTeste:
        """Parser simplificado para teste"""
        
        def __init__(self):
            self.animais_extraidos = []
            self.informacoes_propriedade = {
                'nome_propriedade': None,
                'cnpj_cpf': None,
                'inscricao_estadual': None,
                'data_emissao': None,
            }
            
            self.padroes = {
                'codigo_sisbov': r'(BR\d{13}|\d{15})',
                'numero_manejo': r'(\d{6})',
                'numero_brinco': r'(\d{12,15})',
                'data': r'(\d{2}/\d{2}/\d{4})',
                'cnpj_cpf': r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})',
                'peso': r'(\d+[.,]\d+|\d+)\s*(?:kg|KG)',
                'sexo': r'(?i)(macho|fêmea|femea|m|f)',
                'raca': r'(?i)(nelore|angus|brahman|brangus|hereford|simmental|limousin|charolês|charoles|canchim|tabapuã|tabapua|guzerá|guzera|gir|holandês|holandes)',
            }
        
        def extrair_dados_pdf(self, arquivo_pdf):
            try:
                texto = self._extrair_texto_pdfplumber(arquivo_pdf)
                if not texto:
                    texto = self._extrair_texto_pypdf2(arquivo_pdf)
                if not texto:
                    raise Exception("Nao foi possivel extrair texto do PDF")
                self._processar_texto(texto)
                return {
                    'animais': self.animais_extraidos,
                    'informacoes_propriedade': self.informacoes_propriedade,
                    'total_animais': len(self.animais_extraidos)
                }
            except Exception as e:
                raise Exception(f"Erro ao processar PDF: {str(e)}")
        
        def _extrair_texto_pdfplumber(self, arquivo_pdf):
            try:
                texto_completo = ""
                with pdfplumber.open(arquivo_pdf.file_path) as pdf:
                    for pagina_num, pagina in enumerate(pdf.pages):
                        texto_pagina = pagina.extract_text()
                        if texto_pagina:
                            texto_completo += f"\n--- PAGINA {pagina_num + 1} ---\n"
                            texto_completo += texto_pagina
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
                return ""
        
        def _extrair_texto_pypdf2(self, arquivo_pdf):
            try:
                pdf_reader = PyPDF2.PdfReader(arquivo_pdf.file_path)
                texto_completo = ""
                for pagina_num, pagina in enumerate(pdf_reader.pages):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += f"\n--- PAGINA {pagina_num + 1} ---\n"
                        texto_completo += texto_pagina
                return texto_completo
            except Exception as e:
                return ""
        
        def _processar_texto(self, texto):
            linhas = texto.split('\n')
            self._extrair_informacoes_propriedade(linhas)
            self._extrair_animais(linhas, texto)
        
        def _extrair_informacoes_propriedade(self, linhas):
            texto_completo = ' '.join(linhas)
            cnpj_cpf_match = re.search(self.padroes['cnpj_cpf'], texto_completo)
            if cnpj_cpf_match:
                self.informacoes_propriedade['cnpj_cpf'] = cnpj_cpf_match.group(1)
            datas_encontradas = re.findall(self.padroes['data'], texto_completo)
            if datas_encontradas:
                try:
                    data_str = datas_encontradas[0]
                    self.informacoes_propriedade['data_emissao'] = datetime.strptime(data_str, '%d/%m/%Y').date()
                except ValueError:
                    pass
        
        def _extrair_animais(self, linhas, texto_completo):
            animais_encontrados = []
            codigos_sisbov = re.findall(self.padroes['codigo_sisbov'], texto_completo)
            for codigo_sisbov in codigos_sisbov:
                codigo_limpo = re.sub(r'\D', '', codigo_sisbov)
                if len(codigo_limpo) == 13:
                    codigo_sisbov_formatado = f"BR{codigo_limpo}"
                elif len(codigo_limpo) == 15:
                    if codigo_limpo.startswith('BR'):
                        codigo_sisbov_formatado = codigo_sisbov
                    else:
                        codigo_sisbov_formatado = f"BR{codigo_limpo[2:]}"
                else:
                    continue
                animal_info = self._extrair_info_animal(texto_completo, codigo_sisbov_formatado)
                if animal_info:
                    if not any(a.get('codigo_sisbov') == codigo_sisbov_formatado for a in animais_encontrados):
                        animais_encontrados.append(animal_info)
            self.animais_extraidos = animais_encontrados
        
        def _extrair_info_animal(self, texto, codigo_sisbov):
            posicao = texto.find(codigo_sisbov)
            if posicao == -1:
                return None
            contexto = texto[max(0, posicao - 100):posicao + 500]
            animal_info = {
                'codigo_sisbov': codigo_sisbov,
                'numero_manejo': None,
                'numero_brinco': None,
                'raca': None,
                'sexo': None,
                'data_nascimento': None,
                'peso_kg': None,
            }
            manejo_match = re.search(self.padroes['numero_manejo'], contexto)
            if manejo_match:
                animal_info['numero_manejo'] = manejo_match.group(1)
            brinco_match = re.search(self.padroes['numero_brinco'], contexto)
            if brinco_match:
                brinco = brinco_match.group(1)
                if len(brinco) == 12:
                    brinco = '000' + brinco
                animal_info['numero_brinco'] = brinco
            raca_match = re.search(self.padroes['raca'], contexto, re.IGNORECASE)
            if raca_match:
                animal_info['raca'] = raca_match.group(1).title()
            sexo_match = re.search(self.padroes['sexo'], contexto, re.IGNORECASE)
            if sexo_match:
                sexo_str = sexo_match.group(1).upper()
                if sexo_str in ['M', 'MACHO', 'MALE']:
                    animal_info['sexo'] = 'M'
                elif sexo_str in ['F', 'FÊMEA', 'FEMEA', 'FEMALE']:
                    animal_info['sexo'] = 'F'
            data_match = re.search(self.padroes['data'], contexto)
            if data_match:
                try:
                    data_str = data_match.group(1)
                    animal_info['data_nascimento'] = datetime.strptime(data_str, '%d/%m/%Y').date()
                except ValueError:
                    pass
            peso_match = re.search(self.padroes['peso'], contexto)
            if peso_match:
                try:
                    peso_str = peso_match.group(1).replace(',', '.')
                    animal_info['peso_kg'] = Decimal(peso_str)
                except (ValueError, InvalidOperation):
                    pass
            if animal_info['codigo_sisbov']:
                return animal_info
            return None

except ImportError as e:
    print(f"[ERRO] Biblioteca nao encontrada: {e}")
    print("Instale as dependencias: pip install PyPDF2 pdfplumber")
    sys.exit(1)

def testar_parser_pdf(pdf_path):
    """Testa o parser com um arquivo PDF"""
    
    if not os.path.exists(pdf_path):
        print(f"[ERRO] Arquivo nao encontrado: {pdf_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"TESTE DO PARSER BND SISBOV")
    print(f"{'='*60}")
    print(f"\nArquivo: {pdf_path}")
    print(f"Tamanho: {os.path.getsize(pdf_path)} bytes")
    
    try:
        arquivo = MockUploadedFile(pdf_path)
        
        print("\n[1/3] Criando parser...")
        parser = BNDSisbovParserTeste()
        
        print("[2/3] Extraindo dados do PDF...")
        dados_extraidos = parser.extrair_dados_pdf(arquivo)
        
        print("[3/3] Processamento concluido!")
        
        print(f"\n{'='*60}")
        print("RESULTADOS DA EXTRACAO")
        print(f"{'='*60}")
        
        info_prop = dados_extraidos.get('informacoes_propriedade', {})
        print(f"\n[PROPRIEDADE]")
        print(f"  CNPJ/CPF: {info_prop.get('cnpj_cpf', 'N/A')}")
        print(f"  Data Emissao: {info_prop.get('data_emissao', 'N/A')}")
        
        animais = dados_extraidos.get('animais', [])
        total_animais = len(animais)
        
        print(f"\n[ANIMAIS]")
        print(f"  Total extraido: {total_animais}")
        
        if total_animais > 0:
            print(f"\n  Primeiros 5 animais:")
            for i, animal in enumerate(animais[:5], 1):
                print(f"    {i}. SISBOV: {animal.get('codigo_sisbov', 'N/A')}")
                print(f"       Brinco: {animal.get('numero_brinco', 'N/A')}")
                print(f"       Manejo: {animal.get('numero_manejo', 'N/A')}")
                print(f"       Raca: {animal.get('raca', 'N/A')}")
                print(f"       Sexo: {animal.get('sexo', 'N/A')}")
                print(f"       Nascimento: {animal.get('data_nascimento', 'N/A')}")
                print(f"       Peso: {animal.get('peso_kg', 'N/A')} kg")
                print()
            
            if total_animais > 5:
                print(f"  ... e mais {total_animais - 5} animais")
        
        print(f"\n{'='*60}")
        print("[SUCESSO] Teste concluido!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Falha ao processar PDF:")
        print(f"  {str(e)}")
        import traceback
        print(f"\nTraceback completo:")
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    pdf_teste = 'teste_bnd_sisbov.pdf'
    if len(sys.argv) > 1:
        pdf_teste = sys.argv[1]
    
    sucesso = testar_parser_pdf(pdf_teste)
    
    if sucesso:
        print("\n[DICA] Agora voce pode testar a importacao no sistema Django!")
    else:
        print("\n[ERRO] O teste falhou. Verifique o arquivo PDF.")
        sys.exit(1)


