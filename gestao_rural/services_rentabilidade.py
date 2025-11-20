# -*- coding: utf-8 -*-
"""
Serviço para cálculo de rentabilidade pecuária
- Custo por animal
- Custo por arroba
- Lucratividade real
"""

from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Q, F
from django.utils import timezone

from .models import (
    Propriedade, InventarioRebanho, CategoriaAnimal,
    CustoFixo, CustoVariavel
)
from .models_financeiro import LancamentoFinanceiro, CategoriaFinanceira
from .models_operacional import ConsumoCombustivel, ManutencaoEquipamento
from .models_funcionarios import Funcionario


def calcular_custo_por_animal(propriedade, periodo_dias=365):
    """
    Calcula o custo total por animal considerando todos os custos da operação.
    
    Args:
        propriedade: Propriedade a ser analisada
        periodo_dias: Período em dias para cálculo (padrão: 365 dias = 1 ano)
    
    Returns:
        dict com custos detalhados e custo por animal
    """
    # 1. Custos Fixos (anuais)
    custos_fixos = CustoFixo.objects.filter(
        propriedade=propriedade,
        ativo=True
    )
    custo_fixo_total = sum(c.custo_anual for c in custos_fixos if c.custo_anual)
    
    # 2. Custos Variáveis (por cabeça)
    custos_variaveis = CustoVariavel.objects.filter(
        propriedade=propriedade,
        ativo=True
    )
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_animais = sum(item.quantidade for item in inventario)
    
    custo_variavel_total = Decimal('0')
    for custo_var in custos_variaveis:
        if hasattr(custo_var, 'custo_anual_por_cabeca'):
            custo_variavel_total += custo_var.custo_anual_por_cabeca * total_animais
        elif hasattr(custo_var, 'valor_por_cabeca'):
            custo_variavel_total += custo_var.valor_por_cabeca * total_animais * 12
    
    # 3. Custos Operacionais (do período)
    # Combustível
    data_inicio = timezone.localdate() - timedelta(days=periodo_dias)
    consumos = ConsumoCombustivel.objects.filter(
        tanque__propriedade=propriedade,
        data__gte=data_inicio
    ) if ConsumoCombustivel else []
    custo_combustivel = sum(c.valor_total for c in consumos) if consumos else Decimal('0')
    
    # Folha de pagamento
    funcionarios = Funcionario.objects.filter(
        propriedade=propriedade,
        situacao='ATIVO'
    ) if Funcionario else []
    custo_folha = sum(f.salario_base for f in funcionarios) * (periodo_dias / 30) if funcionarios else Decimal('0')
    
    # Manutenções
    manutencoes = ManutencaoEquipamento.objects.filter(
        equipamento__propriedade=propriedade,
        data__gte=data_inicio
    ) if ManutencaoEquipamento else []
    custo_manutencao = sum(m.custo_total for m in manutencoes if hasattr(m, 'custo_total')) if manutencoes else Decimal('0')
    
    # 4. Custos Financeiros (despesas do período)
    lancamentos_despesas = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_QUITADO,
        data_competencia__gte=data_inicio
    )
    custo_financeiro = lancamentos_despesas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    # 5. Nutrição (suplementação)
    try:
        from .models_operacional import DistribuicaoSuplementacao
        distribuicoes = DistribuicaoSuplementacao.objects.filter(
            estoque__propriedade=propriedade,
            data__gte=data_inicio
        )
        custo_nutricao = sum(d.valor_total for d in distribuicoes) if distribuicoes else Decimal('0')
    except ImportError:
        custo_nutricao = Decimal('0')
    
    # Total de custos
    custo_total = (
        (custo_fixo_total * periodo_dias / 365) +  # Proporcional ao período
        (custo_variavel_total * periodo_dias / 365) +
        custo_combustivel +
        custo_folha +
        custo_manutencao +
        custo_financeiro +
        custo_nutricao
    )
    
    # Custo por animal
    custo_por_animal = custo_total / total_animais if total_animais > 0 else Decimal('0')
    
    return {
        'periodo_dias': periodo_dias,
        'total_animais': total_animais,
        'custos_detalhados': {
            'fixos': float(custo_fixo_total * periodo_dias / 365),
            'variaveis': float(custo_variavel_total * periodo_dias / 365),
            'combustivel': float(custo_combustivel),
            'folha': float(custo_folha),
            'manutencao': float(custo_manutencao),
            'financeiro': float(custo_financeiro),
            'nutricao': float(custo_nutricao),
        },
        'custo_total': float(custo_total),
        'custo_por_animal': float(custo_por_animal),
        'custo_por_animal_mes': float(custo_por_animal * 30 / periodo_dias),
    }


