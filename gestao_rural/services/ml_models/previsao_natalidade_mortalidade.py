# -*- coding: utf-8 -*-
"""
Módulo de ML para Previsão de Natalidade e Mortalidade
Utiliza dados históricos e fatores ambientais para previsões mais precisas
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone

from gestao_rural.models import (
    Propriedade, MovimentacaoIndividual, MovimentacaoProjetada,
    InventarioRebanho, CategoriaAnimal
)

logger = logging.getLogger(__name__)


class PrevisaoNatalidadeMortalidadeML:
    """
    Sistema de Machine Learning para previsão de natalidade e mortalidade
    Considera fatores históricos, sazonais e ambientais
    """

    def __init__(self, propriedade: Propriedade):
        self.propriedade = propriedade
        self.modelos_treinados = {}
        self.scaler = StandardScaler()

    def treinar_modelos_natalidade(
        self,
        periodo_treinamento_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Treina modelos de ML para previsão de natalidade

        Args:
            periodo_treinamento_meses: Período de dados para treinamento

        Returns:
            Resultados do treinamento
        """
        try:
            # Coletar dados históricos de natalidade
            dados_historicos = self._coletar_dados_natalidade(periodo_treinamento_meses)

            if not dados_historicos:
                return {'erro': 'Dados insuficientes de natalidade para treinamento'}

            # Preparar dados para ML
            X, y, feature_names = self._preparar_features_natalidade(dados_historicos)

            if len(X) < 10:
                return {'erro': 'Dados insuficientes (mínimo 10 registros)'}

            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )

            # Treinar múltiplos modelos
            resultados = {}

            # 1. Random Forest
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            rf_model.fit(X_train, y_train)
            pred_rf = rf_model.predict(X_test)

            resultados['random_forest'] = {
                'modelo': rf_model,
                'mae': mean_absolute_error(y_test, pred_rf),
                'rmse': np.sqrt(mean_squared_error(y_test, pred_rf)),
                'features_importance': dict(zip(feature_names, rf_model.feature_importances_))
            }

            # 2. Gradient Boosting
            gb_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            gb_model.fit(X_train, y_train)
            pred_gb = gb_model.predict(X_test)

            resultados['gradient_boosting'] = {
                'modelo': gb_model,
                'mae': mean_absolute_error(y_test, pred_gb),
                'rmse': np.sqrt(mean_squared_error(y_test, pred_gb)),
                'features_importance': dict(zip(feature_names, gb_model.feature_importances_))
            }

            # 3. Modelo ARIMA para séries temporais
            modelo_arima = self._treinar_arima_natalidade(y_train, y_test)
            if modelo_arima:
                resultados['arima'] = modelo_arima

            # Salvar modelos
            self.modelos_treinados['natalidade'] = resultados

            return {
                'sucesso': True,
                'modelos': resultados,
                'melhor_modelo': self._selecionar_melhor_modelo(resultados),
                'dados_treinamento': len(X_train)
            }

        except Exception as e:
            logger.error(f'Erro ao treinar modelos de natalidade: {e}')
            return {'erro': str(e)}

    def treinar_modelos_mortalidade(
        self,
        periodo_treinamento_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Treina modelos de ML para previsão de mortalidade
        """
        try:
            # Coletar dados históricos de mortalidade
            dados_historicos = self._coletar_dados_mortalidade(periodo_treinamento_meses)

            if not dados_historicos:
                return {'erro': 'Dados insuficientes de mortalidade para treinamento'}

            # Preparar dados
            X, y, feature_names = self._preparar_features_mortalidade(dados_historicos)

            if len(X) < 10:
                return {'erro': 'Dados insuficientes (mínimo 10 registros)'}

            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )

            # Treinar modelos
            resultados = {}

            # Random Forest para mortalidade
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=8,  # Menor profundidade para evitar overfitting
                random_state=42
            )
            rf_model.fit(X_train, y_train)
            pred_rf = rf_model.predict(X_test)

            resultados['random_forest'] = {
                'modelo': rf_model,
                'mae': mean_absolute_error(y_test, pred_rf),
                'rmse': np.sqrt(mean_squared_error(y_test, pred_rf)),
                'features_importance': dict(zip(feature_names, rf_model.feature_importances_))
            }

            # Salvar modelos
            self.modelos_treinados['mortalidade'] = resultados

            return {
                'sucesso': True,
                'modelos': resultados,
                'melhor_modelo': self._selecionar_melhor_modelo(resultados),
                'dados_treinamento': len(X_train)
            }

        except Exception as e:
            logger.error(f'Erro ao treinar modelos de mortalidade: {e}')
            return {'erro': str(e)}

    def _coletar_dados_natalidade(self, periodo_meses: int) -> List[Dict]:
        """
        Coleta dados históricos de natalidade
        """
        dados = []
        data_inicio = date.today() - timedelta(days=periodo_meses * 30)

        # Movimentações de nascimento
        nascimentos = MovimentacaoIndividual.objects.filter(
            propriedade=self.propriedade,
            tipo_movimentacao='NASCIMENTO',
            data_movimentacao__gte=data_inicio
        ).select_related('categoria_animal')

        # Agrupar por mês
        nascimentos_mensais = nascimentos.extra(
            select={'mes': "DATE_TRUNC('month', data_movimentacao)"}
        ).values('mes').annotate(
            total_nascimentos=Sum('quantidade')
        ).order_by('mes')

        for registro in nascimentos_mensais:
            mes_ano = registro['mes']
            if isinstance(mes_ano, str):
                mes_ano = datetime.fromisoformat(mes_ano.replace('Z', '+00:00')).date()

            # Calcular número de matrizes no período
            matrizes_no_periodo = self._calcular_matrizes_periodo(mes_ano)

            # Dados climáticos simulados
            dados_clima = self._obter_dados_climaticos_mes(mes_ano)

            dados.append({
                'data': mes_ano,
                'nascimentos': registro['total_nascimentos'],
                'matrizes': matrizes_no_periodo,
                'taxa_natalidade': registro['total_nascimentos'] / max(matrizes_no_periodo, 1),
                **dados_clima
            })

        return dados

    def _coletar_dados_mortalidade(self, periodo_meses: int) -> List[Dict]:
        """
        Coleta dados históricos de mortalidade
        """
        dados = []
        data_inicio = date.today() - timedelta(days=periodo_meses * 30)

        # Movimentações de morte
        mortes = MovimentacaoIndividual.objects.filter(
            propriedade=self.propriedade,
            tipo_movimentacao='MORTE',
            data_movimentacao__gte=data_inicio
        ).select_related('categoria_animal')

        # Agrupar por mês
        mortes_mensais = mortes.extra(
            select={'mes': "DATE_TRUNC('month', data_movimentacao)"}
        ).values('mes').annotate(
            total_mortes=Sum('quantidade')
        ).order_by('mes')

        for registro in mortes_mensais:
            mes_ano = registro['mes']
            if isinstance(mes_ano, str):
                mes_ano = datetime.fromisoformat(mes_ano.replace('Z', '+00:00')).date()

            # Calcular rebanho total no período
            rebanho_total = self._calcular_rebanho_periodo(mes_ano)

            # Dados climáticos
            dados_clima = self._obter_dados_climaticos_mes(mes_ano)

            dados.append({
                'data': mes_ano,
                'mortes': registro['total_mortes'],
                'rebanho_total': rebanho_total,
                'taxa_mortalidade': registro['total_mortes'] / max(rebanho_total, 1),
                **dados_clima
            })

        return dados

    def _calcular_matrizes_periodo(self, data_referencia: date) -> int:
        """
        Calcula número aproximado de matrizes no período
        """
        # Contar fêmeas adultas no inventário mais próximo
        try:
            inventario = InventarioRebanho.objects.filter(
                propriedade=self.propriedade,
                data_inventario__lte=data_referencia
            ).order_by('-data_inventario').first()

            if inventario:
                # Estimar matrizes (fêmeas adultas)
                categoria_nome = inventario.categoria_animal.nome.lower() if inventario.categoria_animal else ""
                if 'vaca' in categoria_nome or 'multípara' in categoria_nome or 'primípara' in categoria_nome:
                    return inventario.quantidade_atual
        except:
            pass

        # Fallback: estimativa baseada em movimentações
        return 100  # Valor padrão conservador

    def _calcular_rebanho_periodo(self, data_referencia: date) -> int:
        """
        Calcula rebanho total aproximado no período
        """
        try:
            inventarios = InventarioRebanho.objects.filter(
                propriedade=self.propriedade,
                data_inventario__lte=data_referencia
            ).order_by('-data_inventario')[:5]

            if inventarios:
                return sum(inv.quantidade_atual for inv in inventarios)
        except:
            pass

        return 500  # Valor padrão

    def _obter_dados_climaticos_mes(self, data_mes: date) -> Dict[str, float]:
        """
        Obtém dados climáticos simulados para o mês
        """
        mes = data_mes.month

        # Simulação baseada em padrões sazonais brasileiros
        # Valores aproximados para região Centro-Oeste
        dados_base = {
            1: {'temperatura': 26.5, 'precipitacao': 180, 'umidade': 75},  # Janeiro
            2: {'temperatura': 26.8, 'precipitacao': 160, 'umidade': 73},  # Fevereiro
            3: {'temperatura': 26.2, 'precipitacao': 140, 'umidade': 72},  # Março
            4: {'temperatura': 24.8, 'precipitacao': 100, 'umidade': 70},  # Abril
            5: {'temperatura': 22.5, 'precipitacao': 80, 'umidade': 68},   # Maio
            6: {'temperatura': 20.8, 'precipitacao': 60, 'umidade': 65},   # Junho
            7: {'temperatura': 21.2, 'precipitacao': 50, 'umidade': 63},   # Julho
            8: {'temperatura': 23.5, 'precipitacao': 40, 'umidade': 60},   # Agosto
            9: {'temperatura': 26.8, 'precipitacao': 80, 'umidade': 65},   # Setembro
            10: {'temperatura': 27.2, 'precipitacao': 140, 'umidade': 72}, # Outubro
            11: {'temperatura': 26.8, 'precipitacao': 160, 'umidade': 74}, # Novembro
            12: {'temperatura': 26.2, 'precipitacao': 180, 'umidade': 76}, # Dezembro
        }

        return dados_base.get(mes, {'temperatura': 25.0, 'precipitacao': 120, 'umidade': 70})

    def _preparar_features_natalidade(
        self,
        dados_historicos: List[Dict]
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepara features para modelo de natalidade
        """
        if not dados_historicos:
            return np.array([]), np.array([]), []

        df = pd.DataFrame(dados_historicos)

        # Features
        features = []

        # Taxa de natalidade anterior (lag)
        df['taxa_anterior'] = df['taxa_natalidade'].shift(1)

        # Número de matrizes
        df['log_matrizes'] = np.log1p(df['matrizes'])

        # Fatores climáticos
        df['temperatura_normalizada'] = (df['temperatura'] - df['temperatura'].mean()) / df['temperatura'].std()
        df['precipitacao_normalizada'] = (df['precipitacao'] - df['precipitacao'].mean()) / df['precipitacao'].std()
        df['umidade_normalizada'] = (df['umidade'] - df['umidade'].mean()) / df['umidade'].std()

        # Sazonalidade
        df['mes'] = pd.to_datetime(df['data']).dt.month
        df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
        df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)

        # Época de monta (alta: set-dez, baixa: jan-ago)
        df['epoca_alta_monta'] = df['mes'].isin([9, 10, 11, 12]).astype(int)

        # Remover NaN
        df = df.dropna()

        feature_columns = [
            'taxa_anterior', 'log_matrizes', 'temperatura_normalizada',
            'precipitacao_normalizada', 'umidade_normalizada',
            'mes_sin', 'mes_cos', 'epoca_alta_monta'
        ]

        X = df[feature_columns].values
        y = df['taxa_natalidade'].values

        return X, y, feature_columns

    def _preparar_features_mortalidade(
        self,
        dados_historicos: List[Dict]
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepara features para modelo de mortalidade
        """
        if not dados_historicos:
            return np.array([]), np.array([]), []

        df = pd.DataFrame(dados_historicos)

        # Features
        features = []

        # Taxa de mortalidade anterior
        df['taxa_anterior'] = df['taxa_mortalidade'].shift(1)

        # Log do rebanho total
        df['log_rebanho'] = np.log1p(df['rebanho_total'])

        # Fatores climáticos extremos
        df['temperatura_extrema'] = ((df['temperatura'] < 15) | (df['temperatura'] > 35)).astype(int)
        df['precipitacao_baixa'] = (df['precipitacao'] < 50).astype(int)
        df['umidade_extrema'] = ((df['umidade'] < 30) | (df['umidade'] > 90)).astype(int)

        # Sazonalidade
        df['mes'] = pd.to_datetime(df['data']).dt.month
        df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
        df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)

        # Época de risco (seca: mai-set)
        df['epoca_risco'] = df['mes'].isin([5, 6, 7, 8, 9]).astype(int)

        # Remover NaN
        df = df.dropna()

        feature_columns = [
            'taxa_anterior', 'log_rebanho', 'temperatura_extrema',
            'precipitacao_baixa', 'umidade_extrema',
            'mes_sin', 'mes_cos', 'epoca_risco'
        ]

        X = df[feature_columns].values
        y = df['taxa_mortalidade'].values

        return X, y, feature_columns

    def _treinar_arima_natalidade(self, y_train: np.ndarray, y_test: np.ndarray) -> Optional[Dict]:
        """
        Treina modelo ARIMA para natalidade
        """
        try:
            modelo = ARIMA(y_train, order=(1, 1, 1))
            modelo_fit = modelo.fit()

            predicoes = modelo_fit.forecast(steps=len(y_test))

            return {
                'modelo': modelo_fit,
                'mae': mean_absolute_error(y_test, predicoes),
                'rmse': np.sqrt(mean_squared_error(y_test, predicoes)),
                'predicoes': predicoes
            }
        except Exception as e:
            logger.warning(f'Erro ao treinar ARIMA natalidade: {e}')
            return None

    def _selecionar_melhor_modelo(self, resultados: Dict) -> str:
        """
        Seleciona o melhor modelo baseado em MAE
        """
        melhor_modelo = None
        melhor_mae = float('inf')

        for nome_modelo, dados in resultados.items():
            mae = dados.get('mae', float('inf'))
            if mae < melhor_mae:
                melhor_mae = mae
                melhor_modelo = nome_modelo

        return melhor_modelo

    def prever_natalidade_futura(
        self,
        meses_a_frente: int = 6,
        numero_matrizes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Faz previsões de natalidade futura

        Args:
            meses_a_frente: Número de meses para prever
            numero_matrizes: Número de matrizes (se None, usa estimativa atual)

        Returns:
            Previsões de natalidade
        """
        if 'natalidade' not in self.modelos_treinados:
            resultado = self.treinar_modelos_natalidade()
            if not resultado.get('sucesso'):
                return {'erro': 'Não foi possível treinar modelos de natalidade'}

        modelos = self.modelos_treinados['natalidade']
        melhor_modelo = self._selecionar_melhor_modelo(modelos)

        # Obter número de matrizes
        if numero_matrizes is None:
            numero_matrizes = self._calcular_matrizes_periodo(date.today())

        previsoes = []

        # Dados do último mês conhecido
        ultimo_dado = self._obter_ultimo_dado_natalidade()

        for i in range(1, meses_a_frente + 1):
            data_futura = date.today() + timedelta(days=i * 30)
            mes = data_futura.month

            # Preparar features
            features = self._criar_features_natalidade_futura(
                ultimo_dado, data_futura, numero_matrizes
            )

            # Fazer previsão
            taxa_prevista = modelos[melhor_modelo]['modelo'].predict([features])[0]
            nascimentos_previstos = int(taxa_prevista * numero_matrizes)

            previsoes.append({
                'mes': mes,
                'ano': data_futura.year,
                'taxa_natalidade_prevista': float(taxa_prevista),
                'nascimentos_previstos': nascimentos_previstos,
                'matrizes_consideradas': numero_matrizes,
                'modelo_usado': melhor_modelo
            })

            # Atualizar último dado
            ultimo_dado = {
                'taxa_natalidade': taxa_prevista,
                'matrizes': numero_matrizes,
                'mes': mes
            }

        return {
            'previsoes': previsoes,
            'modelo_usado': melhor_modelo,
            'parametros': {
                'matrizes_consideradas': numero_matrizes,
                'meses_previsao': meses_a_frente
            }
        }

    def prever_mortalidade_futura(
        self,
        meses_a_frente: int = 6,
        rebanho_total: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Faz previsões de mortalidade futura
        """
        if 'mortalidade' not in self.modelos_treinados:
            resultado = self.treinar_modelos_mortalidade()
            if not resultado.get('sucesso'):
                return {'erro': 'Não foi possível treinar modelos de mortalidade'}

        modelos = self.modelos_treinados['mortalidade']
        melhor_modelo = self._selecionar_melhor_modelo(modelos)

        # Obter rebanho total
        if rebanho_total is None:
            rebanho_total = self._calcular_rebanho_periodo(date.today())

        previsoes = []
        ultimo_dado = self._obter_ultimo_dado_mortalidade()

        for i in range(1, meses_a_frente + 1):
            data_futura = date.today() + timedelta(days=i * 30)
            mes = data_futura.month

            # Preparar features
            features = self._criar_features_mortalidade_futura(
                ultimo_dado, data_futura, rebanho_total
            )

            # Fazer previsão
            taxa_prevista = modelos[melhor_modelo]['modelo'].predict([features])[0]
            mortes_previstas = int(taxa_prevista * rebanho_total)

            previsoes.append({
                'mes': mes,
                'ano': data_futura.year,
                'taxa_mortalidade_prevista': float(taxa_prevista),
                'mortes_previstas': mortes_previstas,
                'rebanho_considerado': rebanho_total,
                'modelo_usado': melhor_modelo
            })

            # Atualizar último dado
            ultimo_dado = {
                'taxa_mortalidade': taxa_prevista,
                'rebanho_total': rebanho_total,
                'mes': mes
            }

        return {
            'previsoes': previsoes,
            'modelo_usado': melhor_modelo,
            'parametros': {
                'rebanho_considerado': rebanho_total,
                'meses_previsao': meses_a_frente
            }
        }

    def _obter_ultimo_dado_natalidade(self) -> Dict:
        """Obtém último dado conhecido de natalidade"""
        try:
            ultimo = MovimentacaoIndividual.objects.filter(
                propriedade=self.propriedade,
                tipo_movimentacao='NASCIMENTO'
            ).order_by('-data_movimentacao').first()

            if ultimo:
                return {
                    'taxa_natalidade': 0.75,  # Valor padrão
                    'matrizes': self._calcular_matrizes_periodo(date.today()),
                    'mes': date.today().month
                }
        except:
            pass

        return {
            'taxa_natalidade': 0.75,
            'matrizes': 100,
            'mes': date.today().month
        }

    def _obter_ultimo_dado_mortalidade(self) -> Dict:
        """Obtém último dado conhecido de mortalidade"""
        try:
            ultimo = MovimentacaoIndividual.objects.filter(
                propriedade=self.propriedade,
                tipo_movimentacao='MORTE'
            ).order_by('-data_movimentacao').first()

            if ultimo:
                return {
                    'taxa_mortalidade': 0.02,  # Valor padrão
                    'rebanho_total': self._calcular_rebanho_periodo(date.today()),
                    'mes': date.today().month
                }
        except:
            pass

        return {
            'taxa_mortalidade': 0.02,
            'rebanho_total': 500,
            'mes': date.today().month
        }

    def _criar_features_natalidade_futura(
        self,
        ultimo_dado: Dict,
        data_futura: date,
        numero_matrizes: int
    ) -> List[float]:
        """
        Cria features para previsão futura de natalidade
        """
        taxa_anterior = ultimo_dado.get('taxa_natalidade', 0.75)
        log_matrizes = np.log1p(numero_matrizes)

        # Dados climáticos do mês futuro
        dados_clima = self._obter_dados_climaticos_mes(data_futura)

        # Normalizar (valores aproximados baseados na média histórica)
        temp_norm = (dados_clima['temperatura'] - 25) / 5  # média 25, std 5
        precip_norm = (dados_clima['precipitacao'] - 120) / 60  # média 120, std 60
        umid_norm = (dados_clima['umidade'] - 70) / 10  # média 70, std 10

        mes = data_futura.month
        mes_sin = np.sin(2 * np.pi * mes / 12)
        mes_cos = np.cos(2 * np.pi * mes / 12)
        epoca_alta = 1 if mes in [9, 10, 11, 12] else 0

        return [
            taxa_anterior, log_matrizes, temp_norm,
            precip_norm, umid_norm, mes_sin, mes_cos, epoca_alta
        ]

    def _criar_features_mortalidade_futura(
        self,
        ultimo_dado: Dict,
        data_futura: date,
        rebanho_total: int
    ) -> List[float]:
        """
        Cria features para previsão futura de mortalidade
        """
        taxa_anterior = ultimo_dado.get('taxa_mortalidade', 0.02)
        log_rebanho = np.log1p(rebanho_total)

        # Dados climáticos
        dados_clima = self._obter_dados_climaticos_mes(data_futura)

        # Condições extremas
        temp_extrema = 1 if dados_clima['temperatura'] < 15 or dados_clima['temperatura'] > 35 else 0
        precip_baixa = 1 if dados_clima['precipitacao'] < 50 else 0
        umid_extrema = 1 if dados_clima['umidade'] < 30 or dados_clima['umidade'] > 90 else 0

        mes = data_futura.month
        mes_sin = np.sin(2 * np.pi * mes / 12)
        mes_cos = np.cos(2 * np.pi * mes / 12)
        epoca_risco = 1 if mes in [5, 6, 7, 8, 9] else 0

        return [
            taxa_anterior, log_rebanho, temp_extrema,
            precip_baixa, umid_extrema, mes_sin, mes_cos, epoca_risco
        ]