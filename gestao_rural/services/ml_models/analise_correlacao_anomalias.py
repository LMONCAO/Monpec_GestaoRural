# -*- coding: utf-8 -*-
"""
Módulo de Análise de Correlações e Detecção de Anomalias
Utiliza estatística e ML para identificar padrões e anomalias nos dados pecuários
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Q, F, Sum
from django.utils import timezone

from gestao_rural.models import (
    Propriedade, InventarioRebanho, MovimentacaoIndividual,
    MovimentacaoProjetada, AtividadePlanejada,
    MetaComercialPlanejada, MetaFinanceiraPlanejada
)

logger = logging.getLogger(__name__)


class AnaliseCorrelacaoAnomalias:
    """
    Sistema de análise avançada para detecção de padrões, correlações
    e anomalias nos dados pecuários
    """

    def __init__(self, propriedade: Propriedade):
        self.propriedade = propriedade
        self.scaler = StandardScaler()

    def analisar_correlacoes_producao(
        self,
        periodo_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Analisa correlações entre fatores de produção

        Args:
            periodo_meses: Período de análise em meses

        Returns:
            Análise de correlações
        """
        try:
            # Coletar dados históricos
            dados = self._coletar_dados_producao(periodo_meses)

            if not dados:
                return {'erro': 'Dados insuficientes para análise'}

            # Criar DataFrame
            df = pd.DataFrame(dados)

            # Calcular correlações
            correlacoes = self._calcular_matriz_correlacao(df)

            # Identificar correlações fortes
            correlacoes_fortes = self._identificar_correlacoes_fortes(correlacoes)

            # Análise de causalidade
            analises_causalidade = self._analisar_relacoes_causa_efeito(df)

            return {
                'matriz_correlacao': correlacoes,
                'correlacoes_fortes': correlacoes_fortes,
                'analises_causalidade': analises_causalidade,
                'insights_principais': self._gerar_insights_correlacao(correlacoes_fortes)
            }

        except Exception as e:
            logger.error(f'Erro na análise de correlações: {e}')
            return {'erro': str(e)}

    def _coletar_dados_producao(self, periodo_meses: int) -> List[Dict]:
        """
        Coleta dados históricos de produção da propriedade
        """
        dados = []
        data_inicio = date.today() - timedelta(days=periodo_meses * 30)

        # Dados de inventário
        inventarios = InventarioRebanho.objects.filter(
            propriedade=self.propriedade,
            data_inventario__gte=data_inicio
        ).order_by('data_inventario')

        for inventario in inventarios:
            dados.append({
                'data': inventario.data_inventario,
                'categoria': inventario.categoria_animal.nome if inventario.categoria_animal else 'DESCONHECIDA',
                'quantidade': inventario.quantidade_atual,
                'tipo_dado': 'INVENTARIO'
            })

        # Dados de movimentações individuais
        movimentacoes = MovimentacaoIndividual.objects.filter(
            propriedade=self.propriedade,
            data_movimentacao__gte=data_inicio
        ).select_related('categoria_animal')

        for mov in movimentacoes:
            dados.append({
                'data': mov.data_movimentacao,
                'categoria': mov.categoria_animal.nome if mov.categoria_animal else 'DESCONHECIDA',
                'quantidade': mov.quantidade,
                'tipo_movimentacao': mov.tipo_movimentacao,
                'tipo_dado': 'MOVIMENTACAO_INDIVIDUAL'
            })

        # Dados climáticos simulados (se disponíveis)
        # Aqui poderiam ser integrados dados reais de clima
        dados_clima = self._gerar_dados_climaticos_simulados(data_inicio, periodo_meses)
        dados.extend(dados_clima)

        return dados

    def _gerar_dados_climaticos_simulados(
        self,
        data_inicio: date,
        periodo_meses: int
    ) -> List[Dict]:
        """
        Gera dados climáticos simulados (substituir por API real)
        """
        dados_clima = []
        data_atual = data_inicio

        for _ in range(periodo_meses):
            # Simulação baseada na localização da propriedade
            # Valores aproximados para região Centro-Oeste
            dados_clima.append({
                'data': data_atual,
                'temperatura_media': 25 + 5 * np.sin(2 * np.pi * data_atual.month / 12),
                'precipitacao': 150 + 100 * np.sin(2 * np.pi * (data_atual.month - 3) / 12),
                'umidade': 70 + 20 * np.sin(2 * np.pi * data_atual.month / 12),
                'tipo_dado': 'CLIMA'
            })

            # Avançar um mês
            if data_atual.month == 12:
                data_atual = date(data_atual.year + 1, 1, 1)
            else:
                data_atual = date(data_atual.year, data_atual.month + 1, 1)

        return dados_clima

    def _calcular_matriz_correlacao(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calcula matriz de correlação entre variáveis
        """
        # Preparar dados numéricos
        df_numerico = df.select_dtypes(include=[np.number])

        # Calcular correlação de Pearson
        correlacao = df_numerico.corr()

        # Converter para dicionário
        matriz_correlacao = {}
        for col1 in correlacao.columns:
            matriz_correlacao[col1] = {}
            for col2 in correlacao.columns:
                valor = correlacao.loc[col1, col2]
                if not np.isnan(valor):
                    matriz_correlacao[col1][col2] = float(valor)
                else:
                    matriz_correlacao[col1][col2] = 0.0

        return matriz_correlacao

    def _identificar_correlacoes_fortes(
        self,
        matriz_correlacao: Dict[str, Dict[str, float]],
        limiar: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Identifica correlações fortes (> limiar absoluto)
        """
        correlacoes_fortes = []

        for var1, correlacoes in matriz_correlacao.items():
            for var2, valor in correlacoes.items():
                if var1 != var2 and abs(valor) >= limiar:
                    correlacoes_fortes.append({
                        'variavel_1': var1,
                        'variavel_2': var2,
                        'correlacao': valor,
                        'forca': 'FORTE' if abs(valor) >= 0.8 else 'MODERADA',
                        'direcao': 'POSITIVA' if valor > 0 else 'NEGATIVA'
                    })

        # Ordenar por força da correlação
        correlacoes_fortes.sort(key=lambda x: abs(x['correlacao']), reverse=True)

        return correlacoes_fortes

    def _analisar_relacoes_causa_efeito(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analisa possíveis relações de causa e efeito
        """
        analises = []

        # Análise específica para pecuária
        if 'precipitacao' in df.columns and 'quantidade' in df.columns:
            # Correlação entre chuva e produtividade
            correlacao_chuva_prod = df['precipitacao'].corr(df['quantidade'])
            if abs(correlacao_chuva_prod) > 0.5:
                analises.append({
                    'relacao': 'CHUVA_VS_PRODUTIVIDADE',
                    'correlacao': float(correlacao_chuva_prod),
                    'interpretacao': 'Precipitação influencia a produtividade do rebanho'
                })

        if 'temperatura_media' in df.columns and 'quantidade' in df.columns:
            # Correlação entre temperatura e produtividade
            correlacao_temp_prod = df['temperatura_media'].corr(df['quantidade'])
            if abs(correlacao_temp_prod) > 0.4:
                analises.append({
                    'relacao': 'TEMPERATURA_VS_PRODUTIVIDADE',
                    'correlacao': float(correlacao_temp_prod),
                    'interpretacao': 'Temperatura afeta o desempenho reprodutivo'
                })

        return analises

    def _gerar_insights_correlacao(self, correlacoes_fortes: List[Dict]) -> List[str]:
        """
        Gera insights baseados nas correlações encontradas
        """
        insights = []

        for correlacao in correlacoes_fortes[:5]:  # Top 5 correlações
            var1 = correlacao['variavel_1']
            var2 = correlacao['variavel_2']
            valor = correlacao['correlacao']
            direcao = correlacao['direcao']

            if 'precipitacao' in [var1, var2] and 'quantidade' in [var1, var2]:
                if direcao == 'POSITIVA':
                    insights.append("Aumento na precipitação está correlacionado com maior produtividade")
                else:
                    insights.append("Períodos de seca podem impactar negativamente a produção")

            elif 'temperatura' in str(var1 + var2).lower():
                insights.append(f"Variações de temperatura mostram correlação {direcao.lower()} com os indicadores produtivos")

            else:
                insights.append(f"Correlação {direcao.lower()} identificada entre {var1} e {var2} (r={valor:.2f})")

        return insights

    def detectar_anomalias(
        self,
        tipo_analise: str = 'producao',
        periodo_meses: int = 12
    ) -> Dict[str, Any]:
        """
        Detecta anomalias nos dados usando Isolation Forest

        Args:
            tipo_analise: Tipo de análise ('producao', 'financeiro', 'reprodutivo')
            periodo_meses: Período de análise

        Returns:
            Detecção de anomalias
        """
        try:
            # Coletar dados baseados no tipo
            if tipo_analise == 'producao':
                dados = self._coletar_dados_producao(periodo_meses)
            elif tipo_analise == 'financeiro':
                dados = self._coletar_dados_financeiros(periodo_meses)
            elif tipo_analise == 'reprodutivo':
                dados = self._coletar_dados_reprodutivos(periodo_meses)
            else:
                return {'erro': f'Tipo de análise não suportado: {tipo_analise}'}

            if not dados:
                return {'erro': 'Dados insuficientes para detecção de anomalias'}

            # Preparar dados para ML
            df = pd.DataFrame(dados)
            dados_numericos = self._preparar_dados_anomalias(df)

            if dados_numericos.shape[0] < 10:
                return {'erro': 'Dados insuficientes (mínimo 10 registros)'}

            # Aplicar Isolation Forest
            isolation_forest = IsolationForest(
                contamination=0.1,  # 10% de anomalias esperadas
                random_state=42,
                n_estimators=100
            )

            # Normalizar dados
            dados_normalizados = self.scaler.fit_transform(dados_numericos)

            # Fazer predições
            predicoes = isolation_forest.fit_predict(dados_normalizados)

            # Identificar anomalias (predição = -1)
            indices_anomalias = np.where(predicoes == -1)[0]

            # Calcular scores de anomalia
            scores_anomalia = isolation_forest.decision_function(dados_normalizados)

            # Organizar resultados
            anomalias_detectadas = []
            for idx in indices_anomalias:
                registro_original = df.iloc[idx]
                anomalias_detectadas.append({
                    'data': registro_original.get('data', 'N/A'),
                    'categoria': registro_original.get('categoria', 'N/A'),
                    'valor_anomalo': registro_original.get('quantidade', registro_original.get('valor', 0)),
                    'score_anomalia': float(scores_anomalia[idx]),
                    'tipo_dado': registro_original.get('tipo_dado', 'DESCONHECIDO')
                })

            # Estatísticas
            estatisticas = {
                'total_registros': len(df),
                'anomalias_detectadas': len(anomalias_detectadas),
                'percentual_anomalias': len(anomalias_detectadas) / len(df) * 100,
                'media_score_anomalia': float(scores_anomalia.mean()),
                'score_minimo': float(scores_anomalia.min()),
                'score_maximo': float(scores_anomalia.max())
            }

            return {
                'anomalias_detectadas': anomalias_detectadas,
                'estatisticas': estatisticas,
                'insights': self._gerar_insights_anomalias(anomalias_detectadas, tipo_analise)
            }

        except Exception as e:
            logger.error(f'Erro na detecção de anomalias: {e}')
            return {'erro': str(e)}

    def _preparar_dados_anomalias(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepara dados para detecção de anomalias
        """
        # Selecionar colunas numéricas relevantes
        colunas_numericas = []

        if 'quantidade' in df.columns:
            colunas_numericas.append('quantidade')
        if 'valor' in df.columns:
            colunas_numericas.append('valor')
        if 'precipitacao' in df.columns:
            colunas_numericas.append('precipitacao')
        if 'temperatura_media' in df.columns:
            colunas_numericas.append('temperatura_media')

        if not colunas_numericas:
            # Fallback: usar todas as colunas numéricas
            df_numerico = df.select_dtypes(include=[np.number])
            colunas_numericas = df_numerico.columns.tolist()

        if not colunas_numericas:
            raise ValueError("Nenhuma coluna numérica encontrada")

        # Preencher valores faltantes
        df_prep = df[colunas_numericas].fillna(df[colunas_numericas].mean())

        return df_prep.values

    def _coletar_dados_financeiros(self, periodo_meses: int) -> List[Dict]:
        """
        Coleta dados financeiros para análise
        """
        dados = []
        data_inicio = date.today() - timedelta(days=periodo_meses * 30)

        # Movimentações financeiras (simulação baseada em vendas)
        movimentacoes_vendas = MovimentacaoIndividual.objects.filter(
            propriedade=self.propriedade,
            tipo_movimentacao='VENDA',
            data_movimentacao__gte=data_inicio
        )

        for mov in movimentacoes_vendas:
            dados.append({
                'data': mov.data_movimentacao,
                'valor': float(mov.valor_unitario * mov.quantidade) if mov.valor_unitario else 0,
                'categoria': mov.categoria_animal.nome if mov.categoria_animal else 'DESCONHECIDA',
                'tipo_dado': 'VENDA'
            })

        return dados

    def _coletar_dados_reprodutivos(self, periodo_meses: int) -> List[Dict]:
        """
        Coleta dados reprodutivos para análise
        """
        dados = []
        data_inicio = date.today() - timedelta(days=periodo_meses * 30)

        # Movimentações de nascimento
        nascimentos = MovimentacaoIndividual.objects.filter(
            propriedade=self.propriedade,
            tipo_movimentacao='NASCIMENTO',
            data_movimentacao__gte=data_inicio
        )

        for nascimento in nascimentos:
            dados.append({
                'data': nascimento.data_movimentacao,
                'quantidade': nascimento.quantidade,
                'categoria': nascimento.categoria_animal.nome if nascimento.categoria_animal else 'DESCONHECIDA',
                'tipo_dado': 'NASCIMENTO'
            })

        # Movimentações de morte
        mortes = MovimentacaoIndividual.objects.filter(
            propriedade=self.propriedade,
            tipo_movimentacao='MORTE',
            data_movimentacao__gte=data_inicio
        )

        for morte in mortes:
            dados.append({
                'data': morte.data_movimentacao,
                'quantidade': morte.quantidade,
                'categoria': morte.categoria_animal.nome if morte.categoria_animal else 'DESCONHECIDA',
                'tipo_dado': 'MORTE'
            })

        return dados

    def _gerar_insights_anomalias(
        self,
        anomalias: List[Dict],
        tipo_analise: str
    ) -> List[str]:
        """
        Gera insights baseados nas anomalias detectadas
        """
        insights = []

        if not anomalias:
            insights.append("Nenhuma anomalia significativa detectada no período analisado")
            return insights

        # Contar anomalias por categoria/tipo
        contagem_por_tipo = {}
        for anomalia in anomalias:
            tipo = anomalia.get('tipo_dado', 'DESCONHECIDO')
            contagem_por_tipo[tipo] = contagem_por_tipo.get(tipo, 0) + 1

        # Gerar insights específicos
        if tipo_analise == 'producao':
            if contagem_por_tipo.get('INVENTARIO', 0) > 0:
                insights.append(f"Anomalias detectadas no inventário: {contagem_por_tipo['INVENTARIO']} registros atípicos")

        elif tipo_analise == 'financeiro':
            if contagem_por_tipo.get('VENDA', 0) > 0:
                insights.append(f"Vendas atípicas detectadas: {contagem_por_tipo['VENDA']} transações fora do padrão")

        elif tipo_analise == 'reprodutivo':
            nascimentos_anomalos = contagem_por_tipo.get('NASCIMENTO', 0)
            mortes_anomalos = contagem_por_tipo.get('MORTE', 0)

            if nascimentos_anomalos > 0:
                insights.append(f"Nascimentos atípicos: {nascimentos_anomalos} registros fora do padrão")
            if mortes_anomalos > 0:
                insights.append(f"Mortes atípicas: {mortes_anomalos} registros que podem indicar problemas sanitários")

        # Insight geral
        percentual_anomalias = len(anomalias) / max(len(anomalias) * 2, 1) * 100  # Estimativa
        if percentual_anomalias > 15:
            insights.append("Alto número de anomalias detectadas - revisar processos de registro de dados")
        elif percentual_anomalias > 5:
            insights.append("Número moderado de anomalias - monitorar tendências")
        else:
            insights.append("Baixo nível de anomalias - dados dentro dos padrões esperados")

        return insights

    def clustering_fazendas_similares(
        self,
        numero_clusters: int = 3
    ) -> Dict[str, Any]:
        """
        Agrupa fazendas similares usando clustering

        Args:
            numero_clusters: Número de grupos para formar

        Returns:
            Análise de clustering
        """
        try:
            # Simulação: na prática, precisaria de dados de múltiplas fazendas
            # Por enquanto, usar dados históricos da própria fazenda segmentados por período

            dados_cluster = self._preparar_dados_clustering()

            if dados_cluster.shape[0] < numero_clusters:
                return {'erro': 'Dados insuficientes para clustering'}

            # Aplicar K-Means
            kmeans = KMeans(
                n_clusters=min(numero_clusters, dados_cluster.shape[0]),
                random_state=42,
                n_init=10
            )

            clusters = kmeans.fit_predict(dados_cluster)

            # Analisar clusters
            analise_clusters = []
            for i in range(kmeans.n_clusters):
                indices_cluster = np.where(clusters == i)[0]
                dados_cluster_i = dados_cluster[indices_cluster]

                analise_clusters.append({
                    'cluster_id': i,
                    'tamanho': len(indices_cluster),
                    'centroide': kmeans.cluster_centers_[i].tolist(),
                    'caracteristicas': self._interpretar_cluster(dados_cluster_i)
                })

            return {
                'numero_clusters': kmeans.n_clusters,
                'clusters': analise_clusters,
                'inertia': float(kmeans.inertia_),
                'silhouette_score': self._calcular_silhouette_score(dados_cluster, clusters)
            }

        except Exception as e:
            logger.error(f'Erro no clustering: {e}')
            return {'erro': str(e)}

    def _preparar_dados_clustering(self) -> np.ndarray:
        """
        Prepara dados para clustering (segmentação temporal da própria fazenda)
        """
        # Dividir dados históricos em períodos para simular diferentes "perfis"
        periodo_meses = 24
        dados = self._coletar_dados_producao(periodo_meses)

        if not dados:
            return np.array([])

        df = pd.DataFrame(dados)

        # Agrupar por meses e calcular métricas
        df['mes_ano'] = pd.to_datetime(df['data']).dt.to_period('M')
        df_mensal = df.groupby('mes_ano').agg({
            'quantidade': ['sum', 'mean', 'std'],
        }).fillna(0)

        # Achatar colunas multi-nível
        df_mensal.columns = ['_'.join(col).strip() for col in df_mensal.columns]

        return df_mensal.values

    def _interpretar_cluster(self, dados_cluster: np.ndarray) -> Dict[str, Any]:
        """
        Interpreta características de um cluster
        """
        if dados_cluster.shape[0] == 0:
            return {}

        return {
            'media_quantidade': float(dados_cluster[:, 0].mean()),
            'variabilidade': float(dados_cluster[:, 0].std()),
            'tamanho_amostra': dados_cluster.shape[0]
        }

    def _calcular_silhouette_score(self, dados: np.ndarray, clusters: np.ndarray) -> float:
        """
        Calcula silhouette score para avaliar qualidade do clustering
        """
        try:
            from sklearn.metrics import silhouette_score
            return float(silhouette_score(dados, clusters))
        except:
            return 0.0