# -*- coding: utf-8 -*-
"""
Views para relatórios consolidados multi-propriedade
Sistema para comprovação de empréstimo bancário
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta
from collections import defaultdict

from .models import (
    Propriedade, ProdutorRural, InventarioRebanho, CategoriaAnimal,
    MovimentacaoProjetada, VendaProjetada
)
from .models_financeiro import (
    LancamentoFinanceiro, CategoriaFinanceira, ContaFinanceira,
    ReceitaAnual, DespesaConfigurada, GrupoDespesa, CentroCusto
)
from collections import defaultdict
from .models import BemImobilizado, CategoriaImobilizado


@login_required
def dashboard_consolidado(request):
    """
    Dashboard consolidado para visualização de todas as propriedades
    ou seleção de propriedades específicas.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    # Buscar propriedades do produtor
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Filtro de propriedades (GET parameter)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    # Ano de referência
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Calcular totais consolidados
    totais = calcular_totais_consolidados(propriedades_selecionadas, ano)
    
    # Dados históricos para gráficos (últimos 5 anos)
    anos_historicos = [ano - 4, ano - 3, ano - 2, ano - 1, ano]
    dados_historicos = []
    
    for ano_hist in anos_historicos:
        totais_hist = calcular_totais_consolidados(propriedades_selecionadas, ano_hist)
        dados_historicos.append({
            'ano': ano_hist,
            'rebanho': float(totais_hist['rebanho']['total_cabecas']),
            'valor_rebanho': float(totais_hist['rebanho']['valor_total']),
            'receitas': float(totais_hist['financeiro']['receitas']),
            'despesas': float(totais_hist['financeiro']['despesas']),
            'saldo': float(totais_hist['financeiro']['saldo']),
        })
    
    # Fluxo de caixa mensal do ano atual
    fluxo_mensal = []
    for mes in range(1, 13):
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano, 12, 31)
        else:
            data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
        
        receitas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__range=(data_inicio, data_fim),
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        despesas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__range=(data_inicio, data_fim),
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        fluxo_mensal.append({
            'mes': mes,
            'mes_nome': data_inicio.strftime('%b/%Y'),
            'receitas': float(receitas),
            'despesas': float(despesas),
            'saldo': float(receitas - despesas),
        })
    
    # Dados para gráficos (JSON)
    grafico_historico = {
        'labels': [str(d['ano']) for d in dados_historicos],
        'rebanho': [d['rebanho'] for d in dados_historicos],
        'receitas': [d['receitas'] for d in dados_historicos],
        'despesas': [d['despesas'] for d in dados_historicos],
        'saldo': [d['saldo'] for d in dados_historicos],
    }
    
    grafico_mensal = {
        'labels': [f['mes_nome'] for f in fluxo_mensal],
        'receitas': [f['receitas'] for f in fluxo_mensal],
        'despesas': [f['despesas'] for f in fluxo_mensal],
        'saldo': [f['saldo'] for f in fluxo_mensal],
    }
    
    # Distribuição do rebanho por categoria
    distribuicao_rebanho = []
    for item in totais['rebanho']['inventarios']:
        distribuicao_rebanho.append({
            'categoria': item['categoria__nome'],
            'quantidade': int(item['quantidade_total']),
            'valor': float(item['valor_total']),
        })
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'ano': ano,
        'totais': totais,
        'dados_historicos': dados_historicos,
        'fluxo_mensal': fluxo_mensal,
        'grafico_historico': grafico_historico,
        'grafico_mensal': grafico_mensal,
        'distribuicao_rebanho': distribuicao_rebanho,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/dashboard.html', context)


def calcular_rebanho_por_movimentacoes(propriedade, data_referencia):
    """
    Calcula o rebanho atual baseado no inventário inicial + movimentações projetadas.
    Similar à lógica usada nas projeções da Fazenda Canta Galo.
    """
    from collections import defaultdict
    from datetime import date
    
    # Buscar inventário inicial (mais recente antes da data de referência)
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    if not inventario_inicial:
        return {}
    
    # Buscar todos os inventários da mesma data
    data_inventario = inventario_inicial.data_inventario
    inventarios = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario=data_inventario
    ).select_related('categoria')
    
    # Inicializar saldos com inventário inicial
    saldos = defaultdict(int)
    for inv in inventarios:
        saldos[inv.categoria.nome] = inv.quantidade
    
    # Aplicar todas as movimentações até a data de referência
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__gt=data_inventario,
        data_movimentacao__lte=data_referencia
    ).select_related('categoria')
    
    for mov in movimentacoes:
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldos[categoria] += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldos[categoria] -= mov.quantidade
            # Garantir que não fique negativo
            if saldos[categoria] < 0:
                saldos[categoria] = 0
    
    return dict(saldos)


