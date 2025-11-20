# -*- coding: utf-8 -*-
"""
Módulo de Consolidação Financeira
Consolida dados de todos os módulos para análise bancária
"""

from .models import *


def consolidar_dados_propriedade(propriedade):
    """
    Consolida dados de todos os módulos da propriedade
    
    Args:
        propriedade: Objeto Propriedade
        
    Returns:
        dict: Dicionário com todos os dados consolidados
    """
    
    # Inicializar dicionário de retorno
    dados = {
        'pecuaria': {},
        'agricultura': {},
        'patrimonio': {},
        'financeiro': {},
        'consolidado': {},
    }
    
    # 1. PECUÁRIA
    try:
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        valor_rebanho = sum(item.valor_total for item in inventario)
        quantidade_total = sum(item.quantidade for item in inventario)
        
        dados['pecuaria'] = {
            'valor_total': valor_rebanho,
            'quantidade_total': quantidade_total,
            'itens': inventario,
        }
    except Exception as e:
        dados['pecuaria'] = {'valor_total': 0, 'quantidade_total': 0, 'itens': []}
    
    # 2. AGRICULTURA
    try:
        ciclos = CicloProducaoAgricola.objects.filter(propriedade=propriedade)
        receita_agricola = sum(ciclo.receita_esperada_total for ciclo in ciclos)
        
        dados['agricultura'] = {
            'receita_total': receita_agricola,
            'ciclos': ciclos,
        }
    except Exception as e:
        dados['agricultura'] = {'receita_total': 0, 'ciclos': []}
    
    # 3. PATRIMÔNIO
    try:
        bens = BemImobilizado.objects.filter(propriedade=propriedade, ativo=True)
        valor_patrimonio = sum(bem.valor_aquisicao for bem in bens)
        
        dados['patrimonio'] = {
            'valor_total': valor_patrimonio,
            'bens': bens,
        }
    except Exception as e:
        dados['patrimonio'] = {'valor_total': 0, 'bens': []}
    
    # 4. CUSTOS
    try:
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
        
        total_custos_fixos = sum(custo.custo_anual if hasattr(custo, 'custo_anual') else 0 
                                  for custo in custos_fixos)
        total_custos_variaveis = sum(custo.custo_anual if hasattr(custo, 'custo_anual') else 0 
                                      for custo in custos_variaveis)
        
        dados['financeiro'] = {
            'custos_fixos': total_custos_fixos,
            'custos_variaveis': total_custos_variaveis,
            'custos_totais': total_custos_fixos + total_custos_variaveis,
        }
    except Exception as e:
        dados['financeiro'] = {
            'custos_fixos': 0,
            'custos_variaveis': 0,
            'custos_totais': 0,
        }
    
    # 5. DÍVIDAS
    try:
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        total_dividas = sum(f.valor_parcela * 12 for f in financiamentos)
        
        dados['financeiro']['dividas_totais'] = total_dividas
    except Exception as e:
        dados['financeiro']['dividas_totais'] = 0
    
    # CONSOLIDAÇÃO FINAL
    receita_pecuaria = dados['pecuaria']['valor_total'] * 0.15  # Estimativa 15% de vendas/ano
    receita_agricola = dados['agricultura']['receita_total']
    receita_total = receita_pecuaria + receita_agricola
    
    custos_totais = dados['financeiro']['custos_totais']
    lucro_bruto = receita_total - custos_totais
    
    dividas_totais = dados['financeiro']['dividas_totais']
    capacidade_pagamento = lucro_bruto - dividas_totais
    
    cobertura = receita_total / dividas_totais if dividas_totais > 0 else 0
    
    valor_patrimonio = dados['patrimonio']['valor_total']
    ltv = (dividas_totais / valor_patrimonio * 100) if valor_patrimonio > 0 else 0
    
    # Cálculo de score de risco (0-100)
    score = 0
    
    # Cobertura
    if cobertura > 3:
        score += 30
    elif cobertura > 1.5:
        score += 20
    else:
        score += 10 if cobertura > 0 else 0
    
    # LTV
    if ltv < 30:
        score += 30
    elif ltv < 60:
        score += 20
    else:
        score += 10 if ltv < 100 else 0
    
    # Diversificação
    if receita_pecuaria > 0 and receita_agricola > 0:
        score += 20
    
    # Capacidade positiva
    if capacidade_pagamento > 0:
        score += 20
    
    # Recomendação
    if score >= 80:
        recomendacao = "APROVAR"
        recomendacao_icon = "✅"
    elif score >= 60:
        recomendacao = "APROVAR COM CONDIÇÕES"
        recomendacao_icon = "⚠️"
    else:
        recomendacao = "REPROVAR"
        recomendacao_icon = "❌"
    
    dados['consolidado'] = {
        'receita_pecuaria': receita_pecuaria,
        'receita_agricola': receita_agricola,
        'receita_total': receita_total,
        'custos_totais': custos_totais,
        'lucro_bruto': lucro_bruto,
        'dividas_totais': dividas_totais,
        'capacidade_pagamento': capacidade_pagamento,
        'cobertura': cobertura,
        'valor_patrimonio': valor_patrimonio,
        'ltv': ltv,
        'score': score,
        'recomendacao': recomendacao,
        'recomendacao_icon': recomendacao_icon,
    }
    
    return dados
