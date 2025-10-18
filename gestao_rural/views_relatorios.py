from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Avg, Count
from decimal import Decimal
from datetime import datetime, timedelta
import json
from .models import Propriedade, InventarioRebanho, MovimentacaoProjetada
from .models import CustoFixo, CustoVariavel, Financiamento, IndicadorFinanceiro


def relatorios_dashboard(request, propriedade_id):
    """Dashboard do módulo de relatórios"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca dados para resumo
    resumo_dados = gerar_resumo_propriedade(propriedade)
    
    context = {
        'propriedade': propriedade,
        'resumo_dados': resumo_dados,
    }
    
    return render(request, 'gestao_rural/relatorios_dashboard.html', context)


def relatorio_inventario(request, propriedade_id):
    """Relatório de inventário do rebanho"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca inventário atual
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade).order_by('categoria__nome')
    
    # Calcula totais
    total_animais = sum(item.quantidade for item in inventario)
    valor_total_rebanho = sum(item.valor_total for item in inventario if item.valor_total)
    
    # Agrupa por categoria
    inventario_por_categoria = {}
    for item in inventario:
        categoria = item.categoria.nome
        if categoria not in inventario_por_categoria:
            inventario_por_categoria[categoria] = {
                'quantidade': 0,
                'valor_total': Decimal('0.00'),
                'itens': []
            }
        inventario_por_categoria[categoria]['quantidade'] += item.quantidade
        inventario_por_categoria[categoria]['valor_total'] += item.valor_total or Decimal('0.00')
        inventario_por_categoria[categoria]['itens'].append(item)
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'inventario_por_categoria': inventario_por_categoria,
        'total_animais': total_animais,
        'valor_total_rebanho': valor_total_rebanho,
        'data_relatorio': datetime.now().date(),
    }
    
    return render(request, 'gestao_rural/relatorio_inventario.html', context)


def relatorio_financeiro(request, propriedade_id):
    """Relatório financeiro completo"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Dados financeiros
    dados_financeiros = gerar_dados_financeiros(propriedade)
    
    # Indicadores financeiros recentes
    indicadores = IndicadorFinanceiro.objects.filter(
        propriedade=propriedade
    ).order_by('-data_referencia')[:20]
    
    context = {
        'propriedade': propriedade,
        'dados_financeiros': dados_financeiros,
        'indicadores': indicadores,
        'data_relatorio': datetime.now().date(),
    }
    
    return render(request, 'gestao_rural/relatorio_financeiro.html', context)


def relatorio_custos(request, propriedade_id):
    """Relatório de custos de produção"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Custos fixos
    custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
    total_custos_fixos_mes = sum(custo.valor_mensal for custo in custos_fixos if custo.valor_mensal)
    total_custos_fixos_ano = sum(custo.custo_anual for custo in custos_fixos)
    
    # Custos variáveis
    custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
    total_custos_variaveis_ano = sum(custo.custo_anual_por_cabeca for custo in custos_variaveis)
    
    # Agrupa custos fixos por tipo
    custos_fixos_por_tipo = {}
    for custo in custos_fixos:
        tipo = custo.tipo_custo
        if tipo not in custos_fixos_por_tipo:
            custos_fixos_por_tipo[tipo] = {
                'total_mensal': Decimal('0.00'),
                'total_anual': Decimal('0.00'),
                'custos': []
            }
        custos_fixos_por_tipo[tipo]['total_mensal'] += custo.valor_mensal or Decimal('0.00')
        custos_fixos_por_tipo[tipo]['total_anual'] += custo.custo_anual
        custos_fixos_por_tipo[tipo]['custos'].append(custo)
    
    context = {
        'propriedade': propriedade,
        'custos_fixos': custos_fixos,
        'custos_variaveis': custos_variaveis,
        'custos_fixos_por_tipo': custos_fixos_por_tipo,
        'total_custos_fixos_mes': total_custos_fixos_mes,
        'total_custos_fixos_ano': total_custos_fixos_ano,
        'total_custos_variaveis_ano': total_custos_variaveis_ano,
        'data_relatorio': datetime.now().date(),
    }
    
    return render(request, 'gestao_rural/relatorio_custos.html', context)


