"""Views do novo módulo financeiro."""
from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required  # noqa: F401
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms_financeiro import (
    CategoriaFinanceiraForm,
    CentroCustoFinanceiroForm,
    ContaFinanceiraForm,
    LancamentoFinanceiroForm,
    ContaPagarForm,
    ContaReceberForm,
)
from .models import Propriedade
from .models_financeiro import (
    CategoriaFinanceira,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
)
from .services_financeiro import (
    PeriodoFinanceiro,
    analisar_tendencias_categoria,
    calcular_indicadores_financeiros,
    calcular_saldos_contas,
    calcular_totais_lancamentos,
    comparar_com_periodo_anterior,
    gerar_insights_financeiros,
    gerar_series_temporais,
    integrar_dados_compras,
    integrar_dados_pecuaria,
    listar_pendencias,
    periodo_mes_atual,
)


def _obter_propriedade(usuario, propriedade_id) -> Propriedade:
    """Garante que a propriedade pertence ao contexto do usuário."""
    return get_object_or_404(
        Propriedade.objects.select_related("produtor"),
        id=propriedade_id,
    )


@login_required
def financeiro_dashboard(request, propriedade_id):
    """Dashboard unificado de visão financeira."""

    propriedade = _obter_propriedade(request.user, propriedade_id)

    # Verificar se há parâmetros de período nos GET
    from django.utils.dateparse import parse_date
    
    inicio_str = request.GET.get('inicio')
    fim_str = request.GET.get('fim')
    
    if inicio_str and fim_str:
        try:
            inicio = parse_date(inicio_str)
            fim = parse_date(fim_str)
            if inicio and fim and inicio <= fim:
                periodo = PeriodoFinanceiro(inicio=inicio, fim=fim)
            else:
                periodo = periodo_mes_atual()
        except (ValueError, TypeError):
            periodo = periodo_mes_atual()
    else:
        periodo = periodo_mes_atual()
    resumo = calcular_totais_lancamentos(propriedade, periodo)
    pendencias = listar_pendencias(propriedade)
    saldos_contas = calcular_saldos_contas(propriedade)
    grafico_fluxo = gerar_series_temporais(propriedade, periodo)
    
    # Análises avançadas
    indicadores = calcular_indicadores_financeiros(propriedade, periodo)
    comparacao = comparar_com_periodo_anterior(propriedade, periodo)
    dados_pecuaria = integrar_dados_pecuaria(propriedade, periodo)
    dados_compras = integrar_dados_compras(propriedade, periodo)
    insights = gerar_insights_financeiros(propriedade, periodo)
    tendencias_categoria = analisar_tendencias_categoria(propriedade, periodo)

    # Dados para gráfico de pizza por centro de custo
    from django.db.models import Sum, Q, Count
    from .models_financeiro import CentroCusto
    
    lancamentos_periodo = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        data_competencia__range=periodo.range_lookup,
        status=LancamentoFinanceiro.STATUS_QUITADO,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
    )
    
    # Diagnosticar problema (para mensagem mais útil)
    total_despesas = lancamentos_periodo.count()
    despesas_sem_centro_custo = lancamentos_periodo.filter(centro_custo__isnull=True).count()
    total_centros_custo = CentroCusto.objects.filter(propriedade=propriedade, ativo=True).count()
    
    # Gráfico por centro de custo
    centros_custo_data = (
        lancamentos_periodo
        .filter(centro_custo__isnull=False)
        .values('centro_custo__nome', 'centro_custo__id')
        .annotate(total=Sum('valor'))
        .order_by('-total')[:10]
    )
    grafico_centro_custo = {
        'labels': [item['centro_custo__nome'] for item in centros_custo_data],
        'valores': [float(item['total']) for item in centros_custo_data],
        # Informações de diagnóstico
        'total_despesas': total_despesas,
        'despesas_sem_centro_custo': despesas_sem_centro_custo,
        'total_centros_custo': total_centros_custo,
    }
    
    # Dados para gráfico de pizza por fornecedor
    # Tentar relacionar através de NotaFiscal ou OrdemCompra
    try:
        from .models_compras_financeiro import Fornecedor, NotaFiscal, OrdemCompra
        
        # Buscar despesas que podem estar relacionadas a fornecedores
        # Através de NotaFiscal vinculada a lançamentos
        fornecedores_data = []
        
        # Buscar notas fiscais do período
        notas_periodo = NotaFiscal.objects.filter(
            propriedade=propriedade,
            data_emissao__range=periodo.range_lookup,
            tipo='ENTRADA'
        ).select_related('fornecedor')
        
        # Agrupar por fornecedor
        fornecedores_dict = {}
        for nota in notas_periodo:
            fornecedor_nome = nota.fornecedor.nome if nota.fornecedor else 'Sem Fornecedor'
            if fornecedor_nome not in fornecedores_dict:
                fornecedores_dict[fornecedor_nome] = 0
            fornecedores_dict[fornecedor_nome] += float(nota.valor_total or 0)
        
        # Se não houver dados de NF, tentar por OrdemCompra
        if not fornecedores_dict:
            ordens_periodo = OrdemCompra.objects.filter(
                propriedade=propriedade,
                data_emissao__range=periodo.range_lookup
            ).select_related('fornecedor')
            
            for ordem in ordens_periodo:
                fornecedor_nome = ordem.fornecedor.nome if ordem.fornecedor else 'Sem Fornecedor'
                if fornecedor_nome not in fornecedores_dict:
                    fornecedores_dict[fornecedor_nome] = 0
                fornecedores_dict[fornecedor_nome] += float(ordem.valor_total or 0)
        
        # Ordenar e limitar
        fornecedores_lista = sorted(
            fornecedores_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        grafico_fornecedor = {
            'labels': [item[0] for item in fornecedores_lista],
            'valores': [item[1] for item in fornecedores_lista],
        }
    except ImportError:
        # Se não houver módulo de compras, usar dados genéricos
        grafico_fornecedor = {
            'labels': [],
            'valores': [],
        }
    
    # Gráfico mensal (meses do período filtrado ou últimos 12 meses se período muito grande)
    from datetime import timedelta
    from calendar import monthrange
    
    meses_grafico = []
    receitas_mensais = []
    despesas_mensais = []
    
    # Calcular quantos meses há no período filtrado
    meses_no_periodo = (periodo.fim.year - periodo.inicio.year) * 12 + (periodo.fim.month - periodo.inicio.month) + 1
    
    # Se o período for maior que 12 meses, mostrar apenas os últimos 12 meses do período
    if meses_no_periodo > 12:
        # Começar 11 meses antes do fim do período
        mes_inicio_grafico = periodo.fim.replace(day=1) - timedelta(days=335)  # ~11 meses antes
        mes_inicio_grafico = mes_inicio_grafico.replace(day=1)
    else:
        # Usar o período completo
        mes_inicio_grafico = periodo.inicio.replace(day=1)
    
    # Iterar pelos meses do período
    mes_atual = mes_inicio_grafico
    meses_processados = 0
    max_meses = min(12, meses_no_periodo)
    
    while meses_processados < max_meses and mes_atual <= periodo.fim:
        ultimo_dia = monthrange(mes_atual.year, mes_atual.month)[1]
        mes_fim = date(mes_atual.year, mes_atual.month, ultimo_dia)
        
        # Garantir que não ultrapasse o fim do período
        if mes_fim > periodo.fim:
            mes_fim = periodo.fim
        
        lancamentos_mes = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia__range=(mes_atual, mes_fim),
            status=LancamentoFinanceiro.STATUS_QUITADO,
        )
        
        receitas = lancamentos_mes.filter(
            tipo=CategoriaFinanceira.TIPO_RECEITA
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        despesas = lancamentos_mes.filter(
            tipo=CategoriaFinanceira.TIPO_DESPESA
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        meses_grafico.append(mes_atual.strftime('%m/%Y'))
        receitas_mensais.append(float(receitas))
        despesas_mensais.append(float(despesas))
        
        # Avançar para o próximo mês
        if mes_atual.month == 12:
            mes_atual = date(mes_atual.year + 1, 1, 1)
        else:
            mes_atual = date(mes_atual.year, mes_atual.month + 1, 1)
        
        meses_processados += 1
    
    grafico_mensal = {
        'labels': meses_grafico,
        'receitas': receitas_mensais,
        'despesas': despesas_mensais,
    }

    context = {
        "propriedade": propriedade,
        "periodo": periodo,
        "resumo": resumo,
        "pendencias": pendencias,
        "saldos_contas": saldos_contas,
        "grafico_fluxo": grafico_fluxo,
        "grafico_centro_custo": grafico_centro_custo,
        "grafico_fornecedor": grafico_fornecedor,
        "grafico_mensal": grafico_mensal,
        "indicadores": indicadores,
        "comparacao": comparacao,
        "dados_pecuaria": dados_pecuaria,
        "dados_pecuaria_disponivel": dados_pecuaria.get("modulo_disponivel", False),
        "dados_compras": dados_compras,
        "dados_compras_disponivel": dados_compras.get("modulo_disponivel", False),
        "insights": insights,
        "tendencias_categoria": tendencias_categoria,
        "url_lancamentos": reverse(
            "financeiro_lancamentos",
            args=[propriedade.id],
        ),
        "url_categorias": reverse(
            "financeiro_categorias",
            args=[propriedade.id],
        ),
        "url_contas": reverse(
            "financeiro_contas",
            args=[propriedade.id],
        ),
    }

    return render(request, "gestao_rural/financeiro/dashboard.html", context)


@login_required
def lancamentos_lista(request, propriedade_id):
    """Lista filtrada de lançamentos financeiros."""

    propriedade = _obter_propriedade(request.user, propriedade_id)
    status = request.GET.get("status")
    tipo = request.GET.get("tipo")

    lancamentos = LancamentoFinanceiro.objects.filter(propriedade=propriedade)

    if status:
        lancamentos = lancamentos.filter(status=status)
    if tipo:
        lancamentos = lancamentos.filter(tipo=tipo)

    lancamentos = lancamentos.select_related(
        "categoria",
        "centro_custo",
        "conta_origem",
        "conta_destino",
    ).order_by("-data_competencia", "-id")

    context = {
        "propriedade": propriedade,
        "lancamentos": lancamentos,
        "status": status,
        "tipo": tipo,
        "url_novo": reverse("financeiro_lancamento_novo", args=[propriedade.id]),
    }

    return render(request, "gestao_rural/financeiro/lancamentos_lista.html", context)


@login_required
def lancamento_novo(request, propriedade_id):
    """Cria um novo lançamento financeiro."""

    propriedade = _obter_propriedade(request.user, propriedade_id)

    if request.method == "POST":
        form = LancamentoFinanceiroForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.propriedade = propriedade
            try:
                with transaction.atomic():
                    lancamento.save()
            except Exception as exc:
                messages.error(request, f"Erro ao salvar lançamento: {exc}")
            else:
                messages.success(request, "Lançamento registrado com sucesso.")
                return redirect("financeiro_lancamentos", propriedade_id=propriedade.id)
    else:
        form = LancamentoFinanceiroForm(
            propriedade=propriedade,
            initial={
                "propriedade": propriedade,
                "status": LancamentoFinanceiro.STATUS_PENDENTE,
                "data_competencia": datetime.today().date(),
                "data_vencimento": datetime.today().date(),
            },
        )
    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Novo Lançamento",
    }

    return render(request, "gestao_rural/financeiro/lancamento_form.html", context)


@login_required
def lancamento_editar(request, propriedade_id, lancamento_id):
    """Edição de lançamento existente."""

    propriedade = _obter_propriedade(request.user, propriedade_id)
    lancamento = get_object_or_404(
        LancamentoFinanceiro,
        id=lancamento_id,
        propriedade=propriedade,
    )

    if request.method == "POST":
        form = LancamentoFinanceiroForm(
            request.POST,
            instance=lancamento,
            propriedade=propriedade,
        )
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
            except Exception as exc:
                messages.error(request, f"Erro ao atualizar lançamento: {exc}")
            else:
                messages.success(request, "Lançamento atualizado com sucesso.")
                return redirect("financeiro_lancamentos", propriedade_id=propriedade.id)
    else:
        form = LancamentoFinanceiroForm(
            instance=lancamento,
            propriedade=propriedade,
        )

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Editar Lançamento",
    }

    return render(request, "gestao_rural/financeiro/lancamento_form.html", context)