def calcular_totais_consolidados(propriedades, ano):
    """Calcula totais consolidados de todas as propriedades selecionadas."""
    from django.db.models import Sum, Count, Max
    from datetime import date
    from collections import defaultdict
    
    # Data de referência: final do ano
    data_referencia = date(ano, 12, 31)
    
    # REBANHO - Calcular baseado em inventário + movimentações (como nas projeções)
    saldos_consolidados = defaultdict(int)
    valor_total_consolidado = Decimal('0.00')
    inventarios_por_categoria = defaultdict(lambda: {'quantidade': 0, 'valor_total': Decimal('0.00')})
    
    for propriedade in propriedades:
        # Calcular rebanho atual baseado em movimentações
        saldos_prop = calcular_rebanho_por_movimentacoes(propriedade, data_referencia)
        
        # Buscar valores por categoria do inventário inicial
        inventario_inicial = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).order_by('-data_inventario').first()
        
        if inventario_inicial:
            # Buscar todos os inventários da mesma data para obter valores
            data_inventario = inventario_inicial.data_inventario
            inventarios_valores = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                data_inventario=data_inventario
            ).select_related('categoria')
            
            # Criar dicionário de valores por categoria
            valores_por_categoria = {}
            for inv in inventarios_valores:
                valores_por_categoria[inv.categoria.nome] = inv.valor_por_cabeca
            
            # Consolidar saldos e valores
            for categoria_nome, quantidade in saldos_prop.items():
                saldos_consolidados[categoria_nome] += quantidade
                valor_por_cabeca = valores_por_categoria.get(categoria_nome, Decimal('0.00'))
                valor_categoria = quantidade * valor_por_cabeca
                valor_total_consolidado += valor_categoria
                
                inventarios_por_categoria[categoria_nome]['quantidade'] += quantidade
                inventarios_por_categoria[categoria_nome]['valor_total'] += valor_categoria
    
    # Converter para formato esperado
    inventarios = []
    for categoria_nome, dados in inventarios_por_categoria.items():
        inventarios.append({
            'categoria__nome': categoria_nome,
            'quantidade_total': dados['quantidade'],
            'valor_total': dados['valor_total']
        })
    
    total_cabecas = sum(saldos_consolidados.values())
    
    # BENS
    bens_objs = BemImobilizado.objects.filter(
        propriedade__in=propriedades,
        ativo=True
    )
    total_bens = bens_objs.count()
    valor_total_bens = sum(b.valor_aquisicao for b in bens_objs)
    valor_depreciado = sum(b.depreciacao_acumulada for b in bens_objs)
    
    # FINANCEIRO
    receitas = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    despesas = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    # DRE
    receitas_anuais = ReceitaAnual.objects.filter(
        propriedade__in=propriedades,
        ano=ano
    )
    
    return {
        'rebanho': {
            'inventarios': inventarios,
            'total_cabecas': total_cabecas,
            'valor_total': valor_total_consolidado,
        },
        'bens': {
            'total_bens': total_bens,
            'valor_total': Decimal(str(valor_total_bens)),
            'valor_depreciado': Decimal(str(valor_depreciado)),
            'valor_liquido': Decimal(str(valor_total_bens)) - Decimal(str(valor_depreciado)),
        },
        'financeiro': {
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas,
        },
        'receitas_anuais': receitas_anuais,
    }


