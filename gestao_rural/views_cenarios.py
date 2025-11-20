# -*- coding: utf-8 -*-
"""
Views para análise de cenários de planejamento
Sistema completo de gerenciamento e comparação de cenários
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, datetime

from .models import (
    Propriedade,
    PlanejamentoAnual, 
    CenarioPlanejamento,
    MovimentacaoProjetada,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada
)


@login_required
def analise_cenarios(request, propriedade_id):
    """Página principal de análise de cenários"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    # Buscar planejamento atual (ano atual ou mais recente)
    ano_atual = timezone.now().year
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=propriedade
    ).order_by('-ano').first()
    
    # Se não existe planejamento, criar um para o ano atual
    if not planejamento:
        planejamento = PlanejamentoAnual.objects.create(
            propriedade=propriedade,
            ano=ano_atual,
            descricao=f"Planejamento {ano_atual}",
            status='RASCUNHO'
        )
        # Criar cenário baseline
        CenarioPlanejamento.objects.create(
            planejamento=planejamento,
            nome="Baseline",
            descricao="Cenário base de referência",
            is_baseline=True
        )
    
    # Buscar todos os cenários do planejamento
    cenarios = planejamento.cenarios.all().order_by('-is_baseline', 'nome')
    
    # Processar dados de cada cenário
    cenarios_data = []
    for cenario in cenarios:
        dados = calcular_metricas_cenario(planejamento, cenario)
        cenarios_data.append({
            'cenario': cenario,
            'dados': dados
        })
    
    context = {
        'propriedade': propriedade,
        'planejamento': planejamento,
        'cenarios_data': cenarios_data,
        'ano_atual': ano_atual,
    }
    
    return render(request, 'gestao_rural/analise_cenarios.html', context)


@login_required
def criar_cenario(request, propriedade_id):
    """Criar novo cenário"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    planejamento_id = request.POST.get('planejamento_id')
    planejamento = get_object_or_404(PlanejamentoAnual, id=planejamento_id, propriedade=propriedade)
    
    nome = request.POST.get('nome', '').strip()
    if not nome:
        messages.error(request, 'Nome do cenário é obrigatório')
        return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    descricao = request.POST.get('descricao', '').strip()
    is_baseline = request.POST.get('is_baseline') == 'on'
    
    # Se marcar como baseline, desmarcar outros
    if is_baseline:
        CenarioPlanejamento.objects.filter(planejamento=planejamento, is_baseline=True).update(is_baseline=False)
    
    # Ajustes percentuais
    ajuste_preco = Decimal(request.POST.get('ajuste_preco_percentual', '0') or '0')
    ajuste_custo = Decimal(request.POST.get('ajuste_custo_percentual', '0') or '0')
    ajuste_producao = Decimal(request.POST.get('ajuste_producao_percentual', '0') or '0')
    ajuste_taxas = Decimal(request.POST.get('ajuste_taxas_percentual', '0') or '0')
    
    cenario = CenarioPlanejamento.objects.create(
        planejamento=planejamento,
        nome=nome,
        descricao=descricao,
        is_baseline=is_baseline,
        ajuste_preco_percentual=ajuste_preco,
        ajuste_custo_percentual=ajuste_custo,
        ajuste_producao_percentual=ajuste_producao,
        ajuste_taxas_percentual=ajuste_taxas
    )
    
    messages.success(request, f'Cenário "{nome}" criado com sucesso!')
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def editar_cenario(request, propriedade_id, cenario_id):
    """Editar cenário existente"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    cenario = get_object_or_404(
        CenarioPlanejamento, 
        id=cenario_id,
        planejamento__propriedade=propriedade
    )
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        if not nome:
            messages.error(request, 'Nome do cenário é obrigatório')
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
        
        cenario.nome = nome
        cenario.descricao = request.POST.get('descricao', '').strip()
        is_baseline = request.POST.get('is_baseline') == 'on'
        
        # Se marcar como baseline, desmarcar outros
        if is_baseline and not cenario.is_baseline:
            CenarioPlanejamento.objects.filter(
                planejamento=cenario.planejamento, 
                is_baseline=True
            ).exclude(id=cenario.id).update(is_baseline=False)
        
        cenario.is_baseline = is_baseline
        cenario.ajuste_preco_percentual = Decimal(request.POST.get('ajuste_preco_percentual', '0') or '0')
        cenario.ajuste_custo_percentual = Decimal(request.POST.get('ajuste_custo_percentual', '0') or '0')
        cenario.ajuste_producao_percentual = Decimal(request.POST.get('ajuste_producao_percentual', '0') or '0')
        cenario.ajuste_taxas_percentual = Decimal(request.POST.get('ajuste_taxas_percentual', '0') or '0')
        cenario.save()
        
        messages.success(request, f'Cenário "{nome}" atualizado com sucesso!')
        return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    # GET - retornar dados do cenário em JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'id': cenario.id,
            'nome': cenario.nome,
            'descricao': cenario.descricao or '',
            'is_baseline': cenario.is_baseline,
            'ajuste_preco_percentual': str(cenario.ajuste_preco_percentual),
            'ajuste_custo_percentual': str(cenario.ajuste_custo_percentual),
            'ajuste_producao_percentual': str(cenario.ajuste_producao_percentual),
            'ajuste_taxas_percentual': str(cenario.ajuste_taxas_percentual),
        })
    
    # GET normal - redirecionar para a página principal
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def excluir_cenario(request, propriedade_id, cenario_id):
    """Excluir cenário"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    cenario = get_object_or_404(
        CenarioPlanejamento, 
        id=cenario_id,
        planejamento__propriedade=propriedade
    )
    
    # Não permitir excluir baseline se for o único cenário
    if cenario.is_baseline:
        total_cenarios = CenarioPlanejamento.objects.filter(planejamento=cenario.planejamento).count()
        if total_cenarios == 1:
            messages.error(request, 'Não é possível excluir o cenário baseline se for o único cenário.')
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    nome = cenario.nome
    cenario.delete()
    
    messages.success(request, f'Cenário "{nome}" excluído com sucesso!')
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def comparar_cenarios_api(request, propriedade_id):
    """API para comparar cenários"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    planejamento_id = request.GET.get('planejamento_id')
    if not planejamento_id:
        return JsonResponse({'erro': 'planejamento_id é obrigatório'}, status=400)
    
    planejamento = get_object_or_404(PlanejamentoAnual, id=planejamento_id, propriedade=propriedade)
    
    cenarios_ids = request.GET.getlist('cenarios_ids[]')
    if not cenarios_ids:
        cenarios = planejamento.cenarios.all()
    else:
        cenarios = CenarioPlanejamento.objects.filter(
            id__in=cenarios_ids,
            planejamento=planejamento
        )
    
    dados_comparacao = []
    for cenario in cenarios:
        metricas = calcular_metricas_cenario(planejamento, cenario)
        dados_comparacao.append({
            'id': cenario.id,
            'nome': cenario.nome,
            'is_baseline': cenario.is_baseline,
            'metricas': metricas
        })
    
    return JsonResponse({
        'cenarios': dados_comparacao
    })


