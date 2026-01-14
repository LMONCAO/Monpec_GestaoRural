# -*- coding: utf-8 -*-
"""
Machine Learning para Previsão de Natalidade e Mortalidade
Modelos preditivos baseados em dados históricos da propriedade
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
from django.db.models import Q, Avg, Count, Sum, F
from django.utils import timezone

from ..models import (
    MovimentacaoIndividual,
    MovimentacaoProjetada,
    InventarioRebanho,
    CategoriaAnimal,
    Propriedade
)

logger = logging.getLogger(__name__)


class MLNatalidadeMortalidadeService:
    """
    Serviço de Machine Learning para previsão de taxas de natalidade e mortalidade
    Usa dados históricos da propriedade para criar modelos preditivos
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

    def prever_taxa_natalidade(
        self,
        propriedade_id: int,
        categoria_mae: str,
        periodo_meses: int = 12
    ) -> Dict[str, Any]:
        """
        Previsão de taxa de natalidade baseada em dados históricos

        Args:
            propriedade_id: ID da propriedade
            categoria_mae: Categoria das matrizes (ex: 'Multípara')
            periodo_meses: Período para análise histórica

        Returns:
            Dicionário com previsões e métricas
        """
        try:
            # 1. Coletar dados históricos
            dados_historicos = self._coletar_dados_natalidade(
                propriedade_id, categoria_mae, periodo_meses
            )

            if len(dados_historicos) < 6:  # Mínimo 6 meses de dados
                return {
                    'sucesso': False,
                    'erro': 'Dados históricos insuficientes para previsão de natalidade'
                }

            # 2. Preparar dados para ML
            X, y = self._preparar_dados_natalidade_ml(dados_historicos)

            # 3. Treinar modelo e fazer previsões
            previsao = self._prever_natalidade_ml(X, y)

            # 4. Calcular métricas de confiança
            metricas = self._calcular_metricas_natalidade(X, y)

            return {
                'sucesso': True,
                'taxa_prevista': previsao,
                'taxa_historica_media': np.mean([d['taxa_natalidade'] for d in dados_historicos]),
                'metricas': metricas,
                'dados_historicos': len(dados_historicos),
                'categoria': categoria_mae,
                'periodo_analisado': periodo_meses
            }

        except Exception as e:
            logger.error(f'Erro na previsão de natalidade: {e}', exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def prever_taxa_mortalidade(
        self,
        propriedade_id: int,
        categoria: str,
        periodo_meses: int = 12
    ) -> Dict[str, Any]:
        """
        Previsão de taxa de mortalidade baseada em dados históricos
        """
        try:
            # 1. Coletar dados históricos
            dados_historicos = self._coletar_dados_mortalidade(
                propriedade_id, categoria, periodo_meses
            )

            if len(dados_historicos) < 6:
                return {
                    'sucesso': False,
                    'erro': 'Dados históricos insuficientes para previsão de mortalidade'
                }

            # 2. Preparar dados para ML
            X, y = self._preparar_dados_mortalidade_ml(dados_historicos)

            # 3. Treinar modelo e fazer previsões
            previsao = self._prever_mortalidade_ml(X, y)

            # 4. Calcular métricas de confiança
            metricas = self._calcular_metricas_mortalidade(X, y)

            return {
                'sucesso': True,
                'taxa_prevista': previsao,
                'taxa_historica_media': np.mean([d['taxa_mortalidade'] for d in dados_historicos]),
                'metricas': metricas,
                'dados_historicos': len(dados_historicos),
                'categoria': categoria,
                'periodo_analisado': periodo_meses
            }

        except Exception as e:
            logger.error(f'Erro na previsão de mortalidade: {e}', exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def _coletar_dados_natalidade(
        self,
        propriedade_id: int,
        categoria_mae: str,
        periodo_meses: int
    ) -> List[Dict]:
        """
        Coleta dados históricos de natalidade da propriedade
        """
        dados = []
        data_atual = timezone.now()

        # Buscar matrizes da categoria especificada
        try:
            categoria = CategoriaAnimal.objects.get(
                nome__icontains=categoria_mae,
                ativo=True
            )
        except CategoriaAnimal.DoesNotExist:
            return dados

        for meses_atras in range(periodo_meses):
            data_inicio = data_atual - timedelta(days=30 * (meses_atras + 1))
            data_fim = data_atual - timedelta(days=30 * meses_atras)

            # Contar matrizes no período
            matrizes_inicio = InventarioRebanho.objects.filter(
                propriedade_id=propriedade_id,
                categoria=categoria,
                data__lte=data_inicio
            ).aggregate(total=Sum('quantidade'))['total'] or 0

            # Contar nascimentos no período
            nascimentos = MovimentacaoIndividual.objects.filter(
                propriedade_id=propriedade_id,
                tipo_movimentacao='NASCIMENTO',
                data__gte=data_inicio,
                data__lt=data_fim
            ).count()

            # Calcular taxa de natalidade (nascimentos por matriz por mês)
            taxa_natalidade = 0
            if matrizes_inicio > 0:
                taxa_natalidade = nascimentos / matrizes_inicio

            dados.append({
                'data': data_inicio,
                'mes': data_inicio.month,
                'ano': data_inicio.year,
                'matrizes': matrizes_inicio,
                'nascimentos': nascimentos,
                'taxa_natalidade': taxa_natalidade,
                'categoria_mae': categoria_mae
            })

        return dados

    def _coletar_dados_mortalidade(
        self,
        propriedade_id: int,
        categoria: str,
        periodo_meses: int
    ) -> List[Dict]:
        """
        Coleta dados históricos de mortalidade da propriedade
        """
        dados = []
        data_atual = timezone.now()

        # Buscar categoria
        try:
            categoria_obj = CategoriaAnimal.objects.get(
                nome__icontains=categoria,
                ativo=True
            )
        except CategoriaAnimal.DoesNotExist:
            return dados

        for meses_atras in range(periodo_meses):
            data_inicio = data_atual - timedelta(days=30 * (meses_atras + 1))
            data_fim = data_atual - timedelta(days=30 * meses_atras)

            # Contar animais no início do período
            animais_inicio = InventarioRebanho.objects.filter(
                propriedade_id=propriedade_id,
                categoria=categoria_obj,
                data__lte=data_inicio
            ).aggregate(total=Sum('quantidade'))['total'] or 0

            # Contar mortes no período
            mortes = MovimentacaoIndividual.objects.filter(
                propriedade_id=propriedade_id,
                tipo_movimentacao='MORTE',
                categoria_animal=categoria_obj,
                data__gte=data_inicio,
                data__lt=data_fim
            ).count()

            # Calcular taxa de mortalidade
            taxa_mortalidade = 0
            if animais_inicio > 0:
                taxa_mortalidade = mortes / animais_inicio

            dados.append({
                'data': data_inicio,
                'mes': data_inicio.month,
                'ano': data_inicio.year,
                'animais_inicio': animais_inicio,
                'mortes': mortes,
                'taxa_mortalidade': taxa_mortalidade,
                'categoria': categoria
            })

        return dados

    def _preparar_dados_natalidade_ml(self, dados_historicos: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara dados de natalidade para algoritmos de ML
        """
        df = pd.DataFrame(dados_historicos)

        # Features: mês, ano, número de matrizes, sazonalidade
        df['mes_num'] = df['mes']
        df['ano_num'] = df['ano'] - df['ano'].min()
        df['matrizes_log'] = np.log1p(df['matrizes'])  # Log para normalizar

        # Features sazonais (época de monta: setembro a dezembro)
        df['epoca_monta'] = df['mes'].isin([9, 10, 11, 12]).astype(int)

        # Features: taxa do mês anterior
        df['taxa_anterior'] = df['taxa_natalidade'].shift(1).fillna(df['taxa_natalidade'].mean())

        # Remover NaN
        df = df.dropna()

        # Features (X) e target (y)
        features_cols = ['mes_num', 'ano_num', 'matrizes_log', 'epoca_monta', 'taxa_anterior']
        X = df[features_cols].values
        y = df['taxa_natalidade'].values

        return X, y

    def _preparar_dados_mortalidade_ml(self, dados_historicos: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara dados de mortalidade para algoritmos de ML
        """
        df = pd.DataFrame(dados_historicos)

        # Features: mês, ano, número de animais, idade da categoria
        df['mes_num'] = df['mes']
        df['ano_num'] = df['ano'] - df['ano'].min()
        df['animais_log'] = np.log1p(df['animais_inicio'])

        # Features sazonais (épocas críticas: verão/inverno)
        df['verao'] = df['mes'].isin([12, 1, 2]).astype(int)  # Verão brasileiro
        df['inverno'] = df['mes'].isin([6, 7, 8]).astype(int)  # Inverno

        # Features: taxa do mês anterior
        df['taxa_anterior'] = df['taxa_mortalidade'].shift(1).fillna(df['taxa_mortalidade'].mean())

        # Remover NaN
        df = df.dropna()

        # Features (X) e target (y)
        features_cols = ['mes_num', 'ano_num', 'animais_log', 'verao', 'inverno', 'taxa_anterior']
        X = df[features_cols].values
        y = df['taxa_mortalidade'].values

        return X, y

    def _prever_natalidade_ml(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Faz previsão de natalidade usando ensemble de modelos
        """
        if len(X) < 3:
            return np.mean(y)  # Média simples se poucos dados

        # Modelo 1: Regressão Linear
        modelo_linear = LinearRegression()
        modelo_linear.fit(X, y)
        pred_linear = modelo_linear.predict(X[-1].reshape(1, -1))[0]

        # Modelo 2: Random Forest
        modelo_rf = RandomForestRegressor(n_estimators=50, random_state=42)
        modelo_rf.fit(X, y)
        pred_rf = modelo_rf.predict(X[-1].reshape(1, -1))[0]

        # Ensemble: média ponderada
        previsao = (pred_rf * 0.7) + (pred_linear * 0.3)

        # Garantir limites realistas (0.5 a 1.2)
        previsao = np.clip(previsao, 0.5, 1.2)

        return float(previsao)

    def _prever_mortalidade_ml(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Faz previsão de mortalidade usando ensemble de modelos
        """
        if len(X) < 3:
            return np.mean(y)

        # Modelo 1: Regressão Linear
        modelo_linear = LinearRegression()
        modelo_linear.fit(X, y)
        pred_linear = modelo_linear.predict(X[-1].reshape(1, -1))[0]

        # Modelo 2: Random Forest
        modelo_rf = RandomForestRegressor(n_estimators=50, random_state=42)
        modelo_rf.fit(X, y)
        pred_rf = modelo_rf.predict(X[-1].reshape(1, -1))[0]

        # Ensemble: média ponderada
        previsao = (pred_rf * 0.7) + (pred_linear * 0.3)

        # Garantir limites realistas (0.01 a 0.15)
        previsao = np.clip(previsao, 0.01, 0.15)

        return float(previsao)

    def _calcular_metricas_natalidade(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Calcula métricas de confiança para o modelo de natalidade
        """
        try:
            if len(X) < 5:
                return {'amostras_insuficientes': True}

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )

            modelo = RandomForestRegressor(n_estimators=50, random_state=42)
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)

            erro_percentual_medio = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 0.01))) * 100

            return {
                'mae': round(float(mae), 4),
                'mse': round(float(mse), 6),
                'erro_percentual_medio': round(float(erro_percentual_medio), 2),
                'amostras_teste': len(y_test),
                'acuracia_esperada': max(0, 100 - erro_percentual_medio)
            }

        except Exception as e:
            logger.error(f'Erro ao calcular métricas de natalidade: {e}')
            return {'erro': 'Não foi possível calcular métricas'}

    def _calcular_metricas_mortalidade(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Calcula métricas de confiança para o modelo de mortalidade
        """
        try:
            if len(X) < 5:
                return {'amostras_insuficientes': True}

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )

            modelo = RandomForestRegressor(n_estimators=50, random_state=42)
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)

            erro_percentual_medio = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 0.001))) * 100

            return {
                'mae': round(float(mae), 4),
                'mse': round(float(mse), 6),
                'erro_percentual_medio': round(float(erro_percentual_medio), 2),
                'amostras_teste': len(y_test),
                'acuracia_esperada': max(0, 100 - erro_percentual_medio)
            }

        except Exception as e:
            logger.error(f'Erro ao calcular métricas de mortalidade: {e}')
            return {'erro': 'Não foi possível calcular métricas'}

    def analisar_fatores_risco(
        self,
        propriedade_id: int,
        categoria: str,
        periodo_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Análise avançada dos fatores que influenciam natalidade e mortalidade
        """
        try:
            # Dados de natalidade
            dados_nat = self._coletar_dados_natalidade(propriedade_id, categoria, periodo_meses)

            # Dados de mortalidade
            dados_mort = self._coletar_dados_mortalidade(propriedade_id, categoria, periodo_meses)

            if len(dados_nat) < 6 or len(dados_mort) < 6:
                return {'sucesso': False, 'erro': 'Dados insuficientes para análise'}

            # Análise estatística
            analise_natalidade = self._analisar_fatores_natalidade(dados_nat)
            analise_mortalidade = self._analisar_fatores_mortalidade(dados_mort)

            # Correlações entre variáveis
            correlacoes = self._calcular_correlacoes(dados_nat, dados_mort)

            return {
                'sucesso': True,
                'natalidade': analise_natalidade,
                'mortalidade': analise_mortalidade,
                'correlacoes': correlacoes,
                'periodo_analisado': periodo_meses
            }

        except Exception as e:
            logger.error(f'Erro na análise de fatores de risco: {e}')
            return {'sucesso': False, 'erro': str(e)}

    def _analisar_fatores_natalidade(self, dados: List[Dict]) -> Dict[str, Any]:
        """
        Análise estatística dos fatores que afetam a natalidade
        """
        df = pd.DataFrame(dados)

        # Média por mês (sazonalidade)
        media_mensal = df.groupby('mes')['taxa_natalidade'].mean()

        # Correlação entre número de matrizes e taxa
        correlacao_matrizes = df['matrizes'].corr(df['taxa_natalidade'])

        # Meses com melhor e pior natalidade
        melhor_mes = media_mensal.idxmax()
        pior_mes = media_mensal.idxmin()

        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        return {
            'taxa_media': round(float(df['taxa_natalidade'].mean()), 4),
            'taxa_desvio_padrao': round(float(df['taxa_natalidade'].std()), 4),
            'melhor_mes': melhor_mes,
            'melhor_mes_nome': meses_pt.get(melhor_mes, str(melhor_mes)),
            'pior_mes': pior_mes,
            'pior_mes_nome': meses_pt.get(pior_mes, str(pior_mes)),
            'correlacao_matrizes': round(float(correlacao_matrizes), 3),
            'variabilidade_sazonal': round(float(media_mensal.max() - media_mensal.min()), 4)
        }

    def _analisar_fatores_mortalidade(self, dados: List[Dict]) -> Dict[str, Any]:
        """
        Análise estatística dos fatores que afetam a mortalidade
        """
        df = pd.DataFrame(dados)

        # Média por mês (sazonalidade)
        media_mensal = df.groupby('mes')['taxa_mortalidade'].mean()

        # Correlação entre número de animais e taxa
        correlacao_animais = df['animais_inicio'].corr(df['taxa_mortalidade'])

        # Meses com maior e menor mortalidade
        pior_mes = media_mensal.idxmax()  # Maior mortalidade
        melhor_mes = media_mensal.idxmin()  # Menor mortalidade

        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        return {
            'taxa_media': round(float(df['taxa_mortalidade'].mean()), 4),
            'taxa_desvio_padrao': round(float(df['taxa_mortalidade'].std()), 4),
            'pior_mes': pior_mes,
            'pior_mes_nome': meses_pt.get(pior_mes, str(pior_mes)),
            'melhor_mes': melhor_mes,
            'melhor_mes_nome': meses_pt.get(melhor_mes, str(melhor_mes)),
            'correlacao_animais': round(float(correlacao_animais), 3),
            'variabilidade_sazonal': round(float(media_mensal.max() - media_mensal.min()), 4)
        }

    def _calcular_correlacoes(self, dados_nat: List[Dict], dados_mort: List[Dict]) -> Dict[str, Any]:
        """
        Calcula correlações entre natalidade e mortalidade
        """
        try:
            df_nat = pd.DataFrame(dados_nat)
            df_mort = pd.DataFrame(dados_mort)

            # Combinar dados por mês/ano
            df_combined = pd.merge(
                df_nat[['ano', 'mes', 'taxa_natalidade']],
                df_mort[['ano', 'mes', 'taxa_mortalidade']],
                on=['ano', 'mes'],
                how='inner'
            )

            if len(df_combined) < 3:
                return {'erro': 'Dados insuficientes para correlação'}

            correlacao = df_combined['taxa_natalidade'].corr(df_combined['taxa_mortalidade'])

            return {
                'natalidade_vs_mortalidade': round(float(correlacao), 3),
                'amostras_correlacao': len(df_combined),
                'interpretacao': self._interpretar_correlacao(correlacao)
            }

        except Exception as e:
            logger.error(f'Erro ao calcular correlações: {e}')
            return {'erro': 'Não foi possível calcular correlações'}

    def _interpretar_correlacao(self, correlacao: float) -> str:
        """
        Interpreta o valor da correlação
        """
        abs_corr = abs(correlacao)

        if abs_corr < 0.3:
            return 'Correlação fraca'
        elif abs_corr < 0.5:
            return 'Correlação moderada'
        elif abs_corr < 0.7:
            return 'Correlação forte'
        else:
            return 'Correlação muito forte'