@login_required
def cenarios_consolidados(request):
    """
    Sistema de cenários para relatórios consolidados.
    Permite criar e comparar diferentes cenários financeiros.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Calcular dados base (cenário atual)
    totais_base = calcular_totais_consolidados(propriedades_selecionadas, ano)
    dre_base = calcular_dre_consolidado(propriedades_selecionadas, ano)
    
    # Criar cenários padrão para comparação
    cenarios = [
        {
            'nome': 'Cenário Atual',
            'descricao': 'Situação atual consolidada',
            'is_baseline': True,
            'ajuste_receita': Decimal('0.00'),
            'ajuste_despesa': Decimal('0.00'),
            'receitas': totais_base['financeiro']['receitas'],
            'despesas': totais_base['financeiro']['despesas'],
            'saldo': totais_base['financeiro']['saldo'],
            'lucro_liquido': dre_base.get('resultado_liquido', Decimal('0.00')),
            'margem': (dre_base.get('resultado_liquido', Decimal('0.00')) / totais_base['financeiro']['receitas'] * 100) if totais_base['financeiro']['receitas'] > 0 else Decimal('0.00'),
        },
        {
            'nome': 'Cenário Otimista',
            'descricao': 'Aumento de 15% nas receitas, redução de 5% nas despesas',
            'is_baseline': False,
            'ajuste_receita': Decimal('15.00'),
            'ajuste_despesa': Decimal('-5.00'),
            'receitas': totais_base['financeiro']['receitas'] * Decimal('1.15'),
            'despesas': totais_base['financeiro']['despesas'] * Decimal('0.95'),
            'saldo': (totais_base['financeiro']['receitas'] * Decimal('1.15')) - (totais_base['financeiro']['despesas'] * Decimal('0.95')),
            'lucro_liquido': dre_base.get('resultado_liquido', Decimal('0.00')) * Decimal('1.20'),
            'margem': Decimal('0.00'),  # Será calculado
        },
        {
            'nome': 'Cenário Pessimista',
            'descricao': 'Redução de 10% nas receitas, aumento de 10% nas despesas',
            'is_baseline': False,
            'ajuste_receita': Decimal('-10.00'),
            'ajuste_despesa': Decimal('10.00'),
            'receitas': totais_base['financeiro']['receitas'] * Decimal('0.90'),
            'despesas': totais_base['financeiro']['despesas'] * Decimal('1.10'),
            'saldo': (totais_base['financeiro']['receitas'] * Decimal('0.90')) - (totais_base['financeiro']['despesas'] * Decimal('1.10')),
            'lucro_liquido': dre_base.get('resultado_liquido', Decimal('0.00')) * Decimal('0.80'),
            'margem': Decimal('0.00'),  # Será calculado
        },
    ]
    
    # Calcular margens
    for cenario in cenarios:
        if cenario['receitas'] > 0:
            cenario['margem'] = (cenario['lucro_liquido'] / cenario['receitas']) * 100
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'ano': ano,
        'cenarios': cenarios,
        'totais_base': totais_base,
        'dre_base': dre_base,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/cenarios.html', context)


@login_required
def relatorio_rebanho_consolidado(request):
    """
    Relatório consolidado de rebanho para comprovação de empréstimo.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Data de referência: final do ano
    from datetime import date
    data_referencia = date(ano, 12, 31)
    
    # Buscar inventários por propriedade calculando baseado em movimentações (como nas projeções)
    inventarios_detalhados = []
    for propriedade in propriedades_selecionadas:
        # Calcular rebanho atual baseado em movimentações
        saldos_prop = calcular_rebanho_por_movimentacoes(propriedade, data_referencia)
        
        # Buscar valores por categoria do inventário inicial
        inventario_inicial = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).order_by('-data_inventario').first()
        
        inventarios_lista = []
        total_cabecas_prop = 0
        valor_total_prop = Decimal('0.00')
        
        if inventario_inicial:
            # Buscar todos os inventários da mesma data para obter valores
            data_inventario = inventario_inicial.data_inventario
            inventarios_valores = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                data_inventario=data_inventario
            ).select_related('categoria')
            
            # Criar dicionário de valores por categoria
            valores_por_categoria = {}
            for inv in inventarios_valores:
                valores_por_categoria[inv.categoria.nome] = inv.valor_por_cabeca
            
            # Criar lista de inventários com saldos calculados
            for categoria_nome, quantidade in saldos_prop.items():
                if quantidade > 0:
                    valor_por_cabeca = valores_por_categoria.get(categoria_nome, Decimal('0.00'))
                    valor_total_categoria = quantidade * valor_por_cabeca
                    
                    # Buscar objeto categoria
                    try:
                        categoria_obj = inventarios_valores.filter(categoria__nome=categoria_nome).first()
                        if categoria_obj:
                            inventarios_lista.append({
                                'categoria': categoria_obj.categoria,
                                'quantidade': quantidade,
                                'valor_por_cabeca': valor_por_cabeca,
                                'valor_total': valor_total_categoria
                            })
                    except:
                        pass
                    
                    total_cabecas_prop += quantidade
                    valor_total_prop += valor_total_categoria
        
        inventarios_detalhados.append({
            'propriedade': propriedade,
            'inventarios': inventarios_lista,
            'total_cabecas': total_cabecas_prop,
            'valor_total': valor_total_prop,
        })
    
    # Totais consolidados - usar os inventários encontrados
    total_cabecas_geral = 0
    valor_total_geral = Decimal('0.00')
    por_categoria_dict = {}
    
    for item in inventarios_detalhados:
        total_cabecas_geral += item['total_cabecas']
        valor_total_geral += item['valor_total']
        
        # Agrupar por categoria
        for inv in item['inventarios']:
            if isinstance(inv, dict):
                categoria_nome = inv.get('categoria').nome if hasattr(inv.get('categoria'), 'nome') else inv.get('categoria', {}).get('nome', '')
                categoria_id = inv.get('categoria').id if hasattr(inv.get('categoria'), 'id') else inv.get('categoria', {}).get('id', 0)
                quantidade = inv.get('quantidade', 0)
                valor_total_cat = inv.get('valor_total', Decimal('0.00'))
            else:
                categoria_nome = inv.categoria.nome
                categoria_id = inv.categoria.id
                quantidade = inv.quantidade
                valor_total_cat = inv.valor_total
            
            cat_key = (categoria_id, categoria_nome)
            if cat_key not in por_categoria_dict:
                por_categoria_dict[cat_key] = {
                    'categoria__id': categoria_id,
                    'categoria__nome': categoria_nome,
                    'quantidade': 0,
                    'valor_total': Decimal('0.00'),
                }
            por_categoria_dict[cat_key]['quantidade'] += quantidade
            por_categoria_dict[cat_key]['valor_total'] += valor_total_cat
    
    total_geral = {
        'total_cabecas': total_cabecas_geral,
        'valor_total': valor_total_geral,
    }
    
    por_categoria = sorted(por_categoria_dict.values(), key=lambda x: x['categoria__nome'])
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'ano': ano,
        'inventarios_detalhados': inventarios_detalhados,
        'total_geral': {
            'total_cabecas': total_geral.get('total_cabecas', 0) or 0,
            'valor_total': total_geral.get('valor_total', Decimal('0.00')) or Decimal('0.00'),
        },
        'por_categoria': por_categoria,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/rebanho.html', context)


