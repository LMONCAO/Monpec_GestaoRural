# -*- coding: utf-8 -*-
"""
Big Data Analytics para Pecuária
Análise avançada de dados históricos com estatísticas e correlações
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from collections import defaultdict, Counter
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from django.db.models import Q, Avg, Count, Sum, Max, Min, F, Case, When
from django.utils import timezone

from ..models import (
    MovimentacaoIndividual,
    MovimentacaoProjetada,
    InventarioRebanho,
    CategoriaAnimal,
    Propriedade,
    PlanejamentoAnual,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada
)

logger = logging.getLogger(__name__)


class BigDataAnalyticsService:
    """
    Serviço de Big Data Analytics para análise avançada de dados pecuários
    Fornece insights estatísticos, correlações e detecção de padrões
    """

    def __init__(self):
        self.cache_analytics = {}
        self.min_amostras = 10  # Mínimo de amostras para análises estatísticas

    def analisar_dados_historicos_completos(
        self,
        propriedade_id: int,
        periodo_meses: int = 24
    ) -> Dict[str, Any]:
        """
        Análise completa de todos os dados históricos da propriedade
        """
        try:
            logger.info(f'Iniciando análise completa de dados históricos para propriedade {propriedade_id}')

            # 1. Coletar todos os dados históricos
            dados_brutos = self._coletar_dados_historicos_completos(propriedade_id, periodo_meses)

            if not dados_brutos or len(dados_brutos['movimentacoes']) < self.min_amostras:
                return {
                    'sucesso': False,
                    'erro': 'Dados históricos insuficientes para análise completa'
                }

            # 2. Análise estatística geral
            estatisticas_gerais = self._calcular_estatisticas_gerais(dados_brutos)

            # 3. Análise de correlações
            analise_correlacoes = self._analisar_correlacoes_completas(dados_brutos)

            # 4. Detecção de anomalias
            deteccao_anomalias = self._detectar_anomalias(dados_brutos)

            # 5. Análise de tendências
            analises_tendencias = self._analisar_tendencias_completas(dados_brutos)

            # 6. Segmentação/clustering de categorias
            segmentacao_categorias = self._segmentar_categorias(dados_brutos)

            # 7. Previsões baseadas em padrões históricos
            previsoes_padroes = self._gerar_previsoes_padroes(dados_brutos)

            return {
                'sucesso': True,
                'estatisticas_gerais': estatisticas_gerais,
                'analise_correlacoes': analise_correlacoes,
                'deteccao_anomalias': deteccao_anomalias,
                'analises_tendencias': analises_tendencias,
                'segmentacao_categorias': segmentacao_categorias,
                'previsoes_padroes': previsoes_padroes,
                'periodo_analisado': periodo_meses,
                'total_registros': len(dados_brutos['movimentacoes']),
                'timestamp_analise': timezone.now().isoformat()
            }

        except Exception as e:
            logger.error(f'Erro na análise completa de dados históricos: {e}', exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def _coletar_dados_historicos_completos(
        self,
        propriedade_id: int,
        periodo_meses: int
    ) -> Dict[str, Any]:
        """
        Coleta todos os dados históricos relevantes da propriedade
        """
        logger.info('Coletando dados históricos completos...')

        data_inicio = timezone.now() - timedelta(days=30 * periodo_meses)

        dados = {
            'movimentacoes': [],
            'inventarios': [],
            'planejamentos': [],
            'metas': [],
            'periodo': {
                'inicio': data_inicio,
                'fim': timezone.now(),
                'meses': periodo_meses
            }
        }

        # 1. Movimentações individuais
        movimentacoes = MovimentacaoIndividual.objects.filter(
            propriedade_id=propriedade_id,
            data__gte=data_inicio
        ).select_related('categoria_animal').order_by('data')

        for mov in movimentacoes:
            dados['movimentacoes'].append({
                'id': mov.id,
                'data': mov.data,
                'tipo': mov.tipo_movimentacao,
                'categoria': mov.categoria_animal.nome if mov.categoria_animal else None,
                'quantidade': mov.quantidade or 1,
                'valor_unitario': float(mov.valor_unitario) if mov.valor_unitario else None,
                'valor_total': float(mov.valor_total) if mov.valor_total else None
            })

        # 2. Inventários
        inventarios = InventarioRebanho.objects.filter(
            propriedade_id=propriedade_id,
            data__gte=data_inicio
        ).select_related('categoria').order_by('data')

        for inv in inventarios:
            dados['inventarios'].append({
                'id': inv.id,
                'data': inv.data,
                'categoria': inv.categoria.nome if inv.categoria else None,
                'quantidade': inv.quantidade,
                'valor_unitario': float(inv.valor_unitario) if inv.valor_unitario else None
            })

        # 3. Planejamentos
        planejamentos = PlanejamentoAnual.objects.filter(
            propriedade_id=propriedade_id,
            ano__gte=data_inicio.year
        ).prefetch_related('metascomerciais_planajada', 'metasfinanceiras_planajada')

        for plan in planejamentos:
            dados['planejamentos'].append({
                'id': plan.id,
                'ano': plan.ano,
                'descricao': plan.descricao,
                'status': plan.status,
                'metas_comerciais': list(plan.metascomerciais_planajada.values(
                    'categoria__nome', 'quantidade_animais', 'preco_medio_esperado'
                )),
                'metas_financeiras': list(plan.metasfinanceiras_planajada.values(
                    'tipo_custo', 'valor_anual_previsto'
                ))
            })

        logger.info(f'Coletados {len(dados["movimentacoes"])} movimentações, {len(dados["inventarios"])} inventários, {len(dados["planejamentos"])} planejamentos')

        return dados

    def _calcular_estatisticas_gerais(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula estatísticas gerais dos dados históricos
        """
        logger.info('Calculando estatísticas gerais...')

        df_mov = pd.DataFrame(dados['movimentacoes'])
        df_inv = pd.DataFrame(dados['inventarios'])

        estatisticas = {
            'periodo': dados['periodo'],
            'movimentacoes': {},
            'inventarios': {},
            'categorias': {},
            'financeiro': {}
        }

        if not df_mov.empty:
            # Estatísticas de movimentações
            estatisticas['movimentacoes'] = {
                'total_registros': len(df_mov),
                'tipos_movimentacao': df_mov['tipo'].value_counts().to_dict(),
                'periodo_cobertura': {
                    'inicio': df_mov['data'].min().isoformat() if df_mov['data'].min() else None,
                    'fim': df_mov['data'].max().isoformat() if df_mov['data'].max() else None
                },
                'movimentacoes_por_mes': df_mov.groupby(pd.Grouper(key='data', freq='M')).size().to_dict(),
                'categorias_mais_ativas': df_mov['categoria'].value_counts().head(10).to_dict() if 'categoria' in df_mov.columns else {}
            }

            # Estatísticas financeiras
            if 'valor_total' in df_mov.columns:
                df_mov_financeiro = df_mov.dropna(subset=['valor_total'])
                estatisticas['financeiro'] = {
                    'total_valor_movimentado': float(df_mov_financeiro['valor_total'].sum()),
                    'media_valor_por_movimentacao': float(df_mov_financeiro['valor_total'].mean()),
                    'mediana_valor_por_movimentacao': float(df_mov_financeiro['valor_total'].median()),
                    'desvio_padrao_valor': float(df_mov_financeiro['valor_total'].std()),
                    'valor_por_tipo': df_mov_financeiro.groupby('tipo')['valor_total'].sum().to_dict()
                }

        if not df_inv.empty:
            # Estatísticas de inventários
            estatisticas['inventarios'] = {
                'total_registros': len(df_inv),
                'quantidade_total_animais': float(df_inv['quantidade'].sum()),
                'media_quantidade_por_inventario': float(df_inv['quantidade'].mean()),
                'quantidade_por_categoria': df_inv.groupby('categoria')['quantidade'].sum().to_dict(),
                'evolucao_temporal': df_inv.groupby(pd.Grouper(key='data', freq='M'))['quantidade'].sum().to_dict()
            }

        # Estatísticas por categoria
        if not df_mov.empty and 'categoria' in df_mov.columns:
            categorias_stats = {}
            for categoria in df_mov['categoria'].dropna().unique():
                mov_cat = df_mov[df_mov['categoria'] == categoria]
                categorias_stats[categoria] = {
                    'total_movimentacoes': len(mov_cat),
                    'tipos_movimentacao': mov_cat['tipo'].value_counts().to_dict(),
                    'periodo_primeira_mov': mov_cat['data'].min().isoformat() if not mov_cat.empty else None,
                    'periodo_ultima_mov': mov_cat['data'].max().isoformat() if not mov_cat.empty else None
                }
            estatisticas['categorias'] = categorias_stats

        return estatisticas

    def _analisar_correlacoes_completas(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise completa de correlações entre variáveis
        """
        logger.info('Analisando correlações completas...')

        df_mov = pd.DataFrame(dados['movimentacoes'])
        df_inv = pd.DataFrame(dados['inventarios'])

        correlacoes = {
            'movimentacoes_inventarios': {},
            'temporal': {},
            'categoria_tipo': {},
            'financeiro_quantidade': {}
        }

        # 1. Correlação entre movimentações e inventários
        if not df_mov.empty and not df_inv.empty:
            try:
                # Agrupar por mês
                mov_mensal = df_mov.groupby(pd.Grouper(key='data', freq='M')).size()
                inv_mensal = df_inv.groupby(pd.Grouper(key='data', freq='M'))['quantidade'].sum()

                # Combinar dados mensais
                df_mensal = pd.DataFrame({
                    'movimentacoes': mov_mensal,
                    'inventario': inv_mensal
                }).dropna()

                if len(df_mensal) >= self.min_amostras:
                    corr_mov_inv, p_value = pearsonr(df_mensal['movimentacoes'], df_mensal['inventario'])
                    correlacoes['movimentacoes_inventarios'] = {
                        'correlacao_pearson': round(float(corr_mov_inv), 3),
                        'p_value': round(float(p_value), 4),
                        'significativo': p_value < 0.05,
                        'amostras': len(df_mensal),
                        'interpretacao': self._interpretar_correlacao(corr_mov_inv)
                    }
            except Exception as e:
                logger.warning(f'Erro na correlação mov-inv: {e}')

        # 2. Correlações temporais (sazonalidade)
        if not df_mov.empty:
            try:
                df_mov['mes'] = pd.to_datetime(df_mov['data']).dt.month
                df_mov['ano'] = pd.to_datetime(df_mov['data']).dt.year

                # Movimentações por mês
                mov_por_mes = df_mov.groupby('mes').size()

                # Testar sazonalidade
                from scipy.stats import chi2_contingency
                tabela_contingencia = pd.crosstab(df_mov['ano'], df_mov['mes'])
                chi2, p_value, dof, expected = chi2_contingency(tabela_contingencia)

                correlacoes['temporal'] = {
                    'sazonalidade_detectada': p_value < 0.05,
                    'p_value_sazonalidade': round(float(p_value), 4),
                    'mes_mais_ativo': int(mov_por_mes.idxmax()),
                    'mes_menos_ativo': int(mov_por_mes.idxmin()),
                    'variacao_mensal_percentual': round(float((mov_por_mes.max() - mov_por_mes.min()) / mov_por_mes.mean() * 100), 1)
                }
            except Exception as e:
                logger.warning(f'Erro na análise temporal: {e}')

        # 3. Correlação entre valor e quantidade
        if not df_mov.empty and 'valor_total' in df_mov.columns and 'quantidade' in df_mov.columns:
            try:
                df_financeiro = df_mov.dropna(subset=['valor_total', 'quantidade'])
                if len(df_financeiro) >= self.min_amostras:
                    corr_valor_qtd, p_value = pearsonr(df_financeiro['valor_total'], df_financeiro['quantidade'])
                    correlacoes['financeiro_quantidade'] = {
                        'correlacao_pearson': round(float(corr_valor_qtd), 3),
                        'p_value': round(float(p_value), 4),
                        'significativo': p_value < 0.05,
                        'amostras': len(df_financeiro)
                    }
            except Exception as e:
                logger.warning(f'Erro na correlação financeiro: {e}')

        return correlacoes

    def _detectar_anomalias(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecção de anomalias nos dados históricos
        """
        logger.info('Detectando anomalias...')

        df_mov = pd.DataFrame(dados['movimentacoes'])

        anomalias = {
            'movimentacoes': {},
            'inventarios': {},
            'financeiro': {},
            'temporais': {}
        }

        if not df_mov.empty:
            # 1. Anomalias em movimentações por período
            try:
                mov_diario = df_mov.groupby('data').size()
                media_mov = mov_diario.mean()
                desvio_mov = mov_diario.std()

                # Z-score para detectar outliers
                z_scores = np.abs((mov_diario - media_mov) / desvio_mov)
                dias_anomalos = z_scores[z_scores > 3]  # Z-score > 3

                anomalias['movimentacoes'] = {
                    'dias_com_movimentacao_anormal': len(dias_anomalos),
                    'media_movimentacoes_diarias': round(float(media_mov), 2),
                    'desvio_padrao_movimentacoes': round(float(desvio_mov), 2),
                    'dias_anomalos': [
                        {'data': str(data), 'movimentacoes': int(qtd), 'z_score': round(float(z), 2)}
                        for data, (qtd, z) in zip(dias_anomalos.index, zip(mov_diario[dias_anomalos.index], dias_anomalos))
                    ]
                }
            except Exception as e:
                logger.warning(f'Erro na detecção de anomalias de movimentação: {e}')

            # 2. Anomalias financeiras
            if 'valor_total' in df_mov.columns:
                try:
                    valores = df_mov['valor_total'].dropna()
                    if len(valores) >= self.min_amostras:
                        media_valor = valores.mean()
                        desvio_valor = valores.std()
                        z_scores_valor = np.abs((valores - media_valor) / desvio_valor)

                        valores_anomalos = valores[z_scores_valor > 3]

                        anomalias['financeiro'] = {
                            'transacoes_valor_anormal': len(valores_anomalos),
                            'media_valor_transacao': round(float(media_valor), 2),
                            'desvio_padrao_valor': round(float(desvio_valor), 2),
                            'valores_anomalos': [
                                {'valor': round(float(v), 2), 'z_score': round(float(z), 2)}
                                for v, z in zip(valores_anomalos, z_scores_valor[z_scores_valor > 3])
                            ]
                        }
                except Exception as e:
                    logger.warning(f'Erro na detecção de anomalias financeiras: {e}')

        return anomalias

    def _analisar_tendencias_completas(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise completa de tendências nos dados
        """
        logger.info('Analisando tendências completas...')

        df_mov = pd.DataFrame(dados['movimentacoes'])
        df_inv = pd.DataFrame(dados['inventarios'])

        tendencias = {
            'movimentacoes': {},
            'inventarios': {},
            'categorias': {},
            'financeiro': {}
        }

        # 1. Tendências de movimentações
        if not df_mov.empty:
            try:
                # Agrupar por mês
                mov_mensal = df_mov.groupby(pd.Grouper(key='data', freq='M')).size()

                # Regressão linear para tendência
                x = np.arange(len(mov_mensal))
                y = mov_mensal.values

                if len(x) >= 3:  # Mínimo para regressão
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

                    # Calcular tendência anual
                    tendencia_anual = slope * 12

                    tendencias['movimentacoes'] = {
                        'tendencia_mensal': round(float(slope), 2),
                        'tendencia_anual': round(float(tendencia_anual), 2),
                        'direcao': 'crescente' if slope > 0 else 'decrescente',
                        'r_quadrado': round(float(r_value**2), 3),
                        'significativo': p_value < 0.05,
                        'periodo_analisado_meses': len(mov_mensal)
                    }
            except Exception as e:
                logger.warning(f'Erro na análise de tendência de movimentações: {e}')

        # 2. Tendências de inventários
        if not df_inv.empty:
            try:
                inv_mensal = df_inv.groupby(pd.Grouper(key='data', freq='M'))['quantidade'].sum()

                x = np.arange(len(inv_mensal))
                y = inv_mensal.values

                if len(x) >= 3:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

                    tendencias['inventarios'] = {
                        'tendencia_mensal': round(float(slope), 2),
                        'tendencia_anual': round(float(tendencia_anual), 2),
                        'direcao': 'crescente' if slope > 0 else 'decrescente',
                        'r_quadrado': round(float(r_value**2), 3),
                        'significativo': p_value < 0.05,
                        'periodo_analisado_meses': len(inv_mensal)
                    }
            except Exception as e:
                logger.warning(f'Erro na análise de tendência de inventários: {e}')

        # 3. Tendências por categoria
        if not df_mov.empty and 'categoria' in df_mov.columns:
            tendencias_categoria = {}
            for categoria in df_mov['categoria'].dropna().unique():
                mov_cat = df_mov[df_mov['categoria'] == categoria]
                if len(mov_cat) >= 6:  # Mínimo para análise
                    mov_cat_mensal = mov_cat.groupby(pd.Grouper(key='data', freq='M')).size()

                    if len(mov_cat_mensal) >= 3:
                        x = np.arange(len(mov_cat_mensal))
                        y = mov_cat_mensal.values
                        slope, _, r_value, p_value, _ = stats.linregress(x, y)

                        tendencias_categoria[categoria] = {
                            'tendencia_mensal': round(float(slope), 2),
                            'direcao': 'crescente' if slope > 0 else 'decrescente',
                            'significativo': p_value < 0.05
                        }

            tendencias['categorias'] = tendencias_categoria

        return tendencias

    def _segmentar_categorias(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Segmentação/clustering das categorias baseado em padrões
        """
        logger.info('Segmentando categorias...')

        df_mov = pd.DataFrame(dados['movimentacoes'])

        segmentacao = {
            'grupos_categoria': {},
            'perfis_categoria': {},
            'recomendacoes_segmentacao': []
        }

        if df_mov.empty or 'categoria' not in df_mov.columns:
            return segmentacao

        # Análise por categoria
        categorias_stats = {}
        for categoria in df_mov['categoria'].dropna().unique():
            mov_cat = df_mov[df_mov['categoria'] == categoria]

            if len(mov_cat) >= 3:  # Mínimo para análise
                stats_cat = {
                    'total_movimentacoes': len(mov_cat),
                    'frequencia_mensal': len(mov_cat) / dados['periodo']['meses'],
                    'tipos_movimentacao': mov_cat['tipo'].value_counts().to_dict(),
                    'valor_medio': mov_cat['valor_total'].mean() if 'valor_total' in mov_cat.columns and not mov_cat['valor_total'].empty else None,
                    'periodo_ativo_meses': (mov_cat['data'].max() - mov_cat['data'].min()).days / 30 if len(mov_cat) > 1 else 0
                }

                # Classificar perfil da categoria
                perfil = self._classificar_perfil_categoria(stats_cat)
                stats_cat['perfil'] = perfil

                categorias_stats[categoria] = stats_cat

        # Agrupar por perfil
        perfis_agrupados = {}
        for categoria, stats in categorias_stats.items():
            perfil = stats['perfil']
            if perfil not in perfis_agrupados:
                perfis_agrupados[perfil] = []
            perfis_agrupados[perfil].append(categoria)

        segmentacao['grupos_categoria'] = perfis_agrupados
        segmentacao['perfis_categoria'] = categorias_stats

        # Recomendações baseadas na segmentação
        segmentacao['recomendacoes_segmentacao'] = self._gerar_recomendacoes_segmentacao(perfis_agrupados)

        return segmentacao

    def _classificar_perfil_categoria(self, stats: Dict[str, Any]) -> str:
        """
        Classifica o perfil de uma categoria baseado em suas estatísticas
        """
        freq = stats['frequencia_mensal']
        tipos = stats['tipos_movimentacao']

        # Lógica de classificação
        if freq > 10:  # Muito ativa
            if 'NASCIMENTO' in tipos and tipos.get('NASCIMENTO', 0) > freq * 0.5:
                return 'reprodutiva_intensiva'
            elif 'VENDA' in tipos and tipos.get('VENDA', 0) > freq * 0.3:
                return 'comercial_intensiva'
            else:
                return 'geral_muito_ativa'
        elif freq > 2:  # Ativa
            if 'MORTE' in tipos and tipos.get('MORTE', 0) > freq * 0.4:
                return 'problematica'
            elif 'NASCIMENTO' in tipos:
                return 'reprodutiva'
            else:
                return 'geral_ativa'
        else:  # Pouco ativa
            return 'pouco_ativa'

    def _gerar_recomendacoes_segmentacao(self, grupos: Dict[str, List]) -> List[str]:
        """
        Gera recomendações baseadas na segmentação de categorias
        """
        recomendacoes = []

        if 'reprodutiva_intensiva' in grupos and len(grupos['reprodutiva_intensiva']) > 0:
            recomendacoes.append(f"🎯 Foco na reprodução: As categorias {', '.join(grupos['reprodutiva_intensiva'])} têm alta atividade reprodutiva. Considere investimentos em melhoramento genético.")

        if 'comercial_intensiva' in grupos and len(grupos['comercial_intensiva']) > 0:
            recomendacoes.append(f"💰 Otimização comercial: As categorias {', '.join(grupos['comercial_intensiva'])} geram alta receita. Foque em estratégias de marketing e precificação.")

        if 'problematica' in grupos and len(grupos['problematica']) > 0:
            recomendacoes.append(f"⚠️ Atenção sanitária: As categorias {', '.join(grupos['problematica'])} têm alta taxa de mortalidade. Revisar protocolos sanitários e manejo.")

        if 'pouco_ativa' in grupos and len(grupos['pouco_ativa']) > 0:
            recomendacoes.append(f"🔄 Reavaliação: As categorias {', '.join(grupos['pouco_ativa'])} têm baixa atividade. Considerar descarte ou reposição.")

        return recomendacoes

    def _gerar_previsoes_padroes(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera previsões baseadas em padrões históricos identificados
        """
        logger.info('Gerando previsões baseadas em padrões...')

        df_mov = pd.DataFrame(dados['movimentacoes'])

        previsoes = {
            'proximos_meses': {},
            'alertas': [],
            'oportunidades': []
        }

        if df_mov.empty:
            return previsoes

        # Previsão de movimentações para os próximos 3 meses
        try:
            mov_mensal = df_mov.groupby(pd.Grouper(key='data', freq='M')).size()

            if len(mov_mensal) >= 3:
                # Usar média móvel simples para previsão
                media_3_meses = mov_mensal.tail(3).mean()
                media_6_meses = mov_mensal.tail(6).mean() if len(mov_mensal) >= 6 else media_3_meses

                # Previsão conservadora (média dos últimos períodos)
                previsao_conservadora = (media_3_meses + media_6_meses) / 2

                # Calcular sazonalidade
                sazonalidade = self._calcular_sazonalidade(mov_mensal)

                # Gerar previsões mensais
                data_atual = timezone.now()
                for i in range(1, 4):
                    data_prev = data_atual + timedelta(days=30 * i)
                    mes = data_prev.month

                    # Ajustar por sazonalidade
                    ajuste_sazonal = sazonalidade.get(mes, 1.0)
                    previsao_mes = previsao_conservadora * ajuste_sazonal

                    previsoes['proximos_meses'][f'{data_prev.year}-{data_prev.month:02d}'] = {
                        'movimentacoes_previstas': round(float(previsao_mes), 1),
                        'ajuste_sazonal': round(float(ajuste_sazonal), 2),
                        'confianca': 'media'  # Poderia ser calculado baseado em histórico
                    }
        except Exception as e:
            logger.warning(f'Erro na geração de previsões: {e}')

        # Gerar alertas baseados em padrões
        alertas = self._gerar_alertas_padroes(dados)
        previsoes['alertas'] = alertas

        # Identificar oportunidades
        oportunidades = self._identificar_oportunidades(dados)
        previsoes['oportunidades'] = oportunidades

        return previsoes

    def _calcular_sazonalidade(self, serie_mensal: pd.Series) -> Dict[int, float]:
        """
        Calcula fatores sazonais por mês
        """
        sazonalidade = {}

        try:
            # Média geral
            media_geral = serie_mensal.mean()

            # Média por mês
            media_mensal = serie_mensal.groupby(serie_mensal.index.month).mean()

            # Calcular fatores sazonais
            for mes in range(1, 13):
                if mes in media_mensal.index:
                    sazonalidade[mes] = media_mensal[mes] / media_geral
                else:
                    sazonalidade[mes] = 1.0  # Neutro

        except Exception as e:
            logger.warning(f'Erro no cálculo de sazonalidade: {e}')
            # Sazonalidade neutra
            for mes in range(1, 13):
                sazonalidade[mes] = 1.0

        return sazonalidade

    def _gerar_alertas_padroes(self, dados: Dict[str, Any]) -> List[str]:
        """
        Gera alertas baseados em padrões identificados
        """
        alertas = []
        df_mov = pd.DataFrame(dados['movimentacoes'])

        if df_mov.empty:
            return alertas

        # Alerta de redução de atividade
        try:
            mov_mensal = df_mov.groupby(pd.Grouper(key='data', freq='M')).size()
            ultimos_3_meses = mov_mensal.tail(3)
            ultimos_6_meses = mov_mensal.tail(6)

            if len(ultimos_6_meses) >= 6:
                media_3_ultimos = ultimos_3_meses.mean()
                media_6_ultimos = ultimos_6_meses.mean()

                if media_3_ultimos < media_6_ultimos * 0.7:  # Redução de 30%
                    alertas.append("⚠️ Redução significativa na atividade: Os últimos 3 meses mostram redução de {:.1f}% na atividade comparado aos 6 meses anteriores.".format(
                        (1 - media_3_ultimos/media_6_ultimos) * 100
                    ))
        except Exception as e:
            logger.warning(f'Erro na geração de alertas: {e}')

        return alertas

    def _identificar_oportunidades(self, dados: Dict[str, Any]) -> List[str]:
        """
        Identifica oportunidades baseadas nos dados históricos
        """
        oportunidades = []
        df_mov = pd.DataFrame(dados['movimentacoes'])

        if df_mov.empty:
            return oportunidades

        # Oportunidade de sazonalidade
        try:
            mov_mensal = df_mov.groupby(pd.Grouper(key='data', freq='M')).size()
            media_mensal = mov_mensal.groupby(mov_mensal.index.month).mean()

            if not media_mensal.empty:
                mes_pico = media_mensal.idxmax()
                mes_valor = media_mensal.max()
                mes_medio = media_mensal.mean()

                if mes_valor > mes_medio * 1.5:  # Pico 50% acima da média
                    meses_pt = {
                        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                    }
                    oportunidades.append(f"📈 Oportunidade sazonal: {meses_pt.get(mes_pico, str(mes_pico))} é o mês de maior atividade (+{((mes_valor/mes_medio - 1) * 100):.0f}%). Considere intensificar operações neste período.")
        except Exception as e:
            logger.warning(f'Erro na identificação de oportunidades: {e}')

        return oportunidades

    def _interpretar_correlacao(self, correlacao: float) -> str:
        """
        Interpreta a força de uma correlação
        """
        abs_corr = abs(correlacao)

        if abs_corr < 0.3:
            return 'correlação fraca'
        elif abs_corr < 0.5:
            return 'correlação moderada'
        elif abs_corr < 0.7:
            return 'correlação forte'
        else:
            return 'correlação muito forte'