from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms_pesagem import AnimalPesagemForm
from .models import (
    AnimalPesagem,
    MovimentacaoIndividual,
    Propriedade,
)

PESO_ALVO_PADRAO = Decimal('520')  # kg


def _calcular_metricas(ultima_pesagem, pesagem_anterior, peso_alvo, hoje):
    peso_atual = ultima_pesagem.peso_kg
    peso_anterior = pesagem_anterior.peso_kg if pesagem_anterior else None

    ganho_peso = None
    ganho_diario = None
    intervalo_dias = None

    if peso_atual is not None and peso_anterior is not None:
        ganho_peso = peso_atual - peso_anterior
        intervalo_dias = (ultima_pesagem.data_pesagem - pesagem_anterior.data_pesagem).days
        if intervalo_dias <= 0:
            intervalo_dias = 1
        try:
            ganho_diario = ganho_peso / Decimal(intervalo_dias)
        except (InvalidOperation, ZeroDivisionError):
            ganho_diario = None

    dias_desde = (hoje - ultima_pesagem.data_pesagem).days
    if dias_desde < 0:
        dias_desde = 0

    dias_para_abate = None
    if (
        peso_alvo
        and peso_atual is not None
        and ganho_diario is not None
        and ganho_diario > 0
    ):
        restante = peso_alvo - peso_atual
        if restante <= 0:
            dias_para_abate = 0
        else:
            try:
                dias_para_abate = int(
                    (restante / ganho_diario).to_integral_value(rounding=ROUND_CEILING)
                )
            except (InvalidOperation, ZeroDivisionError):
                dias_para_abate = None

    return {
        'peso_atual': peso_atual,
        'peso_anterior': peso_anterior,
        'ganho_peso': ganho_peso,
        'ganho_diario': ganho_diario,
        'intervalo_dias': intervalo_dias,
        'dias_desde': dias_desde,
        'dias_para_abate': dias_para_abate,
    }


@login_required
def pesagem_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    hoje = timezone.localdate()
    peso_alvo = PESO_ALVO_PADRAO

    pesagens_qs = (
        AnimalPesagem.objects.filter(animal__propriedade=propriedade)
        .select_related('animal', 'animal__lote_atual', 'responsavel')
        .order_by('animal_id', '-data_pesagem', '-id')
    )

    registros_animais = {}
    lotes_resumo = defaultdict(lambda: {'total': 0, 'peso_total': Decimal('0')})

    for pesagem in pesagens_qs:
        info = registros_animais.get(pesagem.animal_id)
        if not info:
            registros_animais[pesagem.animal_id] = {'ultima': pesagem, 'anterior': None}
        elif not info['anterior']:
            info['anterior'] = pesagem

    registros = []
    ganho_diario_total = Decimal('0')
    ganho_diario_count = 0
    peso_total = Decimal('0')

    for info in registros_animais.values():
        ultima = info['ultima']
        anterior = info['anterior']
        metricas = _calcular_metricas(ultima, anterior, peso_alvo, hoje)

        if metricas['ganho_diario'] is not None:
            ganho_diario_total += metricas['ganho_diario']
            ganho_diario_count += 1

        if metricas['peso_atual'] is not None:
            peso_total += metricas['peso_atual']

        animal = ultima.animal
        lote_atual = getattr(animal.lote_atual, 'nome', 'Sem lote')

        if metricas['peso_atual'] is not None:
            lotes_resumo[lote_atual]['total'] += 1
            lotes_resumo[lote_atual]['peso_total'] += metricas['peso_atual']

        registros.append(
            {
                'animal': animal,
                'ultima_pesagem': ultima,
                'pesagem_anterior': anterior,
                'metricas': metricas,
                'tipo_racao': ultima.tipo_racao,
                'consumo_racao_kg_dia': ultima.consumo_racao_kg_dia,
                'lote_nome': lote_atual,
            }
        )

    registros.sort(key=lambda item: item['ultima_pesagem'].data_pesagem, reverse=True)

    lotes_listagem = []
    for nome, dados in lotes_resumo.items():
        total = dados['total']
        peso_medio = None
        if total > 0:
            try:
                peso_medio = dados['peso_total'] / Decimal(total)
            except (InvalidOperation, ZeroDivisionError):
                peso_medio = None
        lotes_listagem.append(
            {
                'nome': nome,
                'total': total,
                'peso_medio': peso_medio,
            }
        )
    lotes_listagem.sort(key=lambda item: item['nome'] or '')

    total_animais = len(registros_animais)
    total_pesagens = pesagens_qs.count()
    pesagens_30_dias = pesagens_qs.filter(
        data_pesagem__gte=hoje - timedelta(days=30)
    ).count()

    ganho_diario_medio = (
        (ganho_diario_total / Decimal(ganho_diario_count))
        if ganho_diario_count
        else None
    )

    peso_medio_geral = (
        (peso_total / Decimal(total_animais))
        if total_animais
        else None
    )

    context = {
        'propriedade': propriedade,
        'registros': registros,
        'lotes_resumo': lotes_listagem,
        'total_animais': total_animais,
        'total_pesagens': total_pesagens,
        'pesagens_30_dias': pesagens_30_dias,
        'ganho_diario_medio': ganho_diario_medio,
        'peso_medio_geral': peso_medio_geral,
        'peso_alvo': peso_alvo,
    }

    return render(request, 'gestao_rural/pesagem_dashboard.html', context)


@login_required
@transaction.atomic
def pesagem_nova(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)

    if request.method == 'POST':
        form = AnimalPesagemForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            pesagem = form.save(commit=False)
            pesagem.responsavel = request.user
            pesagem.origem_registro = 'MODULO_PESAGEM'
            pesagem.save()

            animal = pesagem.animal
            ultima_pesagem = (
                AnimalPesagem.objects.filter(animal=animal)
                .exclude(id=pesagem.id)
                .order_by('-data_pesagem', '-id')
                .first()
            )

            if not ultima_pesagem or pesagem.data_pesagem >= ultima_pesagem.data_pesagem:
                animal.peso_atual_kg = pesagem.peso_kg
                animal.save(update_fields=['peso_atual_kg', 'data_atualizacao'])

            MovimentacaoIndividual.objects.create(
                animal=animal,
                tipo_movimentacao='PESAGEM',
                data_movimentacao=pesagem.data_pesagem,
                peso_kg=pesagem.peso_kg,
                observacoes=pesagem.observacoes or 'Pesagem registrada no módulo de pesagem',
                responsavel=request.user,
            )

            messages.success(request, 'Pesagem registrada com sucesso.')
            return redirect('pesagem_dashboard', propriedade_id=propriedade_id)
    else:
        form = AnimalPesagemForm(propriedade=propriedade)

    contexto = {
        'propriedade': propriedade,
        'form': form,
    }
    return render(request, 'gestao_rural/pesagem_nova.html', contexto)