def calcular_custo_por_arroba(propriedade, periodo_dias=365):
    """
    Calcula o custo por arroba produzida.
    
    Args:
        propriedade: Propriedade a ser analisada
        periodo_dias: Período em dias para cálculo
    
    Returns:
        dict com custos e produção em arrobas
    """
    # Calcular custo total (reutilizar função anterior)
    custo_por_animal_data = calcular_custo_por_animal(propriedade, periodo_dias)
    custo_total = Decimal(str(custo_por_animal_data['custo_total']))
    
    # Calcular produção em arrobas
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    
    # Peso médio por categoria (em kg)
    peso_total_kg = Decimal('0')
    for item in inventario:
        categoria = item.categoria
        quantidade = item.quantidade
        
        # Usar peso médio da categoria se disponível
        if categoria and categoria.peso_medio_kg:
            peso_categoria = categoria.peso_medio_kg * quantidade
        else:
            # Valores padrão por categoria (em kg)
            peso_padrao = {
                'bezerro': 100,
                'novilha': 250,
                'novilho': 300,
                'vaca': 450,
                'touro': 600,
                'boi': 500,
                'garrote': 350,
            }
            nome_cat = categoria.nome.lower() if categoria else ''
            peso_medio = Decimal('300')  # Padrão
            for chave, valor in peso_padrao.items():
                if chave in nome_cat:
                    peso_medio = Decimal(str(valor))
                    break
            peso_categoria = peso_medio * quantidade
        
        peso_total_kg += peso_categoria
    
    # Converter para arrobas (1 arroba = 15 kg)
    arrobas_totais = peso_total_kg / Decimal('15')
    
    # Custo por arroba
    custo_por_arroba = custo_total / arrobas_totais if arrobas_totais > 0 else Decimal('0')
    
    return {
        'periodo_dias': periodo_dias,
        'peso_total_kg': float(peso_total_kg),
        'arrobas_totais': float(arrobas_totais),
        'custo_total': float(custo_total),
        'custo_por_arroba': float(custo_por_arroba),
    }


def calcular_lucratividade_real(propriedade, periodo_dias=365):
    """
    Calcula a lucratividade real da operação (receitas - custos).
    
    Args:
        propriedade: Propriedade a ser analisada
        periodo_dias: Período em dias para cálculo
    
    Returns:
        dict com receitas, custos e lucratividade
    """
    # Receitas reais (do período)
    data_inicio = timezone.localdate() - timedelta(days=periodo_dias)
    
    # Receitas financeiras
    lancamentos_receitas = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_QUITADO,
        data_competencia__gte=data_inicio
    )
    receita_financeira = lancamentos_receitas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    # Receitas de vendas de animais
    try:
        from .models import MovimentacaoIndividual
        vendas = MovimentacaoIndividual.objects.filter(
            animal__propriedade=propriedade,
            tipo_movimentacao='VENDA',
            data_movimentacao__gte=data_inicio
        )
        receita_vendas = sum(v.valor for v in vendas if v.valor) if vendas else Decimal('0')
    except (ImportError, AttributeError):
        receita_vendas = Decimal('0')
    
    receita_total = receita_financeira + receita_vendas
    
    # Custos totais (reutilizar função)
    custo_data = calcular_custo_por_animal(propriedade, periodo_dias)
    custo_total = Decimal(str(custo_data['custo_total']))
    
    # Lucro
    lucro = receita_total - custo_total
    
    # Margem de lucro
    margem_lucro = (lucro / receita_total * 100) if receita_total > 0 else Decimal('0')
    
    # ROI (Return on Investment)
    # Considerar valor do rebanho como investimento
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    valor_rebanho = sum(item.valor_total or 0 for item in inventario)
    roi = (lucro / valor_rebanho * 100) if valor_rebanho > 0 else Decimal('0')
    
    return {
        'periodo_dias': periodo_dias,
        'receita_total': float(receita_total),
        'receita_financeira': float(receita_financeira),
        'receita_vendas': float(receita_vendas),
        'custo_total': float(custo_total),
        'lucro': float(lucro),
        'margem_lucro': float(margem_lucro),
        'roi': float(roi),
        'valor_rebanho': float(valor_rebanho),
    }


def calcular_indicadores_completos(propriedade, periodo_dias=365):
    """
    Calcula todos os indicadores de rentabilidade de uma vez.
    
    Returns:
        dict consolidado com todos os indicadores
    """
    custo_animal = calcular_custo_por_animal(propriedade, periodo_dias)
    custo_arroba = calcular_custo_por_arroba(propriedade, periodo_dias)
    lucratividade = calcular_lucratividade_real(propriedade, periodo_dias)
    
    return {
        'custo_por_animal': custo_animal,
        'custo_por_arroba': custo_arroba,
        'lucratividade': lucratividade,
        'periodo_dias': periodo_dias,
        'data_calculo': timezone.now().isoformat(),
    }







