from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from .models import Propriedade, TipoFinanciamento, Financiamento
from .forms_endividamento import FinanciamentoForm, TipoFinanciamentoForm


def dividas_financeiras_dashboard(request, propriedade_id):
    """Dashboard do módulo de dívidas financeiras"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca financiamentos ativos
    financiamentos = Financiamento.objects.filter(
        propriedade=propriedade, 
        ativo=True
    ).order_by('-data_contratacao')
    
    # Calcula totais
    total_principal = financiamentos.aggregate(
        total=Sum('valor_principal')
    )['total'] or Decimal('0.00')
    
    total_parcelas_mes = financiamentos.aggregate(
        total=Sum('valor_parcela')
    )['total'] or Decimal('0.00')
    
    # Financiamentos vencendo nos próximos 30 dias
    from datetime import datetime, timedelta
    data_limite = datetime.now().date() + timedelta(days=30)
    
    vencendo_em_breve = financiamentos.filter(
        data_ultimo_vencimento__lte=data_limite
    ).count()
    
    context = {
        'propriedade': propriedade,
        'financiamentos': financiamentos,
        'total_principal': total_principal,
        'total_parcelas_mes': total_parcelas_mes,
        'vencendo_em_breve': vencendo_em_breve,
    }
    
    return render(request, 'gestao_rural/endividamento_dashboard.html', context)


def financiamentos_lista(request, propriedade_id):
    """Lista todos os financiamentos da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    financiamentos = Financiamento.objects.filter(
        propriedade=propriedade
    ).order_by('-data_contratacao')
    
    context = {
        'propriedade': propriedade,
        'financiamentos': financiamentos,
    }
    
    return render(request, 'gestao_rural/financiamentos_lista.html', context)


def financiamento_novo(request, propriedade_id):
    """Adiciona novo financiamento"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        form = FinanciamentoForm(request.POST)
        if form.is_valid():
            financiamento = form.save(commit=False)
            financiamento.propriedade = propriedade
            financiamento.save()
            
            messages.success(request, f'Financiamento "{financiamento.nome}" cadastrado com sucesso!')
            return redirect('financiamentos_lista', propriedade_id=propriedade_id)
    else:
        form = FinanciamentoForm()
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/financiamento_novo.html', context)


def financiamento_editar(request, propriedade_id, financiamento_id):
    """Edita financiamento existente"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    financiamento = get_object_or_404(Financiamento, id=financiamento_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = FinanciamentoForm(request.POST, instance=financiamento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Financiamento "{financiamento.nome}" atualizado com sucesso!')
            return redirect('financiamentos_lista', propriedade_id=propriedade_id)
    else:
        form = FinanciamentoForm(instance=financiamento)
    
    context = {
        'propriedade': propriedade,
        'financiamento': financiamento,
        'form': form,
    }
    
    return render(request, 'gestao_rural/financiamento_editar.html', context)


def financiamento_excluir(request, propriedade_id, financiamento_id):
    """Exclui financiamento"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    financiamento = get_object_or_404(Financiamento, id=financiamento_id, propriedade=propriedade)
    
    if request.method == 'POST':
        nome = financiamento.nome
        financiamento.delete()
        messages.success(request, f'Financiamento "{nome}" excluído com sucesso!')
        return redirect('financiamentos_lista', propriedade_id=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'financiamento': financiamento,
    }
    
    return render(request, 'gestao_rural/financiamento_excluir.html', context)


def tipos_financiamento_lista(request):
    """Lista tipos de financiamento"""
    tipos = TipoFinanciamento.objects.all().order_by('nome')
    
    context = {
        'tipos': tipos,
    }
    
    return render(request, 'gestao_rural/tipos_financiamento_lista.html', context)


def tipo_financiamento_novo(request):
    """Adiciona novo tipo de financiamento"""
    if request.method == 'POST':
        form = TipoFinanciamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de financiamento criado com sucesso!')
            return redirect('tipos_financiamento_lista')
    else:
        form = TipoFinanciamentoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'gestao_rural/tipo_financiamento_novo.html', context)


def calcular_amortizacao(request, financiamento_id):
    """Calcula tabela de amortização do financiamento"""
    financiamento = get_object_or_404(Financiamento, id=financiamento_id)
    
    # Simulação simples de amortização (Sistema Price)
    tabela_amortizacao = []
    saldo_devedor = financiamento.valor_principal
    
    for parcela_num in range(1, financiamento.numero_parcelas + 1):
        # Cálculo simplificado - juros sobre saldo devedor
        juros_mes = saldo_devedor * (financiamento.taxa_juros_anual / 100 / 12)
        amortizacao = financiamento.valor_parcela - juros_mes
        
        if parcela_num == financiamento.numero_parcelas:
            # Última parcela - ajusta para saldar
            amortizacao = saldo_devedor
            juros_mes = financiamento.valor_parcela - amortizacao
        
        saldo_devedor -= amortizacao
        
        tabela_amortizacao.append({
            'parcela': parcela_num,
            'valor_parcela': financiamento.valor_parcela,
            'amortizacao': amortizacao,
            'juros': juros_mes,
            'saldo_devedor': max(saldo_devedor, Decimal('0.00'))
        })
    
    context = {
        'financiamento': financiamento,
        'tabela_amortizacao': tabela_amortizacao,
    }
    
    return render(request, 'gestao_rural/tabela_amortizacao.html', context)
