from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from datetime import date

from .models import Propriedade, CustoFixo, CustoVariavel, FluxoCaixa, InventarioRebanho
from .forms_custos import CustoFixoForm, CustoVariavelForm


@login_required
def custos_dashboard(request, propriedade_id):
    """Dashboard de custos da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar custos existentes
    custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
    custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
    
    # Calcular totais
    custo_fixo_total = sum(custo.valor_mensal for custo in custos_fixos)
    custo_fixo_anual = custo_fixo_total * 12
    
    # Buscar inventário para calcular custos variáveis
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_animais = sum(item.quantidade for item in inventario)
    custo_variavel_por_cabeca = sum(custo.valor_por_cabeca for custo in custos_variaveis)
    custo_variavel_total = custo_variavel_por_cabeca * total_animais
    
    # Calcular receita total (baseada no inventário)
    receita_total = Decimal('0.00')
    for item in inventario:
        if item.valor_por_cabeca:
            receita_total += item.valor_por_cabeca * item.quantidade
    
    # Calcular lucro bruto
    custo_total = custo_fixo_total + custo_variavel_total
    lucro_bruto = receita_total - custo_total
    
    # Calcular margem de lucro
    margem_lucro = Decimal('0.00')
    if receita_total > 0:
        margem_lucro = (lucro_bruto / receita_total) * 100
    
    context = {
        'propriedade': propriedade,
        'custos_fixos_count': custos_fixos.count(),
        'custos_variaveis_count': custos_variaveis.count(),
        'custo_fixo_total': custo_fixo_total,
        'custo_fixo_anual': custo_fixo_anual,
        'custo_variavel_por_cabeca': custo_variavel_por_cabeca,
        'total_animais': total_animais,
        'receita_total': receita_total,
        'custo_total': custo_total,
        'lucro_bruto': lucro_bruto,
        'margem_lucro': margem_lucro,
    }
    
    return render(request, 'gestao_rural/custos_dashboard.html', context)


@login_required
def custos_fixos_lista(request, propriedade_id):
    """Lista de custos fixos"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    custos_fixos = CustoFixo.objects.filter(propriedade=propriedade).order_by('tipo_custo', 'nome_custo')
    
    # Calcular totais
    custo_mensal_total = sum(custo.valor_mensal for custo in custos_fixos)
    custo_anual_total = custo_mensal_total * 12
    
    context = {
        'propriedade': propriedade,
        'custos_fixos': custos_fixos,
        'custo_mensal_total': custo_mensal_total,
        'custo_anual_total': custo_anual_total,
    }
    
    return render(request, 'gestao_rural/custos_fixos_lista.html', context)


@login_required
def custos_fixos_novo(request, propriedade_id):
    """Criar novo custo fixo"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = CustoFixoForm(request.POST)
        if form.is_valid():
            custo = form.save(commit=False)
            custo.propriedade = propriedade
            custo.save()
            messages.success(request, 'Custo fixo cadastrado com sucesso!')
            return redirect('custos_fixos_lista', propriedade_id=propriedade.id)
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados.')
    else:
        form = CustoFixoForm()
    
    # Dados para os meses
    meses_choices = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'meses_choices': meses_choices,
    }
    
    return render(request, 'gestao_rural/custos_fixos_novo.html', context)


@login_required
def custos_variaveis_lista(request, propriedade_id):
    """Lista de custos variáveis"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade).order_by('tipo_custo', 'nome_custo')
    
    # Buscar inventário para calcular totais
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_animais = sum(item.quantidade for item in inventario)
    
    # Calcular totais
    custo_por_cabeca_total = sum(custo.valor_por_cabeca for custo in custos_variaveis)
    custo_total_projecao = custo_por_cabeca_total * total_animais
    
    # Adicionar impacto total para cada custo
    for custo in custos_variaveis:
        custo.impacto_total = custo.valor_por_cabeca * total_animais
    
    context = {
        'propriedade': propriedade,
        'custos_variaveis': custos_variaveis,
        'total_animais': total_animais,
        'custo_por_cabeca_total': custo_por_cabeca_total,
        'custo_total_projecao': custo_total_projecao,
    }
    
    return render(request, 'gestao_rural/custos_variaveis_lista.html', context)


@login_required
def custos_variaveis_novo(request, propriedade_id):
    """Criar novo custo variável"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = CustoVariavelForm(request.POST)
        if form.is_valid():
            custo = form.save(commit=False)
            custo.propriedade = propriedade
            custo.save()
            messages.success(request, 'Custo variável cadastrado com sucesso!')
            return redirect('custos_variaveis_lista', propriedade_id=propriedade.id)
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados.')
    else:
        form = CustoVariavelForm()
    
    # Dados para os meses
    meses_choices = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'meses_choices': meses_choices,
    }
    
    return render(request, 'gestao_rural/custos_variaveis_novo.html', context)


@login_required
def calcular_fluxo_caixa(request, propriedade_id):
    """Calcular fluxo de caixa da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar custos
    custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
    custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
    
    # Buscar inventário
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_cabecas = sum(item.quantidade for item in inventario)
    
    # Calcular receita total (baseada no inventário)
    receita_total = Decimal('0.00')
    for item in inventario:
        if item.valor_por_cabeca:
            receita_total += item.valor_por_cabeca * item.quantidade
    
    # Calcular custos fixos totais
    custo_fixo_total = sum(custo.valor_mensal for custo in custos_fixos)
    
    # Calcular custos variáveis totais
    custo_variavel_total = sum(custo.valor_por_cabeca * total_cabecas for custo in custos_variaveis)
    
    # Calcular lucro bruto
    lucro_bruto = receita_total - custo_fixo_total - custo_variavel_total
    
    # Calcular margem de lucro
    margem_lucro = Decimal('0.00')
    if receita_total > 0:
        margem_lucro = (lucro_bruto / receita_total) * 100
    
    # Salvar ou atualizar fluxo de caixa
    fluxo_caixa, created = FluxoCaixa.objects.update_or_create(
        propriedade=propriedade,
        data_referencia=date.today(),
        defaults={
            'receita_total': receita_total,
            'custo_fixo_total': custo_fixo_total,
            'custo_variavel_total': custo_variavel_total,
            'lucro_bruto': lucro_bruto,
            'margem_lucro': margem_lucro
        }
    )
    
    if created:
        messages.success(request, 'Fluxo de caixa calculado com sucesso!')
    else:
        messages.success(request, 'Fluxo de caixa atualizado com sucesso!')
    
    return redirect('custos_dashboard', propriedade_id=propriedade.id)
