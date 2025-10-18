from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import ProdutorRural, Propriedade, InventarioRebanho, CustoFixo, CustoVariavel, Financiamento
from .models import BemImobilizado, CategoriaImobilizado, IndicadorFinanceiro


def proprietario_dashboard(request, produtor_id):
    """Dashboard consolidado do proprietário com todas as propriedades"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Dados consolidados
    dados_consolidados = consolidar_dados_proprietario(produtor, propriedades)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'dados_consolidados': dados_consolidados,
    }
    
    return render(request, 'gestao_rural/proprietario_dashboard.html', context)


def consolidar_dados_proprietario(produtor, propriedades):
    """Consolida dados de todas as propriedades do proprietário"""
    dados = {}
    
    try:
        # 1. DADOS BÁSICOS
        dados['total_propriedades'] = propriedades.count()
        dados['total_hectares'] = sum(p.area_total_hectares for p in propriedades if p.area_total_hectares)
        
        # 2. INVENTÁRIO CONSOLIDADO
        inventarios = InventarioRebanho.objects.filter(propriedade__in=propriedades)
        dados['total_animais'] = sum(inv.quantidade for inv in inventarios)
        dados['valor_total_rebanho'] = sum(inv.valor_total for inv in inventarios if inv.valor_total)
        
        # 3. CUSTOS CONSOLIDADOS
        custos_fixos = CustoFixo.objects.filter(propriedade__in=propriedades, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade__in=propriedades, ativo=True)
        
        dados['custo_fixo_total'] = sum(c.custo_anual for c in custos_fixos)
        dados['custo_variavel_total'] = sum(c.custo_anual_por_cabeca for c in custos_variaveis)
        dados['custo_total'] = dados['custo_fixo_total'] + dados['custo_variavel_total']
        
        # 4. DÍVIDAS CONSOLIDADAS
        financiamentos = Financiamento.objects.filter(propriedade__in=propriedades, ativo=True)
        dados['total_financiamentos'] = financiamentos.count()
        dados['valor_total_principal'] = sum(f.valor_principal for f in financiamentos)
        dados['parcelas_mensais_total'] = sum(f.valor_parcela for f in financiamentos)
        
        # 5. IMOBILIZADO CONSOLIDADO
        bens = BemImobilizado.objects.filter(propriedade__in=propriedades, ativo=True)
        dados['total_bens'] = bens.count()
        dados['valor_total_imobilizado'] = sum(b.valor_aquisicao for b in bens)
        dados['depreciacao_total'] = sum(b.depreciacao_acumulada for b in bens)
        
        # 6. INDICADORES FINANCEIROS CONSOLIDADOS
        receita_estimada = dados['valor_total_rebanho'] * Decimal('0.15')  # 15% ao ano
        custos_totais = dados['custo_total'] + (dados['parcelas_mensais_total'] * 12)
        
        dados['receita_anual_estimada'] = receita_estimada
        dados['margem_bruta'] = receita_estimada - custos_totais
        dados['indice_rentabilidade'] = (dados['margem_bruta'] / receita_estimada * 100) if receita_estimada > 0 else 0
        dados['indice_endividamento'] = (dados['parcelas_mensais_total'] * 12 / receita_estimada * 100) if receita_estimada > 0 else 0
        
        # 7. CLASSIFICAÇÃO GERAL
        if dados['indice_rentabilidade'] >= 20:
            dados['classificacao'] = "Excelente"
            dados['cor_classificacao'] = "success"
        elif dados['indice_rentabilidade'] >= 10:
            dados['classificacao'] = "Boa"
            dados['cor_classificacao'] = "info"
        elif dados['indice_rentabilidade'] >= 0:
            dados['classificacao'] = "Adequada"
            dados['cor_classificacao'] = "warning"
        else:
            dados['classificacao'] = "Crítica"
            dados['cor_classificacao'] = "danger"
        
        # 8. DADOS POR PROPRIEDADE
        dados['propriedades_detalhadas'] = []
        for prop in propriedades:
            prop_data = {
                'propriedade': prop,
                'inventario': InventarioRebanho.objects.filter(propriedade=prop),
                'custos_fixos': CustoFixo.objects.filter(propriedade=prop, ativo=True),
                'financiamentos': Financiamento.objects.filter(propriedade=prop, ativo=True),
                'bens': BemImobilizado.objects.filter(propriedade=prop, ativo=True),
            }
            dados['propriedades_detalhadas'].append(prop_data)
        
    except Exception as e:
        print(f"Erro ao consolidar dados: {e}")
        dados = {'erro': str(e)}
    
    return dados


def proprietario_dividas_consolidadas(request, produtor_id):
    """Dívidas consolidadas de todas as propriedades"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Busca todos os financiamentos
    financiamentos = Financiamento.objects.filter(propriedade__in=propriedades, ativo=True)
    
    # Dados consolidados
    total_principal = sum(f.valor_principal for f in financiamentos)
    total_parcelas = sum(f.valor_parcela for f in financiamentos)
    total_pago = sum(f.valor_pago for f in financiamentos)
    total_restante = total_principal - total_pago
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'financiamentos': financiamentos,
        'total_principal': total_principal,
        'total_parcelas': total_parcelas,
        'total_pago': total_pago,
        'total_restante': total_restante,
    }
    
    return render(request, 'gestao_rural/proprietario_dividas_consolidadas.html', context)


