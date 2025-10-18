from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Propriedade, InventarioRebanho, CustoFixo, CustoVariavel, Financiamento, IndicadorFinanceiro


def projetos_bancarios_dashboard(request, propriedade_id):
    """Dashboard centralizado de projetos bancários"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca dados de todos os módulos
    dados_consolidados = consolidar_dados_propriedade(propriedade)
    
    # Indicadores financeiros automáticos
    indicadores = calcular_indicadores_automaticos(propriedade)
    
    # Projeções financeiras
    projecoes = gerar_projecoes_financeiras(propriedade)
    
    context = {
        'propriedade': propriedade,
        'dados_consolidados': dados_consolidados,
        'indicadores': indicadores,
        'projecoes': projecoes,
    }
    
    return render(request, 'gestao_rural/projetos_bancarios_dashboard.html', context)


def consolidar_dados_propriedade(propriedade):
    """Consolida dados de todos os módulos da propriedade"""
    dados = {}
    
    try:
        # 1. DADOS DO REBANHO (Pecuária)
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        dados['rebanho'] = {
            'total_animais': sum(item.quantidade for item in inventario),
            'valor_total': sum(item.valor_total for item in inventario if item.valor_total),
            'categorias': len(inventario),
            'detalhes': list(inventario.values('categoria__nome', 'quantidade', 'valor_total'))
        }
        
        # 2. CUSTOS DE PRODUÇÃO
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
        
        dados['custos'] = {
            'fixos_mensal': sum(custo.valor_mensal for custo in custos_fixos if custo.valor_mensal),
            'fixos_anual': sum(custo.custo_anual for custo in custos_fixos),
            'variaveis_anual': sum(custo.custo_anual_por_cabeca for custo in custos_variaveis),
            'total_anual': sum(custo.custo_anual for custo in custos_fixos) + 
                          sum(custo.custo_anual_por_cabeca for custo in custos_variaveis)
        }
        
        # 3. ENDIVIDAMENTO
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        dados['endividamento'] = {
            'total_financiado': sum(f.valor_principal for f in financiamentos),
            'parcelas_mensais': sum(f.valor_parcela for f in financiamentos),
            'parcelas_anuais': sum(f.valor_parcela for f in financiamentos) * 12,
            'financiamentos_ativos': len(financiamentos),
            'detalhes': list(financiamentos.values('nome', 'valor_principal', 'valor_parcela', 'numero_parcelas'))
        }
        
        # 4. ANÁLISE FINANCEIRA
        dados['analise'] = {
            'receita_potencial': dados['rebanho']['valor_total'] * Decimal('0.15'),  # 15% ao ano
            'custos_totais': dados['custos']['total_anual'] + dados['endividamento']['parcelas_anuais'],
            'lucro_estimado': (dados['rebanho']['valor_total'] * Decimal('0.15')) - 
                             (dados['custos']['total_anual'] + dados['endividamento']['parcelas_anuais']),
            'margem_lucro': 0
        }
        
        # Calcular margem de lucro
        if dados['analise']['receita_potencial'] > 0:
            dados['analise']['margem_lucro'] = (dados['analise']['lucro_estimado'] / dados['analise']['receita_potencial']) * 100
        
        # 5. RELATÓRIOS CONSOLIDADOS
        dados['relatorios'] = {
            'data_consolidacao': datetime.now().date(),
            'status_completo': len(inventario) > 0 and len(custos_fixos) > 0 and len(financiamentos) > 0,
            'modulos_ativos': {
                'pecuaria': len(inventario) > 0,
                'custos': len(custos_fixos) > 0 or len(custos_variaveis) > 0,
                'endividamento': len(financiamentos) > 0,
                'analise': True,  # Sempre ativo
                'relatorios': True  # Sempre ativo
            }
        }
        
    except Exception as e:
        print(f"Erro ao consolidar dados: {e}")
        dados = {'erro': str(e)}
    
    return dados


def calcular_indicadores_automaticos(propriedade):
    """Calcula indicadores financeiros automaticamente"""
    indicadores = {}
    
    try:
        # Busca dados básicos
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        valor_rebanho = sum(item.valor_total for item in inventario if item.valor_total)
        
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custo_fixo_anual = sum(custo.custo_anual for custo in custos_fixos)
        
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        parcelas_anuais = sum(f.valor_parcela for f in financiamentos) * 12
        
        # Indicadores calculados
        if valor_rebanho > 0:
            indicadores['valor_por_hectare'] = valor_rebanho / propriedade.area_total_ha
            indicadores['densidade_animal'] = sum(item.quantidade for item in inventario) / propriedade.area_total_ha
        
        if custo_fixo_anual > 0:
            indicadores['custo_por_hectare'] = custo_fixo_anual / propriedade.area_total_ha
        
        if parcelas_anuais > 0 and valor_rebanho > 0:
            indicadores['indice_endividamento'] = (parcelas_anuais / valor_rebanho) * 100
        
        # Receita estimada (15% do valor do rebanho)
        receita_estimada = valor_rebanho * Decimal('0.15')
        custos_totais = custo_fixo_anual + parcelas_anuais
        
        if receita_estimada > 0:
            indicadores['margem_lucro'] = ((receita_estimada - custos_totais) / receita_estimada) * 100
            indicadores['roi'] = ((receita_estimada - custos_totais) / valor_rebanho) * 100
        
    except Exception as e:
        print(f"Erro ao calcular indicadores: {e}")
        indicadores = {'erro': str(e)}
    
    return indicadores


def gerar_projecoes_financeiras(propriedade):
    """Gera projeções financeiras para 5 anos"""
    projecoes = []
    
    try:
        # Dados base
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        valor_rebanho_atual = sum(item.valor_total for item in inventario if item.valor_total)
        
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custo_fixo_anual = sum(custo.custo_anual for custo in custos_fixos)
        
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        parcelas_anuais = sum(f.valor_parcela for f in financiamentos) * 12
        
        # Projeção para 5 anos
        for ano in range(1, 6):
            # Crescimento do rebanho (5% ao ano)
            valor_rebanho_projetado = valor_rebanho_atual * (Decimal('1.05') ** ano)
            
            # Receita estimada (15% do valor do rebanho)
            receita_estimada = valor_rebanho_projetado * Decimal('0.15')
            
            # Custos com inflação (3% ao ano)
            custos_projetados = (custo_fixo_anual + parcelas_anuais) * (Decimal('1.03') ** ano)
            
            # Lucro projetado
            lucro_projetado = receita_estimada - custos_projetados
            
            projecoes.append({
                'ano': datetime.now().year + ano,
                'valor_rebanho': valor_rebanho_projetado,
                'receita_estimada': receita_estimada,
                'custos_totais': custos_projetados,
                'lucro_projetado': lucro_projetado,
                'margem_lucro': (lucro_projetado / receita_estimada) * 100 if receita_estimada > 0 else 0
            })
    
    except Exception as e:
        print(f"Erro ao gerar projeções: {e}")
        projecoes = []
    
    return projecoes

