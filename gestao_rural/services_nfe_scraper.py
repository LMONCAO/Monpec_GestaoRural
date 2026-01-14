# -*- coding: utf-8 -*-
"""
Serviço de Web Scraping para Portal SEFAZ-MS
Consulta automática de NF-e recebidas via scraping
"""

import requests
import logging
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class SefazScraper:
    """
    Scraper para portal SEFAZ-MS
    ATENÇÃO: Uso apenas para fins educacionais
    """

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.sefaz.ms.gov.br"
        self.login_url = f"{self.base_url}/login"
        self.consulta_url = f"{self.base_url}/nfe/consulta"

    def login_com_certificado(self, certificado_path, senha):
        """
        Login usando certificado digital
        """
        try:
            # Configurar sessão com certificado
            self.session.cert = (certificado_path, senha)
            self.session.verify = True

            # Fazer login
            response = self.session.post(self.login_url, data={})
            response.raise_for_status()

            # Verificar se login foi bem-sucedido
            if "Bem-vindo" in response.text:
                logger.info("Login com certificado realizado com sucesso")
                return True
            else:
                logger.error("Falha no login com certificado")
                return False

        except Exception as e:
            logger.error(f"Erro no login com certificado: {e}")
            return False

    def consultar_nfe_recebidas(self, cpf_cnpj, data_inicio, data_fim, limite=50):
        """
        Consultar NF-e recebidas via scraping
        """
        try:
            # Preparar parâmetros da consulta
            params = {
                'tipo': 'recebidas',
                'cpf_cnpj': cpf_cnpj,
                'data_inicio': data_inicio.strftime('%d/%m/%Y'),
                'data_fim': data_fim.strftime('%d/%m/%Y'),
                'limite': limite
            }

            # Fazer consulta
            response = self.session.get(self.consulta_url, params=params)
            response.raise_for_status()

            # Parse do HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extrair dados das NF-e
            notas = []
            tabela_notas = soup.find('table', {'id': 'tabela-notas'})

            if tabela_notas:
                linhas = tabela_notas.find_all('tr')[1:]  # Pular cabeçalho

                for linha in linhas[:limite]:
                    colunas = linha.find_all('td')
                    if len(colunas) >= 6:
                        nota = {
                            'numero': colunas[0].text.strip(),
                            'serie': colunas[1].text.strip(),
                            'chave_acesso': colunas[2].text.strip(),
                            'data_emissao': colunas[3].text.strip(),
                            'fornecedor': colunas[4].text.strip(),
                            'valor': colunas[5].text.strip(),
                            'xml_url': colunas[6].find('a')['href'] if colunas[6].find('a') else None
                        }
                        notas.append(nota)

            return {
                'sucesso': True,
                'notas': notas,
                'total_encontrado': len(notas)
            }

        except Exception as e:
            logger.error(f"Erro na consulta de NF-e: {e}")
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def baixar_xml(self, xml_url):
        """
        Baixar XML de uma NF-e específica
        """
        try:
            response = self.session.get(xml_url)
            response.raise_for_status()

            return {
                'sucesso': True,
                'xml_content': response.text
            }

        except Exception as e:
            logger.error(f"Erro ao baixar XML: {e}")
            return {
                'sucesso': False,
                'erro': str(e)
            }


# Função principal para uso
def consultar_nfe_via_scraper(cpf_cnpj, data_inicio, data_fim, certificado_path, senha_certificado, limite=50):
    """
    Função principal para consultar NF-e via scraper
    """
    scraper = SefazScraper()

    # Fazer login
    if not scraper.login_com_certificado(certificado_path, senha_certificado):
        return {
            'sucesso': False,
            'erro': 'Falha no login com certificado'
        }

    # Consultar notas
    return scraper.consultar_nfe_recebidas(cpf_cnpj, data_inicio, data_fim, limite)


# Exemplo de uso:
"""
resultado = consultar_nfe_via_scraper(
    cpf_cnpj='12345678901234',
    data_inicio=date.today() - timedelta(days=30),
    data_fim=date.today(),
    certificado_path='/caminho/para/certificado.p12',
    senha_certificado='senha_do_certificado',
    limite=100
)

if resultado['sucesso']:
    print(f"Encontradas {resultado['total_encontrado']} notas")
    for nota in resultado['notas']:
        print(f"Nota: {nota['numero']}/{nota['serie']} - R$ {nota['valor']}")
"""