@login_required
def lancamento_quitar(request, propriedade_id, lancamento_id):
    """Marca um lançamento como quitado."""

    propriedade = _obter_propriedade(request.user, propriedade_id)
    lancamento = get_object_or_404(
        LancamentoFinanceiro,
        id=lancamento_id,
        propriedade=propriedade,
    )

    if request.method == "POST":
        data_quitacao = request.POST.get("data_quitacao")
        try:
            lancamento.marcar_como_quitado(
                data=datetime.strptime(data_quitacao, "%Y-%m-%d").date()
                if data_quitacao
                else None
            )
        except Exception as exc:
            messages.error(request, f"Não foi possível quitar: {exc}")
        else:
            messages.success(request, "Lançamento quitado com sucesso.")
        return redirect("financeiro_lancamentos", propriedade_id=propriedade.id)

    context = {
        "propriedade": propriedade,
        "lancamento": lancamento,
    }
    return render(request, "gestao_rural/financeiro/lancamento_quitar.html", context)


@login_required
def lancamento_cancelar(request, propriedade_id, lancamento_id):
    """Cancela um lançamento."""

    propriedade = _obter_propriedade(request.user, propriedade_id)
    lancamento = get_object_or_404(
        LancamentoFinanceiro,
        id=lancamento_id,
        propriedade=propriedade,
    )

    if request.method == "POST":
        motivo = request.POST.get("motivo")
        lancamento.cancelar(motivo=motivo)
        messages.success(request, "Lançamento cancelado.")
        return redirect("financeiro_lancamentos", propriedade_id=propriedade.id)

    context = {
        "propriedade": propriedade,
        "lancamento": lancamento,
    }
    return render(request, "gestao_rural/financeiro/lancamento_cancelar.html", context)


@login_required
def contas_financeiras_lista(request, propriedade_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)
    contas = ContaFinanceira.objects.filter(propriedade=propriedade).order_by("nome")
    context = {
        "propriedade": propriedade,
        "contas": contas,
        "url_novo": reverse("financeiro_conta_nova", args=[propriedade.id]),
    }
    return render(request, "gestao_rural/financeiro/contas_lista.html", context)


@login_required
def conta_financeira_nova(request, propriedade_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)

    if request.method == "POST":
        form = ContaFinanceiraForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.propriedade = propriedade
            conta.save()
            messages.success(request, "Conta criada com sucesso.")
            return redirect("financeiro_contas", propriedade_id=propriedade.id)
    else:
        form = ContaFinanceiraForm(initial={"propriedade": propriedade})

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Nova Conta Financeira",
    }
    return render(request, "gestao_rural/financeiro/conta_form.html", context)


@login_required
def conta_financeira_editar(request, propriedade_id, conta_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)
    conta = get_object_or_404(
        ContaFinanceira,
        id=conta_id,
        propriedade=propriedade,
    )

    if request.method == "POST":
        form = ContaFinanceiraForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta atualizada com sucesso.")
            return redirect("financeiro_contas", propriedade_id=propriedade.id)
    else:
        form = ContaFinanceiraForm(instance=conta)

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Editar Conta Financeira",
    }
    return render(request, "gestao_rural/financeiro/conta_form.html", context)


@login_required
def categorias_lista(request, propriedade_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)
    categorias = CategoriaFinanceira.objects.filter(
        Q(propriedade__isnull=True) | Q(propriedade=propriedade)
    ).order_by("tipo", "nome")
    context = {
        "propriedade": propriedade,
        "categorias": categorias,
        "url_novo": reverse("financeiro_categoria_nova", args=[propriedade.id]),
    }
    return render(request, "gestao_rural/financeiro/categorias_lista.html", context)


@login_required
def categoria_nova(request, propriedade_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)

    if request.method == "POST":
        form = CategoriaFinanceiraForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.propriedade = propriedade
            categoria.save()
            messages.success(request, "Categoria criada com sucesso.")
            return redirect("financeiro_categorias", propriedade_id=propriedade.id)
    else:
        form = CategoriaFinanceiraForm(
            propriedade=propriedade,
            initial={"propriedade": propriedade},
        )

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Nova Categoria Financeira",
    }
    return render(
        request,
        "gestao_rural/financeiro/categoria_form.html",
        context,
    )


@login_required
def categoria_editar(request, propriedade_id, categoria_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)
    categoria = get_object_or_404(
        CategoriaFinanceira,
        id=categoria_id,
        propriedade=propriedade,
    )

    if request.method == "POST":
        form = CategoriaFinanceiraForm(
            request.POST,
            instance=categoria,
            propriedade=propriedade,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada com sucesso.")
            return redirect("financeiro_categorias", propriedade_id=propriedade.id)
    else:
        form = CategoriaFinanceiraForm(
            instance=categoria,
            propriedade=propriedade,
        )

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Editar Categoria Financeira",
    }
    return render(
        request,
        "gestao_rural/financeiro/categoria_form.html",
        context,
    )


@login_required
def centros_custo_lista(request, propriedade_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)
    centros = CentroCustoFinanceiro.objects.filter(
        propriedade=propriedade,
    ).order_by("nome")
    context = {
        "propriedade": propriedade,
        "centros": centros,
        "url_novo": reverse("financeiro_centro_custo_novo", args=[propriedade.id]),
    }
    return render(request, "gestao_rural/financeiro/centros_custo_lista.html", context)


@login_required
def centro_custo_novo(request, propriedade_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)

    if request.method == "POST":
        form = CentroCustoFinanceiroForm(request.POST)
        if form.is_valid():
            centro = form.save(commit=False)
            centro.propriedade = propriedade
            centro.save()
            messages.success(request, "Centro de custo criado com sucesso.")
            return redirect("financeiro_centros_custo", propriedade_id=propriedade.id)
    else:
        form = CentroCustoFinanceiroForm(initial={"propriedade": propriedade})

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Novo Centro de Custo",
    }
    return render(
        request,
        "gestao_rural/financeiro/centro_custo_form.html",
        context,
    )


@login_required
def centro_custo_editar(request, propriedade_id, centro_id):
    propriedade = _obter_propriedade(request.user, propriedade_id)
    centro = get_object_or_404(
        CentroCustoFinanceiro,
        id=centro_id,
        propriedade=propriedade,
    )

    if request.method == "POST":
        form = CentroCustoFinanceiroForm(request.POST, instance=centro)
        if form.is_valid():
            form.save()
            messages.success(request, "Centro de custo atualizado com sucesso.")
            return redirect("financeiro_centros_custo", propriedade_id=propriedade.id)
    else:
        form = CentroCustoFinanceiroForm(instance=centro)

    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Editar Centro de Custo",
    }
    return render(
        request,
        "gestao_rural/financeiro/centro_custo_form.html",
        context,
    )


# ============================================================================
# CONTAS A PAGAR
# ============================================================================

@login_required
def contas_pagar_lista(request, propriedade_id):
    """Lista de contas a pagar."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    status = request.GET.get("status")
    
    from .models_compras_financeiro import ContaPagar
    
    contas = ContaPagar.objects.filter(propriedade=propriedade)
    
    if status:
        contas = contas.filter(status=status)
    
    contas = contas.select_related("fornecedor", "ordem_compra", "nota_fiscal").order_by(
        "-data_vencimento", "-id"
    )
    
    # Resumo
    total_pendente = contas.filter(status="PENDENTE").aggregate(
        total=Sum("valor")
    )["total"] or 0
    total_vencido = contas.filter(status="VENCIDA").aggregate(
        total=Sum("valor")
    )["total"] or 0
    total_pago = contas.filter(status="PAGA").aggregate(
        total=Sum("valor")
    )["total"] or 0
    
    context = {
        "propriedade": propriedade,
        "contas": contas,
        "status": status,
        "total_pendente": total_pendente,
        "total_vencido": total_vencido,
        "total_pago": total_pago,
        "url_novo": reverse("financeiro_conta_pagar_nova", args=[propriedade.id]),
    }
    
    return render(request, "gestao_rural/financeiro/contas_pagar_lista.html", context)


@login_required
def conta_pagar_nova(request, propriedade_id):
    """Cria uma nova conta a pagar."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    if request.method == "POST":
        form = ContaPagarForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.propriedade = propriedade
            conta.save()
            messages.success(request, "Conta a pagar registrada com sucesso.")
            return redirect("financeiro_contas_pagar", propriedade_id=propriedade.id)
    else:
        form = ContaPagarForm(
            propriedade=propriedade,
            initial={
                "propriedade": propriedade,
                "status": "PENDENTE",
                "data_vencimento": datetime.today().date(),
            },
        )
    
    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Nova Conta a Pagar",
    }
    
    return render(request, "gestao_rural/financeiro/conta_pagar_form.html", context)


@login_required
def conta_pagar_editar(request, propriedade_id, conta_id):
    """Edita uma conta a pagar existente."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_compras_financeiro import ContaPagar
    conta = get_object_or_404(ContaPagar, id=conta_id, propriedade=propriedade)
    
    if request.method == "POST":
        form = ContaPagarForm(request.POST, instance=conta, propriedade=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta a pagar atualizada com sucesso.")
            return redirect("financeiro_contas_pagar", propriedade_id=propriedade.id)
    else:
        form = ContaPagarForm(instance=conta, propriedade=propriedade)
    
    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Editar Conta a Pagar",
        "conta": conta,
    }
    
    return render(request, "gestao_rural/financeiro/conta_pagar_form.html", context)


@login_required
def conta_pagar_pagar(request, propriedade_id, conta_id):
    """Marca uma conta a pagar como paga."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_compras_financeiro import ContaPagar
    conta = get_object_or_404(ContaPagar, id=conta_id, propriedade=propriedade)
    
    if request.method == "POST":
        data_pagamento = request.POST.get("data_pagamento")
        try:
            conta.data_pagamento = (
                datetime.strptime(data_pagamento, "%Y-%m-%d").date()
                if data_pagamento
                else timezone.localdate()
            )
            conta.status = "PAGA"
            conta.save()
            messages.success(request, "Conta a pagar marcada como paga.")
        except Exception as exc:
            messages.error(request, f"Erro ao processar pagamento: {exc}")
        return redirect("financeiro_contas_pagar", propriedade_id=propriedade.id)
    
    context = {
        "propriedade": propriedade,
        "conta": conta,
    }
    
    return render(request, "gestao_rural/financeiro/conta_pagar_pagar.html", context)


