"""
Views para os novos módulos: Bens, Financeiro e Projetos
Adicionar ao final do arquivo gestao_rural/views.py
"""

# ============================================================
# MÓDULO: BENS E PATRIMÔNIO
# ============================================================

@login_required
def patrimonio_dashboard(request, propriedade_id):
    """Dashboard de Bens e Patrimônio"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'total_bens': 0,
        'valor_total': '0,00',
        'depreciacao_total': '0,00',
        'valor_atual': '0,00',
        'terras_valor': '0,00',
        'maquinas_valor': '0,00',
        'veiculos_valor': '0,00',
        'instalacoes_valor': '0,00',
        'bens': [],
    }
    
    return render(request, 'gestao_rural/patrimonio_dashboard.html', context)


# ============================================================
# MÓDULO: FINANCEIRO
# ============================================================

@login_required
def financeiro_dashboard(request, propriedade_id):
    """Dashboard Financeiro"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'total_receitas': '0,00',
        'total_despesas': '0,00',
        'saldo': '0,00',
        'margem': '0',
        'lancamentos': [],
    }
    
    return render(request, 'gestao_rural/financeiro_dashboard.html', context)


# ============================================================
# MÓDULO: PROJETOS
# ============================================================

@login_required
def projetos_dashboard(request, propriedade_id):
    """Dashboard de Projetos"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'total_projetos': 0,
        'em_andamento': 0,
        'orcamento_total': '0,00',
        'realizado': '0,00',
        'projetos': [],
    }
    
    return render(request, 'gestao_rural/projetos_dashboard.html', context)