@login_required
def relatorio_bens_consolidado(request):
    """
    Relatório consolidado de bens imobilizados para comprovação de empréstimo.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    # Buscar bens por propriedade
    bens_detalhados = []
    for propriedade in propriedades_selecionadas:
        bens = BemImobilizado.objects.filter(
            propriedade=propriedade,
            ativo=True
        ).select_related('categoria').order_by('categoria__nome', 'nome')
        
        total_bens_prop = bens.count()
        valor_aquisicao_prop = sum(b.valor_aquisicao for b in bens)
        depreciacao_acumulada_prop = sum(b.depreciacao_acumulada for b in bens)
        valor_liquido = Decimal(str(valor_aquisicao_prop)) - Decimal(str(depreciacao_acumulada_prop))
        
        bens_detalhados.append({
            'propriedade': propriedade,
            'bens': bens,
            'total_bens': total_bens_prop,
            'valor_aquisicao': Decimal(str(valor_aquisicao_prop)),
            'depreciacao_acumulada': Decimal(str(depreciacao_acumulada_prop)),
            'valor_liquido': valor_liquido,
        })
    
    # Totais consolidados
    bens_geral = BemImobilizado.objects.filter(
        propriedade__in=propriedades_selecionadas,
        ativo=True
    )
    total_bens_geral = bens_geral.count()
    valor_aquisicao_geral = sum(b.valor_aquisicao for b in bens_geral)
    depreciacao_acumulada_geral = sum(b.depreciacao_acumulada for b in bens_geral)
    valor_liquido_geral = Decimal(str(valor_aquisicao_geral)) - Decimal(str(depreciacao_acumulada_geral))
    
    # Por categoria (consolidado)
    por_categoria_dict = {}
    for bem in bens_geral:
        cat_key = (bem.categoria.id, bem.categoria.nome)
        if cat_key not in por_categoria_dict:
            por_categoria_dict[cat_key] = {
                'categoria__id': bem.categoria.id,
                'categoria__nome': bem.categoria.nome,
                'quantidade': 0,
                'valor_aquisicao': Decimal('0.00'),
                'depreciacao_acumulada': Decimal('0.00'),
            }
        por_categoria_dict[cat_key]['quantidade'] += 1
        por_categoria_dict[cat_key]['valor_aquisicao'] += bem.valor_aquisicao
        por_categoria_dict[cat_key]['depreciacao_acumulada'] += bem.depreciacao_acumulada
    por_categoria = list(por_categoria_dict.values())
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'bens_detalhados': bens_detalhados,
        'total_geral': {
            'total_bens': total_bens_geral,
            'valor_aquisicao': Decimal(str(valor_aquisicao_geral)),
            'depreciacao_acumulada': Decimal(str(depreciacao_acumulada_geral)),
            'valor_liquido': valor_liquido_geral,
        },
        'por_categoria': por_categoria,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/bens.html', context)


@login_required
def relatorio_dre_consolidado(request):
    """
    Relatório consolidado de DRE (Demonstração do Resultado do Exercício)
    para comprovação de empréstimo.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Buscar receitas anuais de cada propriedade
    receitas_anuais = ReceitaAnual.objects.filter(
        propriedade__in=propriedades_selecionadas,
        ano=ano
    ).select_related('propriedade')
    
    # Calcular DRE consolidado
    dre_consolidado = calcular_dre_consolidado(propriedades_selecionadas, ano)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'ano': ano,
        'receitas_anuais': receitas_anuais,
        'dre_consolidado': dre_consolidado,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/dre.html', context)


