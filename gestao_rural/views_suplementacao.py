# -*- coding: utf-8 -*-
"""
Views para Sistema de Suplementação
- Controle de estoque
- Distribuição no pasto
- Compras
- Relatórios
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from decimal import Decimal
from datetime import date, datetime, timedelta
from .models import Propriedade
from .models_operacional import (
    EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao
)
from .models_controles_operacionais import (
    TipoDistribuicao, DistribuicaoPasto, Pastagem
)


@login_required
def suplementacao_dashboard(request, propriedade_id):
    """Dashboard de suplementação"""
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Estoque atual
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
    
    # Estoque com alertas (abaixo do mínimo)
    estoques_baixo = estoques.filter(
        quantidade_atual__lte=models.F('quantidade_minima')
    )
    
    # Valor total do estoque
    valor_total_estoque = sum(e.valor_total_estoque for e in estoques)
    
    # Distribuições do mês atual
    mes_atual = date.today().replace(day=1)
    distribuicoes_mes = DistribuicaoSuplementacao.objects.filter(
        estoque__propriedade=propriedade,
        data__gte=mes_atual
    )
    
    total_distribuido_mes = sum(d.quantidade for d in distribuicoes_mes)
    valor_distribuido_mes = sum(d.valor_total for d in distribuicoes_mes)
    
    # Compras do mês
    compras_mes = CompraSuplementacao.objects.filter(
        estoque__propriedade=propriedade,
        data__gte=mes_atual
    )
    valor_compras_mes = sum(c.valor_total for c in compras_mes)
    
    # Últimas distribuições
    ultimas_distribuicoes = DistribuicaoSuplementacao.objects.filter(
        estoque__propriedade=propriedade
    ).select_related('estoque').order_by('-data')[:10]
    
    context = {
        'propriedade': propriedade,
        'estoques': estoques,
        'estoques_baixo': estoques_baixo,
        'valor_total_estoque': valor_total_estoque,
        'total_distribuido_mes': total_distribuido_mes,
        'valor_distribuido_mes': valor_distribuido_mes,
        'valor_compras_mes': valor_compras_mes,
        'ultimas_distribuicoes': ultimas_distribuicoes,
    }
    
    return render(request, 'gestao_rural/suplementacao_dashboard.html', context)


@login_required
def estoque_suplementacao_lista(request, propriedade_id):
    """Lista de estoques de suplementação"""
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade).order_by('tipo_suplemento')
    
    context = {
        'propriedade': propriedade,
        'estoques': estoques,
    }
    
    return render(request, 'gestao_rural/estoque_suplementacao_lista.html', context)


@login_required
def estoque_suplementacao_novo(request, propriedade_id):
    """Cadastrar novo estoque de suplementação"""
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        estoque = EstoqueSuplementacao(propriedade=propriedade)
        estoque.tipo_suplemento = request.POST.get('tipo_suplemento')
        estoque.unidade_medida = request.POST.get('unidade_medida', 'KG')
        estoque.quantidade_atual = Decimal(request.POST.get('quantidade_atual', 0))
        estoque.quantidade_minima = Decimal(request.POST.get('quantidade_minima', 0))
        estoque.valor_unitario_medio = Decimal(request.POST.get('valor_unitario_medio', 0))
        estoque.localizacao = request.POST.get('localizacao', '')
        estoque.observacoes = request.POST.get('observacoes', '')
        
        # Calcular valor total
        estoque.valor_total_estoque = estoque.quantidade_atual * estoque.valor_unitario_medio
        
        try:
            estoque.save()
            messages.success(request, 'Estoque cadastrado com sucesso!')
            return redirect('estoque_suplementacao_lista', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar estoque: {str(e)}')
    
    return render(request, 'gestao_rural/estoque_suplementacao_form.html', {
        'propriedade': propriedade,
        'form_type': 'novo'
    })


@login_required
def compra_suplementacao_nova(request, propriedade_id):
    """Registrar compra de suplementação"""
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
    
    if request.method == 'POST':
        estoque_id = request.POST.get('estoque')
        estoque = get_object_or_404(EstoqueSuplementacao, id=estoque_id, propriedade=propriedade)
        
        compra = CompraSuplementacao(estoque=estoque)
        compra.data = datetime.strptime(request.POST.get('data'), '%Y-%m-%d').date()
        compra.fornecedor = request.POST.get('fornecedor', '')
        compra.numero_nota_fiscal = request.POST.get('numero_nota_fiscal', '')
        compra.quantidade = Decimal(request.POST.get('quantidade', 0))
        compra.preco_unitario = Decimal(request.POST.get('preco_unitario', 0))
        compra.observacoes = request.POST.get('observacoes', '')
        compra.responsavel = request.user
        
        try:
            compra.save()  # O save() já atualiza o estoque automaticamente
            messages.success(request, 'Compra registrada com sucesso!')
            return redirect('suplementacao_dashboard', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar compra: {str(e)}')
    
    return render(request, 'gestao_rural/compra_suplementacao_form.html', {
        'propriedade': propriedade,
        'estoques': estoques
    })


@login_required
def distribuicao_suplementacao_nova(request, propriedade_id):
    """Registrar distribuição de suplementação no pasto"""
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
    pastagens = Pastagem.objects.filter(propriedade=propriedade)
    
    if request.method == 'POST':
        estoque_id = request.POST.get('estoque')
        estoque = get_object_or_404(EstoqueSuplementacao, id=estoque_id, propriedade=propriedade)
        
        # Verificar estoque disponível
        if estoque.quantidade_atual <= 0:
            messages.error(request, 'Estoque insuficiente!')
            return render(request, 'gestao_rural/distribuicao_suplementacao_form.html', {
                'propriedade': propriedade,
                'estoques': estoques,
                'pastagens': pastagens
            })
        
        distribuicao = DistribuicaoSuplementacao(estoque=estoque)
        distribuicao.data = datetime.strptime(request.POST.get('data'), '%Y-%m-%d').date()
        distribuicao.pastagem = request.POST.get('pastagem', '')
        distribuicao.quantidade = Decimal(request.POST.get('quantidade', 0))
        distribuicao.numero_animais = int(request.POST.get('numero_animais', 0))
        distribuicao.valor_unitario = estoque.valor_unitario_medio
        distribuicao.observacoes = request.POST.get('observacoes', '')
        distribuicao.responsavel = request.user
        
        # Verificar se tem estoque suficiente
        if distribuicao.quantidade > estoque.quantidade_atual:
            messages.error(request, f'Estoque insuficiente! Disponível: {estoque.quantidade_atual} {estoque.unidade_medida}')
            return render(request, 'gestao_rural/distribuicao_suplementacao_form.html', {
                'propriedade': propriedade,
                'estoques': estoques,
                'pastagens': pastagens
            })
        
        try:
            distribuicao.save()  # O save() já atualiza o estoque automaticamente
            messages.success(request, 'Distribuição registrada com sucesso!')
            return redirect('suplementacao_dashboard', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar distribuição: {str(e)}')
    
    return render(request, 'gestao_rural/distribuicao_suplementacao_form.html', {
        'propriedade': propriedade,
        'estoques': estoques,
        'pastagens': pastagens
    })


@login_required
def estoque_suplementacao_detalhes(request, propriedade_id, estoque_id):
    """Detalhes do estoque de suplementação"""
    # ✅ SEGURANÇA: Verificar permissão de acesso à propriedade
    from .decorators import obter_propriedade_com_permissao
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    estoque = get_object_or_404(EstoqueSuplementacao, id=estoque_id, propriedade=propriedade)
    
    # Histórico de compras
    compras = CompraSuplementacao.objects.filter(estoque=estoque).order_by('-data')[:20]
    
    # Histórico de distribuições
    distribuicoes = DistribuicaoSuplementacao.objects.filter(estoque=estoque).order_by('-data')[:20]
    
    context = {
        'propriedade': propriedade,
        'estoque': estoque,
        'compras': compras,
        'distribuicoes': distribuicoes,
    }
    
    return render(request, 'gestao_rural/estoque_suplementacao_detalhes.html', context)


