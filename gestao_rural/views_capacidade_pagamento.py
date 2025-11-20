from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Propriedade, InventarioRebanho, CustoFixo, CustoVariavel, Financiamento
from .models import IndicadorFinanceiro


@login_required
def capacidade_pagamento_dashboard(request, propriedade_id):
    """Dashboard do módulo de capacidade de pagamento"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Calcula indicadores de capacidade de pagamento
    indicadores = calcular_capacidade_pagamento(propriedade)
    
    # Análise de fluxo de caixa
    fluxo_caixa = analisar_fluxo_caixa(propriedade)
    
    # Cenários de stress
    cenarios = gerar_cenarios_stress(propriedade)
    
    # Recomendações
    recomendacoes = gerar_recomendacoes(propriedade, indicadores)
    
    context = {
        'propriedade': propriedade,
        'indicadores': indicadores,
        'fluxo_caixa': fluxo_caixa,
        'cenarios': cenarios,
        'recomendacoes': recomendacoes,
    }
    
    return render(request, 'gestao_rural/capacidade_pagamento_dashboard.html', context)


def calcular_capacidade_pagamento(propriedade):
    """Calcula indicadores de capacidade de pagamento"""
    indicadores = {}
    
    try:
        # 1. RECEITAS
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        
        # Calcular valor_rebanho manualmente (não é campo do banco)
        valor_rebanho = sum(
            Decimal(str(item.quantidade)) * Decimal(str(item.valor_por_cabeca))
            for item in inventario
        )
        
        # Receita estimada (15% do valor do rebanho ao ano)
        receita_anual_estimada = valor_rebanho * Decimal('0.15')
        receita_mensal_estimada = receita_anual_estimada / Decimal('12')
        
        # 2. CUSTOS
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custo_fixo_mensal = sum(custo.valor_mensal for custo in custos_fixos if custo.valor_mensal)
        custo_fixo_anual = sum(custo.custo_anual for custo in custos_fixos)
        
        custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
        custo_variavel_anual = sum(custo.custo_anual_por_cabeca for custo in custos_variaveis)
        custo_variavel_mensal = custo_variavel_anual / 12
        
        # 3. DÍVIDAS
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        parcelas_mensais = sum(f.valor_parcela for f in financiamentos)
        parcelas_anuais = parcelas_mensais * 12
        
        # 4. INDICADORES DE CAPACIDADE
        custos_totais_mensais = custo_fixo_mensal + custo_variavel_mensal + parcelas_mensais
        custos_totais_anuais = custo_fixo_anual + custo_variavel_anual + parcelas_anuais
        
        # Margem de segurança
        margem_seguranca_mensal = receita_mensal_estimada - custos_totais_mensais
        margem_seguranca_anual = receita_anual_estimada - custos_totais_anuais
        
        # Índices de capacidade
        indice_capacidade_pagamento = (receita_mensal_estimada / custos_totais_mensais) * 100 if custos_totais_mensais > 0 else 0
        indice_endividamento = (parcelas_anuais / receita_anual_estimada) * 100 if receita_anual_estimada > 0 else 0
        indice_cobertura_divida = receita_anual_estimada / parcelas_anuais if parcelas_anuais > 0 else 0
        
        # Classificação da capacidade
        if indice_capacidade_pagamento >= 150:
            classificacao = "Excelente"
            cor_classificacao = "success"
        elif indice_capacidade_pagamento >= 120:
            classificacao = "Boa"
            cor_classificacao = "info"
        elif indice_capacidade_pagamento >= 100:
            classificacao = "Adequada"
            cor_classificacao = "warning"
        else:
            classificacao = "Crítica"
            cor_classificacao = "danger"
        
        indicadores = {
            'receita_mensal': receita_mensal_estimada,
            'receita_anual': receita_anual_estimada,
            'custos_mensais': custos_totais_mensais,
            'custos_anuais': custos_totais_anuais,
            'parcelas_mensais': parcelas_mensais,
            'parcelas_anuais': parcelas_anuais,
            'margem_seguranca_mensal': margem_seguranca_mensal,
            'margem_seguranca_anual': margem_seguranca_anual,
            'indice_capacidade_pagamento': indice_capacidade_pagamento,
            'indice_endividamento': indice_endividamento,
            'indice_cobertura_divida': indice_cobertura_divida,
            'classificacao': classificacao,
            'cor_classificacao': cor_classificacao
        }
        
    except Exception as e:
        print(f"Erro ao calcular capacidade de pagamento: {e}")
        indicadores = {'erro': str(e)}
    
    return indicadores


def analisar_fluxo_caixa(propriedade):
    """Analisa o fluxo de caixa da propriedade"""
    fluxo = {}
    
    try:
        # Busca dados básicos
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        
        # Calcular valor_rebanho manualmente (não é campo do banco)
        valor_rebanho = sum(
            Decimal(str(item.quantidade)) * Decimal(str(item.valor_por_cabeca))
            for item in inventario
        )
        
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custo_fixo_mensal = sum(Decimal(str(custo.valor_mensal)) for custo in custos_fixos if custo.valor_mensal)
        
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        parcelas_mensais = sum(Decimal(str(f.valor_parcela)) for f in financiamentos)
        
        # Receita mensal estimada (convertendo para Decimal)
        receita_mensal = (valor_rebanho * Decimal('0.15')) / Decimal('12')
        
        # Fluxo mensal (convertendo para Decimal)
        fluxo_mensal = receita_mensal - custo_fixo_mensal - parcelas_mensais
        
        # Projeção para 12 meses
        projecao_mensal = []
        saldo_acumulado = Decimal('0.00')
        
        for mes in range(1, 13):
            saldo_acumulado += fluxo_mensal
            projecao_mensal.append({
                'mes': mes,
                'receita': receita_mensal,
                'custos': custo_fixo_mensal + parcelas_mensais,
                'fluxo_mensal': fluxo_mensal,
                'saldo_acumulado': saldo_acumulado
            })
        
        fluxo = {
            'receita_mensal': receita_mensal,
            'custos_mensais': custo_fixo_mensal + parcelas_mensais,
            'fluxo_mensal': fluxo_mensal,
            'projecao_mensal': projecao_mensal,
            'saldo_final': saldo_acumulado
        }
        
    except Exception as e:
        print(f"Erro ao analisar fluxo de caixa: {e}")
        fluxo = {'erro': str(e)}
    
    return fluxo


def gerar_cenarios_stress(propriedade):
    """Gera cenários de stress para análise de capacidade"""
    cenarios = []
    
    try:
        # Cenário base
        indicadores_base = calcular_capacidade_pagamento(propriedade)
        
        # Cenários de stress
        cenarios_stress = [
            {'nome': 'Cenário Base', 'fator_receita': 1.0, 'fator_custos': 1.0},
            {'nome': 'Receita -20%', 'fator_receita': 0.8, 'fator_custos': 1.0},
            {'nome': 'Receita -40%', 'fator_receita': 0.6, 'fator_custos': 1.0},
            {'nome': 'Custos +20%', 'fator_receita': 1.0, 'fator_custos': 1.2},
            {'nome': 'Custos +40%', 'fator_receita': 1.0, 'fator_custos': 1.4},
            {'nome': 'Cenário Crítico', 'fator_receita': 0.7, 'fator_custos': 1.3}
        ]
        
        # Verificar se indicadores_base tem as chaves necessárias
        receita_mensal = indicadores_base.get('receita_mensal', Decimal('0'))
        custos_mensais = indicadores_base.get('custos_mensais', Decimal('0'))
        
        for cenario in cenarios_stress:
            receita_ajustada = receita_mensal * Decimal(str(cenario['fator_receita']))
            custos_ajustados = custos_mensais * Decimal(str(cenario['fator_custos']))
            
            margem = receita_ajustada - custos_ajustados
            indice = float(receita_ajustada / custos_ajustados) * 100 if custos_ajustados > 0 else 0
            
            # Classificação do cenário
            if indice >= 120:
                status = "Adequado"
                cor = "success"
            elif indice >= 100:
                status = "Atenção"
                cor = "warning"
            else:
                status = "Crítico"
                cor = "danger"
            
            cenarios.append({
                'nome': cenario['nome'],
                'receita': receita_ajustada,
                'custos': custos_ajustados,
                'margem': margem,
                'indice': indice,
                'status': status,
                'cor': cor
            })
        
    except Exception as e:
        print(f"Erro ao gerar cenários de stress: {e}")
        cenarios = []
    
    return cenarios


def gerar_recomendacoes(propriedade, indicadores):
    """Gera recomendações baseadas nos indicadores"""
    recomendacoes = []
    
    try:
        # Validar que as chaves existem no dicionário
        indice_capacidade = indicadores.get('indice_capacidade_pagamento', 0)
        indice_endividamento = indicadores.get('indice_endividamento', 0)
        margem_seguranca = indicadores.get('margem_seguranca_mensal', 0)
        
        # Recomendações baseadas no índice de capacidade
        if indice_capacidade < 100:
            recomendacoes.append({
                'tipo': 'Crítica',
                'titulo': 'Capacidade de Pagamento Insuficiente',
                'descricao': 'A receita não cobre os custos totais. Considere reduzir custos ou aumentar receitas.',
                'prioridade': 'Alta',
                'cor': 'danger'
            })
        
        if indice_endividamento > 30:
            recomendacoes.append({
                'tipo': 'Endividamento',
                'titulo': 'Alto Nível de Endividamento',
                'descricao': 'Mais de 30% da receita comprometida com parcelas. Avalie renegociação.',
                'prioridade': 'Média',
                'cor': 'warning'
            })
        
        if margem_seguranca < 0:
            recomendacoes.append({
                'tipo': 'Fluxo de Caixa',
                'titulo': 'Fluxo de Caixa Negativo',
                'descricao': 'Gastos superam receitas. Urgente revisar orçamento.',
                'prioridade': 'Alta',
                'cor': 'danger'
            })
        
        if indice_capacidade > 150:
            recomendacoes.append({
                'tipo': 'Oportunidade',
                'titulo': 'Excelente Capacidade de Pagamento',
                'descricao': 'Boa margem de segurança. Considere investimentos ou expansão.',
                'prioridade': 'Baixa',
                'cor': 'success'
            })
        
        # Recomendações gerais
        if not recomendacoes:
            recomendacoes.append({
                'tipo': 'Geral',
                'titulo': 'Situação Financeira Estável',
                'descricao': 'Continue monitorando os indicadores regularmente.',
                'prioridade': 'Baixa',
                'cor': 'info'
            })
        
    except Exception as e:
        print(f"Erro ao gerar recomendações: {e}")
        recomendacoes = []
    
    return recomendacoes