def proprietario_capacidade_consolidada(request, produtor_id):
    """Capacidade de pagamento consolidada"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Calcula indicadores consolidados
    indicadores = calcular_capacidade_consolidada(produtor, propriedades)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'indicadores': indicadores,
    }
    
    return render(request, 'gestao_rural/proprietario_capacidade_consolidada.html', context)


def calcular_capacidade_consolidada(produtor, propriedades):
    """Calcula capacidade de pagamento consolidada"""
    indicadores = {}
    
    try:
        # Receitas consolidadas
        inventarios = InventarioRebanho.objects.filter(propriedade__in=propriedades)
        valor_rebanho_total = sum(inv.valor_total for inv in inventarios if inv.valor_total)
        receita_anual_estimada = valor_rebanho_total * Decimal('0.15')
        
        # Custos consolidados
        custos_fixos = CustoFixo.objects.filter(propriedade__in=propriedades, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade__in=propriedades, ativo=True)
        financiamentos = Financiamento.objects.filter(propriedade__in=propriedades, ativo=True)
        
        custo_fixo_total = sum(c.custo_anual for c in custos_fixos)
        custo_variavel_total = sum(c.custo_anual_por_cabeca for c in custos_variaveis)
        parcelas_anuais = sum(f.valor_parcela for f in financiamentos) * 12
        
        custos_totais = custo_fixo_total + custo_variavel_total + parcelas_anuais
        
        # Indicadores
        margem_seguranca = receita_anual_estimada - custos_totais
        indice_capacidade = (receita_anual_estimada / custos_totais * 100) if custos_totais > 0 else 0
        indice_endividamento = (parcelas_anuais / receita_anual_estimada * 100) if receita_anual_estimada > 0 else 0
        
        # Classificação
        if indice_capacidade >= 150:
            classificacao = "Excelente"
            cor = "success"
        elif indice_capacidade >= 120:
            classificacao = "Boa"
            cor = "info"
        elif indice_capacidade >= 100:
            classificacao = "Adequada"
            cor = "warning"
        else:
            classificacao = "Crítica"
            cor = "danger"
        
        indicadores = {
            'receita_anual': receita_anual_estimada,
            'custos_totais': custos_totais,
            'parcelas_anuais': parcelas_anuais,
            'margem_seguranca': margem_seguranca,
            'indice_capacidade': indice_capacidade,
            'indice_endividamento': indice_endividamento,
            'classificacao': classificacao,
            'cor': cor
        }
        
    except Exception as e:
        print(f"Erro ao calcular capacidade consolidada: {e}")
        indicadores = {'erro': str(e)}
    
    return indicadores


def proprietario_imobilizado_consolidado(request, produtor_id):
    """Imobilizado consolidado de todas as propriedades"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Busca todos os bens
    bens = BemImobilizado.objects.filter(propriedade__in=propriedades, ativo=True)
    categorias = CategoriaImobilizado.objects.all()
    
    # Dados consolidados
    valor_total = sum(b.valor_aquisicao for b in bens)
    depreciacao_total = sum(b.depreciacao_acumulada for b in bens)
    valor_liquido = valor_total - depreciacao_total
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'bens': bens,
        'categorias': categorias,
        'valor_total': valor_total,
        'depreciacao_total': depreciacao_total,
        'valor_liquido': valor_liquido,
    }
    
    return render(request, 'gestao_rural/proprietario_imobilizado_consolidado.html', context)


