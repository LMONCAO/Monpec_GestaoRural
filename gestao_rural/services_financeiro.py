"""Serviços auxiliares para o novo módulo financeiro."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable, List, Tuple

from django.db.models import Q, Sum
from django.utils import timezone

from .models_financeiro import (
    CategoriaFinanceira,
    ContaFinanceira,
    LancamentoFinanceiro,
)


@dataclass
class PeriodoFinanceiro:
    inicio: date
    fim: date

    @property
    def range_lookup(self) -> Tuple[date, date]:
        return self.inicio, self.fim


def periodo_mes_atual() -> PeriodoFinanceiro:
    hoje = timezone.localdate()
    inicio = hoje.replace(day=1)
    if hoje.month == 12:
        fim = hoje.replace(day=31)
    else:
        proximo_mes = (hoje.replace(day=28) + timedelta(days=4)).replace(day=1)
        fim = proximo_mes - timedelta(days=1)
    return PeriodoFinanceiro(inicio=inicio, fim=fim)


def calcular_totais_lancamentos(
    propriedade,
    periodo: PeriodoFinanceiro,
) -> dict:
    """Retorna totais de receitas, despesas e transferências no período."""

    qs = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        data_competencia__range=periodo.range_lookup,
        status__in=[
            LancamentoFinanceiro.STATUS_PENDENTE,
            LancamentoFinanceiro.STATUS_QUITADO,
        ],
    )

    agregados = qs.aggregate(
        total_receitas=Sum(
            "valor",
            filter=Q(tipo=CategoriaFinanceira.TIPO_RECEITA),
        ),
        total_despesas=Sum(
            "valor",
            filter=Q(tipo=CategoriaFinanceira.TIPO_DESPESA),
        ),
        total_transferencias=Sum(
            "valor",
            filter=Q(tipo=CategoriaFinanceira.TIPO_TRANSFERENCIA),
        ),
    )

    total_receitas = agregados["total_receitas"] or Decimal("0")
    total_despesas = agregados["total_despesas"] or Decimal("0")
    total_transferencias = agregados["total_transferencias"] or Decimal("0")

    saldo_liquido = total_receitas - total_despesas

    return {
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "total_transferencias": total_transferencias,
        "saldo_liquido": saldo_liquido,
        "queryset": qs,
    }


def listar_pendencias(propriedade, limite: int = 10) -> dict:
    """Retorna listas de lançamentos pendentes e atrasados."""

    hoje = timezone.localdate()
    pendentes = (
        LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            status=LancamentoFinanceiro.STATUS_PENDENTE,
        )
        .order_by("data_vencimento")[:limite]
    )

    atrasados = [
        lanc
        for lanc in pendentes
        if lanc.data_vencimento and lanc.data_vencimento < hoje
    ]

    return {
        "pendentes": pendentes,
        "atrasados": atrasados,
    }


def calcular_saldos_contas(propriedade) -> List[dict]:
    """Calcula o saldo atual de cada conta financeira considerando lançamentos quitados."""

    contas = ContaFinanceira.objects.filter(
        propriedade=propriedade,
        ativa=True,
    ).order_by("nome")

    resultados: List[dict] = []

    for conta in contas:
        receitas = (
            LancamentoFinanceiro.objects.filter(
                conta_destino=conta,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            ).aggregate(total=Sum("valor"))["total"]
            or Decimal("0")
        )
        despesas = (
            LancamentoFinanceiro.objects.filter(
                conta_origem=conta,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            ).aggregate(total=Sum("valor"))["total"]
            or Decimal("0")
        )

        saldo = conta.saldo_inicial + receitas - despesas

        resultados.append(
            {
                "conta": conta,
                "saldo": saldo,
                "receitas": receitas,
                "despesas": despesas,
            }
        )

    return resultados


def gerar_series_temporais(propriedade, periodo: PeriodoFinanceiro) -> dict:
    """Gera dados simplificados para gráficos (entradas x saídas por dia)."""

    dias = []
    entradas = []
    saidas = []

    atual = periodo.inicio
    while atual <= periodo.fim:
        diario = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia=atual,
        )
        total_receber = (
            diario.filter(tipo=CategoriaFinanceira.TIPO_RECEITA).aggregate(Sum("valor"))[
                "valor__sum"
            ]
            or Decimal("0")
        )
        total_pagar = (
            diario.filter(tipo=CategoriaFinanceira.TIPO_DESPESA).aggregate(Sum("valor"))[
                "valor__sum"
            ]
            or Decimal("0")
        )
        dias.append(atual.strftime("%d/%m"))
        entradas.append(float(total_receber))
        saidas.append(float(total_pagar))
        atual += timedelta(days=1)

    return {
        "labels": dias,
        "entradas": entradas,
        "saidas": saidas,
    }


def calcular_indicadores_financeiros(propriedade, periodo: PeriodoFinanceiro) -> dict:
    """Calcula indicadores financeiros avançados."""
    resumo = calcular_totais_lancamentos(propriedade, periodo)
    
    receitas = resumo["total_receitas"]
    despesas = resumo["total_despesas"]
    saldo_liquido = resumo["saldo_liquido"]
    
    # Margem de lucro
    margem_lucro = (
        (saldo_liquido / receitas * 100) if receitas > 0 else Decimal("0")
    )
    
    # Taxa de despesas sobre receitas
    taxa_despesas = (
        (despesas / receitas * 100) if receitas > 0 else Decimal("0")
    )
    
    # Média diária de receitas e despesas
    dias_periodo = (periodo.fim - periodo.inicio).days + 1
    media_diaria_receitas = receitas / dias_periodo if dias_periodo > 0 else Decimal("0")
    media_diaria_despesas = despesas / dias_periodo if dias_periodo > 0 else Decimal("0")
    
    return {
        "margem_lucro": margem_lucro,
        "taxa_despesas": taxa_despesas,
        "media_diaria_receitas": media_diaria_receitas,
        "media_diaria_despesas": media_diaria_despesas,
        "dias_periodo": dias_periodo,
    }


def comparar_com_periodo_anterior(propriedade, periodo: PeriodoFinanceiro) -> dict:
    """Compara o período atual com o período anterior equivalente."""
    # Calcular período anterior
    dias_periodo = (periodo.fim - periodo.inicio).days + 1
    periodo_anterior_inicio = periodo.inicio - timedelta(days=dias_periodo)
    periodo_anterior_fim = periodo.inicio - timedelta(days=1)
    
    periodo_anterior = PeriodoFinanceiro(
        inicio=periodo_anterior_inicio,
        fim=periodo_anterior_fim
    )
    
    resumo_atual = calcular_totais_lancamentos(propriedade, periodo)
    resumo_anterior = calcular_totais_lancamentos(propriedade, periodo_anterior)
    
    # Calcular variações percentuais
    def calcular_variacao(atual, anterior):
        if anterior == 0:
            return Decimal("0") if atual == 0 else Decimal("100")
        return ((atual - anterior) / anterior) * 100
    
    variacao_receitas = calcular_variacao(
        resumo_atual["total_receitas"],
        resumo_anterior["total_receitas"]
    )
    variacao_despesas = calcular_variacao(
        resumo_atual["total_despesas"],
        resumo_anterior["total_despesas"]
    )
    variacao_saldo = calcular_variacao(
        resumo_atual["saldo_liquido"],
        resumo_anterior["saldo_liquido"]
    )
    
    return {
        "periodo_anterior": periodo_anterior,
        "resumo_anterior": resumo_anterior,
        "variacao_receitas": variacao_receitas,
        "variacao_despesas": variacao_despesas,
        "variacao_saldo": variacao_saldo,
    }


def integrar_dados_pecuaria(propriedade, periodo: PeriodoFinanceiro) -> dict:
    """Integra dados de vendas de animais do módulo de pecuária."""
    try:
        # Tentar buscar através de MovimentacaoProjetada
        from .models import MovimentacaoProjetada
        
        vendas_animais = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            data_movimentacao__range=periodo.range_lookup,
        )
        
        total_vendas_animais = vendas_animais.aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal("0")
        
        quantidade_vendida = vendas_animais.aggregate(
            total=Sum('quantidade')
        )['total'] or 0
        
        return {
            "total_vendas_animais": total_vendas_animais,
            "quantidade_vendida": quantidade_vendida,
            "numero_vendas": vendas_animais.count(),
        }
    except (ImportError, AttributeError):
        # Se não encontrar, buscar através de lançamentos financeiros com categoria de venda de animais
        try:
            lancamentos_vendas = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                data_competencia__range=periodo.range_lookup,
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao__icontains='venda',
            )
            
            total_vendas_animais = lancamentos_vendas.aggregate(
                total=Sum('valor')
            )['total'] or Decimal("0")
            
            return {
                "total_vendas_animais": total_vendas_animais,
                "quantidade_vendida": 0,
                "numero_vendas": lancamentos_vendas.count(),
            }
        except Exception:
            return {
                "total_vendas_animais": Decimal("0"),
                "quantidade_vendida": 0,
                "numero_vendas": 0,
            }


def integrar_dados_compras(propriedade, periodo: PeriodoFinanceiro) -> dict:
    """Integra dados de compras do módulo de compras."""
    try:
        from .models_compras_financeiro import OrdemCompra, NotaFiscal
        
        # Buscar ordens de compra do período
        ordens_compra = OrdemCompra.objects.filter(
            propriedade=propriedade,
            data_emissao__range=periodo.range_lookup,
        )
        
        total_compras = ordens_compra.aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal("0")
        
        # Buscar notas fiscais do período
        notas_fiscais = NotaFiscal.objects.filter(
            propriedade=propriedade,
            data_emissao__range=periodo.range_lookup,
            tipo='ENTRADA',
        )
        
        total_notas = notas_fiscais.aggregate(
            total=Sum('valor_total')
        )['total'] or Decimal("0")
        
        return {
            "total_compras": total_compras,
            "total_notas_fiscais": total_notas,
            "numero_ordens": ordens_compra.count(),
            "numero_notas": notas_fiscais.count(),
        }
    except (ImportError, AttributeError):
        return {
            "total_compras": Decimal("0"),
            "total_notas_fiscais": Decimal("0"),
            "numero_ordens": 0,
            "numero_notas": 0,
        }


def gerar_insights_financeiros(propriedade, periodo: PeriodoFinanceiro) -> List[dict]:
    """Gera insights e alertas financeiros baseados nos dados."""
    insights = []
    resumo = calcular_totais_lancamentos(propriedade, periodo)
    comparacao = comparar_com_periodo_anterior(propriedade, periodo)
    pendencias = listar_pendencias(propriedade)
    
    # Insight 1: Variação de receitas
    if abs(comparacao["variacao_receitas"]) > 20:
        tipo = "success" if comparacao["variacao_receitas"] > 0 else "warning"
        insights.append({
            "tipo": tipo,
            "icone": "bi-arrow-up-circle" if comparacao["variacao_receitas"] > 0 else "bi-arrow-down-circle",
            "titulo": "Variação significativa de receitas",
            "descricao": f"Receitas {'aumentaram' if comparacao['variacao_receitas'] > 0 else 'diminuíram'} {abs(comparacao['variacao_receitas']):.1f}% em relação ao período anterior.",
        })
    
    # Insight 2: Pendências atrasadas
    if len(pendencias["atrasados"]) > 0:
        total_atrasado = sum(
            lanc.valor for lanc in pendencias["atrasados"]
        )
        insights.append({
            "tipo": "danger",
            "icone": "bi-exclamation-triangle-fill",
            "titulo": "Lançamentos atrasados",
            "descricao": f"{len(pendencias['atrasados'])} lançamento(s) atrasado(s) totalizando {total_atrasado:.2f}.",
        })
    
    # Insight 3: Margem de lucro
    indicadores = calcular_indicadores_financeiros(propriedade, periodo)
    if indicadores["margem_lucro"] < 0:
        insights.append({
            "tipo": "danger",
            "icone": "bi-x-circle-fill",
            "titulo": "Margem negativa",
            "descricao": f"O período apresenta margem de lucro negativa de {abs(indicadores['margem_lucro']):.1f}%.",
        })
    elif indicadores["margem_lucro"] < 10:
        insights.append({
            "tipo": "warning",
            "icone": "bi-exclamation-circle",
            "titulo": "Margem baixa",
            "descricao": f"Margem de lucro de apenas {indicadores['margem_lucro']:.1f}%. Considere revisar custos.",
        })
    
    # Insight 4: Saldo negativo
    if resumo["saldo_liquido"] < 0:
        insights.append({
            "tipo": "danger",
            "icone": "bi-cash-stack",
            "titulo": "Saldo líquido negativo",
            "descricao": f"O saldo líquido do período é negativo: {resumo['saldo_liquido']:.2f}.",
        })
    
    return insights


def analisar_tendencias_categoria(propriedade, periodo: PeriodoFinanceiro, limite: int = 5) -> dict:
    """Analisa as categorias com maiores receitas e despesas."""
    lancamentos = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        data_competencia__range=periodo.range_lookup,
        status=LancamentoFinanceiro.STATUS_QUITADO,
    )
    
    # Top categorias de receitas
    top_receitas_raw = (
        lancamentos
        .filter(tipo=CategoriaFinanceira.TIPO_RECEITA)
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')[:limite]
    )
    
    # Converter para lista e calcular percentuais
    top_receitas = []
    total_receitas = sum(item['total'] or Decimal('0') for item in top_receitas_raw)
    for item in top_receitas_raw:
        total = item['total'] or Decimal('0')
        percentual = (total / total_receitas * 100) if total_receitas > 0 else Decimal('0')
        top_receitas.append({
            'categoria__nome': item['categoria__nome'],
            'total': total,
            'percentual': float(percentual),
        })
    
    # Top categorias de despesas
    top_despesas_raw = (
        lancamentos
        .filter(tipo=CategoriaFinanceira.TIPO_DESPESA)
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')[:limite]
    )
    
    # Converter para lista e calcular percentuais
    top_despesas = []
    total_despesas = sum(item['total'] or Decimal('0') for item in top_despesas_raw)
    for item in top_despesas_raw:
        total = item['total'] or Decimal('0')
        percentual = (total / total_despesas * 100) if total_despesas > 0 else Decimal('0')
        top_despesas.append({
            'categoria__nome': item['categoria__nome'],
            'total': total,
            'percentual': float(percentual),
        })
    
    return {
        "top_receitas": top_receitas,
        "top_despesas": top_despesas,
    }





