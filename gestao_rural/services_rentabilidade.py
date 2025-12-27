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
import logging

logger = logging.getLogger(__name__)

from .models import (
    Propriedade, InventarioRebanho, CategoriaAnimal,
    CustoFixo, CustoVariavel
)
from .models_financeiro import LancamentoFinanceiro, CategoriaFinanceira
from .models_operacional import ConsumoCombustivel, ManutencaoEquipamento
from .models_funcionarios import Funcionario


def calcular_custo_por_animal(propriedade, periodo_dias=365, data_inicio=None, data_fim=None):
    """
    Calcula o custo total por animal considerando todos os custos da operação.
    
    Args:
        propriedade: Propriedade a ser analisada
        periodo_dias: Período em dias para cálculo (padrão: 365 dias = 1 ano)
        data_inicio: Data de início do período (opcional, calculada automaticamente se não fornecida)
        data_fim: Data de fim do período (opcional, usa hoje se não fornecida)
    
    Returns:
        dict com custos detalhados e custo por animal
    """
    # Definir período de cálculo
    if data_fim is None:
        data_fim = timezone.localdate()
    if data_inicio is None:
        data_inicio = data_fim - timedelta(days=periodo_dias)
    else:
        # Recalcular periodo_dias baseado nas datas fornecidas
        periodo_dias = (data_fim - data_inicio).days
    
    logger.debug(f"Calculando custos - Propriedade: {propriedade.id}, Período: {data_inicio} a {data_fim} ({periodo_dias} dias)")
    
    # 1. Custos Fixos (anuais) - proporcional ao período
    custos_fixos = CustoFixo.objects.filter(
        propriedade=propriedade,
        ativo=True
    )
    custo_fixo_total_anual = sum(c.custo_anual for c in custos_fixos if c.custo_anual)
    custo_fixo_total = (custo_fixo_total_anual * periodo_dias / 365) if periodo_dias > 0 else Decimal('0')
    
    # 2. Custos Variáveis (por cabeça) - proporcional ao período
    custos_variaveis = CustoVariavel.objects.filter(
        propriedade=propriedade,
        ativo=True
    )
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_animais = sum(item.quantidade for item in inventario)
    
    custo_variavel_total_anual = Decimal('0')
    for custo_var in custos_variaveis:
        if hasattr(custo_var, 'custo_anual_por_cabeca') and custo_var.custo_anual_por_cabeca:
            custo_variavel_total_anual += custo_var.custo_anual_por_cabeca * total_animais
        elif hasattr(custo_var, 'valor_por_cabeca') and custo_var.valor_por_cabeca:
            custo_variavel_total_anual += custo_var.valor_por_cabeca * total_animais * 12
    
    custo_variavel_total = (custo_variavel_total_anual * periodo_dias / 365) if periodo_dias > 0 else Decimal('0')
    
    # Se não houver custos variáveis cadastrados mas houver animais, criar valor padrão estimado
    if custo_variavel_total == Decimal('0') and total_animais > 0 and periodo_dias > 0:
        try:
            # Estimativa: R$ 50/animal/ano (custo variável padrão)
            custo_variavel_total = Decimal('50') * Decimal(str(total_animais)) * (Decimal(str(periodo_dias)) / Decimal('365'))
        except (ValueError, TypeError, ZeroDivisionError):
            custo_variavel_total = Decimal('0')
    
    # 3. Custos Operacionais (do período específico)
    # Combustível
    try:
        consumos = ConsumoCombustivel.objects.filter(
            tanque__propriedade=propriedade,
            data__gte=data_inicio,
            data__lte=data_fim
        )
        custo_combustivel = sum(c.valor_total or Decimal('0') for c in consumos) if consumos.exists() else Decimal('0')
    except Exception as e:
        logger.error(f"Erro ao calcular custo de combustível: {e}")
        custo_combustivel = Decimal('0')
    
    # Folha de pagamento - calcular proporcional ao período
    try:
        funcionarios = Funcionario.objects.filter(
            propriedade=propriedade,
            situacao='ATIVO'
        )
        # Calcular folha proporcional ao período (em meses)
        meses_periodo = Decimal(str(periodo_dias)) / Decimal('30.44') if periodo_dias > 0 else Decimal('0')  # Média de dias por mês
        custo_folha = sum(f.salario_base or Decimal('0') for f in funcionarios) * meses_periodo if funcionarios.exists() else Decimal('0')
        
        # Se não houver funcionários cadastrados mas houver animais, criar valor padrão estimado
        if custo_folha == Decimal('0') and total_animais > 0:
            # Estimativa: 1 funcionário para cada 300 animais, salário mínimo de R$ 1.500
            try:
                funcionarios_estimados = max(1, int(float(total_animais) / 300))
                custo_folha = Decimal('1500') * Decimal(str(funcionarios_estimados)) * meses_periodo
            except (ValueError, TypeError, ZeroDivisionError):
                # Se houver erro no cálculo, usar valor mínimo
                custo_folha = Decimal('1500') * meses_periodo
    except Exception as e:
        logger.error(f"Erro ao calcular custo de folha: {e}")
        custo_folha = Decimal('0')
    
    # Manutenções
    try:
        manutencoes = ManutencaoEquipamento.objects.filter(
            equipamento__propriedade=propriedade,
            data_agendamento__gte=data_inicio,
            data_agendamento__lte=data_fim
        )
        custo_manutencao = sum(
            getattr(m, 'custo_total', Decimal('0')) or Decimal('0') 
            for m in manutencoes 
            if hasattr(m, 'custo_total')
        ) if manutencoes.exists() else Decimal('0')
        
        # Se não houver manutenções no período, buscar de todo o período histórico para estimativa
        if custo_manutencao == Decimal('0') and periodo_dias > 0:
            try:
                from .models_operacional import Equipamento
                equipamentos = Equipamento.objects.filter(propriedade=propriedade, ativo=True)
                total_equipamentos = equipamentos.count()
                if total_equipamentos > 0:
                    # Estimativa: R$ 200/equipamento/ano
                    custo_manutencao = Decimal('200') * Decimal(str(total_equipamentos)) * (Decimal(str(periodo_dias)) / Decimal('365'))
            except (ImportError, AttributeError, ValueError, TypeError, ZeroDivisionError) as e:
                logger.debug(f"Não foi possível calcular estimativa de manutenção: {e}")
                pass
    except Exception as e:
        logger.error(f"Erro ao calcular custo de manutenção: {e}")
        custo_manutencao = Decimal('0')
    
    # 6. Veterinário (medicamentos e vacinas) - MOVER ANTES DO CUSTO FINANCEIRO
    # Buscar categorias relacionadas a veterinário, medicamentos e vacinas
    categoria_nomes_veterinario = [
        'Medicamentos e Veterinário',
        'Medicamentos',
        'Vacinas',
        'Veterinário',
        'Produtos Veterinários',
        'Vet(Med e Vac)',
        'Medicamentos e Vacinas'
    ]
    
    categorias_veterinario = CategoriaFinanceira.objects.filter(
        (Q(propriedade__isnull=True) | Q(propriedade=propriedade)) &
        Q(tipo=CategoriaFinanceira.TIPO_DESPESA) &
        (Q(nome__in=categoria_nomes_veterinario) |
         Q(nome__icontains='veterin') |
         Q(nome__icontains='medicamento') |
         Q(nome__icontains='vacina')) &
        Q(ativa=True)
    ).distinct()
    
    # Buscar lançamentos com essas categorias no período
    lancamentos_veterinario = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        categoria__in=categorias_veterinario,
        data_competencia__gte=data_inicio,
        data_competencia__lte=data_fim
    )
    custo_veterinario = sum(l.valor or Decimal('0') for l in lancamentos_veterinario) if lancamentos_veterinario else Decimal('0')
    
    # 4. Outras Despesas Financeiras (excluindo categorias já calculadas)
    # Buscar categorias que devem ser excluídas (já calculadas separadamente)
    categorias_excluir = []
    
    # Adicionar categoria de combustível
    try:
        cat_combustivel = CategoriaFinanceira.objects.filter(
            Q(propriedade__isnull=True) | Q(propriedade=propriedade),
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            nome__icontains='combust'
        ).first()
        if cat_combustivel:
            categorias_excluir.append(cat_combustivel.id)
    except:
        pass
    
    # Adicionar categorias de veterinário
    categorias_vet_ids = [c.id for c in categorias_veterinario] if categorias_veterinario else []
    categorias_excluir.extend(categorias_vet_ids)
    
    # Adicionar categoria de suplementação
    try:
        cat_suplemento = CategoriaFinanceira.objects.filter(
            Q(propriedade__isnull=True) | Q(propriedade=propriedade),
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            nome__icontains='suplement'
        ).first()
        if cat_suplemento:
            categorias_excluir.append(cat_suplemento.id)
    except:
        pass
    
    # Buscar outras despesas (excluindo as já calculadas)
    query_despesas = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        data_competencia__gte=data_inicio,
        data_competencia__lte=data_fim
    )
    
    if categorias_excluir:
        query_despesas = query_despesas.exclude(categoria_id__in=categorias_excluir)
    
    # Excluir também despesas de folha (será calculado via Funcionario)
    try:
        cat_folha = CategoriaFinanceira.objects.filter(
            (Q(propriedade__isnull=True) | Q(propriedade=propriedade)) &
            Q(tipo=CategoriaFinanceira.TIPO_DESPESA) &
            (Q(nome__icontains='folha') | Q(nome__icontains='salário') | Q(nome__icontains='funcionário'))
        ).first()
        if cat_folha:
            query_despesas = query_despesas.exclude(categoria_id=cat_folha.id)
    except:
        pass
    
    custo_financeiro = query_despesas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    # 5. Nutrição (suplementação)
    try:
        from .models_operacional import DistribuicaoSuplementacao
        distribuicoes = DistribuicaoSuplementacao.objects.filter(
            estoque__propriedade=propriedade,
            data__gte=data_inicio,
            data__lte=data_fim
        )
        custo_nutricao = sum(d.valor_total or Decimal('0') for d in distribuicoes) if distribuicoes.exists() else Decimal('0')
    except (ImportError, AttributeError) as e:
        logger.debug(f"Não foi possível calcular custo de nutrição: {e}")
        custo_nutricao = Decimal('0')
    
    # Se não houver despesas financeiras no período mas houver custos operacionais, estimar
    # Despesas financeiras geralmente representam 5-10% dos custos operacionais
    if custo_financeiro == Decimal('0') and total_animais > 0:
        try:
            custos_operacionais_base = custo_combustivel + custo_folha + custo_manutencao + custo_nutricao + custo_veterinario
            if custos_operacionais_base > Decimal('0'):
                # Estimativa: 7% dos custos operacionais
                custo_financeiro = custos_operacionais_base * Decimal('0.07')
        except (ValueError, TypeError) as e:
            logger.debug(f"Não foi possível calcular estimativa de custo financeiro: {e}")
            pass
    
    # Total de custos (custos fixos e variáveis já estão proporcionais ao período)
    custo_total = (
        custo_fixo_total +  # Já proporcional ao período
        custo_variavel_total +  # Já proporcional ao período
        custo_combustivel +
        custo_folha +
        custo_manutencao +
        custo_financeiro +
        custo_nutricao +
        custo_veterinario
    )
    
    # Custo por animal
    custo_por_animal = (custo_total / Decimal(str(total_animais))) if total_animais > 0 else Decimal('0')
    
    # Custo mensal médio (custo por animal / número de meses no período)
    # Usar 30.44 como média de dias por mês para cálculo mais preciso
    meses_no_periodo = Decimal(str(periodo_dias)) / Decimal('30.44') if periodo_dias > 0 else Decimal('1')
    custo_por_animal_mes = (custo_por_animal / meses_no_periodo) if meses_no_periodo > 0 else Decimal('0')
    
    logger.debug(f"Resultado - Custo Total: {custo_total}, Custo por Animal: {custo_por_animal}, Custo Mensal: {custo_por_animal_mes}, Total Animais: {total_animais}")
    
    return {
        'periodo_dias': periodo_dias,
        'total_animais': total_animais,
        'custos_detalhados': {
            'fixos': float(custo_fixo_total),  # Já proporcional
            'variaveis': float(custo_variavel_total),  # Já proporcional
            'combustivel': float(custo_combustivel),
            'folha': float(custo_folha),
            'manutencao': float(custo_manutencao),
            'financeiro': float(custo_financeiro),
            'nutricao': float(custo_nutricao),
            'veterinario': float(custo_veterinario),
        },
        'custo_total': float(custo_total),
        'custo_por_animal': float(custo_por_animal),
        'custo_por_animal_mes': float(custo_por_animal_mes),
    }