def proprietario_analise_consolidada(request, produtor_id):
    """Análise consolidada de todas as propriedades"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Calcula indicadores consolidados
    indicadores = calcular_indicadores_consolidados(produtor, propriedades)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'indicadores': indicadores,
    }
    
    return render(request, 'gestao_rural/proprietario_analise_consolidada.html', context)


def calcular_indicadores_consolidados(produtor, propriedades):
    """Calcula indicadores financeiros consolidados"""
    indicadores = {}
    
    try:
        # Dados básicos
        inventarios = InventarioRebanho.objects.filter(propriedade__in=propriedades)
        custos_fixos = CustoFixo.objects.filter(propriedade__in=propriedades, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade__in=propriedades, ativo=True)
        financiamentos = Financiamento.objects.filter(propriedade__in=propriedades, ativo=True)
        bens = BemImobilizado.objects.filter(propriedade__in=propriedades, ativo=True)
        
        # Receitas
        valor_rebanho = sum(inv.valor_total for inv in inventarios if inv.valor_total)
        receita_anual = valor_rebanho * Decimal('0.15')
        
        # Custos
        custo_fixo_total = sum(c.custo_anual for c in custos_fixos)
        custo_variavel_total = sum(c.custo_anual_por_cabeca for c in custos_variaveis)
        parcelas_anuais = sum(f.valor_parcela for f in financiamentos) * 12
        
        # Imobilizado
        valor_imobilizado = sum(b.valor_aquisicao for b in bens)
        depreciacao_total = sum(b.depreciacao_acumulada for b in bens)
        
        # Indicadores
        margem_bruta = receita_anual - (custo_fixo_total + custo_variavel_total)
        margem_liquida = margem_bruta - parcelas_anuais
        
        indicadores = {
            'receita_anual': receita_anual,
            'custo_total': custo_fixo_total + custo_variavel_total,
            'parcelas_anuais': parcelas_anuais,
            'margem_bruta': margem_bruta,
            'margem_liquida': margem_liquida,
            'valor_imobilizado': valor_imobilizado,
            'depreciacao_total': depreciacao_total,
            'valor_liquido_imobilizado': valor_imobilizado - depreciacao_total,
            'indice_rentabilidade': (margem_liquida / receita_anual * 100) if receita_anual > 0 else 0,
            'indice_endividamento': (parcelas_anuais / receita_anual * 100) if receita_anual > 0 else 0,
        }
        
    except Exception as e:
        print(f"Erro ao calcular indicadores: {e}")
        indicadores = {'erro': str(e)}
    
    return indicadores


def proprietario_relatorios_consolidados(request, produtor_id):
    """Relatórios consolidados de todas as propriedades"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    # Gera relatórios consolidados
    relatorios = gerar_relatorios_consolidados(produtor, propriedades)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
        'relatorios': relatorios,
    }
    
    return render(request, 'gestao_rural/proprietario_relatorios_consolidados.html', context)


def gerar_relatorios_consolidados(produtor, propriedades):
    """Gera relatórios consolidados"""
    relatorios = {}
    
    try:
        # Relatório de Inventário
        inventarios = InventarioRebanho.objects.filter(propriedade__in=propriedades)
        relatorios['inventario'] = {
            'total_animais': sum(inv.quantidade for inv in inventarios),
            'valor_total': sum(inv.valor_total for inv in inventarios if inv.valor_total),
            'por_propriedade': []
        }
        
        for prop in propriedades:
            inv_prop = inventarios.filter(propriedade=prop)
            relatorios['inventario']['por_propriedade'].append({
                'propriedade': prop,
                'total_animais': sum(inv.quantidade for inv in inv_prop),
                'valor_total': sum(inv.valor_total for inv in inv_prop if inv.valor_total)
            })
        
        # Relatório de Custos
        custos_fixos = CustoFixo.objects.filter(propriedade__in=propriedades, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade__in=propriedades, ativo=True)
        
        relatorios['custos'] = {
            'fixo_total': sum(c.custo_anual for c in custos_fixos),
            'variavel_total': sum(c.custo_anual_por_cabeca for c in custos_variaveis),
            'total': sum(c.custo_anual for c in custos_fixos) + sum(c.custo_anual_por_cabeca for c in custos_variaveis)
        }
        
        # Relatório de Dívidas
        financiamentos = Financiamento.objects.filter(propriedade__in=propriedades, ativo=True)
        relatorios['dividas'] = {
            'total_financiamentos': financiamentos.count(),
            'valor_total': sum(f.valor_principal for f in financiamentos),
            'parcelas_mensais': sum(f.valor_parcela for f in financiamentos),
            'valor_pago': sum(f.valor_pago for f in financiamentos),
            'valor_restante': sum(f.valor_principal for f in financiamentos) - sum(f.valor_pago for f in financiamentos)
        }
        
        # Relatório de Imobilizado
        bens = BemImobilizado.objects.filter(propriedade__in=propriedades, ativo=True)
        relatorios['imobilizado'] = {
            'total_bens': bens.count(),
            'valor_total': sum(b.valor_aquisicao for b in bens),
            'depreciacao_total': sum(b.depreciacao_acumulada for b in bens),
            'valor_liquido': sum(b.valor_aquisicao for b in bens) - sum(b.depreciacao_acumulada for b in bens)
        }
        
    except Exception as e:
        print(f"Erro ao gerar relatórios: {e}")
        relatorios = {'erro': str(e)}
    
    return relatorios