def calcular_metricas_cenario(planejamento, cenario):
    """Calcula métricas financeiras e operacionais de um cenário"""
    # Buscar metas comerciais
    metas_comerciais = MetaComercialPlanejada.objects.filter(planejamento=planejamento)
    
    # Calcular receitas projetadas com ajuste de preço
    receitas_totais = Decimal('0')
    quantidade_animais = 0
    arrobas_totais = Decimal('0')
    
    for meta in metas_comerciais:
        preco_ajustado = meta.preco_medio_esperado * (1 + cenario.ajuste_preco_percentual / 100)
        quantidade_ajustada = int(meta.quantidade_animais * (1 + cenario.ajuste_producao_percentual / 100))
        
        receita_meta = preco_ajustado * quantidade_ajustada
        if meta.arrobas_totais:
            receita_meta = preco_ajustado * meta.arrobas_totais * (1 + cenario.ajuste_producao_percentual / 100)
        
        receitas_totais += receita_meta
        quantidade_animais += quantidade_ajustada
        if meta.arrobas_totais:
            arrobas_totais += meta.arrobas_totais * (1 + cenario.ajuste_producao_percentual / 100)
    
    # Buscar metas financeiras (custos)
    metas_financeiras = MetaFinanceiraPlanejada.objects.filter(planejamento=planejamento)
    
    custos_totais = Decimal('0')
    for meta in metas_financeiras:
        custo_ajustado = meta.valor_anual_previsto * (1 + cenario.ajuste_custo_percentual / 100)
        custos_totais += custo_ajustado
    
    # Calcular lucro
    lucro = receitas_totais - custos_totais
    
    # Calcular margem
    margem = (lucro / receitas_totais * 100) if receitas_totais > 0 else Decimal('0')
    
    return {
        'receitas_totais': float(receitas_totais),
        'custos_totais': float(custos_totais),
        'lucro': float(lucro),
        'margem': float(margem),
        'quantidade_animais': quantidade_animais,
        'arrobas_totais': float(arrobas_totais),
    }