def calcular_dre_consolidado(propriedades, ano):
    """Calcula DRE consolidado de todas as propriedades com despesas detalhadas."""
    receitas_anuais = ReceitaAnual.objects.filter(
        propriedade__in=propriedades,
        ano=ano
    )
    
    # Consolidar valores
    receita_bruta = sum(r.valor_receita for r in receitas_anuais)
    
    # Deduções
    icms_vendas = sum(r.icms_vendas or Decimal('0.00') for r in receitas_anuais)
    funrural_vendas = sum(r.funviral_vendas or Decimal('0.00') for r in receitas_anuais)
    outros_impostos_vendas = sum(r.outros_impostos_vendas or Decimal('0.00') for r in receitas_anuais)
    devolucoes_vendas = sum(r.devolucoes_vendas or Decimal('0.00') for r in receitas_anuais)
    abatimentos_vendas = sum(r.abatimentos_vendas or Decimal('0.00') for r in receitas_anuais)
    
    total_deducoes = icms_vendas + funrural_vendas + outros_impostos_vendas + devolucoes_vendas + abatimentos_vendas
    receita_liquida = receita_bruta - total_deducoes
    
    # CPV
    cpv = sum(r.custo_produtos_vendidos or Decimal('0.00') for r in receitas_anuais)
    lucro_bruto = receita_liquida - cpv
    
    # Despesas operacionais detalhadas
    retirada_labore = sum(r.retirada_labore or Decimal('0.00') for r in receitas_anuais)
    assistencia_contabil = sum(r.assistencia_contabil or Decimal('0.00') for r in receitas_anuais)
    encargos_inss = sum(r.encargos_inss or Decimal('0.00') for r in receitas_anuais)
    taxas_diversas = sum(r.taxas_diversas or Decimal('0.00') for r in receitas_anuais)
    despesas_administrativas = sum(r.despesas_administrativas or Decimal('0.00') for r in receitas_anuais)
    material_uso_consumo = sum(r.material_uso_consumo or Decimal('0.00') for r in receitas_anuais)
    despesas_comunicacao = sum(r.despesas_comunicacao or Decimal('0.00') for r in receitas_anuais)
    despesas_viagens = sum(r.despesas_viagens or Decimal('0.00') for r in receitas_anuais)
    despesas_energia_eletrica = sum(r.despesas_energia_eletrica or Decimal('0.00') for r in receitas_anuais)
    despesas_transportes = sum(r.despesas_transportes or Decimal('0.00') for r in receitas_anuais)
    despesas_combustivel = sum(r.despesas_combustivel or Decimal('0.00') for r in receitas_anuais)
    despesas_manutencao = sum(r.despesas_manutencao or Decimal('0.00') for r in receitas_anuais)
    depreciacao = sum(r.depreciacao_amortizacao or Decimal('0.00') for r in receitas_anuais)
    
    # Total despesas detalhadas
    despesas_detalhadas = (
        retirada_labore + assistencia_contabil + encargos_inss + taxas_diversas +
        despesas_administrativas + material_uso_consumo + despesas_comunicacao +
        despesas_viagens + despesas_energia_eletrica + despesas_transportes +
        despesas_combustivel + despesas_manutencao + depreciacao
    )
    
    # Despesas configuradas (grupos)
    despesas_configuradas = Decimal('0.00')
    despesas_por_grupo = defaultdict(lambda: {'fixas': Decimal('0.00'), 'variaveis': Decimal('0.00')})
    
    for r in receitas_anuais:
        despesas = DespesaConfigurada.objects.filter(
            propriedade=r.propriedade,
            ativo=True
        ).select_related('grupo')
        
        for despesa in despesas:
            valor_anual = despesa.calcular_valor_anual(r.valor_receita)
            despesas_configuradas += valor_anual
            
            if despesa.grupo.tipo == GrupoDespesa.TIPO_FIXA:
                despesas_por_grupo[despesa.grupo.nome]['fixas'] += valor_anual
            else:
                despesas_por_grupo[despesa.grupo.nome]['variaveis'] += valor_anual
    
    total_despesas_fixas = sum(d['fixas'] for d in despesas_por_grupo.values())
    total_despesas_variaveis = sum(d['variaveis'] for d in despesas_por_grupo.values())
    
    # Total despesas operacionais
    despesas_operacionais = despesas_detalhadas + despesas_configuradas
    
    # Resultado operacional
    resultado_operacional = lucro_bruto - despesas_operacionais
    
    # Resultado financeiro
    despesas_financeiras = sum(r.despesas_financeiras or Decimal('0.00') for r in receitas_anuais)
    receitas_financeiras = sum(r.receitas_financeiras or Decimal('0.00') for r in receitas_anuais)
    resultado_financeiro = receitas_financeiras - despesas_financeiras
    
    # LAIR
    lair = resultado_operacional + resultado_financeiro
    
    # Impostos
    csll = sum(r.csll or Decimal('0.00') for r in receitas_anuais)
    irpj = sum(r.irpj or Decimal('0.00') for r in receitas_anuais)
    total_impostos = csll + irpj
    
    # Resultado líquido
    resultado_liquido = lair - total_impostos
    
    return {
        'receita_bruta': receita_bruta,
        'icms_vendas': icms_vendas,
        'funrural_vendas': funrural_vendas,
        'outros_impostos_vendas': outros_impostos_vendas,
        'devolucoes_vendas': devolucoes_vendas,
        'abatimentos_vendas': abatimentos_vendas,
        'total_deducoes': total_deducoes,
        'receita_liquida': receita_liquida,
        'cpv': cpv,
        'lucro_bruto': lucro_bruto,
        'despesas_operacionais': despesas_operacionais,
        'despesas_detalhadas': despesas_detalhadas,
        'despesas_configuradas': despesas_configuradas,
        'despesas_por_grupo': dict(despesas_por_grupo),
        'total_despesas_fixas': total_despesas_fixas,
        'total_despesas_variaveis': total_despesas_variaveis,
        'retirada_labore': retirada_labore,
        'assistencia_contabil': assistencia_contabil,
        'encargos_inss': encargos_inss,
        'taxas_diversas': taxas_diversas,
        'despesas_administrativas': despesas_administrativas,
        'material_uso_consumo': material_uso_consumo,
        'despesas_comunicacao': despesas_comunicacao,
        'despesas_viagens': despesas_viagens,
        'despesas_energia_eletrica': despesas_energia_eletrica,
        'despesas_transportes': despesas_transportes,
        'despesas_combustivel': despesas_combustivel,
        'despesas_manutencao': despesas_manutencao,
        'depreciacao': depreciacao,
        'resultado_operacional': resultado_operacional,
        'despesas_financeiras': despesas_financeiras,
        'receitas_financeiras': receitas_financeiras,
        'resultado_financeiro': resultado_financeiro,
        'lair': lair,
        'csll': csll,
        'irpj': irpj,
        'total_impostos': total_impostos,
        'resultado_liquido': resultado_liquido,
    }


