from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, Q
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Propriedade, IndicadorFinanceiro, InventarioRebanho, MovimentacaoProjetada
from .models import CustoFixo, CustoVariavel, Financiamento
from .forms_analise import IndicadorFinanceiroForm


def analise_dashboard(request, propriedade_id):
    """Dashboard do módulo de análise"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca indicadores recentes
    indicadores = IndicadorFinanceiro.objects.filter(
        propriedade=propriedade
    ).order_by('-data_referencia')[:10]
    
    # Calcula indicadores básicos
    indicadores_calculados = calcular_indicadores_basicos(propriedade)
    
    # Busca histórico de indicadores
    historico_liquidez = IndicadorFinanceiro.objects.filter(
        propriedade=propriedade,
        tipo='LIQUIDEZ'
    ).order_by('data_referencia')[:12]
    
    historico_rentabilidade = IndicadorFinanceiro.objects.filter(
        propriedade=propriedade,
        tipo='RENTABILIDADE'
    ).order_by('data_referencia')[:12]
    
    context = {
        'propriedade': propriedade,
        'indicadores': indicadores,
        'indicadores_calculados': indicadores_calculados,
        'historico_liquidez': historico_liquidez,
        'historico_rentabilidade': historico_rentabilidade,
    }
    
    return render(request, 'gestao_rural/analise_dashboard.html', context)


def indicadores_lista(request, propriedade_id):
    """Lista todos os indicadores da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Filtros
    tipo_filter = request.GET.get('tipo', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    indicadores = IndicadorFinanceiro.objects.filter(propriedade=propriedade)
    
    if tipo_filter:
        indicadores = indicadores.filter(tipo=tipo_filter)
    
    if data_inicio:
        indicadores = indicadores.filter(data_referencia__gte=data_inicio)
    
    if data_fim:
        indicadores = indicadores.filter(data_referencia__lte=data_fim)
    
    indicadores = indicadores.order_by('-data_referencia')
    
    context = {
        'propriedade': propriedade,
        'indicadores': indicadores,
        'tipo_filter': tipo_filter,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    
    return render(request, 'gestao_rural/indicadores_lista.html', context)


def indicador_novo(request, propriedade_id):
    """Adiciona novo indicador"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        form = IndicadorFinanceiroForm(request.POST)
        if form.is_valid():
            indicador = form.save(commit=False)
            indicador.propriedade = propriedade
            indicador.save()
            
            messages.success(request, f'Indicador "{indicador.nome}" cadastrado com sucesso!')
            return redirect('indicadores_lista', propriedade_id=propriedade_id)
    else:
        form = IndicadorFinanceiroForm()
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/indicador_novo.html', context)


def indicador_editar(request, propriedade_id, indicador_id):
    """Edita indicador existente"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    indicador = get_object_or_404(IndicadorFinanceiro, id=indicador_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = IndicadorFinanceiroForm(request.POST, instance=indicador)
        if form.is_valid():
            form.save()
            messages.success(request, f'Indicador "{indicador.nome}" atualizado com sucesso!')
            return redirect('indicadores_lista', propriedade_id=propriedade_id)
    else:
        form = IndicadorFinanceiroForm(instance=indicador)
    
    context = {
        'propriedade': propriedade,
        'indicador': indicador,
        'form': form,
    }
    
    return render(request, 'gestao_rural/indicador_editar.html', context)


def calcular_indicadores_automaticos(request, propriedade_id):
    """Calcula indicadores automaticamente baseado nos dados da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Calcula indicadores básicos
    indicadores = calcular_indicadores_basicos(propriedade)
    
    # Salva os indicadores calculados
    data_referencia = datetime.now().date()
    
    for nome, dados in indicadores.items():
        indicador, created = IndicadorFinanceiro.objects.get_or_create(
            propriedade=propriedade,
            nome=nome,
            data_referencia=data_referencia,
            defaults={
                'tipo': dados['tipo'],
                'valor': dados['valor'],
                'unidade': dados['unidade'],
                'descricao': dados['descricao']
            }
        )
        
        if not created:
            indicador.valor = dados['valor']
            indicador.save()
    
    messages.success(request, f'{len(indicadores)} indicadores calculados automaticamente!')
    return redirect('analise_dashboard', propriedade_id=propriedade_id)


def relatorio_analise(request, propriedade_id):
    """Gera relatório de análise financeira"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca dados para o relatório
    indicadores_calculados = calcular_indicadores_basicos(propriedade)
    
    # Busca histórico dos últimos 12 meses
    data_limite = datetime.now().date() - timedelta(days=365)
    indicadores_historico = IndicadorFinanceiro.objects.filter(
        propriedade=propriedade,
        data_referencia__gte=data_limite
    ).order_by('data_referencia')
    
    # Agrupa por tipo
    indicadores_por_tipo = {}
    for indicador in indicadores_historico:
        if indicador.tipo not in indicadores_por_tipo:
            indicadores_por_tipo[indicador.tipo] = []
        indicadores_por_tipo[indicador.tipo].append(indicador)
    
    context = {
        'propriedade': propriedade,
        'indicadores_calculados': indicadores_calculados,
        'indicadores_historico': indicadores_historico,
        'indicadores_por_tipo': indicadores_por_tipo,
    }
    
    return render(request, 'gestao_rural/relatorio_analise.html', context)


def calcular_indicadores_basicos(propriedade):
    """Calcula indicadores financeiros básicos"""
    indicadores = {}
    
    try:
        # Valor do rebanho
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        valor_rebanho = sum(item.valor_total for item in inventario if item.valor_total)
        
        # Custos fixos mensais
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custo_fixo_mensal = sum(custo.valor_mensal for custo in custos_fixos if custo.valor_mensal)
        
        # Financiamentos ativos
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        total_parcelas_mes = sum(f.valor_parcela for f in financiamentos if f.valor_parcela)
        total_financiado = sum(f.valor_principal for f in financiamentos if f.valor_principal)
        
        # Indicadores calculados
        indicadores['Valor do Rebanho'] = {
            'tipo': 'LIQUIDEZ',
            'valor': valor_rebanho,
            'unidade': 'R$',
            'descricao': 'Valor total do rebanho baseado no inventário'
        }
        
        indicadores['Custo Fixo Mensal'] = {
            'tipo': 'EFICIENCIA',
            'valor': custo_fixo_mensal,
            'unidade': 'R$',
            'descricao': 'Total de custos fixos mensais'
        }
        
        indicadores['Parcelas Mensais'] = {
            'tipo': 'ENDIVIDAMENTO',
            'valor': total_parcelas_mes,
            'unidade': 'R$',
            'descricao': 'Total de parcelas de financiamentos por mês'
        }
        
        if valor_rebanho > 0 and total_parcelas_mes > 0:
            indicadores['Índice de Endividamento'] = {
                'tipo': 'ENDIVIDAMENTO',
                'valor': (total_parcelas_mes / valor_rebanho) * 100,
                'unidade': '%',
                'descricao': 'Percentual do valor do rebanho comprometido com parcelas'
            }
        
        if valor_rebanho > 0:
            indicadores['Custo por R$ Rebanho'] = {
                'tipo': 'EFICIENCIA',
                'valor': (custo_fixo_mensal / valor_rebanho) * 100,
                'unidade': '%',
                'descricao': 'Percentual de custos fixos em relação ao valor do rebanho'
            }
        
    except Exception as e:
        print(f"Erro ao calcular indicadores: {e}")
    
    return indicadores

