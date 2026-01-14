# -*- coding: utf-8 -*-
"""
Módulo de Machine Learning para Previsão de Preços
Utiliza regressão linear, séries temporais e algoritmos de ML para prever preços
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, date, timedelta

from django.db.models import Avg, Count, Q
from django.utils import timezone

from gestao_rural.models import (
    PrecoCEPEA, PrecoIMEA, PrecoScot,
    MovimentacaoIndividual, MovimentacaoProjetada,
    InventarioRebanho, Propriedade
)

logger = logging.getLogger(__name__)


class PrevisaoPrecosML:
    """
    Sistema de Machine Learning para previsão de preços pecuários
    Utiliza múltiplas fontes de dados e algoritmos para previsões mais precisas
    """

    def __init__(self, propriedade: Propriedade):
        self.propriedade = propriedade
        self.modelos_treinados = {}
        self.scaler = StandardScaler()

    def treinar_modelos_previsao(
        self,
        uf: str,
        tipo_categoria: str,
        periodo_treinamento_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Treina modelos de ML para previsão de preços

        Args:
            uf: Estado
            tipo_categoria: Categoria do animal
            periodo_treinamento_meses: Período de dados para treinamento

        Returns:
            Dicionário com métricas dos modelos treinados
        """
        try:
            # Coletar dados históricos
            dados_historicos = self._coletar_dados_historicos_precos(
                uf, tipo_categoria, periodo_treinamento_meses
            )

            if not dados_historicos:
                return {'erro': 'Dados insuficientes para treinamento'}

            # Preparar dados para ML
            X, y, feature_names = self._preparar_dados_ml(dados_historicos)

            if len(X) < 10:  # Mínimo de dados necessário
                return {'erro': 'Dados insuficientes (mínimo 10 registros)'}

            # Dividir dados em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )

            # Treinar modelos
            resultados = {}

            # 1. Regressão Linear
            modelo_linear = LinearRegression()
            modelo_linear.fit(X_train, y_train)
            predicoes_linear = modelo_linear.predict(X_test)

            resultados['regressao_linear'] = {
                'modelo': modelo_linear,
                'mae': mean_absolute_error(y_test, predicoes_linear),
                'rmse': np.sqrt(mean_squared_error(y_test, predicoes_linear)),
                'r2': r2_score(y_test, predicoes_linear),
                'features_importance': dict(zip(feature_names, modelo_linear.coef_))
            }

            # 2. Random Forest
            modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
            modelo_rf.fit(X_train, y_train)
            predicoes_rf = modelo_rf.predict(X_test)

            resultados['random_forest'] = {
                'modelo': modelo_rf,
                'mae': mean_absolute_error(y_test, predicoes_rf),
                'rmse': np.sqrt(mean_squared_error(y_test, predicoes_rf)),
                'r2': r2_score(y_test, predicoes_rf),
                'features_importance': dict(zip(feature_names, modelo_rf.feature_importances_))
            }

            # 3. Modelo ARIMA para séries temporais
            modelo_arima = self._treinar_modelo_arima(y_train, y_test)
            if modelo_arima:
                resultados['arima'] = modelo_arima

            # Salvar modelos treinados
            self.modelos_treinados[f"{uf}_{tipo_categoria}"] = resultados

            return {
                'sucesso': True,
                'modelos': resultados,
                'dados_treinamento': len(X_train),
                'dados_teste': len(X_test),
                'melhor_modelo': self._selecionar_melhor_modelo(resultados)
            }

        except Exception as e:
            logger.error(f'Erro ao treinar modelos: {e}', exc_info=True)
            return {'erro': str(e)}

    def _coletar_dados_historicos_precos(
        self,
        uf: str,
        tipo_categoria: str,
        periodo_meses: int
    ) -> List[Dict]:
        """
        Coleta dados históricos de preços de múltiplas fontes
        """
        dados = []
        data_inicio = date.today() - timedelta(days=periodo_meses * 30)

        # 1. Dados CEPEA
        precos_cepea = PrecoCEPEA.objects.filter(
            uf=uf,
            tipo_categoria=tipo_categoria,
            criado_em__date__gte=data_inicio
        ).order_by('criado_em')

        for preco in precos_cepea:
            dados.append({
                'data': preco.criado_em.date(),
                'preco': float(preco.preco_medio),
                'fonte': 'CEPEA',
                'volume': preco.volume_negociado or 0,
                'tipo_categoria': tipo_categoria
            })

        # 2. Dados IMEA (se disponível)
        if uf in ['MT', 'MS']:
            precos_imea = PrecoIMEA.objects.filter(
                uf=uf,
                tipo_categoria=tipo_categoria,
                criado_em__date__gte=data_inicio
            ).order_by('criado_em')

            for preco in precos_imea:
                dados.append({
                    'data': preco.criado_em.date(),
                    'preco': float(preco.preco_medio),
                    'fonte': 'IMEA',
                    'volume': preco.volume_negociado or 0,
                    'tipo_categoria': tipo_categoria
                })

        # 3. Dados Scot Consultoria
        precos_scot = PrecoScot.objects.filter(
            uf=uf,
            tipo_categoria=tipo_categoria,
            criado_em__date__gte=data_inicio
        ).order_by('criado_em')

        for preco in precos_scot:
            dados.append({
                'data': preco.criado_em.date(),
                'preco': float(preco.preco_arroba),
                'fonte': 'SCOT',
                'volume': preco.volume_negociado or 0,
                'tipo_categoria': tipo_categoria
            })

        # Ordenar por data
        dados.sort(key=lambda x: x['data'])

        return dados

    def _preparar_dados_ml(self, dados_historicos: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepara dados para algoritmos de Machine Learning
        """
        if not dados_historicos:
            return np.array([]), np.array([]), []

        # Criar DataFrame
        df = pd.DataFrame(dados_historicos)

        # Features
        features = []

        # Preço anterior (lag de 1 mês)
        df['preco_anterior'] = df['preco'].shift(1)

        # Média móvel de 3 meses
        df['media_movel_3'] = df['preco'].rolling(window=3).mean()

        # Média móvel de 6 meses
        df['media_movel_6'] = df['preco'].rolling(window=6).mean()

        # Variação percentual
        df['variacao_percentual'] = df['preco'].pct_change()

        # Volume relativo
        df['volume_normalizado'] = (df['volume'] - df['volume'].mean()) / df['volume'].std()

        # Mês do ano (sazonalidade)
        df['mes'] = pd.to_datetime(df['data']).dt.month
        df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
        df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)

        # Dummy para fonte
        df['fonte_cepea'] = (df['fonte'] == 'CEPEA').astype(int)
        df['fonte_imea'] = (df['fonte'] == 'IMEA').astype(int)
        df['fonte_scot'] = (df['fonte'] == 'SCOT').astype(int)

        # Remover linhas com NaN
        df = df.dropna()

        # Definir features e target
        feature_columns = [
            'preco_anterior', 'media_movel_3', 'media_movel_6',
            'variacao_percentual', 'volume_normalizado',
            'mes_sin', 'mes_cos',
            'fonte_cepea', 'fonte_imea', 'fonte_scot'
        ]

        X = df[feature_columns].values
        y = df['preco'].values

        return X, y, feature_columns

    def _treinar_modelo_arima(self, y_train: np.ndarray, y_test: np.ndarray) -> Optional[Dict]:
        """
        Treina modelo ARIMA para séries temporais
        """
        try:
            # Ajustar modelo ARIMA
            modelo_arima = ARIMA(y_train, order=(1, 1, 1))
            modelo_fit = modelo_arima.fit()

            # Fazer previsões
            predicoes = modelo_fit.forecast(steps=len(y_test))

            return {
                'modelo': modelo_fit,
                'mae': mean_absolute_error(y_test, predicoes),
                'rmse': np.sqrt(mean_squared_error(y_test, predicoes)),
                'predicoes': predicoes
            }

        except Exception as e:
            logger.warning(f'Erro ao treinar ARIMA: {e}')
            return None

    def _selecionar_melhor_modelo(self, resultados: Dict) -> str:
        """
        Seleciona o melhor modelo baseado nas métricas
        """
        melhor_modelo = None
        melhor_r2 = -float('inf')

        for nome_modelo, dados in resultados.items():
            r2 = dados.get('r2', -float('inf'))
            if r2 > melhor_r2:
                melhor_r2 = r2
                melhor_modelo = nome_modelo

        return melhor_modelo

    def prever_preco_futuro(
        self,
        uf: str,
        tipo_categoria: str,
        meses_a_frente: int = 6,
        usar_melhor_modelo: bool = True
    ) -> Dict[str, Any]:
        """
        Faz previsões de preços futuros usando os modelos treinados

        Args:
            uf: Estado
            tipo_categoria: Categoria do animal
            meses_a_frente: Número de meses para prever
            usar_melhor_modelo: Usar o melhor modelo ou todos

        Returns:
            Dicionário com previsões
        """
        chave_modelo = f"{uf}_{tipo_categoria}"

        if chave_modelo not in self.modelos_treinados:
            # Tentar treinar modelos automaticamente
            resultado_treinamento = self.treinar_modelos_previsao(uf, tipo_categoria)
            if not resultado_treinamento.get('sucesso'):
                return {'erro': 'Não foi possível treinar modelos'}

        modelos = self.modelos_treinados[chave_modelo]

        if usar_melhor_modelo:
            melhor_modelo = self._selecionar_melhor_modelo(modelos)
            return self._prever_com_modelo_especifico(
                modelos[melhor_modelo]['modelo'],
                uf, tipo_categoria, meses_a_frente,
                melhor_modelo
            )
        else:
            # Usar todos os modelos
            previsoes = {}
            for nome_modelo, dados_modelo in modelos.items():
                previsao = self._prever_com_modelo_especifico(
                    dados_modelo['modelo'],
                    uf, tipo_categoria, meses_a_frente,
                    nome_modelo
                )
                if 'previsoes' in previsao:
                    previsoes[nome_modelo] = previsao['previsoes']

            return {
                'previsoes_por_modelo': previsoes,
                'melhor_modelo': self._selecionar_melhor_modelo(modelos)
            }

    def _prever_com_modelo_especifico(
        self,
        modelo,
        uf: str,
        tipo_categoria: str,
        meses_a_frente: int,
        nome_modelo: str
    ) -> Dict[str, Any]:
        """
        Faz previsão usando um modelo específico
        """
        try:
            previsoes = []

            # Obter dados mais recentes para base da previsão
            dados_recentes = self._coletar_dados_historicos_precos(uf, tipo_categoria, 12)

            if not dados_recentes:
                return {'erro': 'Dados insuficientes para previsão'}

            # Para modelos de regressão, criar features futuras
            if nome_modelo in ['regressao_linear', 'random_forest']:
                # Usar os últimos dados como base
                ultimo_dado = dados_recentes[-1]

                for i in range(1, meses_a_frente + 1):
                    data_futura = date.today() + timedelta(days=i * 30)

                    # Criar features para o mês futuro
                    features = self._criar_features_futuras(ultimo_dado, data_futura, uf)

                    # Fazer previsão
                    preco_previsto = modelo.predict([features])[0]

                    previsoes.append({
                        'mes': data_futura.month,
                        'ano': data_futura.year,
                        'preco_previsto': float(preco_previsto),
                        'fonte_modelo': nome_modelo
                    })

                    # Atualizar último dado para próxima iteração
                    ultimo_dado = {
                        'data': data_futura,
                        'preco': preco_previsto,
                        'fonte': 'PREVISAO',
                        'volume': ultimo_dado['volume'],
                        'tipo_categoria': tipo_categoria
                    }

            elif nome_modelo == 'arima':
                # Para ARIMA, usar forecast direto
                predicoes_arima = modelo.forecast(steps=meses_a_frente)

                for i, preco in enumerate(predicoes_arima):
                    data_futura = date.today() + timedelta(days=(i + 1) * 30)
                    previsoes.append({
                        'mes': data_futura.month,
                        'ano': data_futura.year,
                        'preco_previsto': float(preco),
                        'fonte_modelo': 'arima'
                    })

            return {
                'previsoes': previsoes,
                'modelo_usado': nome_modelo,
                'meses_previsao': meses_a_frente
            }

        except Exception as e:
            logger.error(f'Erro na previsão: {e}')
            return {'erro': str(e)}

    def _criar_features_futuras(
        self,
        ultimo_dado: Dict,
        data_futura: date,
        uf: str
    ) -> List[float]:
        """
        Cria features para previsão futura baseada no último dado conhecido
        """
        preco_anterior = ultimo_dado['preco']
        volume_normalizado = 0  # Usar média

        # Mês futuro
        mes = data_futura.month
        mes_sin = np.sin(2 * np.pi * mes / 12)
        mes_cos = np.cos(2 * np.pi * mes / 12)

        # Assumir fonte CEPEA como padrão
        fonte_cepea = 1
        fonte_imea = 0
        fonte_scot = 0

        # Features na ordem correta
        features = [
            preco_anterior,  # preco_anterior
            preco_anterior,  # media_movel_3 (aproximação)
            preco_anterior,  # media_movel_6 (aproximação)
            0.0,            # variacao_percentual (neutra)
            volume_normalizado,
            mes_sin,
            mes_cos,
            fonte_cepea,
            fonte_imea,
            fonte_scot
        ]

        return features

    def analisar_tendencias_mercado(
        self,
        uf: str,
        tipo_categoria: str
    ) -> Dict[str, Any]:
        """
        Analisa tendências do mercado usando ML

        Args:
            uf: Estado
            tipo_categoria: Categoria do animal

        Returns:
            Análise de tendências
        """
        try:
            # Coletar dados históricos
            dados = self._coletar_dados_historicos_precos(uf, tipo_categoria, 24)

            if not dados:
                return {'erro': 'Dados insuficientes'}

            # Criar DataFrame
            df = pd.DataFrame(dados)

            # Calcular métricas
            analise = {
                'tendencia_geral': self._calcular_tendencia(df),
                'volatilidade': self._calcular_volatilidade(df),
                'sazonalidade': self._detectar_sazonalidade(df),
                'ciclos_identificados': self._identificar_ciclos(df),
                'previsao_curto_prazo': self.prever_preco_futuro(uf, tipo_categoria, 3),
            }

            return analise

        except Exception as e:
            logger.error(f'Erro na análise de tendências: {e}')
            return {'erro': str(e)}

    def _calcular_tendencia(self, df: pd.DataFrame) -> str:
        """Calcula tendência geral dos preços"""
        if len(df) < 2:
            return 'INSUFICIENTE'

        # Regressão linear simples
        x = np.arange(len(df))
        y = df['preco'].values

        slope = np.polyfit(x, y, 1)[0]

        if slope > 0.1:
            return 'CRESCENTE'
        elif slope < -0.1:
            return 'DECRESCENTE'
        else:
            return 'ESTAVEL'

    def _calcular_volatilidade(self, df: pd.DataFrame) -> float:
        """Calcula volatilidade dos preços"""
        if len(df) < 2:
            return 0.0

        # Desvio padrão das variações percentuais
        variacoes = df['preco'].pct_change().dropna()
        return float(variacoes.std())

    def _detectar_sazonalidade(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta padrões sazonais"""
        if len(df) < 12:
            return {'detectada': False, 'meses_alta': [], 'meses_baixa': []}

        # Agrupar por mês
        df['mes'] = pd.to_datetime(df['data']).dt.month
        media_por_mes = df.groupby('mes')['preco'].mean()

        # Identificar meses de alta e baixa
        media_geral = media_por_mes.mean()
        meses_alta = media_por_mes[media_por_mes > media_geral].index.tolist()
        meses_baixa = media_por_mes[media_por_mes < media_geral].index.tolist()

        return {
            'detectada': True,
            'meses_alta': meses_alta,
            'meses_baixa': meses_baixa,
            'intensidade': float((media_por_mes.max() - media_por_mes.min()) / media_geral)
        }

    def _identificar_ciclos(self, df: pd.DataFrame) -> List[Dict]:
        """Identifica ciclos nos preços"""
        # Implementação básica - detectar pontos de inflexão
        ciclos = []

        if len(df) < 10:
            return ciclos

        precos = df['preco'].values

        # Detectar mudanças de direção
        for i in range(2, len(precos) - 2):
            # Verificar se é ponto de máximo ou mínimo local
            if (precos[i] > precos[i-1] and precos[i] > precos[i+1]) or \
               (precos[i] < precos[i-1] and precos[i] < precos[i+1]):
                ciclos.append({
                    'data': df.iloc[i]['data'].isoformat(),
                    'preco': float(precos[i]),
                    'tipo': 'MAXIMO' if precos[i] > precos[i-1] else 'MINIMO'
                })

        return ciclos