# ============================================================================
# CONTAS A RECEBER
# ============================================================================

@login_required
def contas_receber_lista(request, propriedade_id):
    """Lista de contas a receber."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    status = request.GET.get("status")
    
    from .models_compras_financeiro import ContaReceber
    
    contas = ContaReceber.objects.filter(propriedade=propriedade)
    
    if status:
        contas = contas.filter(status=status)
    
    contas = contas.order_by("-data_vencimento", "-id")
    
    # Resumo
    total_pendente = contas.filter(status="PENDENTE").aggregate(
        total=Sum("valor")
    )["total"] or 0
    total_vencido = contas.filter(status="VENCIDA").aggregate(
        total=Sum("valor")
    )["total"] or 0
    total_recebido = contas.filter(status="RECEBIDA").aggregate(
        total=Sum("valor")
    )["total"] or 0
    
    context = {
        "propriedade": propriedade,
        "contas": contas,
        "status": status,
        "total_pendente": total_pendente,
        "total_vencido": total_vencido,
        "total_recebido": total_recebido,
        "url_novo": reverse("financeiro_conta_receber_nova", args=[propriedade.id]),
    }
    
    return render(request, "gestao_rural/financeiro/contas_receber_lista.html", context)


@login_required
def conta_receber_nova(request, propriedade_id):
    """Cria uma nova conta a receber."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    if request.method == "POST":
        form = ContaReceberForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.propriedade = propriedade
            conta.save()
            messages.success(request, "Conta a receber registrada com sucesso.")
            return redirect("financeiro_contas_receber", propriedade_id=propriedade.id)
    else:
        form = ContaReceberForm(
            propriedade=propriedade,
            initial={
                "propriedade": propriedade,
                "status": "PENDENTE",
                "data_vencimento": datetime.today().date(),
            },
        )
    
    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Nova Conta a Receber",
    }
    
    return render(request, "gestao_rural/financeiro/conta_receber_form.html", context)


@login_required
def conta_receber_editar(request, propriedade_id, conta_id):
    """Edita uma conta a receber existente."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_compras_financeiro import ContaReceber
    conta = get_object_or_404(ContaReceber, id=conta_id, propriedade=propriedade)
    
    if request.method == "POST":
        form = ContaReceberForm(request.POST, instance=conta, propriedade=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta a receber atualizada com sucesso.")
            return redirect("financeiro_contas_receber", propriedade_id=propriedade.id)
    else:
        form = ContaReceberForm(instance=conta, propriedade=propriedade)
    
    context = {
        "propriedade": propriedade,
        "form": form,
        "titulo": "Editar Conta a Receber",
        "conta": conta,
    }
    
    return render(request, "gestao_rural/financeiro/conta_receber_form.html", context)


@login_required
def conta_receber_receber(request, propriedade_id, conta_id):
    """Marca uma conta a receber como recebida."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_compras_financeiro import ContaReceber
    conta = get_object_or_404(ContaReceber, id=conta_id, propriedade=propriedade)
    
    if request.method == "POST":
        data_recebimento = request.POST.get("data_recebimento")
        try:
            conta.data_recebimento = (
                datetime.strptime(data_recebimento, "%Y-%m-%d").date()
                if data_recebimento
                else timezone.localdate()
            )
            conta.status = "RECEBIDA"
            conta.save()
            messages.success(request, "Conta a receber marcada como recebida.")
        except Exception as exc:
            messages.error(request, f"Erro ao processar recebimento: {exc}")
        return redirect("financeiro_contas_receber", propriedade_id=propriedade.id)
    
    context = {
        "propriedade": propriedade,
        "conta": conta,
    }
    
    return render(request, "gestao_rural/financeiro/conta_receber_receber.html", context)


# ========== GESTÃO DE DESPESAS E RECEITAS ANUAIS ==========

@login_required
def despesas_grupos_lista(request, propriedade_id):
    """Lista grupos de despesas."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import GrupoDespesa
    
    grupos = GrupoDespesa.objects.filter(propriedade=propriedade).order_by('ordem', 'nome')
    
    context = {
        "propriedade": propriedade,
        "grupos": grupos,
    }
    
    return render(request, "gestao_rural/financeiro/despesas_grupos_lista.html", context)


@login_required
def despesas_grupo_novo(request, propriedade_id):
    """Cria novo grupo de despesas."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import GrupoDespesa
    from django import forms
    
    class GrupoDespesaForm(forms.ModelForm):
        class Meta:
            model = GrupoDespesa
            fields = ['nome', 'tipo', 'descricao', 'ordem', 'ativo']
            widgets = {
                'descricao': forms.Textarea(attrs={'rows': 3}),
            }
    
    if request.method == 'POST':
        form = GrupoDespesaForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.propriedade = propriedade
            grupo.save()
            messages.success(request, f"Grupo '{grupo.nome}' criado com sucesso!")
            return redirect('financeiro_despesas_grupos', propriedade_id=propriedade_id)
    else:
        form = GrupoDespesaForm()
    
    context = {
        "propriedade": propriedade,
        "form": form,
    }
    
    return render(request, "gestao_rural/financeiro/despesas_grupo_form.html", context)


@login_required
def despesas_grupo_editar(request, propriedade_id, grupo_id):
    """Edita grupo de despesas."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import GrupoDespesa
    from django import forms
    
    grupo = get_object_or_404(GrupoDespesa, id=grupo_id, propriedade=propriedade)
    
    class GrupoDespesaForm(forms.ModelForm):
        class Meta:
            model = GrupoDespesa
            fields = ['nome', 'tipo', 'descricao', 'ordem', 'ativo']
            widgets = {
                'descricao': forms.Textarea(attrs={'rows': 3}),
            }
    
    if request.method == 'POST':
        form = GrupoDespesaForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Grupo '{grupo.nome}' atualizado com sucesso!")
            return redirect('financeiro_despesas_grupos', propriedade_id=propriedade_id)
    else:
        form = GrupoDespesaForm(instance=grupo)
    
    context = {
        "propriedade": propriedade,
        "grupo": grupo,
        "form": form,
    }
    
    return render(request, "gestao_rural/financeiro/despesas_grupo_form.html", context)


@login_required
def despesas_configuradas_lista(request, propriedade_id):
    """Lista despesas configuradas com cálculos automáticos."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import DespesaConfigurada, GrupoDespesa, ReceitaAnual
    from decimal import Decimal
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Buscar receita do ano
    receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
    receita_anual = receita_anual_obj.valor_receita if receita_anual_obj else Decimal("0.00")
    
    # Buscar despesas agrupadas por grupo
    grupos = GrupoDespesa.objects.filter(propriedade=propriedade, ativo=True).order_by('ordem', 'nome')
    despesas_por_grupo = {}
    
    for grupo in grupos:
        despesas = DespesaConfigurada.objects.filter(
            propriedade=propriedade,
            grupo=grupo,
            ativo=True
        ).order_by('ordem', 'nome')
        
        total_grupo = Decimal("0.00")
        despesas_com_valores = []
        for despesa in despesas:
            valor_anual = despesa.calcular_valor_anual(receita_anual)
            valor_mensal = despesa.calcular_valor_mensal(receita_anual)
            total_grupo += valor_anual
            despesas_com_valores.append({
                'despesa': despesa,
                'valor_anual': valor_anual,
                'valor_mensal': valor_mensal,
            })
        
        if despesas.exists():
            despesas_por_grupo[grupo] = {
                'despesas': despesas_com_valores,
                'total': total_grupo,
            }
    
    # Calcular totais
    total_despesas = sum(d['total'] for d in despesas_por_grupo.values())
    resultado_caixa = receita_anual - total_despesas
    
    # Anos disponíveis
    anos = ReceitaAnual.objects.filter(propriedade=propriedade).values_list('ano', flat=True).distinct().order_by('-ano')
    
    context = {
        "propriedade": propriedade,
        "ano": ano,
        "receita_anual": receita_anual,
        "receita_anual_obj": receita_anual_obj,
        "despesas_por_grupo": despesas_por_grupo,
        "total_despesas": total_despesas,
        "resultado_caixa": resultado_caixa,
        "anos": anos,
    }
    
    return render(request, "gestao_rural/financeiro/despesas_configuradas_lista.html", context)


@login_required
def despesa_configurada_nova(request, propriedade_id):
    """Cria nova despesa configurada."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import DespesaConfigurada, GrupoDespesa, CategoriaFinanceira
    from django import forms
    
    class DespesaConfiguradaForm(forms.ModelForm):
        class Meta:
            model = DespesaConfigurada
            fields = ['grupo', 'categoria_financeira', 'nome', 'descricao', 'tipo_calculo', 
                     'porcentagem_receita', 'valor_fixo', 'ordem', 'ativo']
            widgets = {
                'descricao': forms.Textarea(attrs={'rows': 3}),
                'grupo': forms.Select(attrs={'class': 'form-select'}),
                'categoria_financeira': forms.Select(attrs={'class': 'form-select'}),
            }
        
        def __init__(self, *args, **kwargs):
            propriedade = kwargs.pop('propriedade', None)
            super().__init__(*args, **kwargs)
            if propriedade:
                self.fields['grupo'].queryset = GrupoDespesa.objects.filter(propriedade=propriedade, ativo=True)
                self.fields['categoria_financeira'].queryset = CategoriaFinanceira.objects.filter(
                    propriedade=propriedade,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    ativa=True
                )
    
    if request.method == 'POST':
        form = DespesaConfiguradaForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            despesa = form.save(commit=False)
            despesa.propriedade = propriedade
            despesa.save()
            messages.success(request, f"Despesa '{despesa.nome}' criada com sucesso!")
            return redirect('financeiro_despesas_configuradas', propriedade_id=propriedade_id)
    else:
        form = DespesaConfiguradaForm(propriedade=propriedade)
    
    context = {
        "propriedade": propriedade,
        "form": form,
    }
    
    return render(request, "gestao_rural/financeiro/despesa_configurada_form.html", context)


@login_required
def despesa_configurada_editar(request, propriedade_id, despesa_id):
    """Edita despesa configurada."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import DespesaConfigurada, GrupoDespesa, CategoriaFinanceira
    from django import forms
    
    despesa = get_object_or_404(DespesaConfigurada, id=despesa_id, propriedade=propriedade)
    
    class DespesaConfiguradaForm(forms.ModelForm):
        class Meta:
            model = DespesaConfigurada
            fields = ['grupo', 'categoria_financeira', 'nome', 'descricao', 'tipo_calculo', 
                     'porcentagem_receita', 'valor_fixo', 'ordem', 'ativo']
            widgets = {
                'descricao': forms.Textarea(attrs={'rows': 3}),
            }
        
        def __init__(self, *args, **kwargs):
            propriedade = kwargs.pop('propriedade', None)
            super().__init__(*args, **kwargs)
            if propriedade:
                self.fields['grupo'].queryset = GrupoDespesa.objects.filter(propriedade=propriedade, ativo=True)
                self.fields['categoria_financeira'].queryset = CategoriaFinanceira.objects.filter(
                    propriedade=propriedade,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    ativa=True
                )
    
    if request.method == 'POST':
        form = DespesaConfiguradaForm(request.POST, instance=despesa, propriedade=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, f"Despesa '{despesa.nome}' atualizada com sucesso!")
            return redirect('financeiro_despesas_configuradas', propriedade_id=propriedade_id)
    else:
        form = DespesaConfiguradaForm(instance=despesa, propriedade=propriedade)
    
    context = {
        "propriedade": propriedade,
        "despesa": despesa,
        "form": form,
    }
    
    return render(request, "gestao_rural/financeiro/despesa_configurada_form.html", context)


