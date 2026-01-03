# -*- coding: utf-8 -*-
"""
Utils para módulo de Pecuária
Funções auxiliares para parâmetros e projeções
"""

from decimal import Decimal


def obter_presets_parametros(tipo_ciclo):
    """Retorna parâmetros padrão baseado no tipo de ciclo da propriedade"""
    
    presets = {
        'CRIA': {
            'taxa_natalidade_anual': Decimal('85'),
            'taxa_mortalidade_bezerros_anual': Decimal('5'),
            'taxa_mortalidade_adultos_anual': Decimal('3'),
            'percentual_venda_machos_anual': Decimal('10'),
            'percentual_venda_femeas_anual': Decimal('15'),
            'periodicidade': 'MENSAL',
        },
        'RECRIA': {
            'taxa_natalidade_anual': Decimal('75'),
            'taxa_mortalidade_bezerros_anual': Decimal('3'),
            'taxa_mortalidade_adultos_anual': Decimal('2'),
            'percentual_venda_machos_anual': Decimal('20'),
            'percentual_venda_femeas_anual': Decimal('25'),
            'periodicidade': 'MENSAL',
        },
        'ENGORDA': {
            'taxa_natalidade_anual': Decimal('60'),
            'taxa_mortalidade_bezerros_anual': Decimal('2'),
            'taxa_mortalidade_adultos_anual': Decimal('1'),
            'percentual_venda_machos_anual': Decimal('80'),
            'percentual_venda_femeas_anual': Decimal('50'),
            'periodicidade': 'MENSAL',
        },
        'CICLO_COMPLETO': {
            'taxa_natalidade_anual': Decimal('70'),
            'taxa_mortalidade_bezerros_anual': Decimal('4'),
            'taxa_mortalidade_adultos_anual': Decimal('2'),
            'percentual_venda_machos_anual': Decimal('40'),
            'percentual_venda_femeas_anual': Decimal('30'),
            'periodicidade': 'MENSAL',
        },
        'DEFAULT': {
            'taxa_natalidade_anual': Decimal('70'),
            'taxa_mortalidade_bezerros_anual': Decimal('5'),
            'taxa_mortalidade_adultos_anual': Decimal('3'),
            'percentual_venda_machos_anual': Decimal('30'),
            'percentual_venda_femeas_anual': Decimal('25'),
            'periodicidade': 'MENSAL',
        }
    }
    
    return presets.get(tipo_ciclo, presets['DEFAULT'])


def aplicar_presets_parametros(parametros, tipo_ciclo):
    """Aplica presets de parâmetros baseado no tipo de ciclo"""
    
    if not tipo_ciclo:
        return parametros
    
    presets = obter_presets_parametros(tipo_ciclo)
    
    # Aplicar presets apenas se os valores ainda não foram configurados
    if not parametros.taxa_natalidade_anual:
        parametros.taxa_natalidade_anual = presets['taxa_natalidade_anual']
    
    if not parametros.taxa_mortalidade_bezerros_anual:
        parametros.taxa_mortalidade_bezerros_anual = presets['taxa_mortalidade_bezerros_anual']
    
    if not parametros.taxa_mortalidade_adultos_anual:
        parametros.taxa_mortalidade_adultos_anual = presets['taxa_mortalidade_adultos_anual']
    
    if not parametros.percentual_venda_machos_anual:
        parametros.percentual_venda_machos_anual = presets['percentual_venda_machos_anual']
    
    if not parametros.percentual_venda_femeas_anual:
        parametros.percentual_venda_femeas_anual = presets['percentual_venda_femeas_anual']
    
    if not parametros.periodicidade:
        parametros.periodicidade = presets['periodicidade']
    
    return parametros


def calcular_resumo_projecao(propriedade_id):
    """Calcula resumo da projeção para visualização"""
    from .models import MovimentacaoProjetada, InventarioRebanho
    
    movimentacoes = MovimentacaoProjetada.objects.filter(propriedade_id=propriedade_id)
    inventario = InventarioRebanho.objects.filter(propriedade_id=propriedade_id)
    
    resumo = {
        'total_animais_inicial': sum(item.quantidade for item in inventario),
        'total_animais_final': 0,
        'total_receitas': Decimal('0'),
        'total_custos': Decimal('0'),
        'anos_projecao': 0,
    }
    
    # Calcular totais
    for mov in movimentacoes:
        if mov.tipo_movimentacao == 'VENDA':
            resumo['total_receitas'] += mov.valor_total or Decimal('0')
        elif mov.tipo_movimentacao == 'CUSTO':
            resumo['total_custos'] += mov.valor_total or Decimal('0')
    
    return resumo


def gerar_series_tempo(movimentacoes, anos=5):
    """Gera séries temporais para gráficos"""
    
    # Agrupar por mês
    dados_mes = {}
    for mov in movimentacoes:
        mes_ano = f"{mov.data_movimentacao.year}-{mov.data_movimentacao.month:02d}"
        
        if mes_ano not in dados_mes:
            dados_mes[mes_ano] = {
                'vendas': Decimal('0'),
                'compras': Decimal('0'),
                'custos': Decimal('0'),
                'nascimentos': Decimal('0'),
                'mortalidade': Decimal('0'),
            }
        
        if mov.tipo_movimentacao == 'VENDA':
            dados_mes[mes_ano]['vendas'] += mov.valor_total or Decimal('0')
        elif mov.tipo_movimentacao == 'COMPRA':
            dados_mes[mes_ano]['compras'] += mov.valor_total or Decimal('0')
        elif mov.tipo_movimentacao == 'CUSTO':
            dados_mes[mes_ano]['custos'] += mov.valor_total or Decimal('0')
        elif mov.tipo_movimentacao == 'NASCIMENTO':
            dados_mes[mes_ano]['nascimentos'] += mov.quantidade or Decimal('0')
        elif mov.tipo_movimentacao == 'MORTALIDADE':
            dados_mes[mes_ano]['mortalidade'] += mov.quantidade or Decimal('0')
    
    # Ordenar por data
    dados_ordenados = sorted(dados_mes.items())
    
    return {
        'labels': [item[0] for item in dados_ordenados],
        'vendas': [float(item[1]['vendas']) for item in dados_ordenados],
        'compras': [float(item[1]['compras']) for item in dados_ordenados],
        'custos': [float(item[1]['custos']) for item in dados_ordenados],
        'nascimentos': [float(item[1]['nascimentos']) for item in dados_ordenados],
        'mortalidade': [float(item[1]['mortalidade']) for item in dados_ordenados],
    }

