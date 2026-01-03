# -*- coding: utf-8 -*-
"""
Views para justificativa de endividamento e análise de capacidade de pagamento
Sistema para documentar situação financeira e justificar empréstimo
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal
from datetime import date, datetime
import json

from .models import Propriedade, ProdutorRural
from .models_financeiro import LancamentoFinanceiro, CategoriaFinanceira


@login_required
def justificativa_endividamento(request):
    """
    Página principal de justificativa de endividamento.
    Mostra situação atual, histórico e capacidade de pagamento.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Buscar dados do SCR se existir
    from .models import SCRBancoCentral
    scr_mais_recente = SCRBancoCentral.objects.filter(
        produtor=produtor
    ).order_by('-data_referencia_scr').first()
    
    # Calcular capacidade de pagamento
    ano_atual = timezone.now().year
    capacidade_pagamento = calcular_capacidade_pagamento(propriedades, ano_atual)
    
    # Histórico de preços (se disponível)
    # TODO: Integrar com dados de preços de mercado (CEPEA, etc.)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'scr': scr_mais_recente,
        'capacidade_pagamento': capacidade_pagamento,
        'ano_atual': ano_atual,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/justificativa_endividamento.html', context)


def calcular_capacidade_pagamento(propriedades, ano):
    """Calcula a capacidade de pagamento baseada em receitas e despesas."""
    # Receitas do ano
    receitas = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    # Despesas operacionais do ano
    despesas_operacionais = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    ).exclude(
        categoria__nome__icontains='financiamento'
    ).exclude(
        categoria__nome__icontains='empréstimo'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    # Saldo disponível para pagamento de dívidas
    saldo_disponivel = receitas - despesas_operacionais
    
    # Capacidade de pagamento mensal (conservador: 70% do saldo disponível)
    capacidade_mensal = (saldo_disponivel / 12) * Decimal('0.70')
    
    return {
        'receitas_anuais': receitas,
        'despesas_operacionais': despesas_operacionais,
        'saldo_disponivel': saldo_disponivel,
        'capacidade_mensal': capacidade_mensal,
        'capacidade_anual': capacidade_mensal * 12,
    }


@login_required
def relatorio_justificativa_completo(request):
    """
    Relatório completo de justificativa de endividamento para apresentação bancária.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Buscar SCR
    from .models import SCRBancoCentral, DividaBanco
    scr = SCRBancoCentral.objects.filter(
        produtor=produtor
    ).order_by('-data_referencia_scr').first()
    
    dividas_por_banco = []
    if scr:
        dividas_por_banco = DividaBanco.objects.filter(scr=scr).order_by('banco')
    
    # Calcular capacidade de pagamento
    capacidade_pagamento = calcular_capacidade_pagamento(propriedades, ano)
    
    # Dados do rebanho e bens (garantias)
    from .models import InventarioRebanho, BemImobilizado
    from django.db.models import Sum
    
    # Calcular valor_total usando F() para multiplicar quantidade * valor_por_cabeca
    rebanho = InventarioRebanho.objects.filter(
        propriedade__in=propriedades,
        data_inventario__year=ano
    ).annotate(
        valor_total_calc=F('quantidade') * F('valor_por_cabeca')
    ).aggregate(
        total_cabecas=Sum('quantidade'),
        valor_total=Sum('valor_total_calc')
    )
    
    bens = BemImobilizado.objects.filter(
        propriedade__in=propriedades,
        ativo=True
    )
    valor_bens = sum(b.valor_atual for b in bens)
    
    # Histórico de receitas (últimos 3 anos)
    historico_receitas = []
    for ano_hist in range(ano - 2, ano + 1):
        receitas_ano = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            data_competencia__year=ano_hist,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        historico_receitas.append({
            'ano': ano_hist,
            'receitas': receitas_ano,
        })
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'ano': ano,
        'scr': scr,
        'dividas_por_banco': dividas_por_banco,
        'capacidade_pagamento': capacidade_pagamento,
        'rebanho': {
            'total_cabecas': rebanho.get('total_cabecas', 0) or 0,
            'valor_total': rebanho.get('valor_total', Decimal('0.00')) or Decimal('0.00'),
        },
        'bens': {
            'valor_liquido': Decimal(str(valor_bens)),
        },
        'historico_receitas': historico_receitas,
        'valor_garantias': (rebanho.get('valor_total', Decimal('0.00')) or Decimal('0.00')) + Decimal(str(valor_bens)),
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/relatorio_justificativa_completo.html', context)


@login_required
def importar_scr(request):
    """
    View para importar arquivo SCR do Banco Central.
    """
    if request.method == 'POST' and request.FILES.get('arquivo_scr'):
        # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
        produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
        if not produtor:
            return JsonResponse({'erro': 'Produtor não encontrado'}, status=400)
        
        arquivo = request.FILES['arquivo_scr']
        
        # Criar registro do SCR
        from .models import SCRBancoCentral
        from django.utils import timezone
        
        scr = SCRBancoCentral.objects.create(
            produtor=produtor,
            arquivo_pdf=arquivo,
            data_referencia_scr=timezone.now().date(),
            status='IMPORTADO',
        )
        
        # TODO: Processar PDF e extrair dados das dívidas
        # Por enquanto, apenas salva o arquivo
        
        return JsonResponse({
            'sucesso': True,
            'scr_id': scr.id,
            'mensagem': 'SCR importado com sucesso. Processamento dos dados em desenvolvimento.'
        })
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