@login_required
def receitas_anuais_lista(request, propriedade_id):
    """Lista receitas anuais."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import ReceitaAnual
    
    receitas = ReceitaAnual.objects.filter(propriedade=propriedade).order_by('-ano')
    
    context = {
        "propriedade": propriedade,
        "receitas": receitas,
    }
    
    return render(request, "gestao_rural/financeiro/receitas_anuais_lista.html", context)


@login_required
def receita_anual_nova(request, propriedade_id):
    """Cria nova receita anual."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import ReceitaAnual
    from django import forms
    
    class ReceitaAnualForm(forms.ModelForm):
        class Meta:
            model = ReceitaAnual
            fields = [
                'ano', 'valor_receita', 
                'icms_vendas', 'funviral_vendas', 'outros_impostos_vendas',
                'devolucoes_vendas', 'abatimentos_vendas',
                'custo_produtos_vendidos',
                'depreciacao_amortizacao',
                # Despesas Operacionais Detalhadas
                'retirada_labore', 'assistencia_contabil', 'encargos_inss',
                'taxas_diversas', 'despesas_administrativas', 'material_uso_consumo',
                'despesas_comunicacao', 'despesas_viagens', 'despesas_energia_eletrica',
                'despesas_transportes', 'despesas_combustivel', 'despesas_manutencao',
                # Resultado Financeiro
                'despesas_financeiras', 'receitas_financeiras',
                # Impostos
                'csll', 'irpj',
                'descricao'
            ]
            widgets = {
                'descricao': forms.Textarea(attrs={'rows': 3}),
                'ano': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
            }
            labels = {
                'valor_receita': 'Receita Bruta (R$)',
                'icms_vendas': 'ICMS sobre Vendas (R$)',
                'funviral_vendas': 'Funviral sobre Vendas (R$)',
                'outros_impostos_vendas': 'Outros Impostos sobre Vendas (R$)',
                'devolucoes_vendas': 'Devoluções de Vendas (R$)',
                'abatimentos_vendas': 'Abatimentos sobre Vendas (R$)',
                'custo_produtos_vendidos': 'Custo dos Produtos Vendidos - CPV (R$)',
                'depreciacao_amortizacao': 'Depreciação e Amortização (R$)',
                'despesas_financeiras': 'Despesas Financeiras (R$)',
                'receitas_financeiras': 'Receitas Financeiras (R$)',
                'csll': 'Contribuição Social sobre Lucro Líquido - CSLL (R$)',
                'irpj': 'Imposto de Renda Pessoa Jurídica - IRPJ (R$)',
            }
    
    if request.method == 'POST':
        form = ReceitaAnualForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.propriedade = propriedade
            receita.save()
            messages.success(request, f"Receita anual de {receita.ano} criada com sucesso!")
            return redirect('financeiro_receitas_anuais', propriedade_id=propriedade_id)
    else:
        ano_inicial = request.GET.get('ano', timezone.now().year)
        form = ReceitaAnualForm(initial={'ano': ano_inicial})
    
    context = {
        "propriedade": propriedade,
        "form": form,
    }
    
    return render(request, "gestao_rural/financeiro/receita_anual_form.html", context)


@login_required
def receita_anual_editar(request, propriedade_id, receita_id):
    """Edita receita anual."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import ReceitaAnual
    from django import forms
    from .services_calculo_dre import calcular_dre_automatico
    
    receita = get_object_or_404(ReceitaAnual, id=receita_id, propriedade=propriedade)
    
    # Se solicitado, preencher automaticamente com base nos lançamentos
    if request.GET.get('preencher_automatico') == '1':
        valores = calcular_dre_automatico(propriedade, receita.ano)
        
        # Contar quantos campos foram preenchidos
        campos_preenchidos = 0
        
        # Preencher apenas campos que estão zerados
        if receita.icms_vendas == 0 and valores['icms_vendas'] > 0:
            receita.icms_vendas = valores['icms_vendas']
            campos_preenchidos += 1
        if receita.funviral_vendas == 0:
            receita.funviral_vendas = valores['funviral_vendas']
            if valores['funviral_vendas'] > 0:
                campos_preenchidos += 1
        if receita.outros_impostos_vendas == 0 and valores['outros_impostos_vendas'] > 0:
            receita.outros_impostos_vendas = valores['outros_impostos_vendas']
            campos_preenchidos += 1
        if receita.devolucoes_vendas == 0 and valores['devolucoes_vendas'] > 0:
            receita.devolucoes_vendas = valores['devolucoes_vendas']
            campos_preenchidos += 1
        if receita.abatimentos_vendas == 0 and valores['abatimentos_vendas'] > 0:
            receita.abatimentos_vendas = valores['abatimentos_vendas']
            campos_preenchidos += 1
        if receita.custo_produtos_vendidos == 0 and valores['custo_produtos_vendidos'] > 0:
            receita.custo_produtos_vendidos = valores['custo_produtos_vendidos']
            campos_preenchidos += 1
        if receita.depreciacao_amortizacao == 0 and valores['depreciacao_amortizacao'] > 0:
            receita.depreciacao_amortizacao = valores['depreciacao_amortizacao']
            campos_preenchidos += 1
        if receita.despesas_financeiras == 0 and valores['despesas_financeiras'] > 0:
            receita.despesas_financeiras = valores['despesas_financeiras']
            campos_preenchidos += 1
        if receita.receitas_financeiras == 0 and valores['receitas_financeiras'] > 0:
            receita.receitas_financeiras = valores['receitas_financeiras']
            campos_preenchidos += 1
        if receita.csll == 0 and valores['csll'] > 0:
            receita.csll = valores['csll']
            campos_preenchidos += 1
        if receita.irpj == 0 and valores['irpj'] > 0:
            receita.irpj = valores['irpj']
            campos_preenchidos += 1
        
        receita.save()
        
        # Buscar informações sobre os lançamentos para mensagem mais informativa
        from .models_financeiro import LancamentoFinanceiro, CategoriaFinanceira
        from django.db.models import Sum
        from decimal import Decimal
        total_despesas = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia__year=receita.ano,
            status=LancamentoFinanceiro.STATUS_QUITADO,
            tipo=CategoriaFinanceira.TIPO_DESPESA
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        if campos_preenchidos > 0:
            messages.success(
                request, 
                f"DRE preenchido automaticamente! {campos_preenchidos} campo(s) preenchido(s). "
                f"CPV: R$ {valores['custo_produtos_vendidos']:,.2f} | "
                f"Total de despesas encontradas: R$ {total_despesas:,.2f}"
            )
        else:
            if total_despesas > 0:
                messages.warning(
                    request,
                    f"Nenhum campo foi preenchido automaticamente, mas foram encontradas despesas no valor de R$ {total_despesas:,.2f}. "
                    f"Verifique se os campos já estão preenchidos ou se há algum problema na identificação dos lançamentos."
                )
            else:
                messages.info(
                    request,
                    f"Nenhum lançamento financeiro quitado encontrado para o ano {receita.ano}. "
                    f"Cadastre os lançamentos financeiros primeiro."
                )
    
    class ReceitaAnualForm(forms.ModelForm):
        class Meta:
            model = ReceitaAnual
            fields = [
                'ano', 'valor_receita', 
                'icms_vendas', 'funviral_vendas', 'outros_impostos_vendas',
                'devolucoes_vendas', 'abatimentos_vendas',
                'custo_produtos_vendidos',
                'depreciacao_amortizacao',
                # Despesas Operacionais Detalhadas
                'retirada_labore', 'assistencia_contabil', 'encargos_inss',
                'taxas_diversas', 'despesas_administrativas', 'material_uso_consumo',
                'despesas_comunicacao', 'despesas_viagens', 'despesas_energia_eletrica',
                'despesas_transportes', 'despesas_combustivel', 'despesas_manutencao',
                # Resultado Financeiro
                'despesas_financeiras', 'receitas_financeiras',
                # Impostos
                'csll', 'irpj',
                'descricao'
            ]
            widgets = {
                'descricao': forms.Textarea(attrs={'rows': 3}),
                'ano': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
            }
            labels = {
                'valor_receita': 'Receita Bruta (R$)',
                'icms_vendas': 'ICMS sobre Vendas (R$)',
                'funviral_vendas': 'Funviral sobre Vendas (R$)',
                'outros_impostos_vendas': 'Outros Impostos sobre Vendas (R$)',
                'devolucoes_vendas': 'Devoluções de Vendas (R$)',
                'abatimentos_vendas': 'Abatimentos sobre Vendas (R$)',
                'custo_produtos_vendidos': 'Custo dos Produtos Vendidos - CPV (R$)',
                'depreciacao_amortizacao': 'Depreciação e Amortização (R$)',
                'despesas_financeiras': 'Despesas Financeiras (R$)',
                'receitas_financeiras': 'Receitas Financeiras (R$)',
                'csll': 'Contribuição Social sobre Lucro Líquido - CSLL (R$)',
                'irpj': 'Imposto de Renda Pessoa Jurídica - IRPJ (R$)',
            }
    
    if request.method == 'POST':
        form = ReceitaAnualForm(request.POST, instance=receita)
        if form.is_valid():
            form.save()
            messages.success(request, f"Receita anual de {receita.ano} atualizada com sucesso!")
            return redirect('financeiro_receitas_anuais', propriedade_id=propriedade_id)
    else:
        form = ReceitaAnualForm(instance=receita)
    
    context = {
        "propriedade": propriedade,
        "receita": receita,
        "form": form,
    }
    
    return render(request, "gestao_rural/financeiro/receita_anual_form.html", context)


@login_required
def relatorio_fluxo_caixa(request, propriedade_id):
    """Relatório de Fluxo de Caixa anual."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import ReceitaAnual, DespesaConfigurada, GrupoDespesa
    from decimal import Decimal
    from collections import defaultdict
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
    if not receita_anual_obj:
        messages.warning(request, f"Não há receita cadastrada para o ano {ano}. Cadastre primeiro a receita anual.")
        return redirect('financeiro_receitas_anuais', propriedade_id=propriedade_id)
    
    receita_anual = receita_anual_obj.valor_receita
    
    # Calcular despesas por mês
    despesas = DespesaConfigurada.objects.filter(propriedade=propriedade, ativo=True)
    fluxo_mensal = []
    
    # Nomes dos meses em português
    nomes_meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    for mes in range(1, 13):
        total_mes = Decimal("0.00")
        despesas_mes = []
        
        for despesa in despesas:
            valor_mensal = despesa.calcular_valor_mensal(receita_anual)
            total_mes += valor_mensal
            despesas_mes.append({
                'nome': despesa.nome,
                'grupo': despesa.grupo.nome,
                'valor': valor_mensal,
            })
        
        receita_mensal = receita_anual / Decimal("12")
        saldo_mes = receita_mensal - total_mes
        
        fluxo_mensal.append({
            'mes': mes,
            'nome_mes': nomes_meses[mes - 1],
            'receita': receita_mensal,
            'despesas': despesas_mes,
            'total_despesas': total_mes,
            'saldo': saldo_mes,
        })
    
    # Calcular saldo acumulado para cada mês
    saldo_acumulado = Decimal("0.00")
    for item in fluxo_mensal:
        saldo_acumulado += item['saldo']
        item['saldo_acumulado'] = saldo_acumulado
    
    # Totais anuais
    total_receita_anual = receita_anual
    total_despesas_anual = sum(item['total_despesas'] for item in fluxo_mensal)
    saldo_anual = total_receita_anual - total_despesas_anual
    
    # Anos disponíveis (com receitas cadastradas)
    anos_disponiveis = ReceitaAnual.objects.filter(
        propriedade=propriedade
    ).values_list('ano', flat=True).distinct().order_by('-ano')
    
    # Se não houver anos, usar o ano atual e alguns anos próximos
    if not anos_disponiveis.exists():
        anos_disponiveis = list(range(ano - 2, ano + 4))
    
    context = {
        "propriedade": propriedade,
        "ano": ano,
        "receita_anual": receita_anual,
        "fluxo_mensal": fluxo_mensal,
        "total_receita_anual": total_receita_anual,
        "total_despesas_anual": total_despesas_anual,
        "saldo_anual": saldo_anual,
        "anos_disponiveis": anos_disponiveis,
    }
    
    return render(request, "gestao_rural/financeiro/relatorio_fluxo_caixa.html", context)