def calcular_custo_por_arroba(propriedade, periodo_dias=365, data_inicio=None, data_fim=None):
    """
    Calcula o custo por arroba produzida.
    
    Args:
        propriedade: Propriedade a ser analisada
        periodo_dias: Período em dias para cálculo
    
    Returns:
        dict com custos e produção em arrobas
    """
    # Calcular custo total (reutilizar função anterior)
    custo_por_animal_data = calcular_custo_por_animal(propriedade, periodo_dias, data_inicio, data_fim)
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


def calcular_lucratividade_real(propriedade, periodo_dias=365, data_inicio=None, data_fim=None):
    """
    Calcula a lucratividade real da operação (receitas - custos).
    
    Args:
        propriedade: Propriedade a ser analisada
        periodo_dias: Período em dias para cálculo
    
    Returns:
        dict com receitas, custos e lucratividade
    """
    # Definir período de cálculo
    if data_fim is None:
        data_fim = timezone.localdate()
    if data_inicio is None:
        data_inicio = data_fim - timedelta(days=periodo_dias)
    else:
        periodo_dias = (data_fim - data_inicio).days
    
    # Receitas financeiras - incluir todos (quitados e pendentes) para cálculo completo
    # IMPORTANTE: Excluir receitas que já foram registradas via MovimentacaoIndividual (vendas de animais)
    # para evitar duplicação
    lancamentos_receitas = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        data_competencia__gte=data_inicio,
        data_competencia__lte=data_fim
    )
    
    # Excluir transferências (não são receitas reais)
    lancamentos_receitas = lancamentos_receitas.exclude(tipo=CategoriaFinanceira.TIPO_TRANSFERENCIA)
    
    # Verificar se há categoria de "Venda de Animais" para excluir duplicação
    # pois vendas de animais são contabilizadas via MovimentacaoIndividual
    try:
        categorias_venda_animais = CategoriaFinanceira.objects.filter(
            (Q(propriedade__isnull=True) | Q(propriedade=propriedade)) &
            Q(tipo=CategoriaFinanceira.TIPO_RECEITA) &
            (Q(nome__icontains='venda') | Q(nome__icontains='animal') | Q(nome__icontains='pecuária'))
        )
        
        # Se existirem categorias de venda de animais, excluir do cálculo financeiro
        if categorias_venda_animais.exists():
            categoria_ids = [c.id for c in categorias_venda_animais]
            lancamentos_receitas = lancamentos_receitas.exclude(categoria_id__in=categoria_ids)
            logger.debug(f"Excluindo {categorias_venda_animais.count()} categoria(s) de venda de animais do cálculo para evitar duplicação")
    except Exception as e:
        logger.debug(f"Erro ao excluir categorias de venda: {e}")
        pass
    
    receita_financeira = lancamentos_receitas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    # Receitas de vendas de animais (somar apenas se não foram contabilizadas no financeiro)
    try:
        from .models import MovimentacaoIndividual
        vendas = MovimentacaoIndividual.objects.filter(
            animal__propriedade=propriedade,
            tipo_movimentacao='VENDA',
            data_movimentacao__gte=data_inicio,
            data_movimentacao__lte=data_fim
        )
        receita_vendas = sum(v.valor or Decimal('0') for v in vendas if v.valor) if vendas.exists() else Decimal('0')
    except (ImportError, AttributeError) as e:
        logger.debug(f"Não foi possível calcular receitas de vendas: {e}")
        receita_vendas = Decimal('0')
    
    receita_total = receita_financeira + receita_vendas
    
    logger.debug(f"Receitas - Financeira: {receita_financeira}, Vendas: {receita_vendas}, Total: {receita_total}")
    
    # Custos totais (reutilizar função)
    custo_data = calcular_custo_por_animal(propriedade, periodo_dias, data_inicio, data_fim)
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


def calcular_indicadores_completos(propriedade, periodo_dias=365, data_inicio=None, data_fim=None):
    """
    Calcula todos os indicadores de rentabilidade de uma vez.
    
    Returns:
        dict consolidado com todos os indicadores
    """
    custo_animal = calcular_custo_por_animal(propriedade, periodo_dias, data_inicio, data_fim)
    custo_arroba = calcular_custo_por_arroba(propriedade, periodo_dias, data_inicio, data_fim)
    lucratividade = calcular_lucratividade_real(propriedade, periodo_dias, data_inicio, data_fim)
    
    return {
        'custo_por_animal': custo_animal,
        'custo_por_arroba': custo_arroba,
        'lucratividade': lucratividade,
        'periodo_dias': periodo_dias,
        'data_calculo': timezone.now().isoformat(),
    }








