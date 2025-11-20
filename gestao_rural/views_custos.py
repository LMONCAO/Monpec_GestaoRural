from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from datetime import date, datetime, timedelta
from calendar import monthrange
from collections import defaultdict

from .models import Propriedade, CustoFixo, CustoVariavel, FluxoCaixa, InventarioRebanho
from .forms_custos import CustoFixoForm, CustoVariavelForm


@login_required
def custos_dashboard(request, propriedade_id):
    """Dashboard de custos da propriedade com fluxo de caixa mensal e anual"""
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
    
    # ========== FLUXO DE CAIXA MENSAL (Últimos 12 meses) ==========
    hoje = date.today()
    fluxo_mensal = []
    meses_labels = []
    receitas_mensais = []
    despesas_mensais = []
    saldos_mensais = []
    
    for i in range(11, -1, -1):  # Últimos 12 meses
        # Calcular mês de referência
        mes_atual = hoje.month - i
        ano_atual = hoje.year
        while mes_atual <= 0:
            mes_atual += 12
            ano_atual -= 1
        while mes_atual > 12:
            mes_atual -= 12
            ano_atual += 1
        
        mes_inicio = date(ano_atual, mes_atual, 1)
        ultimo_dia = monthrange(ano_atual, mes_atual)[1]
        mes_fim = date(ano_atual, mes_atual, ultimo_dia)
        
        # Buscar fluxos de caixa do mês
        fluxos_mes = FluxoCaixa.objects.filter(
            propriedade=propriedade,
            data_referencia__year=ano_atual,
            data_referencia__month=mes_atual
        ).order_by('-data_referencia')
        
        if fluxos_mes.exists():
            # Usar o fluxo mais recente do mês
            fluxo = fluxos_mes.first()
            receita_mes = fluxo.receita_total / 12  # Receita mensal (anual dividido por 12)
            despesa_mes = fluxo.custo_fixo_total + (fluxo.custo_variavel_total / 12)
            saldo_mes = receita_mes - despesa_mes
        else:
            # Calcular baseado nos custos atuais
            receita_mes = receita_total / 12
            despesa_mes = custo_fixo_total + (custo_variavel_total / 12)
            saldo_mes = receita_mes - despesa_mes
        
        # Nomes dos meses em português
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        nome_mes = f"{meses_pt[mes_atual-1]}/{ano_atual}"
        meses_labels.append(nome_mes)
        receitas_mensais.append(float(receita_mes))
        despesas_mensais.append(float(despesa_mes))
        saldos_mensais.append(float(saldo_mes))
        
        fluxo_mensal.append({
            'mes': nome_mes,
            'ano': ano_atual,
            'mes_numero': mes_atual,
            'receita': receita_mes,
            'despesa': despesa_mes,
            'saldo': saldo_mes,
            'margem': (saldo_mes / receita_mes * 100) if receita_mes > 0 else Decimal('0.00')
        })
    
    # ========== FLUXO DE CAIXA ANUAL (Últimos anos) ==========
    fluxo_anual = []
    anos_labels = []
    receitas_anuais = []
    despesas_anuais = []
    saldos_anuais = []
    
    # Buscar todos os anos com fluxo de caixa
    anos_com_fluxo = FluxoCaixa.objects.filter(
        propriedade=propriedade
    ).values_list('data_referencia__year', flat=True).distinct().order_by('-data_referencia__year')[:5]
    
    if not anos_com_fluxo:
        # Se não houver fluxo, usar ano atual
        anos_com_fluxo = [hoje.year]
    
    for ano in anos_com_fluxo:
        # Buscar fluxos do ano (usar o mais recente de cada ano)
        fluxos_ano = FluxoCaixa.objects.filter(
            propriedade=propriedade,
            data_referencia__year=ano
        ).order_by('-data_referencia')
        
        if fluxos_ano.exists():
            fluxo = fluxos_ano.first()
            receita_ano = fluxo.receita_total
            despesa_ano = (fluxo.custo_fixo_total * 12) + fluxo.custo_variavel_total
            saldo_ano = receita_ano - despesa_ano
        else:
            # Calcular baseado nos custos atuais
            receita_ano = receita_total
            despesa_ano = custo_fixo_anual + custo_variavel_total
            saldo_ano = receita_ano - despesa_ano
        
        anos_labels.append(str(ano))
        receitas_anuais.append(float(receita_ano))
        despesas_anuais.append(float(despesa_ano))
        saldos_anuais.append(float(saldo_ano))
        
        fluxo_anual.append({
            'ano': ano,
            'receita': receita_ano,
            'despesa': despesa_ano,
            'saldo': saldo_ano,
            'margem': (saldo_ano / receita_ano * 100) if receita_ano > 0 else Decimal('0.00')
        })
    
    # ========== PROJEÇÃO FUTURA (Próximos 12 meses) ==========
    projecao_futura = []
    meses_projecao_labels = []
    receitas_projecao = []
    despesas_projecao = []
    saldos_projecao = []
    
    # Calcular média de receita mensal dos últimos meses
    if receitas_mensais:
        receita_media_mensal = sum(receitas_mensais) / len(receitas_mensais)
    else:
        receita_media_mensal = float(receita_total / 12)
    
    despesa_mensal_projetada = float(custo_fixo_total + (custo_variavel_total / 12))
    
    for i in range(1, 13):  # Próximos 12 meses
        mes_projecao = hoje.month + i
        ano_projecao = hoje.year
        while mes_projecao > 12:
            mes_projecao -= 12
            ano_projecao += 1
        
        mes_inicio_proj = date(ano_projecao, mes_projecao, 1)
        # Nomes dos meses em português
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        nome_mes_proj = f"{meses_pt[mes_projecao-1]}/{ano_projecao}"
        
        # Projeção conservadora (usando média)
        receita_proj = receita_media_mensal
        despesa_proj = despesa_mensal_projetada
        saldo_proj = receita_proj - despesa_proj
        
        meses_projecao_labels.append(nome_mes_proj)
        receitas_projecao.append(receita_proj)
        despesas_projecao.append(despesa_proj)
        saldos_projecao.append(saldo_proj)
        
        projecao_futura.append({
            'mes': nome_mes_proj,
            'ano': ano_projecao,
            'mes_numero': mes_projecao,
            'receita': Decimal(str(receita_proj)),
            'despesa': Decimal(str(despesa_proj)),
            'saldo': Decimal(str(saldo_proj)),
            'margem': (saldo_proj / receita_proj * 100) if receita_proj > 0 else Decimal('0.00')
        })
    
    # ========== ESTATÍSTICAS ==========
    if saldos_mensais:
        saldo_medio_mensal = sum(saldos_mensais) / len(saldos_mensais)
        meses_positivos = sum(1 for s in saldos_mensais if s > 0)
        meses_negativos = sum(1 for s in saldos_mensais if s < 0)
    else:
        saldo_medio_mensal = 0
        meses_positivos = 0
        meses_negativos = 0
    
    if saldos_anuais:
        saldo_medio_anual = sum(saldos_anuais) / len(saldos_anuais)
    else:
        saldo_medio_anual = 0
    
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
        # Fluxo mensal
        'fluxo_mensal': fluxo_mensal,
        'grafico_mensal': {
            'labels': meses_labels,
            'receitas': receitas_mensais,
            'despesas': despesas_mensais,
            'saldos': saldos_mensais,
        },
        # Fluxo anual
        'fluxo_anual': fluxo_anual,
        'grafico_anual': {
            'labels': anos_labels,
            'receitas': receitas_anuais,
            'despesas': despesas_anuais,
            'saldos': saldos_anuais,
        },
        # Projeção futura
        'projecao_futura': projecao_futura,
        'grafico_projecao': {
            'labels': meses_projecao_labels,
            'receitas': receitas_projecao,
            'despesas': despesas_projecao,
            'saldos': saldos_projecao,
        },
        # Estatísticas
        'saldo_medio_mensal': saldo_medio_mensal,
        'saldo_medio_anual': saldo_medio_anual,
        'meses_positivos': meses_positivos,
        'meses_negativos': meses_negativos,
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
def custos_fixos_editar(request, propriedade_id, custo_id):
    """Editar custo fixo"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    custo = get_object_or_404(CustoFixo, id=custo_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = CustoFixoForm(request.POST, instance=custo)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Custo fixo "{custo.nome_custo}" atualizado com sucesso!')
                return redirect('custos_fixos_lista', propriedade_id=propriedade.id)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao atualizar custo fixo: {str(e)}', exc_info=True)
                messages.error(request, f'Erro ao atualizar custo: {str(e)}')
        else:
            from .utils_forms import formatar_mensagem_erro_form
            erro_msg = formatar_mensagem_erro_form(form)
            messages.error(request, f'Erro no formulário: {erro_msg}')
    else:
        form = CustoFixoForm(instance=custo)
    
    meses_choices = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    context = {
        'propriedade': propriedade,
        'custo': custo,
        'form': form,
        'meses_choices': meses_choices,
    }
    
    return render(request, 'gestao_rural/custos_fixos_editar.html', context)


@login_required
def custos_fixos_excluir(request, propriedade_id, custo_id):
    """Excluir custo fixo"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    custo = get_object_or_404(CustoFixo, id=custo_id, propriedade=propriedade)
    
    if request.method == 'POST':
        try:
            nome_custo = custo.nome_custo
            custo.delete()
            messages.success(request, f'Custo fixo "{nome_custo}" excluído com sucesso!')
            return redirect('custos_fixos_lista', propriedade_id=propriedade.id)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao excluir custo fixo: {str(e)}', exc_info=True)
            messages.error(request, f'Erro ao excluir custo: {str(e)}')
            return redirect('custos_fixos_lista', propriedade_id=propriedade.id)
    
    context = {
        'propriedade': propriedade,
        'custo': custo,
    }
    
    return render(request, 'gestao_rural/custos_fixos_excluir.html', context)