@login_required
def relatorio_balanco_dre(request, propriedade_id):
    """Relatório consolidado de Balanço e DRE."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import ReceitaAnual, DespesaConfigurada, GrupoDespesa
    from decimal import Decimal
    from collections import defaultdict
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
    if not receita_anual_obj:
        messages.warning(request, f"Não há receita cadastrada para o ano {ano}.")
        return redirect('financeiro_receitas_anuais', propriedade_id=propriedade_id)
    
    receita_bruta = receita_anual_obj.valor_receita
    
    # DRE COMPLETO - Demonstração do Resultado do Exercício
    
    # 1. RECEITA BRUTA (já temos)
    
    # 2. DEDUÇÕES DA RECEITA
    icms_vendas = receita_anual_obj.icms_vendas or Decimal("0.00")
    funviral_vendas = receita_anual_obj.funviral_vendas or Decimal("0.00")
    outros_impostos_vendas = receita_anual_obj.outros_impostos_vendas or Decimal("0.00")
    devolucoes_vendas = receita_anual_obj.devolucoes_vendas or Decimal("0.00")
    abatimentos_vendas = receita_anual_obj.abatimentos_vendas or Decimal("0.00")
    total_impostos_vendas = icms_vendas + funviral_vendas + outros_impostos_vendas
    total_deducoes = total_impostos_vendas + devolucoes_vendas + abatimentos_vendas
    
    # 3. RECEITA LÍQUIDA
    receita_liquida = receita_bruta - total_deducoes
    
    # 4. CUSTO DOS PRODUTOS VENDIDOS (CPV)
    cpv = receita_anual_obj.custo_produtos_vendidos or Decimal("0.00")
    
    # 5. LUCRO BRUTO
    lucro_bruto = receita_liquida - cpv
    
    # 6. DESPESAS OPERACIONAIS
    # Primeiro, somar despesas detalhadas do modelo
    despesas_detalhadas = receita_anual_obj.calcular_despesas_operacionais_detalhadas()
    
    # Depois, somar despesas configuradas (grupos)
    despesas = DespesaConfigurada.objects.filter(propriedade=propriedade, ativo=True).select_related('grupo')
    
    # Agrupar despesas por grupo e tipo
    despesas_por_grupo = defaultdict(lambda: {
        'fixas': Decimal("0.00"), 
        'variaveis': Decimal("0.00"),
        'administrativas': Decimal("0.00"),
        'comerciais': Decimal("0.00"),
        'operacionais': Decimal("0.00")
    })
    
    total_despesas_configuradas = Decimal("0.00")
    total_despesas_fixas = Decimal("0.00")
    total_despesas_variaveis = Decimal("0.00")
    
    for despesa in despesas:
        valor_anual = despesa.calcular_valor_anual(receita_bruta)
        total_despesas_configuradas += valor_anual
        
        if despesa.grupo.tipo == GrupoDespesa.TIPO_FIXA:
            despesas_por_grupo[despesa.grupo.nome]['fixas'] += valor_anual
            total_despesas_fixas += valor_anual
        else:
            despesas_por_grupo[despesa.grupo.nome]['variaveis'] += valor_anual
            total_despesas_variaveis += valor_anual
    
    # Total de despesas operacionais = detalhadas + configuradas
    total_despesas_operacionais = despesas_detalhadas + total_despesas_configuradas
    
    # 7. RESULTADO OPERACIONAL (conforme PDF: Lucro Bruto - Despesas Operacionais)
    # No PDF, a depreciação está incluída nas despesas operacionais
    resultado_operacional = lucro_bruto - total_despesas_operacionais
    
    # 8. DESPESAS E RECEITAS NÃO OPERACIONAIS (separadas conforme PDF)
    despesas_financeiras = receita_anual_obj.despesas_financeiras or Decimal("0.00")
    receitas_financeiras = receita_anual_obj.receitas_financeiras or Decimal("0.00")
    resultado_nao_operacional = receitas_financeiras - despesas_financeiras
    
    # 9. RESULTADO ANTES DO IMPOSTO DE RENDA (LAIR)
    resultado_antes_ir = resultado_operacional + resultado_nao_operacional
    
    # Verificar se é pessoa física (CPF) ou jurídica (CNPJ)
    cpf_cnpj = propriedade.produtor.cpf_cnpj if propriedade.produtor else ""
    cpf_cnpj_limpo = cpf_cnpj.replace(".", "").replace("-", "").replace("/", "")
    is_pessoa_fisica = len(cpf_cnpj_limpo) == 11
    
    # 10. PROVISÃO DE IMPOSTOS (separados conforme PDF)
    # Para pessoa física: apenas IR (CSLL não se aplica)
    # Para pessoa jurídica: CSLL + IRPJ
    if is_pessoa_fisica:
        csll = Decimal("0.00")  # CSLL não se aplica a pessoa física
        irpj = receita_anual_obj.irpj or Decimal("0.00")
    else:
        csll = receita_anual_obj.csll or Decimal("0.00")
        irpj = receita_anual_obj.irpj or Decimal("0.00")
    
    total_impostos_renda = csll + irpj
    
    # 11. RESULTADO LÍQUIDO DO EXERCÍCIO
    resultado_liquido = resultado_antes_ir - total_impostos_renda
    
    # MARGENS
    margem_bruta_pct = (lucro_bruto / receita_bruta * 100) if receita_bruta > 0 else Decimal("0.00")
    margem_operacional_pct = (resultado_operacional / receita_bruta * 100) if receita_bruta > 0 else Decimal("0.00")
    margem_liquida_pct = (resultado_liquido / receita_bruta * 100) if receita_bruta > 0 else Decimal("0.00")
    
    # Separar depreciação das despesas operacionais para exibição
    depreciacao = receita_anual_obj.depreciacao_amortizacao or Decimal("0.00")
    
    # Anos disponíveis
    anos_disponiveis = ReceitaAnual.objects.filter(
        propriedade=propriedade
    ).values_list('ano', flat=True).distinct().order_by('-ano')
    
    context = {
        "propriedade": propriedade,
        "ano": ano,
        "anos_disponiveis": anos_disponiveis,
        "receita_anual_obj": receita_anual_obj,
        # Receitas
        "receita_bruta": receita_bruta,
        "icms_vendas": icms_vendas,
        "funviral_vendas": funviral_vendas,
        "outros_impostos_vendas": outros_impostos_vendas,
        "total_impostos_vendas": total_impostos_vendas,
        "devolucoes_vendas": devolucoes_vendas,
        "abatimentos_vendas": abatimentos_vendas,
        "total_deducoes": total_deducoes,
        "receita_liquida": receita_liquida,
        # Custos
        "cpv": cpv,
        "lucro_bruto": lucro_bruto,
        # Despesas Operacionais
        "despesas_por_grupo": dict(despesas_por_grupo),
        "total_despesas_operacionais": total_despesas_operacionais,
        "total_despesas_configuradas": total_despesas_configuradas,
        "despesas_detalhadas": despesas_detalhadas,
        "total_despesas_fixas": total_despesas_fixas,
        "total_despesas_variaveis": total_despesas_variaveis,
        "depreciacao": depreciacao,
        # Despesas detalhadas individuais
        "retirada_labore": receita_anual_obj.retirada_labore or Decimal("0.00"),
        "assistencia_contabil": receita_anual_obj.assistencia_contabil or Decimal("0.00"),
        "encargos_inss": receita_anual_obj.encargos_inss or Decimal("0.00"),
        "taxas_diversas": receita_anual_obj.taxas_diversas or Decimal("0.00"),
        "despesas_administrativas": receita_anual_obj.despesas_administrativas or Decimal("0.00"),
        "material_uso_consumo": receita_anual_obj.material_uso_consumo or Decimal("0.00"),
        "despesas_comunicacao": receita_anual_obj.despesas_comunicacao or Decimal("0.00"),
        "despesas_viagens": receita_anual_obj.despesas_viagens or Decimal("0.00"),
        "despesas_energia_eletrica": receita_anual_obj.despesas_energia_eletrica or Decimal("0.00"),
        "despesas_transportes": receita_anual_obj.despesas_transportes or Decimal("0.00"),
        "despesas_combustivel": receita_anual_obj.despesas_combustivel or Decimal("0.00"),
        "despesas_manutencao": receita_anual_obj.despesas_manutencao or Decimal("0.00"),
        # Resultados
        "resultado_operacional": resultado_operacional,
        "despesas_financeiras": despesas_financeiras,
        "receitas_financeiras": receitas_financeiras,
        "resultado_nao_operacional": resultado_nao_operacional,
        "resultado_antes_ir": resultado_antes_ir,
        "csll": csll,
        "irpj": irpj,
        "total_impostos_renda": total_impostos_renda,
        "resultado_liquido": resultado_liquido,
        # Margens
        "margem_bruta_pct": margem_bruta_pct,
        "margem_operacional_pct": margem_operacional_pct,
        "margem_liquida_pct": margem_liquida_pct,
        "is_pessoa_fisica": is_pessoa_fisica,
    }
    
    # Usar template específico para pessoa física ou jurídica
    if is_pessoa_fisica:
        template = "gestao_rural/financeiro/relatorio_balanco_dre_pf.html"
    else:
        template = "gestao_rural/financeiro/relatorio_balanco_dre.html"
    
    return render(request, template, context)


@login_required
def exportar_dre_pdf(request, propriedade_id):
    """Exporta DRE completo em PDF."""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from datetime import datetime
    
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import ReceitaAnual, DespesaConfigurada, GrupoDespesa
    from decimal import Decimal
    from collections import defaultdict
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
    if not receita_anual_obj:
        messages.warning(request, f"Não há receita cadastrada para o ano {ano}.")
        return redirect('financeiro_receitas_anuais', propriedade_id=propriedade_id)
    
    receita_bruta = receita_anual_obj.valor_receita
    
    # Calcular todos os valores do DRE (mesma lógica da view)
    icms_vendas = receita_anual_obj.icms_vendas or Decimal("0.00")
    funviral_vendas = receita_anual_obj.funviral_vendas or Decimal("0.00")
    outros_impostos_vendas = receita_anual_obj.outros_impostos_vendas or Decimal("0.00")
    devolucoes_vendas = receita_anual_obj.devolucoes_vendas or Decimal("0.00")
    abatimentos_vendas = receita_anual_obj.abatimentos_vendas or Decimal("0.00")
    total_impostos_vendas = icms_vendas + funviral_vendas + outros_impostos_vendas
    total_deducoes = total_impostos_vendas + devolucoes_vendas + abatimentos_vendas
    
    receita_liquida = receita_bruta - total_deducoes
    cpv = receita_anual_obj.custo_produtos_vendidos or Decimal("0.00")
    lucro_bruto = receita_liquida - cpv
    
    # Despesas detalhadas do modelo
    despesas_detalhadas = receita_anual_obj.calcular_despesas_operacionais_detalhadas()
    
    # Despesas configuradas (grupos)
    despesas = DespesaConfigurada.objects.filter(propriedade=propriedade, ativo=True).select_related('grupo')
    despesas_por_grupo = defaultdict(lambda: {
        'fixas': Decimal("0.00"), 
        'variaveis': Decimal("0.00")
    })
    
    total_despesas_configuradas = Decimal("0.00")
    total_despesas_fixas = Decimal("0.00")
    total_despesas_variaveis = Decimal("0.00")
    
    for despesa in despesas:
        valor_anual = despesa.calcular_valor_anual(receita_bruta)
        total_despesas_configuradas += valor_anual
        
        if despesa.grupo.tipo == GrupoDespesa.TIPO_FIXA:
            despesas_por_grupo[despesa.grupo.nome]['fixas'] += valor_anual
            total_despesas_fixas += valor_anual
        else:
            despesas_por_grupo[despesa.grupo.nome]['variaveis'] += valor_anual
            total_despesas_variaveis += valor_anual
    
    # Total = detalhadas + configuradas
    total_despesas_operacionais = despesas_detalhadas + total_despesas_configuradas
    
    resultado_operacional = lucro_bruto - total_despesas_operacionais
    despesas_financeiras = receita_anual_obj.despesas_financeiras or Decimal("0.00")
    receitas_financeiras = receita_anual_obj.receitas_financeiras or Decimal("0.00")
    resultado_nao_operacional = receitas_financeiras - despesas_financeiras
    resultado_antes_ir = resultado_operacional + resultado_nao_operacional
    csll = receita_anual_obj.csll or Decimal("0.00")
    irpj = receita_anual_obj.irpj or Decimal("0.00")
    total_impostos_renda = csll + irpj
    resultado_liquido = resultado_antes_ir - total_impostos_renda
    depreciacao = receita_anual_obj.depreciacao_amortizacao or Decimal("0.00")
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="DRE_{propriedade.id}_{ano}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a5490')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=10
    )
    
    # Função auxiliar para formatar valores
    def formatar_moeda(valor):
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Cabeçalho Contábil Profissional
    story.append(Paragraph("DEMONSTRAÇÃO DO RESULTADO DO EXERCÍCIO", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Informações da Empresa/Propriedade
    if propriedade.produtor:
        produtor = propriedade.produtor
        story.append(Paragraph(f"<b>{propriedade.nome_propriedade.upper()}</b>", subtitle_style))
        if produtor.cpf_cnpj:
            story.append(Paragraph(f"<b>CPF/CNPJ:</b> {produtor.cpf_cnpj}", subtitle_style))
        if produtor.endereco:
            story.append(Paragraph(f"<b>Endereço:</b> {produtor.endereco}", subtitle_style))
    else:
        story.append(Paragraph(f"<b>{propriedade.nome_propriedade.upper()}</b>", subtitle_style))
    
    story.append(Paragraph(f"<b>Exercício Social:</b> {ano}", subtitle_style))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", subtitle_style))
    story.append(Spacer(1, 1*cm))
    
    # Tabela do DRE
    dre_data = []
    
    # 1. RECEITA BRUTA
    dre_data.append(['<b>3.01.01.01.01</b>', '<b>RECEITA BRUTA DE VENDAS</b>', f'<b>{formatar_moeda(receita_bruta)}</b>'])
    dre_data.append(['3.01.01.01.01.0001', 'Vendas Mercadorias Produção Própria', formatar_moeda(receita_bruta)])
    
    # 2. DEDUÇÕES
    if total_deducoes > 0:
        dre_data.append(['<b>3.01.01.01.02</b>', '<b>DEDUÇÕES DA RECEITA BRUTA</b>', ''])
        if funviral_vendas > 0:
            dre_data.append(['3.01.01.01.02.0004', 'Funrural s/Vendas', f'({formatar_moeda(funviral_vendas)})'])
        if icms_vendas > 0:
            dre_data.append(['3.01.01.01.02.0005', 'ICMS s/Vendas', f'({formatar_moeda(icms_vendas)})'])
        if outros_impostos_vendas > 0:
            dre_data.append(['3.01.01.01.02.0006', 'Outros Impostos s/Vendas', f'({formatar_moeda(outros_impostos_vendas)})'])
        if devolucoes_vendas > 0:
            dre_data.append(['3.01.01.01.02.0007', 'Devoluções de Vendas', f'({formatar_moeda(devolucoes_vendas)})'])
        if abatimentos_vendas > 0:
            dre_data.append(['3.01.01.01.02.0008', 'Abatimentos sobre Vendas', f'({formatar_moeda(abatimentos_vendas)})'])
        dre_data.append(['<b>3.01.01.01.02</b>', '<b>Total Deduções</b>', f'<b>({formatar_moeda(total_deducoes)})</b>'])
    
    # 3. RECEITA LÍQUIDA
    dre_data.append(['<b>3.01.01.01.03</b>', '<b>RECEITA LÍQUIDA</b>', f'<b>{formatar_moeda(receita_liquida)}</b>'])
    
    # 4. CPV
    if cpv > 0:
        dre_data.append(['<b>3.01.01.01.03.</b>', '<b>CUSTOS MERCADORIAS VENDIDAS</b>', ''])
        dre_data.append(['3.01.01.01.03.0001', 'Custos Mercadorias Produção Própria Vendidas', f'({formatar_moeda(cpv)})'])
    
    # 5. LUCRO BRUTO (antes de mostrar como Resultado Operacional)
    if cpv > 0:
        dre_data.append(['<b>3.01.01.01.04</b>', '<b>LUCRO BRUTO</b>', f'<b>{formatar_moeda(lucro_bruto)}</b>'])
    else:
        # Se não há CPV, o Lucro Bruto = Receita Líquida
        dre_data.append(['<b>3.01.01.01.04</b>', '<b>LUCRO BRUTO</b>', f'<b>{formatar_moeda(receita_liquida)}</b>'])
    
    # 6. DESPESAS OPERACIONAIS (usar código 3.01.01.07. como no HTML)
    dre_data.append(['<b>3.01.01.07.</b>', '<b>DESPESAS OPERACIONAIS</b>', ''])
    
    # Despesas Detalhadas (conforme DRE contábil)
    if despesas_detalhadas > 0:
        dre_data.append(['<b>3.01.01.07.01.</b>', '<b>DESPESAS DIVERSAS</b>', ''])
        
        if receita_anual_obj.retirada_labore and receita_anual_obj.retirada_labore > 0:
            dre_data.append(['3.01.01.07.01.0001', 'Retirada Labore', f'({formatar_moeda(receita_anual_obj.retirada_labore)})'])
        if receita_anual_obj.assistencia_contabil and receita_anual_obj.assistencia_contabil > 0:
            dre_data.append(['3.01.01.07.01.0002', 'Assistência Contábil', f'({formatar_moeda(receita_anual_obj.assistencia_contabil)})'])
        if receita_anual_obj.encargos_inss and receita_anual_obj.encargos_inss > 0:
            dre_data.append(['3.01.01.07.01.0003', 'Encargos INSS', f'({formatar_moeda(receita_anual_obj.encargos_inss)})'])
        if receita_anual_obj.taxas_diversas and receita_anual_obj.taxas_diversas > 0:
            dre_data.append(['3.01.01.07.01.0004', 'Taxas Diversas', f'({formatar_moeda(receita_anual_obj.taxas_diversas)})'])
        if receita_anual_obj.despesas_administrativas and receita_anual_obj.despesas_administrativas > 0:
            dre_data.append(['3.01.01.07.01.0005', 'Despesas Administrativas', f'({formatar_moeda(receita_anual_obj.despesas_administrativas)})'])
        if receita_anual_obj.material_uso_consumo and receita_anual_obj.material_uso_consumo > 0:
            dre_data.append(['3.01.01.07.01.0006', 'Material de Uso e Consumo', f'({formatar_moeda(receita_anual_obj.material_uso_consumo)})'])
        if receita_anual_obj.despesas_comunicacao and receita_anual_obj.despesas_comunicacao > 0:
            dre_data.append(['3.01.01.07.01.0007', 'Despesas Comunicação', f'({formatar_moeda(receita_anual_obj.despesas_comunicacao)})'])
        if receita_anual_obj.despesas_viagens and receita_anual_obj.despesas_viagens > 0:
            dre_data.append(['3.01.01.07.01.0008', 'Despesas Viagens', f'({formatar_moeda(receita_anual_obj.despesas_viagens)})'])
        if receita_anual_obj.despesas_energia_eletrica and receita_anual_obj.despesas_energia_eletrica > 0:
            dre_data.append(['3.01.01.07.01.0009', 'Despesas Energia Elétrica', f'({formatar_moeda(receita_anual_obj.despesas_energia_eletrica)})'])
        if receita_anual_obj.despesas_transportes and receita_anual_obj.despesas_transportes > 0:
            dre_data.append(['3.01.01.07.01.0010', 'Despesas Transportes', f'({formatar_moeda(receita_anual_obj.despesas_transportes)})'])
        if receita_anual_obj.despesas_combustivel and receita_anual_obj.despesas_combustivel > 0:
            dre_data.append(['3.01.01.07.01.0011', 'Despesas Combustível', f'({formatar_moeda(receita_anual_obj.despesas_combustivel)})'])
        if receita_anual_obj.despesas_manutencao and receita_anual_obj.despesas_manutencao > 0:
            dre_data.append(['3.01.01.07.01.0012', 'Despesas Manutenção', f'({formatar_moeda(receita_anual_obj.despesas_manutencao)})'])
        if depreciacao > 0:
            dre_data.append(['3.01.01.07.01.0013', 'Despesas Encargos Depreciação', f'({formatar_moeda(depreciacao)})'])
        
        dre_data.append(['<b>3.01.01.07.01</b>', '<b>Total Despesas Diversas</b>', f'<b>({formatar_moeda(despesas_detalhadas)})</b>'])
    
    if total_despesas_variaveis > 0:
        dre_data.append(['<b>3.01.01.07.02.</b>', '<b>Despesas Variáveis</b>', ''])
        contador_var = 2
        for grupo, dados in despesas_por_grupo.items():
            if dados['variaveis'] > 0:
                dre_data.append([f'3.01.01.07.02.{contador_var:04d}', grupo, f'({formatar_moeda(dados["variaveis"])})'])
                contador_var += 1
        dre_data.append(['<b>3.01.01.07.02</b>', '<b>Total Despesas Variáveis</b>', f'<b>({formatar_moeda(total_despesas_variaveis)})</b>'])
    
    if total_despesas_fixas > 0:
        dre_data.append(['<b>3.01.01.07.03.</b>', '<b>Despesas Fixas</b>', ''])
        contador_fix = 1
        for grupo, dados in despesas_por_grupo.items():
            if dados['fixas'] > 0:
                dre_data.append([f'3.01.01.07.03.{contador_fix:04d}', grupo, f'({formatar_moeda(dados["fixas"])})'])
                contador_fix += 1
        dre_data.append(['<b>3.01.01.07.03</b>', '<b>Total Despesas Fixas</b>', f'<b>({formatar_moeda(total_despesas_fixas)})</b>'])
    
    dre_data.append(['<b>3.01.01.07</b>', '<b>Total Despesas Operacionais</b>', f'<b>({formatar_moeda(total_despesas_operacionais)})</b>'])
    
    # 7. RESULTADO OPERACIONAL (após despesas) - usar código 3.01.01.01.01 como no HTML
    cor_resultado = colors.HexColor('#28a745') if resultado_operacional >= 0 else colors.HexColor('#dc3545')
    dre_data.append(['<b>3.01.01.01.01</b>', '<b>RESULTADO OPERACIONAL</b>', f'<b>{formatar_moeda(resultado_operacional)}</b>'])
    
    # 8. DESPESAS E RECEITAS NÃO OPERACIONAIS
    if despesas_financeiras > 0 or receitas_financeiras > 0:
        dre_data.append(['<b>3.01.01.08.</b>', '<b>DESPESAS E RECEITAS NÃO OPERACIONAIS</b>', ''])
        if despesas_financeiras > 0:
            dre_data.append(['3.01.01.08.0001', 'Despesas Juros e Multas', f'({formatar_moeda(despesas_financeiras)})'])
        if receitas_financeiras > 0:
            dre_data.append(['3.01.01.08.0002', 'Receitas Rendimentos Financeiros', formatar_moeda(receitas_financeiras)])
        cor_nao_op = colors.HexColor('#28a745') if resultado_nao_operacional >= 0 else colors.HexColor('#dc3545')
        dre_data.append(['<b>3.01.01.08</b>', '<b>Resultado Não Operacional</b>', f'<b>{formatar_moeda(resultado_nao_operacional)}</b>'])
    
    # 9. RESULTADO ANTES DO IR
    cor_antes_ir = colors.HexColor('#28a745') if resultado_antes_ir >= 0 else colors.HexColor('#dc3545')
    dre_data.append(['<b>3.01.01.09</b>', '<b>RESULTADO ANTES DO IMPOSTO DE RENDA</b>', f'<b>{formatar_moeda(resultado_antes_ir)}</b>'])
    
    # 10. PROVISÃO DE IMPOSTOS
    if total_impostos_renda > 0:
        dre_data.append(['<b>3.01.01.10.</b>', '<b>PROVISÃO DE IMPOSTOS</b>', ''])
        if csll > 0:
            dre_data.append(['3.01.01.10.0001', 'Contribuição Social S/Lucro Líquido - CSLL', f'({formatar_moeda(csll)})'])
        if irpj > 0:
            dre_data.append(['3.01.01.10.0002', 'Imposto de Renda Pessoa Jurídica - IRPJ', f'({formatar_moeda(irpj)})'])
        dre_data.append(['<b>3.01.01.10</b>', '<b>Total Provisão de Impostos</b>', f'<b>({formatar_moeda(total_impostos_renda)})</b>'])
    
    # 11. RESULTADO LÍQUIDO
    cor_liquido = colors.HexColor('#28a745') if resultado_liquido >= 0 else colors.HexColor('#dc3545')
    dre_data.append(['<b>3.01</b>', '<b>RESULTADO LÍQUIDO DO EXERCÍCIO</b>', f'<b>{formatar_moeda(resultado_liquido)}</b>'])
    
    # Criar tabela com 3 colunas (Código, Descrição, Valor)
    dre_table = Table(dre_data, colWidths=[3.5*cm, 10*cm, 3.5*cm])
    
    # Estilo da tabela
    table_style = [
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Código
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Descrição
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'), # Valor
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (0, -1), 6),
        ('RIGHTPADDING', (2, 0), (2, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]
    
    # Aplicar cores e formatação nas linhas principais
    for i, linha in enumerate(dre_data):
        if len(linha) >= 2:
            # Receita Bruta
            if '<b>RECEITA BRUTA DE VENDAS</b>' in linha[1]:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e3f2fd')))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 11))
                table_style.append(('LINEBELOW', (0, i), (-1, i), 1.5, colors.HexColor('#1976d2')))
            # Receita Líquida e Lucro Bruto
            elif '<b>RECEITA LÍQUIDA</b>' in linha[1] or '<b>LUCRO BRUTO</b>' in linha[1]:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#c8e6c9')))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 11))
                table_style.append(('LINEBELOW', (0, i), (-1, i), 1.5, colors.HexColor('#4caf50')))
            # Resultado Operacional
            elif '<b>RESULTADO OPERACIONAL</b>' in linha[1]:
                table_style.append(('BACKGROUND', (0, i), (-1, i), cor_resultado))
                table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 11))
                table_style.append(('LINEBELOW', (0, i), (-1, i), 1.5, colors.HexColor('#1976d2')))
            # Resultado Antes IR
            elif '<b>RESULTADO ANTES DO IMPOSTO DE RENDA</b>' in linha[1]:
                table_style.append(('BACKGROUND', (0, i), (-1, i), cor_antes_ir))
                table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 11))
                table_style.append(('LINEBELOW', (0, i), (-1, i), 1.5, colors.HexColor('#1976d2')))
            # Resultado Líquido (destaque final)
            elif '<b>RESULTADO LÍQUIDO DO EXERCÍCIO</b>' in linha[1]:
                table_style.append(('BACKGROUND', (0, i), (-1, i), cor_liquido))
                table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 13))
                table_style.append(('LINEBELOW', (0, i), (-1, i), 2, colors.HexColor('#1976d2')))
            # Títulos de seções (com código)
            elif '<b>' in linha[0] and '<b>' in linha[1] and linha[1] != '':
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 10))
            # Totais
            elif '<b>Total' in linha[1] or (len(linha) >= 2 and '<b>Total' in linha[0]):
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
                table_style.append(('FONTSIZE', (0, i), (-1, i), 10))
    
    dre_table.setStyle(TableStyle(table_style))
    story.append(dre_table)
    story.append(Spacer(1, 1*cm))
    
    # Indicadores
    margem_bruta_pct = (lucro_bruto / receita_bruta * 100) if receita_bruta > 0 else Decimal("0.00")
    margem_operacional_pct = (resultado_operacional / receita_bruta * 100) if receita_bruta > 0 else Decimal("0.00")
    margem_liquida_pct = (resultado_liquido / receita_bruta * 100) if receita_bruta > 0 else Decimal("0.00")
    
    indicadores_data = [
        ['<b>Indicador</b>', '<b>Valor</b>', '<b>Percentual</b>'],
        ['Margem Bruta', formatar_moeda(lucro_bruto), f'{margem_bruta_pct:.2f}%'],
        ['Margem Operacional', formatar_moeda(resultado_operacional), f'{margem_operacional_pct:.2f}%'],
        ['Margem Líquida', formatar_moeda(resultado_liquido), f'{margem_liquida_pct:.2f}%'],
    ]
    
    indicadores_table = Table(indicadores_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    indicadores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(Paragraph("<b>Indicadores de Rentabilidade</b>", header_style))
    story.append(indicadores_table)
    
    doc.build(story)
    return response


# ========== FUNÇÕES DE INTEGRAÇÃO E PLANILHA ==========

@login_required
def integrar_vendas_financeiro(request, propriedade_id):
    """Integra vendas projetadas com o módulo financeiro."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .services_integracao_vendas_financeiro import (
        sincronizar_receitas_anuais_vendas,
        criar_lancamentos_financeiros_vendas,
        obter_resumo_financeiro_por_ano
    )
    from .models import VendaProjetada
    from django.db.models.functions import ExtractYear
    from django.http import JsonResponse
    
    acao = request.GET.get('acao', 'sincronizar')
    ano = request.GET.get('ano')
    anos = None
    if ano:
        try:
            anos = [int(ano)]
        except (ValueError, TypeError):
            pass
    
    resultado = None
    resumo_financeiro = None
    
    if acao == 'sincronizar':
        resultado = sincronizar_receitas_anuais_vendas(propriedade, anos)
        messages.success(
            request,
            f"Sincronização concluída! {resultado['receitas_criadas']} receitas criadas, "
            f"{resultado['receitas_atualizadas']} atualizadas. Total: R$ {resultado['total_receitas']:,.2f}"
        )
    elif acao == 'criar_lancamentos':
        resultado = criar_lancamentos_financeiros_vendas(propriedade, ano)
        if 'erro' in resultado:
            messages.error(request, resultado['erro'])
        else:
            messages.success(
                request,
                f"{resultado['lancamentos_criados']} lançamentos financeiros criados! "
                f"({resultado['lancamentos_duplicados']} duplicados ignorados)"
            )
    
    # Buscar resumo financeiro
    resumo_financeiro = obter_resumo_financeiro_por_ano(propriedade, anos)
    
    # Buscar anos disponíveis
    anos_com_vendas = VendaProjetada.objects.filter(
        propriedade=propriedade
    ).annotate(ano_venda=ExtractYear('data_venda')).values_list('ano_venda', flat=True).distinct().order_by('-ano_venda')
    
    context = {
        "propriedade": propriedade,
        "resultado": resultado,
        "resumo_financeiro": resumo_financeiro,
        "anos_com_vendas": anos_com_vendas,
        "acao": acao,
        "ano_selecionado": ano,
    }
    
    return render(request, "gestao_rural/financeiro/integrar_vendas_financeiro.html", context)


