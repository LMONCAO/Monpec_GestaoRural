# -*- coding: utf-8 -*-
"""
Views Consolidadas - MÓDULO NUTRIÇÃO E ALIMENTAÇÃO
Agrupa:
- Suplementação
- Cochos (consumo)
- Distribuição no Pasto
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, F
from decimal import Decimal
from datetime import date, datetime

from .models import Propriedade
from .decorators import obter_propriedade_com_permissao
from .models_operacional import (
    EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao
)
from .models_controles_operacionais import (
    TipoDistribuicao, DistribuicaoPasto, Cocho, ControleCocho, Pastagem
)
from .forms_completos import (
    CompraSuplementacaoForm,
    DistribuicaoSuplementacaoForm,
)


@login_required
def nutricao_dashboard(request, propriedade_id):
    """Dashboard consolidado de Nutrição"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # ========== SUPLEMENTAÇÃO ==========
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
    estoques_baixo = estoques.filter(
        quantidade_atual__lte=F('quantidade_minima')
    )
    valor_total_estoque = sum(e.valor_total_estoque for e in estoques)
    
    # Distribuições do mês
    mes_atual = date.today().replace(day=1)
    distribuicoes_mes = DistribuicaoSuplementacao.objects.filter(
        estoque__propriedade=propriedade,
        data__gte=mes_atual
    )
    total_distribuido_mes = sum(d.quantidade for d in distribuicoes_mes)
    valor_distribuido_mes = sum(d.valor_total for d in distribuicoes_mes)
    
    # ========== COCHOS ==========
    cochos = Cocho.objects.filter(propriedade=propriedade)
    cochos_ativos = cochos.filter(status='ATIVO')
    
    # Controles recentes
    controles_recentes = ControleCocho.objects.filter(
        cocho__propriedade=propriedade
    ).select_related('cocho').order_by('-data')[:10]
    
    # ========== DISTRIBUIÇÃO NO PASTO ==========
    distribuicoes_pasto = DistribuicaoPasto.objects.filter(
        propriedade=propriedade
    ).select_related('pastagem', 'tipo_distribuicao').order_by('-data_distribuicao')[:10]
    
    context = {
        'propriedade': propriedade,
        # Suplementação
        'estoques': estoques,
        'estoques_baixo': estoques_baixo,
        'valor_total_estoque': valor_total_estoque,
        'total_distribuido_mes': total_distribuido_mes,
        'valor_distribuido_mes': valor_distribuido_mes,
        # Cochos
        'cochos': cochos_ativos,
        'controles_recentes': controles_recentes,
        # Distribuição
        'distribuicoes_pasto': distribuicoes_pasto,
    }
    
    return render(request, 'gestao_rural/nutricao_dashboard.html', context)


# ========== SUPLEMENTAÇÃO ==========

@login_required
def estoque_suplementacao_lista(request, propriedade_id):
    """Lista de estoques de suplementação"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade).order_by('tipo_suplemento')
    
    context = {
        'propriedade': propriedade,
        'estoques': estoques,
    }
    
    return render(request, 'gestao_rural/estoque_suplementacao_lista.html', context)


@login_required
def compra_suplementacao_nova(request, propriedade_id):
    """Registrar compra de suplementação"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)

    form = CompraSuplementacaoForm(request.POST or None)
    form.fields['estoque'].queryset = estoques
    form.fields['estoque'].widget.attrs.update({'class': 'form-select'})
    form.fields['fornecedor'].widget.attrs.setdefault('class', 'form-control')
    form.fields['numero_nota_fiscal'].widget.attrs.setdefault('class', 'form-control')
    form.fields['quantidade'].widget.attrs.update({'class': 'form-control', 'step': '0.01', 'min': '0'})
    form.fields['preco_unitario'].widget.attrs.update({'class': 'form-control', 'step': '0.01', 'min': '0'})

    if request.method == 'POST':
        if form.is_valid():
            compra = form.save(commit=False)
            if compra.estoque.propriedade_id != propriedade.id:
                form.add_error('estoque', 'Selecione um estoque pertencente à propriedade atual.')
            else:
                compra.responsavel = request.user
                try:
                    with transaction.atomic():
                        compra.save()
                except Exception as exc:
                    messages.error(request, f'Erro ao registrar compra: {exc}')
                else:
                    messages.success(request, 'Compra registrada com sucesso!')
                    return redirect('nutricao_dashboard', propriedade_id=propriedade.id)

    return render(request, 'gestao_rural/compra_suplementacao_form.html', {
        'propriedade': propriedade,
        'form': form,
    })


