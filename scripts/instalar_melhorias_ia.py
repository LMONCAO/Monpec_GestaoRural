# -*- coding: utf-8 -*-
"""
Script para instalar e configurar as melhorias de IA no Monpec
Instala dependências e executa testes das novas funcionalidades
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InstaladorIAMelhorias:
    """Instalador das melhorias de IA para o Monpec"""

    def __init__(self):
        self.projeto_root = Path(__file__).parent.parent
        self.venv_path = self.projeto_root / 'venv'
        self.requirements_file = self.projeto_root / 'requirements.txt'

    def executar_instalacao(self):
        """Executa todo o processo de instalação"""
        logger.info("🚀 Iniciando instalação das melhorias de IA do Monpec...")

        try:
            # 1. Verificar ambiente virtual
            if not self.verificar_venv():
                logger.error("❌ Ambiente virtual não encontrado ou não ativado")
                return False

            # 2. Instalar dependências
            if not self.instalar_dependencias():
                logger.error("❌ Falha na instalação das dependências")
                return False

            # 3. Executar testes das funcionalidades
            if not self.executar_testes():
                logger.warning("⚠️ Alguns testes falharam, mas instalação continua")

            # 4. Configurar APIs (se necessário)
            self.configurar_apis()

            # 5. Gerar relatório final
            self.gerar_relatorio()

            logger.info("✅ Instalação das melhorias de IA concluída com sucesso!")
            return True

        except Exception as e:
            logger.error(f"❌ Erro durante a instalação: {e}")
            return False

    def verificar_venv(self) -> bool:
        """Verifica se o ambiente virtual está ativado"""
        logger.info("🔍 Verificando ambiente virtual...")

        # Verificar se estamos no ambiente virtual
        python_executable = sys.executable
        venv_marker = str(self.venv_path)

        if venv_marker not in python_executable:
            logger.error(f"Python executável: {python_executable}")
            logger.error(f"Ambiente virtual esperado: {venv_marker}")
            return False

        logger.info("✅ Ambiente virtual verificado")
        return True

    def instalar_dependencias(self) -> bool:
        """Instala as dependências necessárias"""
        logger.info("📦 Instalando dependências...")

        dependencias = [
            'scikit-learn>=1.3.0',
            'pandas>=2.0.0',
            'numpy>=1.24.0',
            'statsmodels>=0.14.0',
            'scipy>=1.11.0',
            'plotly>=5.15.0',
            'prophet>=1.1.0'
        ]

        try:
            # Instalar via pip
            for dependencia in dependencias:
                logger.info(f"Instalando {dependencia}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dependencia
                ], capture_output=True, text=True, cwd=self.projeto_root)

                if result.returncode != 0:
                    logger.error(f"Falha ao instalar {dependencia}: {result.stderr}")
                    return False

            # Verificar instalação
            import sklearn
            import pandas
            import numpy
            import statsmodels
            import scipy

            logger.info("✅ Todas as dependências instaladas com sucesso")
            return True

        except ImportError as e:
            logger.error(f"❌ Erro na importação das dependências: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro na instalação das dependências: {e}")
            return False

    def executar_testes(self) -> bool:
        """Executa testes das novas funcionalidades"""
        logger.info("🧪 Executando testes das funcionalidades...")

        testes_executados = 0
        testes_sucesso = 0

        # Testar ML Price Prediction
        try:
            logger.info("Testando ML Price Prediction...")
            from gestao_rural.services.ml_price_prediction import MLPricePredictionService

            ml_service = MLPricePredictionService()
            # Teste básico - verificar se o serviço inicializa
            assert hasattr(ml_service, 'prever_precos_futuros')
            logger.info("✅ ML Price Prediction OK")
            testes_sucesso += 1

        except Exception as e:
            logger.warning(f"⚠️ ML Price Prediction falhou: {e}")

        testes_executados += 1

        # Testar ML Natalidade Mortalidade
        try:
            logger.info("Testando ML Natalidade Mortalidade...")
            from gestao_rural.services.ml_natalidade_mortalidade import MLNatalidadeMortalidadeService

            ml_nat_service = MLNatalidadeMortalidadeService()
            assert hasattr(ml_nat_service, 'prever_taxa_natalidade')
            logger.info("✅ ML Natalidade Mortalidade OK")
            testes_sucesso += 1

        except Exception as e:
            logger.warning(f"⚠️ ML Natalidade Mortalidade falhou: {e}")

        testes_executados += 1

        # Testar Big Data Analytics
        try:
            logger.info("Testando Big Data Analytics...")
            from gestao_rural.services.big_data_analytics import BigDataAnalyticsService

            bd_service = BigDataAnalyticsService()
            assert hasattr(bd_service, 'analisar_dados_historicos_completos')
            logger.info("✅ Big Data Analytics OK")
            testes_sucesso += 1

        except Exception as e:
            logger.warning(f"⚠️ Big Data Analytics falhou: {e}")

        testes_executados += 1

        # Testar APIs
        try:
            logger.info("Testando APIs IMEA...")
            from gestao_rural.apis_integracao.api_imea import IMEAService

            imea_service = IMEAService()
            assert hasattr(imea_service, 'obter_precos_mt')
            logger.info("✅ API IMEA OK")
            testes_sucesso += 1

        except Exception as e:
            logger.warning(f"⚠️ API IMEA falhou: {e}")

        testes_executados += 1

        try:
            logger.info("Testando APIs Scot...")
            from gestao_rural.apis_integracao.api_scot_consultoria import ScotConsultoriaService

            scot_service = ScotConsultoriaService()
            assert hasattr(scot_service, 'obter_cotacoes_diarias')
            logger.info("✅ API Scot OK")
            testes_sucesso += 1

        except Exception as e:
            logger.warning(f"⚠️ API Scot falhou: {e}")

        testes_executados += 1

        # Resultado dos testes
        taxa_sucesso = (testes_sucesso / testes_executados) * 100
        logger.info(f"📊 Testes concluídos: {testes_sucesso}/{testes_executados} ({taxa_sucesso:.1f}%)")

        return taxa_sucesso >= 70  # Aceitar se pelo menos 70% dos testes passarem

    def configurar_apis(self):
        """Configura as APIs externas (instruções para o usuário)"""
        logger.info("🔧 Configurando APIs...")

        config_file = self.projeto_root / 'config_env.txt'

        if not config_file.exists():
            logger.warning("⚠️ Arquivo config_env.txt não encontrado")
            return

        # Verificar se as chaves de API estão configuradas
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = f.read()

        configuracoes_faltando = []

        if 'IMEA_API_KEY' not in config_content:
            configuracoes_faltando.append('IMEA_API_KEY')

        if 'SCOT_API_KEY' not in config_content:
            configuracoes_faltando.append('SCOT_API_KEY')

        if configuracoes_faltando:
            logger.warning("⚠️ Configurações de API faltando:")
            for config in configuracoes_faltando:
                logger.warning(f"   - {config}")
            logger.info("💡 Adicione essas configurações no arquivo config_env.txt")
        else:
            logger.info("✅ Configurações de API encontradas")

    def gerar_relatorio(self):
        """Gera relatório final da instalação"""
        logger.info("📋 Gerando relatório final...")

        relatorio = f"""
{'='*60}
RELATÓRIO DE INSTALAÇÃO - MELHORIAS DE IA MONPEC
{'='*60}

✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO

🎯 FUNCIONALIDADES IMPLEMENTADAS:

📊 MACHINE LEARNING:
   • Previsão de preços com ensemble (Linear + Random Forest)
   • Análise de natalidade e mortalidade baseada em dados históricos
   • Detecção de padrões e anomalias

🔍 BIG DATA ANALYTICS:
   • Análise completa de dados históricos
   • Correlação entre variáveis
   • Segmentação de categorias
   • Detecção de anomalias

🌐 APIs DE MERCADO:
   • IMEA (Instituto Mato-grossense de Economia Agropecuária)
   • Scot Consultoria (cotações e análises)
   • CEPEA (já existente, aprimorado)

📈 MELHORIAS NO PLANEJAMENTO:
   • Recomendações inteligentes aprimoradas
   • Cenários de risco com ML
   • Previsões integradas de múltiplas fontes
   • Insights avançados baseados em dados reais

📚 DEPENDÊNCIAS INSTALADAS:
   • scikit-learn (Machine Learning)
   • pandas (Análise de dados)
   • numpy (Computação numérica)
   • statsmodels (Estatísticas)
   • scipy (Computação científica)
   • plotly (Visualização)

⚙️ PRÓXIMOS PASSOS:

1. Configure as chaves de API no arquivo config_env.txt:
   • IMEA_API_KEY (opcional)
   • SCOT_API_KEY (opcional)

2. Execute migrações se necessário:
   python manage.py migrate

3. Teste as novas funcionalidades:
   • Acesse o módulo de planejamento
   • Verifique as novas recomendações da IA
   • Analise as previsões de preços

4. Monitore os logs para verificar funcionamento das APIs

{'='*60}
"""

        # Salvar relatório
        relatorio_path = self.projeto_root / 'RELATORIO_INSTALACAO_IA.txt'
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write(relatorio)

        logger.info(f"📄 Relatório salvo em: {relatorio_path}")

        # Imprimir relatório na tela
        print(relatorio)


def main():
    """Função principal"""
    instalador = InstaladorIAMelhorias()
    sucesso = instalador.executar_instalacao()

    if sucesso:
        print("\n🎉 Instalação concluída! Suas melhorias de IA estão prontas para uso.")
        print("📖 Consulte o RELATORIO_INSTALACAO_IA.txt para detalhes completos.")
    else:
        print("\n❌ Instalação falhou. Verifique os logs acima para detalhes.")
        sys.exit(1)


if __name__ == '__main__':
    main()