@login_required
def saldos_consolidados_anuais(request, propriedade_id):
    """Mostra saldos consolidados ano a ano."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .services_integracao_vendas_financeiro import obter_resumo_financeiro_por_ano
    from .models import VendaProjetada
    from django.db.models.functions import ExtractYear
    
    # Buscar anos disponíveis
    anos_com_vendas = VendaProjetada.objects.filter(
        propriedade=propriedade
    ).annotate(ano_venda=ExtractYear('data_venda')).values_list('ano_venda', flat=True).distinct().order_by('-ano_venda')
    
    # Filtrar por anos se fornecido
    anos_filtro = request.GET.getlist('anos')
    if anos_filtro:
        try:
            anos_filtro = [int(a) for a in anos_filtro]
        except (ValueError, TypeError):
            anos_filtro = None
    else:
        anos_filtro = None
    
    resumo_financeiro = obter_resumo_financeiro_por_ano(propriedade, anos_filtro)
    
    context = {
        "propriedade": propriedade,
        "resumo_financeiro": resumo_financeiro,
        "anos_com_vendas": anos_com_vendas,
        "anos_selecionados": anos_filtro or [],
    }
    
    return render(request, "gestao_rural/financeiro/saldos_consolidados_anuais.html", context)


@login_required
def planilha_despesas_porcentual(request, propriedade_id):
    """Planilha interativa para configurar despesas por percentual da receita."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import GrupoDespesa, DespesaConfigurada, ReceitaAnual, CategoriaFinanceira
    from decimal import Decimal
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Buscar ou criar receita anual
    receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
    receita_anual = receita_anual_obj.valor_receita if receita_anual_obj else Decimal("0.00")
    
    # Buscar grupos de despesas
    grupos = GrupoDespesa.objects.filter(propriedade=propriedade, ativo=True).order_by('ordem', 'nome')
    
    # Para cada grupo, buscar ou criar uma despesa padrão se não existir
    grupos_com_despesas = []
    for grupo in grupos:
        # Buscar despesa existente ou criar uma padrão
        despesa = DespesaConfigurada.objects.filter(
            propriedade=propriedade,
            grupo=grupo,
            ativo=True
        ).first()
        
        if not despesa:
            # Criar despesa padrão para o grupo
            categoria_padrao = CategoriaFinanceira.objects.filter(
                propriedade=propriedade,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                ativa=True
            ).first()
            
            if categoria_padrao:
                despesa = DespesaConfigurada.objects.create(
                    propriedade=propriedade,
                    grupo=grupo,
                    categoria_financeira=categoria_padrao,
                    nome=grupo.nome,
                    tipo_calculo=DespesaConfigurada.TIPO_PORCENTAGEM,
                    porcentagem_receita=Decimal("0.00"),
                    ativo=True,
                    ordem=grupo.ordem
                )
        
        if despesa:
            valor_anual = despesa.calcular_valor_anual(receita_anual)
            valor_mensal = despesa.calcular_valor_mensal(receita_anual)
            
            grupos_com_despesas.append({
                'grupo': grupo,
                'despesa': despesa,
                'porcentagem_atual': despesa.porcentagem_receita,
                'valor_anual': valor_anual,
                'valor_mensal': valor_mensal,
            })
    
    # Calcular totais
    total_porcentagem = sum(item['porcentagem_atual'] for item in grupos_com_despesas)
    total_despesas = sum(item['valor_anual'] for item in grupos_com_despesas)
    total_mensal = total_despesas / Decimal('12.00')
    saldo_disponivel = receita_anual - total_despesas
    porcentagem_disponivel = Decimal("100.00") - total_porcentagem
    
    # Anos disponíveis
    anos_disponiveis = ReceitaAnual.objects.filter(
        propriedade=propriedade
    ).values_list('ano', flat=True).distinct().order_by('-ano')
    
    context = {
        "propriedade": propriedade,
        "ano": ano,
        "receita_anual": receita_anual,
        "receita_anual_obj": receita_anual_obj,
        "grupos_com_despesas": grupos_com_despesas,
        "total_porcentagem": total_porcentagem,
        "total_despesas": total_despesas,
        "total_mensal": total_mensal,
        "saldo_disponivel": saldo_disponivel,
        "porcentagem_disponivel": porcentagem_disponivel,
        "anos_disponiveis": anos_disponiveis,
    }
    
    return render(request, "gestao_rural/financeiro/planilha_despesas_porcentual.html", context)


