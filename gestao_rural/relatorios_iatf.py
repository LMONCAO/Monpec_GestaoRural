# -*- coding: utf-8 -*-
"""
Serviços utilitários para consolidação de dados de IATF.

Este módulo centraliza todos os cálculos de indicadores e agrupamentos
utilizados nas exportações (Excel/PDF) e facilita futura reutilização
em gráficos dentro do próprio dashboard.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.db.models import (
    Avg,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

try:
    from .models_iatf_completo import IATFIndividual  # type: ignore
except Exception:  # noqa: BLE001
    IATFIndividual = None  # type: ignore

RESULTADO_CHOICES_FALLBACK: Tuple[Tuple[str, str], ...] = (
    ('PREMIDA', 'Prenhez Confirmada'),
    ('VAZIA', 'Vazia'),
    ('PENDENTE', 'Pendente Diagnóstico'),
    ('ABORTO', 'Aborto'),
    ('REPETICAO', 'Repetição de Cio'),
)


class IATFModuloIndisponivel(RuntimeError):
    """Exceção usada quando o módulo IATF completo não está disponível."""


def _parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    value = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _to_decimal(value: Optional[Decimal]) -> Decimal:
    if value is None:
        return Decimal('0')
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (ValueError, ArithmeticError):
        return Decimal('0')


def _taxa(parte: int, total: int) -> Decimal:
    if not total:
        return Decimal('0')
    return (Decimal(parte) / Decimal(total)) * Decimal('100')


def _media(valor: Decimal, quantidade: int) -> Decimal:
    if not quantidade:
        return Decimal('0')
    return valor / Decimal(quantidade)


def _timedelta_para_dias(valor: Optional[object]) -> Optional[Decimal]:
    if valor is None:
        return None
    total_segundos = getattr(valor, 'total_seconds', None)
    if callable(total_segundos):
        return Decimal(str(total_segundos())) / Decimal('86400')
    # Fallback para objetos que já representem dias
    try:
        return Decimal(str(valor))
    except (ValueError, ArithmeticError):
        return None


def _resolver_rotulo_usuario(item: Dict[str, Any]) -> str:
    primeiro = (item.get('inseminador__first_name') or '').strip()
    ultimo = (item.get('inseminador__last_name') or '').strip()
    if primeiro or ultimo:
        return f"{primeiro} {ultimo}".strip()
    username = (item.get('inseminador__username') or '').strip()
    if username:
        return username
    return 'Não informado'


def _resolver_rotulo_touro(item: Dict[str, Any]) -> str:
    nome = (item.get('touro_semen__nome_touro') or '').strip()
    numero = (item.get('touro_semen__numero_touro') or '').strip()
    if nome and numero:
        return f"{numero} - {nome}"
    if nome:
        return nome
    if numero:
        return numero
    return 'Não informado'


def _resolver_rotulo_generico(item: Dict[str, Any], campo: str, padrao: str = 'Não informado') -> str:
    valor = item.get(campo)
    if valor is None:
        return padrao
    valor = str(valor).strip()
    return valor or padrao


def _agrupar_por(
    qs,
    campos: Iterable[str],
    rotulo_callback,
) -> List[Dict[str, Any]]:
    """
    Agrupa IATFs por campos específicos e calcula estatísticas agregadas.
    Usa nomes diferentes para as agregações para evitar conflitos com campos do modelo.
    """
    agrupado = (
        qs.values(*campos)
        .annotate(
            total=Count('id'),
            prenhezes=Count('id', filter=Q(resultado='PREMIDA')),
            vazias=Count('id', filter=Q(resultado='VAZIA')),
            abortos=Count('id', filter=Q(resultado='ABORTO')),
            repeticoes=Count('id', filter=Q(resultado='REPETICAO')),
            pendentes=Count('id', filter=Q(resultado='PENDENTE')),
            media_dias=Avg('intervalo_diagnostico'),
            # Usar F() para referenciar explicitamente o campo do modelo e evitar conflitos
            # Renomear as agregações para evitar conflito com possíveis anotações anteriores
            custo_total_agg=Coalesce(Sum(F('custo_total')), Value(Decimal('0'))),
            custo_prenhez_agg=Coalesce(Sum(F('custo_total'), filter=Q(resultado='PREMIDA')), Value(Decimal('0'))),
        )
        .order_by('-prenhezes', '-total', *campos)
    )

    resultados: List[Dict[str, Any]] = []
    for item in agrupado:
        total = item['total']
        prenhezes = item['prenhezes']
        # Usar os nomes das agregações que criamos
        custo_total = _to_decimal(item.get('custo_total_agg'))
        custo_prenhez = _to_decimal(item.get('custo_prenhez_agg'))
        resultados.append(
            {
                'rotulo': rotulo_callback(item),
                'total': total,
                'prenhezes': prenhezes,
                'vazias': item['vazias'],
                'abortos': item['abortos'],
                'repeticoes': item['repeticoes'],
                'pendentes': item['pendentes'],
                'taxa_prenhez': _taxa(prenhezes, total),
                'media_dias_diagnostico': _timedelta_para_dias(item.get('media_dias')),
                'custo_total': custo_total,
                'custo_medio_prenhez': _media(custo_prenhez, prenhezes) if prenhezes else Decimal('0'),
            }
        )
    return resultados


def coletar_dados_iatf(propriedade, filtros: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retorna uma estrutura consolidada com dados e indicadores da IATF.
    """
    if IATFIndividual is None:
        raise IATFModuloIndisponivel(
            'O módulo de IATF completo não está disponível. Execute as migrations correspondentes.'
        )

    filtros = filtros or {}
    data_inicio = _parse_date(filtros.get('data_inicio'))
    data_final = _parse_date(filtros.get('data_final'))
    diagnostico_ate = _parse_date(filtros.get('diagnostico_ate')) or date.today()
    resultado = (filtros.get('resultado') or '').strip().upper()
    incluir_sem_diagnostico = bool(filtros.get('incluir_sem_diagnostico'))

    lote_id = filtros.get('lote_id')
    try:
        lote_id = int(lote_id) if lote_id not in (None, '', 'null') else None
    except (TypeError, ValueError):
        lote_id = None

    qs = IATFIndividual.objects.filter(propriedade=propriedade)

    if not incluir_sem_diagnostico:
        qs = qs.filter(data_diagnostico__isnull=False)

    if diagnostico_ate and not incluir_sem_diagnostico:
        qs = qs.filter(data_diagnostico__lte=diagnostico_ate)

    if data_inicio:
        qs = qs.filter(
            Q(data_iatf__gte=data_inicio) | Q(data_iatf_realizada__gte=data_inicio)
        )

    if data_final:
        qs = qs.filter(
            Q(data_iatf__lte=data_final) | Q(data_iatf_realizada__lte=data_final)
        )

    if lote_id:
        qs = qs.filter(lote_iatf_id=lote_id)

    if resultado and resultado != 'TODOS':
        qs = qs.filter(resultado=resultado)

    qs = qs.select_related(
        'animal_individual',
        'animal_individual__categoria',
        'animal_individual__lote_atual',
        'touro_semen',
        'inseminador',
        'lote_iatf',
        'lote_iatf__protocolo',
        'protocolo',
    ).annotate(
        intervalo_diagnostico=ExpressionWrapper(
            F('data_diagnostico') - F('data_iatf'),
            output_field=DurationField(),
        )
    )

    total = qs.count()
    prenhezes = qs.filter(resultado='PREMIDA').count()
    vazias = qs.filter(resultado='VAZIA').count()
    pendentes = qs.filter(resultado='PENDENTE').count()
    abortos = qs.filter(resultado='ABORTO').count()
    repeticoes = qs.filter(resultado='REPETICAO').count()

    custo_total = _to_decimal(
        qs.aggregate(total=Coalesce(Sum('custo_total'), Value(Decimal('0'))))['total']
    )
    custo_prenhezes = _to_decimal(
        qs.filter(resultado='PREMIDA').aggregate(
            total=Coalesce(Sum('custo_total'), Value(Decimal('0')))
        )['total']
    )

    media_dias = qs.aggregate(media=Avg('intervalo_diagnostico'))['media']

    status_counts = list(
        qs.values('resultado').annotate(total=Count('id')).order_by('-total')
    )
    resultado_map = dict(
        getattr(IATFIndividual, 'RESULTADO_CHOICES', RESULTADO_CHOICES_FALLBACK)
    )
    for item in status_counts:
        item['rotulo'] = resultado_map.get(item['resultado'], item['resultado'])
        item['taxa'] = _taxa(item['total'], total)

    por_touro = _agrupar_por(qs, ['touro_semen__id', 'touro_semen__nome_touro', 'touro_semen__numero_touro'], _resolver_rotulo_touro)
    por_inseminador = _agrupar_por(
        qs,
        ['inseminador__id', 'inseminador__first_name', 'inseminador__last_name', 'inseminador__username'],
        _resolver_rotulo_usuario,
    )
    por_invernada = _agrupar_por(
        qs,
        ['animal_individual__lote_atual__nome'],
        lambda item: _resolver_rotulo_generico(item, 'animal_individual__lote_atual__nome', 'Sem lote / invernada'),
    )
    por_lote = _agrupar_por(
        qs,
        ['lote_iatf__id', 'lote_iatf__nome_lote'],
        lambda item: _resolver_rotulo_generico(item, 'lote_iatf__nome_lote', 'Sem lote IATF'),
    )
    por_protocolo = _agrupar_por(
        qs,
        ['protocolo__id', 'protocolo__nome'],
        lambda item: _resolver_rotulo_generico(item, 'protocolo__nome', 'Protocolo não informado'),
    )

    diagnosticos_por_data = list(
        qs.filter(data_diagnostico__isnull=False)
        .values('data_diagnostico')
        .annotate(
            total=Count('id'),
            prenhezes=Count('id', filter=Q(resultado='PREMIDA')),
            vazias=Count('id', filter=Q(resultado='VAZIA')),
        )
        .order_by('data_diagnostico')
    )
    for item in diagnosticos_por_data:
        item['taxa_prenhez'] = _taxa(item['prenhezes'], item['total'])

    detalhes = []
    for registro in qs.order_by('data_diagnostico', 'animal_individual__numero_brinco'):
        animal = registro.animal_individual
        touro_nome = ''
        if getattr(registro, 'touro_semen', None):
            numero = (registro.touro_semen.numero_touro or '').strip()
            nome = (registro.touro_semen.nome_touro or '').strip()
            if numero and nome:
                touro_nome = f"{numero} - {nome}"
            else:
                touro_nome = nome or numero

        inseminador_nome = ''
        if getattr(registro, 'inseminador', None):
            nome_completo = (registro.inseminador.get_full_name() or '').strip()
            inseminador_nome = nome_completo or getattr(registro.inseminador, 'username', '')

        detalhes.append(
            {
                'animal': getattr(animal, 'numero_brinco', ''),
                'categoria': getattr(animal.categoria, 'nome', '') if getattr(animal, 'categoria', None) else '',
                'invernada': getattr(animal.lote_atual, 'nome', '') if getattr(animal, 'lote_atual', None) else '',
                'protocolo': getattr(registro.protocolo, 'nome', ''),
                'lote_iatf': getattr(registro.lote_iatf, 'nome_lote', ''),
                'touro': touro_nome,
                'inseminador': inseminador_nome,
                'resultado': registro.get_resultado_display(),
                'status': registro.get_status_display(),
                'data_iatf': registro.data_iatf,
                'data_diagnostico': registro.data_diagnostico,
                'dias_para_diagnostico': registro.dias_ate_diagnostico,
                'custo_total': registro.custo_total,
                'observacoes': registro.observacoes or '',
            }
        )

    filtros_aplicados = {
        'data_inicio': data_inicio,
        'data_final': data_final,
        'diagnostico_ate': diagnostico_ate if not incluir_sem_diagnostico else None,
        'resultado': resultado if resultado else None,
        'lote_id': lote_id,
        'incluir_sem_diagnostico': incluir_sem_diagnostico,
    }

    return {
        'resumo': {
            'total_animais': total,
            'total_prenhezes': prenhezes,
            'total_vazias': vazias,
            'total_pendentes': pendentes,
            'total_abortos': abortos,
            'total_repeticoes': repeticoes,
            'taxa_prenhez': _taxa(prenhezes, total),
            'media_dias_diagnostico': _timedelta_para_dias(media_dias),
            'custo_total': custo_total,
            'custo_medio_animal': _media(custo_total, total) if total else Decimal('0'),
            'custo_medio_prenhez': _media(custo_prenhezes, prenhezes) if prenhezes else Decimal('0'),
        },
        'status_counts': status_counts,
        'por_touro': por_touro,
        'por_inseminador': por_inseminador,
        'por_invernada': por_invernada,
        'por_lote': por_lote,
        'por_protocolo': por_protocolo,
        'diagnosticos_por_data': diagnosticos_por_data,
        'detalhes': detalhes,
        'filtros_aplicados': filtros_aplicados,
        'resultado_choices': list(
            getattr(IATFIndividual, 'RESULTADO_CHOICES', RESULTADO_CHOICES_FALLBACK)
        ),
    }