@login_required
def custos_variaveis_editar(request, propriedade_id, custo_id):
    """Editar custo variável"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    custo = get_object_or_404(CustoVariavel, id=custo_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = CustoVariavelForm(request.POST, instance=custo)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Custo variável "{custo.nome_custo}" atualizado com sucesso!')
                return redirect('custos_variaveis_lista', propriedade_id=propriedade.id)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao atualizar custo variável: {str(e)}', exc_info=True)
                messages.error(request, f'Erro ao atualizar custo: {str(e)}')
        else:
            from .utils_forms import formatar_mensagem_erro_form
            erro_msg = formatar_mensagem_erro_form(form)
            messages.error(request, f'Erro no formulário: {erro_msg}')
    else:
        form = CustoVariavelForm(instance=custo)
    
    meses_choices = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    context = {
        'propriedade': propriedade,
        'custo': custo,
        'form': form,
        'meses_choices': meses_choices,
    }
    
    return render(request, 'gestao_rural/custos_variaveis_editar.html', context)


@login_required
def custos_variaveis_excluir(request, propriedade_id, custo_id):
    """Excluir custo variável"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    custo = get_object_or_404(CustoVariavel, id=custo_id, propriedade=propriedade)
    
    if request.method == 'POST':
        try:
            nome_custo = custo.nome_custo
            custo.delete()
            messages.success(request, f'Custo variável "{nome_custo}" excluído com sucesso!')
            return redirect('custos_variaveis_lista', propriedade_id=propriedade.id)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao excluir custo variável: {str(e)}', exc_info=True)
            messages.error(request, f'Erro ao excluir custo: {str(e)}')
            return redirect('custos_variaveis_lista', propriedade_id=propriedade.id)
    
    context = {
        'propriedade': propriedade,
        'custo': custo,
    }
    
    return render(request, 'gestao_rural/custos_variaveis_excluir.html', context)


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
