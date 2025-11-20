"""Views do novo módulo financeiro."""
from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
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
    
    # Gráfico mensal (últimos 12 meses)
    from datetime import timedelta
    from calendar import monthrange
    
    meses_grafico = []
    receitas_mensais = []
    despesas_mensais = []
    
    hoje = timezone.localdate()
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
        
        lancamentos_mes = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia__range=(mes_inicio, mes_fim),
            status=LancamentoFinanceiro.STATUS_QUITADO,
        )
        
        receitas = lancamentos_mes.filter(
            tipo=CategoriaFinanceira.TIPO_RECEITA
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        despesas = lancamentos_mes.filter(
            tipo=CategoriaFinanceira.TIPO_DESPESA
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        meses_grafico.append(mes_inicio.strftime('%m/%Y'))
        receitas_mensais.append(float(receitas))
        despesas_mensais.append(float(despesas))
    
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
        "dados_compras": dados_compras,
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