def relatorio_endividamento(request, propriedade_id):
    """Relatório de endividamento"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Financiamentos ativos
    financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
    
    # Calcula totais
    total_financiado = sum(f.valor_principal for f in financiamentos)
    total_parcelas_mes = sum(f.valor_parcela for f in financiamentos)
    total_parcelas_ano = total_parcelas_mes * 12
    
    # Agrupa por tipo
    financiamentos_por_tipo = {}
    for financiamento in financiamentos:
        tipo = financiamento.tipo.nome
        if tipo not in financiamentos_por_tipo:
            financiamentos_por_tipo[tipo] = {
                'total_principal': Decimal('0.00'),
                'total_parcelas_mes': Decimal('0.00'),
                'financiamentos': []
            }
        financiamentos_por_tipo[tipo]['total_principal'] += financiamento.valor_principal
        financiamentos_por_tipo[tipo]['total_parcelas_mes'] += financiamento.valor_parcela
        financiamentos_por_tipo[tipo]['financiamentos'].append(financiamento)
    
    context = {
        'propriedade': propriedade,
        'financiamentos': financiamentos,
        'financiamentos_por_tipo': financiamentos_por_tipo,
        'total_financiado': total_financiado,
        'total_parcelas_mes': total_parcelas_mes,
        'total_parcelas_ano': total_parcelas_ano,
        'data_relatorio': datetime.now().date(),
    }
    
    return render(request, 'gestao_rural/relatorio_endividamento.html', context)


def relatorio_consolidado(request, propriedade_id):
    """Relatório consolidado geral"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca todos os dados
    resumo_dados = gerar_resumo_propriedade(propriedade)
    dados_financeiros = gerar_dados_financeiros(propriedade)
    
    # Inventário
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    valor_total_rebanho = sum(item.valor_total for item in inventario if item.valor_total)
    
    # Custos
    custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
    total_custos_fixos_ano = sum(custo.custo_anual for custo in custos_fixos)
    
    # Financiamentos
    financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
    total_parcelas_ano = sum(f.valor_parcela for f in financiamentos) * 12
    
    context = {
        'propriedade': propriedade,
        'resumo_dados': resumo_dados,
        'dados_financeiros': dados_financeiros,
        'valor_total_rebanho': valor_total_rebanho,
        'total_custos_fixos_ano': total_custos_fixos_ano,
        'total_parcelas_ano': total_parcelas_ano,
        'data_relatorio': datetime.now().date(),
    }
    
    return render(request, 'gestao_rural/relatorio_consolidado.html', context)


def gerar_resumo_propriedade(propriedade):
    """Gera resumo geral da propriedade"""
    resumo = {}
    
    try:
        # Inventário
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        resumo['total_animais'] = sum(item.quantidade for item in inventario)
        resumo['valor_rebanho'] = sum(item.valor_total for item in inventario if item.valor_total)
        
        # Custos
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        resumo['custos_fixos_mes'] = sum(custo.valor_mensal for custo in custos_fixos if custo.valor_mensal)
        
        # Financiamentos
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        resumo['total_financiado'] = sum(f.valor_principal for f in financiamentos)
        resumo['parcelas_mes'] = sum(f.valor_parcela for f in financiamentos)
        
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")
    
    return resumo


def gerar_dados_financeiros(propriedade):
    """Gera dados financeiros para relatórios"""
    dados = {}
    
    try:
        # Receitas (simuladas baseadas no rebanho)
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        dados['receita_potencial_ano'] = sum(item.valor_total for item in inventario if item.valor_total) * Decimal('0.15')  # 15% ao ano
        
        # Custos
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        dados['custos_fixos_ano'] = sum(custo.custo_anual for custo in custos_fixos)
        
        # Financiamentos
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        dados['parcelas_ano'] = sum(f.valor_parcela for f in financiamentos) * 12
        
        # Resultado
        dados['lucro_estimado'] = dados['receita_potencial_ano'] - dados['custos_fixos_ano'] - dados['parcelas_ano']
        
    except Exception as e:
        print(f"Erro ao gerar dados financeiros: {e}")
    
    return dados