@login_required
def relatorio_fluxo_caixa_consolidado(request):
    """
    Relatório consolidado de Fluxo de Caixa para comprovação de empréstimo.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Calcular fluxo de caixa mensal consolidado
    fluxo_mensal = []
    saldo_acumulado = Decimal('0.00')
    
    for mes in range(1, 13):
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano, 12, 31)
        else:
            data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
        
        # Receitas do mês
        receitas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__range=(data_inicio, data_fim),
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # Despesas do mês
        despesas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__range=(data_inicio, data_fim),
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        fluxo_liquido = receitas - despesas
        saldo_acumulado += fluxo_liquido
        
        fluxo_mensal.append({
            'mes': mes,
            'mes_nome': data_inicio.strftime('%B/%Y'),
            'receitas': receitas,
            'despesas': despesas,
            'fluxo_liquido': fluxo_liquido,
            'saldo_acumulado': saldo_acumulado,
        })
    
    # Totais anuais
    receitas_anuais = sum(f['receitas'] for f in fluxo_mensal)
    despesas_anuais = sum(f['despesas'] for f in fluxo_mensal)
    fluxo_liquido_anual = receitas_anuais - despesas_anuais
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'ano': ano,
        'fluxo_mensal': fluxo_mensal,
        'totais': {
            'receitas': receitas_anuais,
            'despesas': despesas_anuais,
            'fluxo_liquido': fluxo_liquido_anual,
            'saldo_final': saldo_acumulado,
        },
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/fluxo_caixa.html', context)


@login_required
def relatorio_completo_emprestimo(request):
    """
    Relatório completo para comprovação de empréstimo bancário.
    Consolida todos os dados: Rebanho, Bens, Financeiro, DRE, Fluxo de Caixa, Produção, Endividamento.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Buscar todos os dados consolidados
    totais = calcular_totais_consolidados(propriedades_selecionadas, ano)
    dre_consolidado = calcular_dre_consolidado(propriedades_selecionadas, ano)
    
    # Fluxo de caixa mensal
    fluxo_mensal = []
    saldo_acumulado = Decimal('0.00')
    
    for mes in range(1, 13):
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano, 12, 31)
        else:
            data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
        
        receitas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__range=(data_inicio, data_fim),
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        despesas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__range=(data_inicio, data_fim),
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        fluxo_liquido = receitas - despesas
        saldo_acumulado += fluxo_liquido
        
        fluxo_mensal.append({
            'mes': mes,
            'mes_nome': data_inicio.strftime('%B/%Y'),
            'receitas': receitas,
            'despesas': despesas,
            'fluxo_liquido': fluxo_liquido,
            'saldo_acumulado': saldo_acumulado,
        })
    
    # DADOS DE PRODUÇÃO (Vendas Projetadas e Movimentações)
    vendas_projetadas = VendaProjetada.objects.filter(
        propriedade__in=propriedades_selecionadas,
        data_venda__year=ano
    ).select_related('categoria', 'propriedade')
    
    total_vendas_producao = vendas_projetadas.aggregate(
        total_quantidade=Sum('quantidade'),
        total_valor=Sum('valor_total')
    )
    
    # Movimentações projetadas
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade__in=propriedades_selecionadas,
        data_movimentacao__year=ano
    ).select_related('categoria', 'propriedade')
    
    movimentacoes_por_tipo = movimentacoes.values('tipo_movimentacao').annotate(
        quantidade_total=Sum('quantidade'),
        valor_total=Sum('valor_total')
    )
    
    # DADOS DE ENDIVIDAMENTO (SCR)
    from .models import SCRBancoCentral, DividaBanco
    scr = SCRBancoCentral.objects.filter(
        produtor=produtor
    ).order_by('-data_referencia_scr').first()
    
    dividas_por_banco = []
    total_dividas = Decimal('0.00')
    if scr:
        dividas_por_banco = DividaBanco.objects.filter(scr=scr).order_by('banco')
        total_dividas = sum(d.valor_total_divida for d in dividas_por_banco)
    
    # Capacidade de pagamento
    from .views_justificativa_endividamento import calcular_capacidade_pagamento
    capacidade_pagamento = calcular_capacidade_pagamento(propriedades_selecionadas, ano)
    
    # Histórico de receitas (últimos 3 anos)
    historico_receitas = []
    for ano_hist in range(ano - 2, ano + 1):
        receitas_ano = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__year=ano_hist,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        despesas_ano = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades_selecionadas,
            data_competencia__year=ano_hist,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        historico_receitas.append({
            'ano': ano_hist,
            'receitas': receitas_ano,
            'despesas': despesas_ano,
            'saldo': receitas_ano - despesas_ano,
        })
    
    # Indicadores financeiros
    patrimonio_total = totais['rebanho']['valor_total'] + totais['bens']['valor_liquido']
    valor_emprestimo = Decimal('20000000.00')
    cobertura_patrimonial = (patrimonio_total / valor_emprestimo * 100) if valor_emprestimo > 0 else Decimal('0.00')
    cobertura_receitas = (totais['financeiro']['receitas'] / valor_emprestimo * 100) if valor_emprestimo > 0 else Decimal('0.00')
    
    # Calcular margem de lucro
    margem_lucro = Decimal('0.00')
    if dre_consolidado['receita_bruta'] > 0:
        margem_lucro = (dre_consolidado['resultado_liquido'] / dre_consolidado['receita_bruta']) * 100
    
    # Calcular valores médios por cabeça para o rebanho
    valor_medio_por_cabeca = Decimal('0.00')
    if totais['rebanho']['total_cabecas'] > 0:
        valor_medio_por_cabeca = totais['rebanho']['valor_total'] / Decimal(str(totais['rebanho']['total_cabecas']))
    
    # Adicionar valor médio aos inventários (converter queryset para lista)
    inventarios_lista = list(totais['rebanho']['inventarios'])
    inventarios_com_medio = []
    for item in inventarios_lista:
        valor_medio_item = Decimal('0.00')
        quantidade = item.get('quantidade_total', 0) or 0
        valor_total_item = Decimal(str(item.get('valor_total', 0) or 0))
        if quantidade > 0:
            valor_medio_item = valor_total_item / Decimal(str(quantidade))
        item_dict = dict(item)
        item_dict['valor_medio'] = valor_medio_item
        inventarios_com_medio.append(item_dict)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'propriedades_selecionadas': propriedades_selecionadas,
        'ano': ano,
        'totais': totais,
        'dre_consolidado': dre_consolidado,
        'fluxo_mensal': fluxo_mensal,
        'valor_emprestimo': valor_emprestimo,
        # Dados de produção
        'vendas_projetadas': list(vendas_projetadas[:50]),  # Limitar para não sobrecarregar
        'total_vendas_producao': {
            'quantidade': total_vendas_producao.get('total_quantidade', 0) or 0,
            'valor': total_vendas_producao.get('total_valor', Decimal('0.00')) or Decimal('0.00'),
        },
        'movimentacoes_por_tipo': list(movimentacoes_por_tipo),
        # Dados de endividamento
        'scr': scr,
        'dividas_por_banco': list(dividas_por_banco),
        'total_dividas': total_dividas,
        'capacidade_pagamento': capacidade_pagamento,
        # Histórico e indicadores
        'historico_receitas': historico_receitas,
        'patrimonio_total': patrimonio_total,
        'cobertura_patrimonial': cobertura_patrimonial,
        'cobertura_receitas': cobertura_receitas,
        'margem_lucro': margem_lucro,
        'valor_medio_por_cabeca': valor_medio_por_cabeca,
        'inventarios_com_medio': inventarios_com_medio,
    }
    
    return render(request, 'gestao_rural/relatorios_consolidados/relatorio_completo_emprestimo.html', context)


