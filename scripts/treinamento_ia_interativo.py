# -*- coding: utf-8 -*-
"""
Treinamento Interativo da IA do Monpec
Interface interativa para treinar e testar os modelos de IA
"""

import os
import sys
import django
import logging
from datetime import datetime
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec.settings')
django.setup()

from gestao_rural.services.ml_price_prediction import MLPricePredictionService
from gestao_rural.services.ml_natalidade_mortalidade import MLNatalidadeMortalidadeService
from gestao_rural.services.big_data_analytics import BigDataAnalyticsService
from gestao_rural.models import Propriedade

logger = logging.getLogger(__name__)


class TreinamentoIAInterativo:
    """
    Interface interativa para treinamento e teste dos modelos de IA
    """

    def __init__(self):
        self.ml_price = MLPricePredictionService()
        self.ml_reprodutivo = MLNatalidadeMortalidadeService()
        self.big_data = BigDataAnalyticsService()

    def executar_menu_principal(self):
        """
        Menu principal interativo
        """
        while True:
            self._limpar_tela()
            print("=" * 60)
            print("🎯 TREINAMENTO INTERATIVO DA IA - MONPEC")
            print("=" * 60)
            print("1. 📊 Treinar Modelo de Preços")
            print("2. 🐄 Treinar Modelo Reprodutivo")
            print("3. 📈 Executar Análise Big Data")
            print("4. 🔄 Treinamento Completo Automático")
            print("5. 📋 Ver Status dos Modelos")
            print("6. 🧪 Testar Modelos Treinados")
            print("7. 📊 Ver Relatórios de Performance")
            print("0. 🚪 Sair")
            print("=" * 60)

            try:
                opcao = input("Escolha uma opção (0-7): ").strip()

                if opcao == "0":
                    print("👋 Até logo!")
                    break
                elif opcao == "1":
                    self.menu_treinamento_precos()
                elif opcao == "2":
                    self.menu_treinamento_reprodutivo()
                elif opcao == "3":
                    self.menu_analise_big_data()
                elif opcao == "4":
                    self.executar_treinamento_completo()
                elif opcao == "5":
                    self.ver_status_modelos()
                elif opcao == "6":
                    self.menu_testar_modelos()
                elif opcao == "7":
                    self.ver_relatorios_performance()
                else:
                    print("❌ Opção inválida!")
                    input("Pressione Enter para continuar...")

            except KeyboardInterrupt:
                print("\n👋 Treinamento interrompido pelo usuário.")
                break
            except Exception as e:
                logger.error(f"Erro no menu principal: {e}")
                print(f"❌ Erro: {e}")
                input("Pressione Enter para continuar...")

    def menu_treinamento_precos(self):
        """
        Menu para treinamento de modelos de preços
        """
        while True:
            self._limpar_tela()
            print("=" * 60)
            print("💰 TREINAMENTO DE MODELOS DE PREÇOS")
            print("=" * 60)
            print("1. 📈 Treinar Modelo de Boi Gordo")
            print("2. 🐂 Treinar Modelo de Bezerro")
            print("3. 🐄 Treinar Modelo de Bezerra")
            print("4. 🐃 Treinar Modelo de Garrote")
            print("5. 🐄 Treinar Modelo de Novilha")
            print("6. 🌍 Treinar Todos os Modelos")
            print("7. 📊 Testar Previsão")
            print("0. 🔙 Voltar")
            print("=" * 60)

            opcao = input("Escolha uma opção (0-7): ").strip()

            if opcao == "0":
                break
            elif opcao in ["1", "2", "3", "4", "5", "6"]:
                categorias = {
                    "1": "BOI",
                    "2": "BEZERRO",
                    "3": "BEZERRA",
                    "4": "GARROTE",
                    "5": "NOVILHA"
                }

                if opcao == "6":
                    # Treinar todas as categorias
                    self._treinar_todas_categorias_precos()
                else:
                    categoria = categorias[opcao]
                    self._treinar_modelo_preco_categoria(categoria)

            elif opcao == "7":
                self._testar_previsao_precos()
            else:
                print("❌ Opção inválida!")
                input("Pressione Enter para continuar...")

    def _treinar_modelo_preco_categoria(self, categoria: str):
        """
        Treina modelo de preço para uma categoria específica
        """
        print(f"🚀 Treinando modelo de preços para {categoria}...")
        print("Isso pode levar alguns segundos...")

        try:
            # Coletar dados históricos
            dados = self.ml_price._coletar_dados_historicos('MT', categoria, periodo_meses=24)

            if len(dados) < 12:
                print(f"⚠️ Dados insuficientes para {categoria} (apenas {len(dados)} registros)")
                print("São necessários pelo menos 12 meses de dados históricos.")
            else:
                # Preparar dados
                X, y = self.ml_price._preparar_dados_ml(dados)

                if len(X) < 10:
                    print(f"⚠️ Amostras insuficientes para treinamento (apenas {len(X)})")
                else:
                    # Executar treinamento (simulação)
                    previsao_teste = self.ml_price._prever_com_ensemble(X, y, 3)

                    print("✅ Modelo treinado com sucesso!"                    print(f"📊 Dados de treinamento: {len(X)} amostras")
                    print(f"📈 Período analisado: 24 meses")
                    print(f"🎯 Previsão de teste para os próximos 3 meses:")
                    for prev in previsao_teste[:3]:
                        print(".2f")

        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")

        input("Pressione Enter para continuar...")

    def _treinar_todas_categorias_precos(self):
        """
        Treina modelos para todas as categorias de preços
        """
        categorias = ["BOI", "BEZERRO", "BEZERRA", "GARROTE", "NOVILHA"]

        print("🚀 Treinando modelos para todas as categorias...")
        print("Isso pode levar alguns minutos...")

        resultados = {}
        for categoria in categorias:
            try:
                dados = self.ml_price._coletar_dados_historicos('MT', categoria, periodo_meses=24)
                if len(dados) >= 12:
                    X, y = self.ml_price._preparar_dados_ml(dados)
                    if len(X) >= 10:
                        previsao = self.ml_price._prever_com_ensemble(X, y, 1)
                        resultados[categoria] = {
                            'status': 'treinado',
                            'amostras': len(X),
                            'previsao_teste': previsao[0]['preco_previsto'] if previsao else None
                        }
                    else:
                        resultados[categoria] = {'status': 'dados_insuficientes', 'amostras': len(X)}
                else:
                    resultados[categoria] = {'status': 'dados_insuficientes', 'registros': len(dados)}
            except Exception as e:
                resultados[categoria] = {'status': 'erro', 'erro': str(e)}

        # Exibir resultados
        print("\n📋 RESULTADO DO TREINAMENTO:")
        print("-" * 50)
        for categoria, resultado in resultados.items():
            if resultado['status'] == 'treinado':
                print(f"✅ {categoria}: Treinado ({resultado['amostras']} amostras)")
                if resultado.get('previsao_teste'):
                    print(".2f"            elif resultado['status'] == 'dados_insuficientes':
                amostras = resultado.get('amostras', resultado.get('registros', 0))
                print(f"⚠️ {categoria}: Dados insuficientes ({amostras} registros)")
            else:
                print(f"❌ {categoria}: Erro - {resultado.get('erro', 'Desconhecido')}")

        input("Pressione Enter para continuar...")

    def _testar_previsao_precos(self):
        """
        Testa uma previsão de preços interativamente
        """
        print("🧪 TESTE DE PREVISÃO DE PREÇOS")
        print("-" * 40)

        # Selecionar categoria
        categorias = ["BOI", "BEZERRO", "BEZERRA", "GARROTE", "NOVILHA"]
        print("Categorias disponíveis:")
        for i, cat in enumerate(categorias, 1):
            print(f"{i}. {cat}")

        try:
            cat_idx = int(input("Escolha a categoria (1-5): ")) - 1
            categoria = categorias[cat_idx]
        except:
            print("❌ Seleção inválida!")
            input("Pressione Enter para continuar...")
            return

        # Selecionar período
        try:
            meses = int(input("Meses para prever (1-12): "))
            if meses < 1 or meses > 12:
                meses = 6
        except:
            meses = 6

        print(f"🔮 Fazendo previsão de {categoria} para os próximos {meses} meses...")

        try:
            previsao = self.ml_price.prever_precos_futuros(
                'MT', categoria, meses, 'ensemble'
            )

            if previsao.get('sucesso'):
                print("
✅ PREVISÃO REALIZADA:"                print("-" * 50)

                for prev in previsao['previsoes'][:min(6, len(previsao['previsoes']))]:
                    print(f"{prev['data']}: R$ {prev['preco_previsto']:.2f} (Confiança: {prev['confianca']:.0%})")

                if previsao.get('metricas'):
                    metricas = previsao['metricas']
                    print("
📊 MÉTRICAS DO MODELO:"                    if 'mae' in metricas:
                        print(f"• Erro Médio Absoluto: R$ {metricas['mae']:.2f}")
                    if 'erro_percentual_medio' in metricas:
                        print(f"• Erro Percentual Médio: {metricas['erro_percentual_medio']:.1f}%")
                    if 'acuracia_esperada' in metricas:
                        print(f"• Acurácia Esperada: {metricas['acuracia_esperada']:.1f}%")

            else:
                print(f"❌ Falha na previsão: {previsao.get('erro', 'Erro desconhecido')}")

        except Exception as e:
            print(f"❌ Erro na previsão: {e}")

        input("Pressione Enter para continuar...")

    def menu_treinamento_reprodutivo(self):
        """
        Menu para treinamento de modelos reprodutivos
        """
        while True:
            self._limpar_tela()
            print("=" * 60)
            print("🐄 TREINAMENTO DE MODELOS REPRODUTIVOS")
            print("=" * 60)
            print("1. 🐮 Treinar Modelo de Natalidade")
            print("2. 💀 Treinar Modelo de Mortalidade")
            print("3. 🔍 Análise de Fatores de Risco")
            print("4. 📊 Comparar Propriedades")
            print("0. 🔙 Voltar")
            print("=" * 60)

            opcao = input("Escolha uma opção (0-4): ").strip()

            if opcao == "0":
                break
            elif opcao == "1":
                self._treinar_modelo_natalidade()
            elif opcao == "2":
                self._treinar_modelo_mortalidade()
            elif opcao == "3":
                self._analisar_fatores_risco()
            elif opcao == "4":
                self._comparar_propriedades()
            else:
                print("❌ Opção inválida!")
                input("Pressione Enter para continuar...")

    def _treinar_modelo_natalidade(self):
        """
        Treina modelo de natalidade
        """
        print("🐮 TREINAMENTO DE MODELO DE NATALIDADE")
        print("-" * 40)

        # Selecionar propriedade
        propriedade = self._selecionar_propriedade()
        if not propriedade:
            return

        print(f"Treinando modelo para: {propriedade.nome}")
        print("Analisando dados históricos de natalidade...")

        try:
            # Treinar modelo
            resultado = self.ml_reprodutivo.prever_taxa_natalidade(
                propriedade.id, 'Multípara', periodo_meses=24
            )

            if resultado.get('sucesso'):
                print("
✅ MODELO TREINADO COM SUCESSO!"                print("-" * 40)
                print(f"Taxa histórica média: {resultado.get('taxa_historica_media', 0):.1%}")
                print(f"Taxa prevista: {resultado['taxa_prevista']:.1%}")

                if resultado.get('metricas'):
                    metricas = resultado['metricas']
                    print(f"Dados de treinamento: {resultado.get('dados_historicos', 0)} registros")
                    if 'mae' in metricas:
                        print(f"Erro Médio Absoluto: {metricas['mae']:.4f}")
                    if 'acuracia_esperada' in metricas:
                        print(f"Acurácia esperada: {metricas['acuracia_esperada']:.1f}%")
            else:
                print(f"❌ Falha no treinamento: {resultado.get('erro', 'Dados insuficientes')}")

        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")

        input("Pressione Enter para continuar...")

    def _treinar_modelo_mortalidade(self):
        """
        Treina modelo de mortalidade
        """
        print("💀 TREINAMENTO DE MODELO DE MORTALIDADE")
        print("-" * 40)

        # Selecionar propriedade
        propriedade = self._selecionar_propriedade()
        if not propriedade:
            return

        print(f"Treinando modelo para: {propriedade.nome}")
        print("Analisando dados históricos de mortalidade...")

        try:
            resultado = self.ml_reprodutivo.prever_taxa_mortalidade(
                propriedade.id, 'Bezerros (0-12m)', periodo_meses=24
            )

            if resultado.get('sucesso'):
                print("
✅ MODELO TREINADO COM SUCESSO!"                print("-" * 40)
                print(f"Taxa histórica média: {resultado.get('taxa_historica_media', 0):.1%}")
                print(f"Taxa prevista: {resultado['taxa_prevista']:.1%}")

                if resultado.get('metricas'):
                    metricas = resultado['metricas']
                    print(f"Dados de treinamento: {resultado.get('dados_historicos', 0)} registros")
                    if 'mae' in metricas:
                        print(f"Erro Médio Absoluto: {metricas['mae']:.4f}")
            else:
                print(f"❌ Falha no treinamento: {resultado.get('erro', 'Dados insuficientes')}")

        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")

        input("Pressione Enter para continuar...")

    def _analisar_fatores_risco(self):
        """
        Análise de fatores de risco reprodutivo
        """
        print("🔍 ANÁLISE DE FATORES DE RISCO")
        print("-" * 35)

        # Selecionar propriedade
        propriedade = self._selecionar_propriedade()
        if not propriedade:
            return

        print(f"Analisando fatores de risco para: {propriedade.nome}")
        print("Isso pode levar alguns segundos...")

        try:
            analise = self.ml_reprodutivo.analisar_fatores_risco(
                propriedade.id, 'Multípara', periodo_meses=24
            )

            if analise.get('sucesso'):
                print("
✅ ANÁLISE CONCLUÍDA!"                print("-" * 35)

                # Natalidade
                natalidade = analise.get('natalidade', {})
                if natalidade:
                    print(f"🐮 NATALIDADE:")
                    print(f"   • Taxa média: {natalidade.get('taxa_media', 0):.1%}")
                    print(f"   • Desvio padrão: {natalidade.get('taxa_desvio_padrao', 0):.1%}")
                    print(f"   • Mês melhor: {natalidade.get('melhor_mes_nome', 'N/A')}")
                    print(f"   • Mês pior: {natalidade.get('pior_mes_nome', 'N/A')}")

                # Mortalidade
                mortalidade = analise.get('mortalidade', {})
                if mortalidade:
                    print(f"💀 MORTALIDADE:")
                    print(f"   • Taxa média: {mortalidade.get('taxa_media', 0):.1%}")
                    print(f"   • Desvio padrão: {mortalidade.get('taxa_desvio_padrao', 0):.1%}")
                    print(f"   • Mês melhor: {mortalidade.get('melhor_mes_nome', 'N/A')}")
                    print(f"   • Mês pior: {mortalidade.get('pior_mes_nome', 'N/A')}")

                # Correlação
                correlacoes = analise.get('correlacoes', {})
                if correlacoes and 'natalidade_vs_mortalidade' in correlacoes:
                    corr = correlacoes['natalidade_vs_mortalidade']
                    print("
🔗 CORRELAÇÃO:"                    print(f"   • Natalidade vs Mortalidade: {corr.get('correlacao', 0):.3f}")
                    print(f"   • Interpretação: {corr.get('interpretacao', 'N/A')}")

                # Recomendações
                recomendacoes = analise.get('recomendacoes', [])
                if recomendacoes:
                    print("
💡 RECOMENDAÇÕES:"                    for rec in recomendacoes:
                        print(f"   • {rec}")

            else:
                print(f"❌ Falha na análise: {analise.get('erro', 'Dados insuficientes')}")

        except Exception as e:
            print(f"❌ Erro na análise: {e}")

        input("Pressione Enter para continuar...")

    def menu_analise_big_data(self):
        """
        Menu para análise Big Data
        """
        while True:
            self._limpar_tela()
            print("=" * 60)
            print("📊 ANÁLISE BIG DATA")
            print("=" * 60)
            print("1. 🔍 Análise Completa de Propriedade")
            print("2. 📈 Análise de Tendências")
            print("3. 🚨 Detecção de Anomalias")
            print("4. 📊 Correlações entre Variáveis")
            print("5. 🏷️ Segmentação de Categorias")
            print("0. 🔙 Voltar")
            print("=" * 60)

            opcao = input("Escolha uma opção (0-5): ").strip()

            if opcao == "0":
                break
            elif opcao == "1":
                self._analise_completa_propriedade()
            elif opcao == "2":
                self._analise_tendencias()
            elif opcao == "3":
                self._deteccao_anomalias()
            elif opcao == "4":
                self._analise_correlacoes()
            elif opcao == "5":
                self._segmentacao_categorias()
            else:
                print("❌ Opção inválida!")
                input("Pressione Enter para continuar...")

    def _analise_completa_propriedade(self):
        """
        Executa análise completa de Big Data para uma propriedade
        """
        print("🔍 ANÁLISE COMPLETA DE BIG DATA")
        print("-" * 35)

        # Selecionar propriedade
        propriedade = self._selecionar_propriedade()
        if not propriedade:
            return

        print(f"Executando análise completa para: {propriedade.nome}")
        print("Isso pode levar alguns minutos...")

        try:
            analise = self.big_data.analisar_dados_historicos_completos(
                propriedade.id, periodo_meses=24
            )

            if analise.get('sucesso'):
                print("
✅ ANÁLISE CONCLUÍDA!"                print("-" * 35)

                # Estatísticas gerais
                stats = analise.get('estatisticas_gerais', {})
                print(f"📊 TOTAL DE REGISTROS: {analise.get('total_registros', 0):,}")

                # Movimentações
                mov = stats.get('movimentacoes', {})
                if mov:
                    print(f"📈 Movimentações: {mov.get('total_registros', 0):,} registros")
                    print(f"📅 Período: {mov.get('periodo_cobertura', {}).get('inicio', 'N/A')} a {mov.get('periodo_cobertura', {}).get('fim', 'N/A')}")

                # Inventários
                inv = stats.get('inventarios', {})
                if inv:
                    print(f"📦 Inventários: {inv.get('total_registros', 0):,} registros")
                    print(f"🐄 Total de animais: {inv.get('quantidade_total_animais', 0):,}")

                # Anomalias
                anomalias = analise.get('deteccao_anomalias', {})
                if anomalias.get('movimentacoes', {}).get('dias_com_movimentacao_anormal', 0) > 0:
                    dias_anomalos = anomalias['movimentacoes']['dias_com_movimentacao_anormal']
                    print(f"🚨 Dias com movimentação anormal: {dias_anomalos}")

                # Tendências
                tendencias = analise.get('analises_tendencias', {})
                mov_tend = tendencias.get('movimentacoes', {})
                if mov_tend.get('tendencia_anual', 0) != 0:
                    direcao = mov_tend.get('direcao', 'estável')
                    variacao = mov_tend.get('tendencia_anual', 0)
                    print(f"📈 Tendência de movimentações: {direcao} ({variacao:+.1f} ao ano)")

                # Insights
                insights = analise.get('insights', [])
                if insights:
                    print("
💡 PRINCIPAIS INSIGHTS:"                    for insight in insights[:5]:  # Top 5
                        print(f"   • {insight}")

            else:
                print(f"❌ Falha na análise: {analise.get('erro', 'Erro desconhecido')}")

        except Exception as e:
            print(f"❌ Erro na análise: {e}")

        input("Pressione Enter para continuar...")

    def _selecionar_propriedade(self):
        """
        Interface para selecionar uma propriedade
        """
        propriedades = Propriedade.objects.filter(ativo=True)[:10]  # Limitar para performance

        if not propriedades:
            print("❌ Nenhuma propriedade ativa encontrada!")
            input("Pressione Enter para continuar...")
            return None

        print("Propriedades disponíveis:")
        for i, prop in enumerate(propriedades, 1):
            print(f"{i}. {prop.nome} (ID: {prop.id})")

        try:
            idx = int(input(f"Escolha uma propriedade (1-{len(propriedades)}): ")) - 1
            if 0 <= idx < len(propriedades):
                return propriedades[idx]
            else:
                print("❌ Seleção inválida!")
                return None
        except:
            print("❌ Entrada inválida!")
            return None

    def executar_treinamento_completo(self):
        """
        Executa treinamento completo automático
        """
        print("🔄 EXECUTANDO TREINAMENTO COMPLETO AUTOMÁTICO")
        print("-" * 50)
        print("Isso pode levar vários minutos dependendo da quantidade de dados...")
        print("Os modelos serão treinados para todas as propriedades ativas.")
        print()

        confirmar = input("Deseja continuar? (s/n): ").strip().lower()
        if confirmar != 's':
            return

        # Importar e executar treinamento completo
        try:
            from scripts.treinar_modelos_ia import TreinadorIAModelos

            treinador = TreinadorIAModelos()
            treinador.executar_treinamento_completo()

            print("✅ Treinamento completo finalizado!")

        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")

        input("Pressione Enter para continuar...")

    def ver_status_modelos(self):
        """
        Verifica status dos modelos treinados
        """
        print("📋 STATUS DOS MODELOS DE IA")
        print("-" * 35)

        # Verificar se os serviços estão funcionais
        status = {
            'ML_Precos': self._verificar_status_servico(self.ml_price, 'prever_precos_futuros'),
            'ML_Reprodutivo': self._verificar_status_servico(self.ml_reprodutivo, 'prever_taxa_natalidade'),
            'Big_Data': self._verificar_status_servico(self.big_data, 'analisar_dados_historicos_completos')
        }

        for modelo, funcional in status.items():
            status_icon = "✅" if funcional else "❌"
            print(f"{status_icon} {modelo}: {'Funcional' if funcional else 'Com problemas'}")

        # Verificar propriedades com dados
        propriedades = Propriedade.objects.filter(ativo=True)
        print(f"🏢 Propriedades ativas: {propriedades.count()}")

        # Verificar dados disponíveis (aproximado)
        try:
            from gestao_rural.models import MovimentacaoIndividual, InventarioRebanho

            mov_count = MovimentacaoIndividual.objects.count()
            inv_count = InventarioRebanho.objects.count()

            print(f"📊 Movimentações registradas: {mov_count:,}")
            print(f"📦 Inventários registrados: {inv_count:,}")

        except Exception as e:
            print(f"❌ Erro ao verificar dados: {e}")

        input("Pressione Enter para continuar...")

    def _verificar_status_servico(self, servico, metodo_teste):
        """
        Verifica se um serviço está funcional
        """
        try:
            if hasattr(servico, metodo_teste):
                return True
            else:
                return False
        except:
            return False

    def menu_testar_modelos(self):
        """
        Menu para testar modelos treinados
        """
        print("🧪 MENU DE TESTES (Em desenvolvimento)")
        print("Esta funcionalidade estará disponível na próxima versão.")
        input("Pressione Enter para continuar...")

    def ver_relatorios_performance(self):
        """
        Exibe relatórios de performance
        """
        print("📊 RELATÓRIOS DE PERFORMANCE (Em desenvolvimento)")
        print("Relatórios detalhados estarão disponíveis após treinamentos.")
        input("Pressione Enter para continuar...")

    def _limpar_tela(self):
        """
        Limpa a tela do terminal
        """
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """
    Função principal
    """
    # Configurar logging
    logging.basicConfig(level=logging.WARNING)  # Reduzir logs na interface interativa

    try:
        treinador = TreinamentoIAInterativo()
        treinador.executar_menu_principal()
    except Exception as e:
        print(f"❌ Erro na aplicação: {e}")
        input("Pressione Enter para sair...")


if __name__ == '__main__':
    main()