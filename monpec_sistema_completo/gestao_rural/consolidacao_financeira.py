from .models import *

def consolidar_dados_propriedade(propriedade):
    dados = {'pecuaria': {}, 'agricultura': {}, 'patrimonio': {}, 'financeiro': {}, 'consolidado': {}}
    
    # Pecuária
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    valor_rebanho = sum(item.valor_total for item in inventario)
    dados['pecuaria'] = {'valor_total': valor_rebanho, 'quantidade_total': sum(item.quantidade for item in inventario)}
    
    # Agricultura
    ciclos = CicloProducaoAgricola.objects.filter(propriedade=propriedade)
    receita_agricola = sum(ciclo.receita_esperada_total for ciclo in ciclos)
    dados['agricultura'] = {'receita_total': receita_agricola}
    
    # Patrimônio
    bens = BemImobilizado.objects.filter(propriedade=propriedade, ativo=True)
    dados['patrimonio'] = {'valor_total': sum(bem.valor_aquisicao for bem in bens)}
    
    # Custos
    custos_fixos = sum(c.custo_anual for c in CustoFixo.objects.filter(propriedade=propriedade, ativo=True))
    custos_variaveis = sum(c.custo_anual for c in CustoVariavel.objects.filter(propriedade=propriedade, ativo=True))
    dados['financeiro'] = {'custos_totais': custos_fixos + custos_variaveis}
    
    # Dívidas
    dividas = sum(f.valor_parcela * 12 for f in Financiamento.objects.filter(propriedade=propriedade, ativo=True))
    dados['financeiro']['dividas_totais'] = dividas
    
    # Consolidação
    receita_pecuaria = valor_rebanho * 0.15
    receita_total = receita_pecuaria + receita_agricola
    lucro = receita_total - dados['financeiro']['custos_totais']
    capacidade = lucro - dividas
    cobertura = receita_total / dividas if dividas > 0 else 0
    ltv = (dividas / dados['patrimonio']['valor_total'] * 100) if dados['patrimonio']['valor_total'] > 0 else 0
    
    score = 0
    if cobertura > 3: score += 30
    elif cobertura > 1.5: score += 20
    if ltv < 30: score += 30
    elif ltv < 60: score += 20
    if receita_pecuaria > 0 and receita_agricola > 0: score += 20
    if capacidade > 0: score += 20
    
    rec = "APROVAR" if score >= 80 else "APROVAR COM CONDIÇÕES" if score >= 60 else "REPROVAR"
    
    dados['consolidado'] = {
        'receita_total': receita_total, 'capacidade_pagamento': capacidade,
        'cobertura': cobertura, 'valor_patrimonio': dados['patrimonio']['valor_total'],
        'ltv': ltv, 'score': score, 'recomendacao': rec
    }
    return dados