@login_required
def distribuicao_suplementacao_nova(request, propriedade_id):
    """Registrar distribuição de suplementação"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
    pastagens = Pastagem.objects.filter(propriedade=propriedade)

    form = DistribuicaoSuplementacaoForm(request.POST or None)
    form.fields['estoque'].queryset = estoques
    form.fields['estoque'].widget.attrs.update({'class': 'form-select'})
    form.fields['data'].widget.attrs.setdefault('class', 'form-control')
    form.fields['pastagem'].widget.attrs.update({
        'class': 'form-control',
        'list': 'pastagens-disponiveis',
        'placeholder': 'Informe a pastagem/piquete'
    })
    form.fields['quantidade'].widget.attrs.update({'class': 'form-control', 'step': '0.01', 'min': '0'})
    form.fields['numero_animais'].widget.attrs.update({'class': 'form-control', 'min': '0'})
    form.fields['observacoes'].widget.attrs.setdefault('class', 'form-control')

    if request.method == 'POST':
        if form.is_valid():
            distribuicao = form.save(commit=False)
            if distribuicao.estoque.propriedade_id != propriedade.id:
                form.add_error('estoque', 'Selecione um estoque pertencente à propriedade atual.')
            elif distribuicao.quantidade > distribuicao.estoque.quantidade_atual:
                form.add_error('quantidade', f'Estoque insuficiente! Disponível: {distribuicao.estoque.quantidade_atual}')
            else:
                distribuicao.valor_unitario = distribuicao.estoque.valor_unitario_medio
                distribuicao.responsavel = request.user
                try:
                    with transaction.atomic():
                        distribuicao.save()
                except Exception as exc:
                    messages.error(request, f'Erro ao registrar distribuição: {exc}')
                else:
                    messages.success(request, 'Distribuição registrada com sucesso!')
                    return redirect('nutricao_dashboard', propriedade_id=propriedade.id)

    return render(request, 'gestao_rural/distribuicao_suplementacao_form.html', {
        'propriedade': propriedade,
        'form': form,
        'pastagens': pastagens,
    })


# ========== COCHOS ==========

@login_required
def cochos_lista(request, propriedade_id):
    """Lista de cochos"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    cochos = Cocho.objects.filter(propriedade=propriedade).select_related('pastagem').order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'cochos': cochos,
    }
    
    return render(request, 'gestao_rural/cochos_lista.html', context)


@login_required
def controle_cocho_novo(request, propriedade_id):
    """Registrar controle de cocho"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    cochos = Cocho.objects.filter(propriedade=propriedade, status='ATIVO')
    
    if request.method == 'POST':
        cocho_id = request.POST.get('cocho')
        cocho = get_object_or_404(Cocho, id=cocho_id, propriedade=propriedade)
        
        controle = ControleCocho(cocho=cocho)
        controle.data = datetime.strptime(request.POST.get('data'), '%Y-%m-%d').date()
        if request.POST.get('hora'):
            controle.hora = datetime.strptime(request.POST.get('hora'), '%H:%M').time()
        controle.quantidade_abastecida = Decimal(request.POST.get('quantidade_abastecida', 0))
        controle.quantidade_restante = Decimal(request.POST.get('quantidade_restante', 0)) if request.POST.get('quantidade_restante') else None
        controle.numero_animais = int(request.POST.get('numero_animais', 0))
        controle.valor_unitario = Decimal(request.POST.get('valor_unitario', 0))
        controle.condicao_cocho = request.POST.get('condicao_cocho', '')
        controle.observacoes = request.POST.get('observacoes', '')
        controle.responsavel = request.user
        
        try:
            controle.save()
            messages.success(request, 'Controle de cocho registrado com sucesso!')
            return redirect('nutricao_dashboard', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar controle: {str(e)}')
    
    return render(request, 'gestao_rural/controle_cocho_form.html', {
        'propriedade': propriedade,
        'cochos': cochos
    })