@login_required
def atualizar_porcentual_despesa_ajax(request, propriedade_id):
    """Atualiza percentual de uma despesa via AJAX."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import DespesaConfigurada, ReceitaAnual
    from decimal import Decimal
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        despesa_id = request.POST.get('despesa_id')
        porcentagem = Decimal(request.POST.get('porcentagem', '0'))
        ano = int(request.POST.get('ano', timezone.now().year))
        
        if porcentagem < 0 or porcentagem > 100:
            return JsonResponse({'erro': 'Percentual deve estar entre 0 e 100'}, status=400)
        
        despesa = get_object_or_404(DespesaConfigurada, id=despesa_id, propriedade=propriedade)
        
        # Atualizar percentual
        despesa.porcentagem_receita = porcentagem
        despesa.tipo_calculo = DespesaConfigurada.TIPO_PORCENTAGEM
        despesa.save()
        
        # Buscar receita anual
        receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
        receita_anual = receita_anual_obj.valor_receita if receita_anual_obj else Decimal("0.00")
        
        # Calcular novos valores
        valor_anual = despesa.calcular_valor_anual(receita_anual)
        valor_mensal = despesa.calcular_valor_mensal(receita_anual)
        
        # Recalcular totais
        todas_despesas = DespesaConfigurada.objects.filter(
            propriedade=propriedade,
            ativo=True
        )
        total_porcentagem = sum(
            d.porcentagem_receita for d in todas_despesas 
            if d.tipo_calculo == DespesaConfigurada.TIPO_PORCENTAGEM
        )
        total_despesas = sum(
            d.calcular_valor_anual(receita_anual) for d in todas_despesas
        )
        saldo_disponivel = receita_anual - total_despesas
        porcentagem_disponivel = Decimal("100.00") - total_porcentagem
        
        return JsonResponse({
            'sucesso': True,
            'valor_anual': str(valor_anual),
            'valor_mensal': str(valor_mensal),
            'total_porcentagem': str(total_porcentagem),
            'total_despesas': str(total_despesas),
            'saldo_disponivel': str(saldo_disponivel),
            'porcentagem_disponivel': str(porcentagem_disponivel),
        })
    except ValueError as e:
        return JsonResponse({'sucesso': False, 'erro': f'Valor inválido: {str(e)}'}, status=400)
    except DespesaConfigurada.DoesNotExist:
        return JsonResponse({'sucesso': False, 'erro': 'Despesa não encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({
            'sucesso': False, 
            'erro': f'Erro ao atualizar: {str(e)}'
        }, status=500)


@login_required
def gerar_lancamentos_planilha(request, propriedade_id):
    """Gera lançamentos financeiros baseados na planilha de despesas."""
    propriedade = _obter_propriedade(request.user, propriedade_id)
    
    from .models_financeiro import (
        DespesaConfigurada, ReceitaAnual, CategoriaFinanceira, 
        ContaFinanceira, LancamentoFinanceiro
    )
    from decimal import Decimal
    from django.db import transaction
    
    if request.method != 'POST':
        messages.error(request, "Método não permitido")
        return HttpResponseRedirect(reverse('financeiro_planilha_despesas', kwargs={'propriedade_id': propriedade_id}))
    
    ano = int(request.POST.get('ano', timezone.now().year))
    criar_receita = request.POST.get('criar_receita') == 'on'
    criar_despesas = request.POST.get('criar_despesas') == 'on'
    
    # Buscar receita anual
    receita_anual_obj = ReceitaAnual.objects.filter(propriedade=propriedade, ano=ano).first()
    if not receita_anual_obj:
        messages.error(request, f"Receita anual não encontrada para o ano {ano}")
        url = reverse('financeiro_planilha_despesas', kwargs={'propriedade_id': propriedade_id})
        return HttpResponseRedirect(f"{url}?ano={ano}")
    
    receita_anual = receita_anual_obj.valor_receita
    
    # Buscar conta padrão
    conta_padrao = ContaFinanceira.objects.filter(
        propriedade=propriedade,
        ativa=True
    ).first()
    
    if not conta_padrao:
        messages.error(request, "Nenhuma conta financeira ativa encontrada. Crie uma conta primeiro.")
        url = reverse('financeiro_planilha_despesas', kwargs={'propriedade_id': propriedade_id})
        return HttpResponseRedirect(f"{url}?ano={ano}")
    
    lancamentos_criados = 0
    
    with transaction.atomic():
        # Criar lançamento de receita
        if criar_receita:
            categoria_receita = CategoriaFinanceira.objects.filter(
                propriedade=propriedade,
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                ativa=True
            ).first()
            
            if not categoria_receita:
                categoria_receita = CategoriaFinanceira.objects.create(
                    propriedade=propriedade,
                    nome='Receita Anual',
                    tipo=CategoriaFinanceira.TIPO_RECEITA,
                    descricao='Receita anual consolidada',
                    ativa=True
                )
            
            # Verificar se já existe lançamento de receita para este ano
            lancamento_receita_existente = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                descricao__icontains=f"Receita Anual {ano}",
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                data_competencia__year=ano
            ).first()
            
            if not lancamento_receita_existente:
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_receita,
                    conta_destino=conta_padrao,
                    tipo=CategoriaFinanceira.TIPO_RECEITA,
                    descricao=f"Receita Anual {ano}",
                    valor=receita_anual,
                    data_competencia=timezone.datetime(ano, 1, 1).date(),
                    data_vencimento=timezone.datetime(ano, 1, 1).date(),
                    data_quitacao=timezone.datetime(ano, 1, 1).date(),
                    forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                    status=LancamentoFinanceiro.STATUS_QUITADO,
                    observacoes=f"Receita anual gerada automaticamente da planilha"
                )
                lancamentos_criados += 1
        
        # Criar lançamentos de despesas
        if criar_despesas:
            despesas = DespesaConfigurada.objects.filter(
                propriedade=propriedade,
                ativo=True,
                tipo_calculo=DespesaConfigurada.TIPO_PORCENTAGEM
            )
            
            for despesa in despesas:
                valor_anual = despesa.calcular_valor_anual(receita_anual)
                
                if valor_anual > 0:
                    # Verificar se já existe lançamento para esta despesa neste ano
                    lancamento_existente = LancamentoFinanceiro.objects.filter(
                        propriedade=propriedade,
                        descricao__icontains=despesa.nome,
                        tipo=CategoriaFinanceira.TIPO_DESPESA,
                        data_competencia__year=ano
                    ).first()
                    
                    if not lancamento_existente:
                        # Criar 12 lançamentos mensais
                        for mes in range(1, 13):
                            valor_mensal = valor_anual / Decimal("12")
                            data_competencia = timezone.datetime(ano, mes, 1).date()
                            
                            LancamentoFinanceiro.objects.create(
                                propriedade=propriedade,
                                categoria=despesa.categoria_financeira,
                                conta_origem=conta_padrao,
                                tipo=CategoriaFinanceira.TIPO_DESPESA,
                                descricao=f"{despesa.nome} - {data_competencia.strftime('%m/%Y')}",
                                valor=valor_mensal,
                                data_competencia=data_competencia,
                                data_vencimento=data_competencia,
                                forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                                status=LancamentoFinanceiro.STATUS_PENDENTE,
                                observacoes=f"Despesa gerada automaticamente da planilha ({despesa.porcentagem_receita}% da receita)"
                            )
                            lancamentos_criados += 1
    
    messages.success(
        request,
        f"{lancamentos_criados} lançamento(s) financeiro(s) criado(s) com sucesso!"
    )
    url = reverse('financeiro_planilha_despesas', kwargs={'propriedade_id': propriedade_id})
    return HttpResponseRedirect(f"{url}?ano={ano}")
