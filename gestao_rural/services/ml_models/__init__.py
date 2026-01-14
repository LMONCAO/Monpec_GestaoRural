# -*- coding: utf-8 -*-
"""
Módulo de Machine Learning para o Monpec
Integração de todos os modelos ML para análise pecuária avançada
"""

from .previsao_precos import PrevisaoPrecosML
from .analise_correlacao_anomalias import AnaliseCorrelacaoAnomalias
from .previsao_natalidade_mortalidade import PrevisaoNatalidadeMortalidadeML

__all__ = [
    'PrevisaoPrecosML',
    'AnaliseCorrelacaoAnomalias',
    'PrevisaoNatalidadeMortalidadeML',
]