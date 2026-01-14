# -*- coding: utf-8 -*-
"""
Machine Learning para Previsão de Preços de Mercado
Sistema avançado de previsão usando séries temporais e regressão
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from django.db.models import Avg, Count, Max, Min, Sum
from django.utils import timezone

from ..models import PrecoCEPEA, MovimentacaoIndividual, CategoriaAnimal
from ..apis_integracao.api_cepea import CEPEAService

logger = logging.getLogger(__name__)


class MLPricePredictionService:
    """
    Serviço de Machine Learning para previsão de preços de mercado
    Usa múltiplos algoritmos para máxima precisão
    """

    def __init__(self):
        self.cepea_service = CEPEAService()
        self.scaler = StandardScaler()

    def prever_precos_futuros(
        self,
        uf: str,
        categoria: str,
        meses_a_frente: int = 6,
        metodo: str = 'ensemble'
    ) -> Dict[str, Any]:
        """
        Previsão avançada de preços usando ensemble de algoritmos

        Args:
            uf: Estado (ex: 'MT', 'MS')
            categoria: Categoria animal
            meses_a_frente: Quantos meses prever
            metodo: 'linear', 'rf', 'arima', 'ensemble'

        Returns:
            Dicionário com previsões e métricas
        """
        try:
            # 1. Coletar dados históricos
            dados_historicos = self._coletar_dados_historicos(uf, categoria)

            if len(dados_historicos) < 12:  # Mínimo 1 ano de dados
                return {
                    'sucesso': False,
                    'erro': 'Dados históricos insuficientes para previsão'
                }

            # 2. Preparar dados para ML
            X, y = self._preparar_dados_ml(dados_historicos)

            # 3. Treinar modelos e fazer previsões
            if metodo == 'ensemble':
                previsoes = self._prever_com_ensemble(X, y, meses_a_frente)
            elif metodo == 'linear':
                previsoes = self._prever_com_regressao_linear(X, y, meses_a_frente)
            elif metodo == 'rf':
                previsoes = self._prever_com_random_forest(X, y, meses_a_frente)
            elif metodo == 'arima':
                previsoes = self._prever_com_arima(dados_historicos, meses_a_frente)
            else:
                return {'sucesso': False, 'erro': 'Método não reconhecido'}

            # 4. Calcular métricas de confiança
            metricas = self._calcular_metricas_confianca(X, y, previsoes)

            return {
                'sucesso': True,
                'previsoes': previsoes,
                'metricas': metricas,
                'dados_historicos': len(dados_historicos),
                'metodo': metodo,
                'periodo': meses_a_frente
            }

        except Exception as e:
            logger.error(f'Erro na previsão de preços: {e}', exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def _coletar_dados_historicos(self, uf: str, categoria: str) -> List[Dict]:
        """
        Coleta dados históricos de preços do CEPEA
        """
        dados = []

        # Buscar dados dos últimos 5 anos
        ano_atual = timezone.now().year
        for ano in range(ano_atual - 5, ano_atual + 1):
            for mes in range(1, 13):
                try:
                    preco = self.cepea_service.obter_preco_por_categoria(
                        uf, ano, categoria
                    )

                    if preco:
                        data = datetime(ano, mes, 1)
                        dados.append({
                            'data': data,
                            'ano': ano,
                            'mes': mes,
                            'preco': float(preco),
                            'uf': uf,
                            'categoria': categoria
                        })

                except Exception as e:
                    logger.debug(f'Erro ao buscar preço {uf}-{categoria}-{ano}-{mes}: {e}')
                    continue

        # Ordenar por data
        dados.sort(key=lambda x: x['data'])
        return dados

    def _preparar_dados_ml(self, dados_historicos: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara dados para algoritmos de Machine Learning
        """
        df = pd.DataFrame(dados_historicos)

        # Features: ano, mês, tendência temporal
        df['mes_num'] = df['mes']
        df['ano_num'] = df['ano'] - df['ano'].min()  # Normalizar anos
        df['tempo'] = range(len(df))  # Tendência temporal

        # Features sazonais (dummy variables para meses)
        for mes in range(1, 13):
            df[f'mes_{mes}'] = (df['mes'] == mes).astype(int)

        # Features: preço do mês anterior (se disponível)
        df['preco_anterior'] = df['preco'].shift(1).fillna(df['preco'].mean())

        # Remover primeiras linhas com NaN
        df = df.dropna()

        # Features (X) e target (y)
        features_cols = ['ano_num', 'tempo', 'preco_anterior'] + [f'mes_{i}' for i in range(1, 13)]
        X = df[features_cols].values
        y = df['preco'].values

        return X, y

    def _prever_com_ensemble(
        self,
        X: np.ndarray,
        y: np.ndarray,
        meses_a_frente: int
    ) -> List[Dict]:
        """
        Previsão usando ensemble de modelos (média ponderada)
        """
        previsoes = []

        # Modelo 1: Regressão Linear
        modelo_linear = LinearRegression()
        modelo_linear.fit(X, y)

        # Modelo 2: Random Forest
        modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo_rf.fit(X, y)

        # Fazer previsões para cada mês futuro
        data_atual = datetime.now()

        for i in range(1, meses_a_frente + 1):
            data_futura = data_atual + timedelta(days=30 * i)

            # Preparar features para o mês futuro
            features_futuras = self._preparar_features_futuras(X, data_futura)

            # Previsões individuais
            pred_linear = modelo_linear.predict(features_futuras.reshape(1, -1))[0]
            pred_rf = modelo_rf.predict(features_futuras.reshape(1, -1))[0]

            # Ensemble: média ponderada (70% RF, 30% Linear)
            preco_previsto = (pred_rf * 0.7) + (pred_linear * 0.3)

            previsoes.append({
                'data': data_futura.strftime('%Y-%m-%d'),
                'mes': data_futura.month,
                'ano': data_futura.year,
                'preco_previsto': round(float(preco_previsto), 2),
                'preco_linear': round(float(pred_linear), 2),
                'preco_rf': round(float(pred_rf), 2),
                'confianca': self._calcular_confianca_individual(pred_linear, pred_rf)
            })

        return previsoes

    def _prever_com_regressao_linear(
        self,
        X: np.ndarray,
        y: np.ndarray,
        meses_a_frente: int
    ) -> List[Dict]:
        """
        Previsão usando apenas regressão linear
        """
        modelo = LinearRegression()
        modelo.fit(X, y)

        previsoes = []
        data_atual = datetime.now()

        for i in range(1, meses_a_frente + 1):
            data_futura = data_atual + timedelta(days=30 * i)
            features = self._preparar_features_futuras(X, data_futura)

            preco_previsto = modelo.predict(features.reshape(1, -1))[0]

            previsoes.append({
                'data': data_futura.strftime('%Y-%m-%d'),
                'mes': data_futura.month,
                'ano': data_futura.year,
                'preco_previsto': round(float(preco_previsto), 2),
                'confianca': 0.7  # Confiança média para regressão linear
            })

        return previsoes

    def _prever_com_random_forest(
        self,
        X: np.ndarray,
        y: np.ndarray,
        meses_a_frente: int
    ) -> List[Dict]:
        """
        Previsão usando Random Forest
        """
        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X, y)

        previsoes = []
        data_atual = datetime.now()

        for i in range(1, meses_a_frente + 1):
            data_futura = data_atual + timedelta(days=30 * i)
            features = self._preparar_features_futuras(X, data_futura)

            preco_previsto = modelo.predict(features.reshape(1, -1))[0]

            previsoes.append({
                'data': data_futura.strftime('%Y-%m-%d'),
                'mes': data_futura.month,
                'ano': data_futura.year,
                'preco_previsto': round(float(preco_previsto), 2),
                'confianca': 0.8  # RF geralmente tem melhor confiança
            })

        return previsoes

    def _prever_com_arima(
        self,
        dados_historicos: List[Dict],
        meses_a_frente: int
    ) -> List[Dict]:
        """
        Previsão usando modelo ARIMA para séries temporais
        """
        try:
            # Preparar série temporal
            df = pd.DataFrame(dados_historicos)
            df['data'] = pd.to_datetime(df['data'])
            df = df.set_index('data')
            serie_precos = df['preco']

            # Treinar modelo ARIMA
            modelo = ARIMA(serie_precos, order=(1, 1, 1))
            modelo_fit = modelo.fit()

            # Fazer previsões
            previsoes_arima = modelo_fit.forecast(steps=meses_a_frente)

            previsoes = []
            data_atual = datetime.now()

            for i in range(meses_a_frente):
                data_futura = data_atual + timedelta(days=30 * (i + 1))

                previsoes.append({
                    'data': data_futura.strftime('%Y-%m-%d'),
                    'mes': data_futura.month,
                    'ano': data_futura.year,
                    'preco_previsto': round(float(previsoes_arima.iloc[i]), 2),
                    'confianca': 0.75  # Confiança típica do ARIMA
                })

            return previsoes

        except Exception as e:
            logger.error(f'Erro no modelo ARIMA: {e}')
            # Fallback para regressão linear
            return self._prever_com_regressao_linear(
                *self._preparar_dados_ml(dados_historicos),
                meses_a_frente
            )

    def _preparar_features_futuras(self, X_historico: np.ndarray, data_futura: datetime) -> np.ndarray:
        """
        Prepara features para previsão futura
        """
        # Última linha histórica como base
        ultima_linha = X_historico[-1].copy()

        # Atualizar features temporais
        ano_base = 2023  # Ajustar conforme necessário
        ultima_linha[0] = data_futura.year - ano_base  # ano_num
        ultima_linha[1] = ultima_linha[1] + 1  # tempo (incrementar)

        # Preço anterior (usar último preço conhecido)
        ultima_linha[2] = ultima_linha[2]  # Manter preço anterior

        # Resetar dummies de mês
        for i in range(3, 15):  # Índices 3-14 são os meses
            ultima_linha[i] = 0

        # Ativar dummy do mês futuro
        mes_index = 3 + (data_futura.month - 1)  # mes_1 está no índice 3
        if 3 <= mes_index <= 14:
            ultima_linha[mes_index] = 1

        return ultima_linha

    def _calcular_confianca_individual(self, pred1: float, pred2: float) -> float:
        """
        Calcula confiança baseada na concordância entre modelos
        """
        # Quanto mais próximos os modelos, maior a confiança
        diferenca_percentual = abs(pred1 - pred2) / max(pred1, pred2)

        if diferenca_percentual < 0.05:  # < 5% diferença
            return 0.9
        elif diferenca_percentual < 0.1:  # < 10% diferença
            return 0.8
        elif diferenca_percentual < 0.2:  # < 20% diferença
            return 0.7
        else:
            return 0.6

    def _calcular_metricas_confianca(
        self,
        X: np.ndarray,
        y: np.ndarray,
        previsoes: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calcula métricas de confiança do modelo usando validação cruzada
        """
        try:
            # Dividir dados para validação
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Treinar modelo
            modelo = RandomForestRegressor(n_estimators=100, random_state=42)
            modelo.fit(X_train, y_train)

            # Fazer previsões no conjunto de teste
            y_pred = modelo.predict(X_test)

            # Calcular métricas
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)

            # Calcular erro percentual médio
            erro_percentual_medio = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

            return {
                'mae': round(float(mae), 2),
                'rmse': round(float(rmse), 2),
                'erro_percentual_medio': round(float(erro_percentual_medio), 2),
                'amostras_teste': len(y_test),
                'acuracia_esperada': max(0, 100 - erro_percentual_medio)
            }

        except Exception as e:
            logger.error(f'Erro ao calcular métricas: {e}')
            return {
                'erro': 'Não foi possível calcular métricas de confiança'
            }

    def analisar_tendencias_mercado(
        self,
        uf: str,
        categoria: str,
        periodo_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Análise avançada de tendências de mercado usando estatísticas
        """
        try:
            # Coletar dados históricos
            dados = self._coletar_dados_historicos(uf, categoria)

            if len(dados) < 12:
                return {'sucesso': False, 'erro': 'Dados insuficientes'}

            df = pd.DataFrame(dados)
            df['data'] = pd.to_datetime(df['data'])
            df = df.set_index('data')

            # Análise de tendência
            tendencia = self._calcular_tendencia(df['preco'])

            # Análise sazonal
            sazonalidade = self._analisar_sazonalidade(df)

            # Volatilidade
            volatilidade = self._calcular_volatilidade(df['preco'])

            # Previsão de curto prazo (3 meses)
            previsao_curto = self.prever_precos_futuros(uf, categoria, 3, 'ensemble')

            return {
                'sucesso': True,
                'tendencia': tendencia,
                'sazonalidade': sazonalidade,
                'volatilidade': volatilidade,
                'previsao_curto_prazo': previsao_curto,
                'periodo_analisado': periodo_meses
            }

        except Exception as e:
            logger.error(f'Erro na análise de tendências: {e}')
            return {'sucesso': False, 'erro': str(e)}

    def _calcular_tendencia(self, serie_precos: pd.Series) -> Dict[str, Any]:
        """
        Calcula tendência linear dos preços
        """
        x = np.arange(len(serie_precos))
        y = serie_precos.values

        # Regressão linear
        coef = np.polyfit(x, y, 1)
        tendencia_anual = coef[0] * 12  # Variação mensal × 12

        return {
            'direcao': 'alta' if tendencia_anual > 0 else 'baixa',
            'variacao_mensal': round(float(coef[0]), 2),
            'variacao_anual': round(float(tendencia_anual), 2),
            'variacao_percentual_anual': round(float((tendencia_anual / serie_precos.iloc[0]) * 100), 2)
        }

    def _analisar_sazonalidade(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analisa padrões sazonais nos preços
        """
        # Média por mês
        media_mensal = df.groupby(df.index.month)['preco'].mean()

        # Meses de alta e baixa
        mes_alta = media_mensal.idxmax()
        mes_baixa = media_mensal.idxmin()

        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        return {
            'melhor_mes': mes_alta,
            'melhor_mes_nome': meses_pt.get(mes_alta, str(mes_alta)),
            'pior_mes': mes_baixa,
            'pior_mes_nome': meses_pt.get(mes_baixa, str(mes_baixa)),
            'amplitude_sazonal': round(float(media_mensal.max() - media_mensal.min()), 2)
        }

    def _calcular_volatilidade(self, serie_precos: pd.Series) -> Dict[str, Any]:
        """
        Calcula volatilidade histórica dos preços
        """
        # Retornos percentuais
        retornos = serie_precos.pct_change().dropna()

        # Volatilidade mensal e anual
        vol_mensal = retornos.std()
        vol_anual = vol_mensal * np.sqrt(12)

        return {
            'volatilidade_mensal': round(float(vol_mensal), 4),
            'volatilidade_anual': round(float(vol_anual), 4),
            'volatilidade_percentual': round(float(vol_anual * 100), 2)
        }