@login_required
def exportar_relatorio_completo_pdf(request):
    """
    Exporta relatório completo em PDF para comprovação de empréstimo.
    """
    # Buscar produtor do usuário (pode haver múltiplos, usar o primeiro)
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    if not produtor:
        return redirect('landing_page')
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    propriedades_selecionadas_ids = request.GET.getlist('propriedades')
    
    if propriedades_selecionadas_ids:
        propriedades_selecionadas = propriedades.filter(id__in=propriedades_selecionadas_ids)
    else:
        propriedades_selecionadas = propriedades
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except (ValueError, TypeError):
        ano = timezone.now().year
    
    # Usar a mesma lógica do relatório completo
    from .views_financeiro import exportar_dre_pdf
    
    # Por enquanto, retornar JSON com os dados
    # TODO: Implementar geração de PDF completo
    totais = calcular_totais_consolidados(propriedades_selecionadas, ano)
    dre_consolidado = calcular_dre_consolidado(propriedades_selecionadas, ano)
    
    return JsonResponse({
        'produtor': {
            'nome': produtor.nome,
            'cpf_cnpj': produtor.cpf_cnpj,
        },
        'propriedades': [p.nome_propriedade for p in propriedades_selecionadas],
        'ano': ano,
        'totais': {
            'rebanho': {
                'total_cabecas': int(totais['rebanho']['total_cabecas']),
                'valor_total': str(totais['rebanho']['valor_total']),
            },
            'bens': {
                'total_bens': int(totais['bens']['total_bens']),
                'valor_total': str(totais['bens']['valor_total']),
                'valor_liquido': str(totais['bens']['valor_liquido']),
            },
            'financeiro': {
                'receitas': str(totais['financeiro']['receitas']),
                'despesas': str(totais['financeiro']['despesas']),
                'saldo': str(totais['financeiro']['saldo']),
            },
        },
        'dre': {k: str(v) for k, v in dre_consolidado.items()},
    })

