# -*- coding: utf-8 -*-
"""
Views Consolidadas - MÓDULO PECUÁRIA COMPLETA
Agrupa:
- Inventário de Rebanho
- Rastreabilidade (PNIB)
- Reprodução
- Movimentações
"""

# pyright: reportMissingImports=false

import json
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum, F, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def _is_usuario_demo(user):
    """
    Função helper para verificar se um usuário é demo.
    Retorna True se:
    - username está em ['demo', 'demo_monpec']
    - ou tem registro UsuarioAtivo (criado pelo botão demonstração)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar se é usuário demo padrão
    if user.username in ['demo', 'demo_monpec']:
        return True
    
    # Verificar se tem UsuarioAtivo (usuário criado pelo popup)
    try:
        from .models_auditoria import UsuarioAtivo
        UsuarioAtivo.objects.get(usuario=user)
        return True
    except:
        return False


from .decorators import obter_propriedade_com_permissao
from .models import (
    Propriedade, CategoriaAnimal, InventarioRebanho,
    AnimalIndividual, MovimentacaoIndividual, BrincoAnimal,
    MovimentacaoProjetada, IndicadorFinanceiro, FluxoCaixa, Financiamento,
    PlanejamentoAnual, AtividadePlanejada, MetaComercialPlanejada,
    MetaFinanceiraPlanejada, IndicadorPlanejado, CenarioPlanejamento
)
from .services.planejamento import PlanejamentoAnalyzer

# Imports de módulos opcionais com logging
modulos_indisponiveis = []

try:
    from .models_reproducao import (
        Touro, EstacaoMonta, IATF, MontaNatural, Nascimento, CalendarioReprodutivo
    )
except ImportError as e:
    # Se não existir, criar classes vazias para não quebrar
    logger.warning(f'Módulo de reprodução não disponível: {e}')
    Touro = None
    EstacaoMonta = None
    IATF = None
    MontaNatural = None
    Nascimento = None
    CalendarioReprodutivo = None
    modulos_indisponiveis.append('reproducao')

# Imports para outros módulos
try:
    from .models_operacional import (
        EstoqueSuplementacao, DistribuicaoSuplementacao,
        TanqueCombustivel, ConsumoCombustivel,
        Equipamento, ManutencaoEquipamento
    )
except ImportError as e:
    logger.warning(f'Módulo operacional não disponível: {e}')
    EstoqueSuplementacao = None
    DistribuicaoSuplementacao = None
    TanqueCombustivel = None
    ConsumoCombustivel = None
    Equipamento = None
    ManutencaoEquipamento = None
    modulos_indisponiveis.append('operacoes')

try:
    from .models_controles_operacionais import Cocho, ControleCocho
except ImportError as e:
    logger.warning(f'Módulo de controles operacionais não disponível: {e}')
    Cocho = None
    ControleCocho = None
    modulos_indisponiveis.append('nutricao')

try:
    from .models_funcionarios import Funcionario
except ImportError:
    Funcionario = None

try:
    from .models_financeiro import LancamentoFinanceiro, ContaFinanceira, CategoriaFinanceira
except ImportError as e:
    logger.warning(f'Módulo financeiro não disponível: {e}')
    LancamentoFinanceiro = None
    ContaFinanceira = None
    CategoriaFinanceira = None
    modulos_indisponiveis.append('financeiro')

try:
    from .models_compras_financeiro import (
        RequisicaoCompra, OrdemCompra, Fornecedor
    )
except ImportError as e:
    logger.warning(f'Módulo de compras não disponível: {e}')
    RequisicaoCompra = None
    OrdemCompra = None
    Fornecedor = None
    modulos_indisponiveis.append('compras')

try:
    from .models_patrimonio import BemPatrimonial
except ImportError as e:
    logger.warning(f'Módulo de patrimônio não disponível: {e}')
    BemPatrimonial = None
    modulos_indisponiveis.append('patrimonio')


@login_required
def pecuaria_completa_dashboard(request, propriedade_id):
    """Dashboard consolidado estilo Power BI com todos os módulos"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # ========== FILTROS GLOBAIS (BI Style) ==========
    from datetime import timedelta
    
    # Filtro de período - padrão: 01/01/2025 até hoje
    # Verificar se há parâmetros de data na URL
    data_inicio_param = request.GET.get('data_inicio')
    data_fim_param = request.GET.get('data_fim')
    
    if data_inicio_param and data_fim_param:
        # Usar datas fornecidas via URL
        try:
            data_inicio = datetime.strptime(data_inicio_param, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_param, '%Y-%m-%d').date()
            periodo_dias = (data_fim - data_inicio).days
        except (ValueError, TypeError):
            # Se houver erro, usar padrão
            data_fim = date.today()
            data_inicio = date(2025, 1, 1)  # 01/01/2025
            periodo_dias = (data_fim - data_inicio).days
    elif request.GET.get('periodo_dias'):
        # Se usar periodo_dias na URL, manter comportamento anterior
        try:
            periodo_dias = int(request.GET.get('periodo_dias', 30))
            if periodo_dias < 1 or periodo_dias > 365:
                periodo_dias = 30
        except (ValueError, TypeError):
            periodo_dias = 30
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=periodo_dias)
    else:
        # Padrão: 01/01/2025 até hoje
        data_fim = date.today()
        data_inicio = date(2025, 1, 1)  # 01/01/2025
        periodo_dias = (data_fim - data_inicio).days
    
    # Filtro por módulo (padrão: todos)
    modulo_filtro = request.GET.get('modulo', '').upper()
    
    # Período anterior para comparação de tendências
    dias_periodo_anterior = periodo_dias
    data_inicio_anterior = data_inicio - timedelta(days=dias_periodo_anterior)
    data_fim_anterior = data_inicio - timedelta(days=1)
    
    mes_atual = date.today().replace(day=1)
    
    # ========== PECUÁRIA ==========
    # Buscar apenas o inventário mais recente de cada categoria para evitar duplicatas
    # Primeiro, obter a data mais recente
    data_inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).aggregate(Max('data_inventario'))['data_inventario__max']
    
    if data_inventario_recente:
        # Buscar apenas inventários da data mais recente
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario_recente
        ).select_related('categoria')
    else:
        inventario = InventarioRebanho.objects.none()
    
    # Calcular totais sempre (independente de ter inventário ou não)
    total_animais_inventario = sum(item.quantidade or 0 for item in inventario)
    # Calcular valor total do rebanho - valor_total é uma property que calcula quantidade * valor_por_cabeca
    valor_total_rebanho = Decimal('0')
    for item in inventario:
        # valor_total é uma property, sempre retorna um valor (pode ser 0)
        valor_item = item.valor_total  # Isso chama a property: quantidade * valor_por_cabeca
        if valor_item:
            valor_total_rebanho += Decimal(str(valor_item))
        # Se valor_por_cabeca não estiver preenchido, calcular manualmente como fallback
        elif item.valor_por_cabeca and item.quantidade:
            valor_total_rebanho += (Decimal(str(item.valor_por_cabeca)) * Decimal(str(item.quantidade)))
    
    # Inventário por categoria para gráfico
    inventario_por_categoria = inventario.values('categoria__nome').annotate(
        total=Sum('quantidade'),
        valor=Sum(F('quantidade') * F('valor_por_cabeca'))
    ).order_by('-total')[:10]
    
    # Rastreabilidade
    animais_rastreados = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).count() if AnimalIndividual else 0
    
    animais_por_status = AnimalIndividual.objects.filter(
        propriedade=propriedade
    ).values('status').annotate(total=Count('id')) if AnimalIndividual else []
    
    movimentacoes_recentes = MovimentacaoIndividual.objects.filter(
        animal__propriedade=propriedade
    ).select_related('animal').order_by('-data_movimentacao')[:10] if MovimentacaoIndividual else []
    
    # Reprodução
    touros_aptos = Touro.objects.filter(
        propriedade=propriedade,
        status='APTO'
    ).count() if Touro else 0
    
    estacoes_monta_ativas = EstacaoMonta.objects.filter(
        propriedade=propriedade,
        ativa=True
    ).count() if EstacaoMonta else 0
    
    iatfs_pendentes = IATF.objects.filter(
        propriedade=propriedade,
        status='PROGRAMADA'
    ).count() if IATF else 0
    
    nascimentos_mes = Nascimento.objects.filter(
        propriedade=propriedade,
        data_nascimento__month=date.today().month,
        data_nascimento__year=date.today().year
    ).count() if Nascimento else 0
    
    # ========== NUTRIÇÃO ==========
    if EstoqueSuplementacao and (not modulo_filtro or modulo_filtro == 'NUTRIÇÃO'):
        estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
        estoques_baixo = estoques.filter(quantidade_atual__lte=F('quantidade_minima')).count()
        valor_total_estoque = sum(e.valor_total_estoque or Decimal('0') for e in estoques)
        
        # Aplicar filtro de período
        distribuicoes_mes = DistribuicaoSuplementacao.objects.filter(
            estoque__propriedade=propriedade,
            data__gte=data_inicio,
            data__lte=data_fim
        )
        total_distribuido_mes = sum(d.quantidade or Decimal('0') for d in distribuicoes_mes)
        valor_distribuido_mes = sum(d.valor_total or Decimal('0') for d in distribuicoes_mes)
    else:
        estoques_baixo = 0
        valor_total_estoque = Decimal('0')
        total_distribuido_mes = Decimal('0')
        valor_distribuido_mes = Decimal('0')
    
    if Cocho:
        cochos_ativos = Cocho.objects.filter(propriedade=propriedade, status='ATIVO').count()
    else:
        cochos_ativos = 0
    
    # ========== OPERAÇÕES ==========
    if TanqueCombustivel and (not modulo_filtro or modulo_filtro == 'OPERAÇÕES'):
        tanques = TanqueCombustivel.objects.filter(propriedade=propriedade)
        estoque_total_combustivel = sum(t.estoque_atual or Decimal('0') for t in tanques)
        
        # Aplicar filtro de período
        consumos_mes = []
        if ConsumoCombustivel:
            try:
                consumos_mes = ConsumoCombustivel.objects.filter(
                    tanque__propriedade=propriedade,
                    data__gte=data_inicio,
                    data__lte=data_fim
                )
            except Exception as e:
                logger.warning(f"Erro ao buscar consumos de combustível: {e}")
                consumos_mes = []
        
        total_consumo_mes = sum(
            c.quantidade_litros or Decimal('0') for c in consumos_mes
        ) if consumos_mes else Decimal('0')
        valor_consumo_mes = sum(
            c.valor_total or Decimal('0') for c in consumos_mes
        ) if consumos_mes else Decimal('0')
    else:
        estoque_total_combustivel = Decimal('0')
        total_consumo_mes = Decimal('0')
        valor_consumo_mes = Decimal('0')
    
    if Equipamento:
        equipamentos_ativos = Equipamento.objects.filter(propriedade=propriedade, ativo=True).count()
        # Contar apenas manutenções realmente pendentes:
        # - Status AGENDADA ou EM_ANDAMENTO
        # - E que ainda não foram realizadas (data_realizacao vazia ou não definida)
        # - E que não foram canceladas
        # - E que estão vinculadas a equipamentos ativos
        if ManutencaoEquipamento:
            manutencoes_pendentes = ManutencaoEquipamento.objects.filter(
                equipamento__propriedade=propriedade,
                equipamento__ativo=True,  # Apenas equipamentos ativos
                status__in=['AGENDADA', 'EM_ANDAMENTO'],
                data_realizacao__isnull=True  # Apenas as que ainda não foram realizadas
            ).count()
        else:
            manutencoes_pendentes = 0
    else:
        equipamentos_ativos = 0
        manutencoes_pendentes = 0
    
    if Funcionario:
        funcionarios_ativos = Funcionario.objects.filter(
            propriedade=propriedade,
            situacao='ATIVO'
        ).count()
        folha_mensal = sum(
            f.salario_base or Decimal('0') for f in Funcionario.objects.filter(
                propriedade=propriedade,
                situacao='ATIVO'
            )
        )
    else:
        funcionarios_ativos = 0
        folha_mensal = Decimal('0')
    
    # ========== FINANCEIRO ==========
    # Definir status_quitado antes de usar
    if LancamentoFinanceiro:
        status_quitado = getattr(LancamentoFinanceiro, 'STATUS_QUITADO', 'QUITADO')
    else:
        status_quitado = 'QUITADO'
    
    if LancamentoFinanceiro and (not modulo_filtro or modulo_filtro == 'FINANCEIRO'):
        # Aplicar filtro de período - incluir quitados e pendentes
        # Buscar todos os lançamentos do período (quitados e pendentes) para mostrar valores completos
        lancamentos_periodo = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia__gte=data_inicio,
            data_competencia__lte=data_fim
        )
        
        # Excluir transferências (não são receitas nem despesas reais)
        if CategoriaFinanceira:
            lancamentos_periodo = lancamentos_periodo.exclude(tipo=CategoriaFinanceira.TIPO_TRANSFERENCIA)
        
        # Debug: Log para verificar se há lançamentos
        total_lancamentos = lancamentos_periodo.count()
        logger.debug(f"Total de lançamentos encontrados no período {data_inicio} a {data_fim}: {total_lancamentos}")
        
        # Usar constantes do modelo em vez de strings
        # Incluir todos os lançamentos (quitados e pendentes) para mostrar valores completos
        if CategoriaFinanceira:
            lancamentos_receitas = lancamentos_periodo.filter(tipo=CategoriaFinanceira.TIPO_RECEITA)
            lancamentos_despesas = lancamentos_periodo.filter(tipo=CategoriaFinanceira.TIPO_DESPESA)
            receitas_mes = sum(l.valor or Decimal('0') for l in lancamentos_receitas)
            despesas_mes = sum(l.valor or Decimal('0') for l in lancamentos_despesas)
            
            logger.debug(f"Receitas: {receitas_mes}, Despesas: {despesas_mes}, Total receitas: {lancamentos_receitas.count()}, Total despesas: {lancamentos_despesas.count()}")
        else:
            # Fallback se CategoriaFinanceira não estiver disponível
            lancamentos_receitas = lancamentos_periodo.filter(tipo='RECEITA')
            lancamentos_despesas = lancamentos_periodo.filter(tipo='DESPESA')
            receitas_mes = sum(l.valor or Decimal('0') for l in lancamentos_receitas)
            despesas_mes = sum(l.valor or Decimal('0') for l in lancamentos_despesas)
        saldo_mes = receitas_mes - despesas_mes
        
        # Gráfico de receitas/despesas - dividir período em intervalos
        meses_grafico = []
        receitas_grafico = []
        despesas_grafico = []
        
        # Dividir período em até 6 intervalos
        num_intervalos = min(6, max(1, periodo_dias // 5))
        dias_por_intervalo = periodo_dias / num_intervalos
        
        for i in range(num_intervalos):
            intervalo_inicio = data_inicio + timedelta(days=int(i * dias_por_intervalo))
            intervalo_fim = data_inicio + timedelta(days=int((i + 1) * dias_por_intervalo) - 1)
            if intervalo_fim > data_fim:
                intervalo_fim = data_fim
            
            lanc_intervalo = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                data_competencia__gte=intervalo_inicio,
                data_competencia__lte=intervalo_fim
                # Incluir todos (quitados e pendentes) para gráfico também
            )
            # Usar constantes do modelo
            if CategoriaFinanceira:
                receitas_val = float(sum(
                    l.valor or Decimal('0') for l in lanc_intervalo.filter(
                        tipo=CategoriaFinanceira.TIPO_RECEITA
                    )
                ))
                despesas_val = float(sum(
                    l.valor or Decimal('0') for l in lanc_intervalo.filter(
                        tipo=CategoriaFinanceira.TIPO_DESPESA
                    )
                ))
            else:
                receitas_val = float(sum(
                    l.valor or Decimal('0') for l in lanc_intervalo.filter(tipo='RECEITA')
                ))
                despesas_val = float(sum(
                    l.valor or Decimal('0') for l in lanc_intervalo.filter(tipo='DESPESA')
                ))
            receitas_grafico.append(receitas_val)
            despesas_grafico.append(despesas_val)
            meses_grafico.append(intervalo_inicio.strftime('%d/%m'))
        
        # Serializar para JSON
        meses_grafico = json.dumps(meses_grafico)
        receitas_grafico = json.dumps(receitas_grafico)
        despesas_grafico = json.dumps(despesas_grafico)
    else:
        receitas_mes = Decimal('0')
        despesas_mes = Decimal('0')
        saldo_mes = Decimal('0')
        meses_grafico = json.dumps([])
        receitas_grafico = json.dumps([])
        despesas_grafico = json.dumps([])
    
    if ContaFinanceira:
        contas_ativas = ContaFinanceira.objects.filter(propriedade=propriedade, ativa=True).count()
    else:
        contas_ativas = 0
    
    # ========== BENS E PATRIMÔNIO ==========
    if BemPatrimonial:
        bens = BemPatrimonial.objects.filter(propriedade=propriedade, ativo=True)
        total_bens = bens.count()
        valor_total_bens = sum(b.valor_aquisicao or Decimal('0') for b in bens)
        valor_depreciado_bens = sum(
            (b.valor_aquisicao or Decimal('0')) - (b.valor_residual or Decimal('0'))
            for b in bens
        )
    else:
        total_bens = 0
        valor_total_bens = Decimal('0')
        valor_depreciado_bens = Decimal('0')
    
    # ========== PLANEJAMENTO ==========
    if PlanejamentoAnual:
        planejamentos_ativos = PlanejamentoAnual.objects.filter(
            propriedade=propriedade,
            status__in=['ATIVO', 'EM_ANDAMENTO']
        ).count()
        
        # Buscar total de metas
        planejamentos = PlanejamentoAnual.objects.filter(propriedade=propriedade)
        total_metas_comerciais = sum(
            p.metas_comerciais.count() if hasattr(p, 'metas_comerciais') else 0
            for p in planejamentos
        )
        total_metas_financeiras = sum(
            p.metas_financeiras.count() if hasattr(p, 'metas_financeiras') else 0
            for p in planejamentos
        )
    else:
        planejamentos_ativos = 0
        total_metas_comerciais = 0
        total_metas_financeiras = 0
    
    # ========== COMPRAS ==========
    if RequisicaoCompra and (not modulo_filtro or modulo_filtro == 'COMPRAS'):
        # Aplicar filtro de período nas requisições
        requisicoes_query = RequisicaoCompra.objects.filter(
            propriedade=propriedade,
            status__in=['PENDENTE', 'EM_ANALISE']
        )
        # Se houver campo de data, aplicar filtro
        if hasattr(RequisicaoCompra, 'data_criacao'):
            requisicoes_query = requisicoes_query.filter(
                data_criacao__gte=data_inicio,
                data_criacao__lte=data_fim
            )
        requisicoes_pendentes = requisicoes_query.count()
    else:
        requisicoes_pendentes = 0
    
    if OrdemCompra and (not modulo_filtro or modulo_filtro == 'COMPRAS'):
        # Aplicar filtro de período nas ordens
        ordens_query = OrdemCompra.objects.filter(
            propriedade=propriedade,
            status__in=['RASCUNHO', 'APROVADA', 'ENVIADA']
        )
        # Se houver campo de data, aplicar filtro
        if hasattr(OrdemCompra, 'data_criacao'):
            ordens_query = ordens_query.filter(
                data_criacao__gte=data_inicio,
                data_criacao__lte=data_fim
            )
        ordens_pendentes = ordens_query.count()
        valor_ordens_pendentes = sum(o.valor_total or Decimal('0') for o in ordens_query)
    else:
        ordens_pendentes = 0
        valor_ordens_pendentes = Decimal('0')
    
    if Fornecedor:
        total_fornecedores = Fornecedor.objects.filter(propriedade=propriedade).count()
    else:
        total_fornecedores = 0
    
    # ========== MÉTRICAS CONSOLIDADAS ==========
    total_custos_operacionais = valor_consumo_mes + folha_mensal + valor_distribuido_mes
    margem_lucro = ((receitas_mes - despesas_mes) / receitas_mes * 100) if receitas_mes > 0 else Decimal('0')
    
    # ========== CÁLCULO DE TENDÊNCIAS (Comparação com período anterior) ==========
    from datetime import timedelta
    mes_anterior = (mes_atual - timedelta(days=32)).replace(day=1)
    
    # Animais - tendência
    inventario_anterior = InventarioRebanho.objects.filter(propriedade=propriedade)
    total_animais_anterior = sum(item.quantidade or 0 for item in inventario_anterior)
    tendencia_animais = total_animais_inventario - total_animais_anterior
    percentual_animais = (tendencia_animais / total_animais_anterior * 100) if total_animais_anterior > 0 else Decimal('0')
    percentual_animais_abs = abs(percentual_animais)
    
    # Financeiro - tendência (comparar com período anterior)
    # Usar todos os lançamentos (quitados e pendentes) para comparação consistente
    if LancamentoFinanceiro:
        lancamentos_anterior = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia__gte=data_inicio_anterior,
            data_competencia__lte=data_fim_anterior
        )
        # Usar constantes do modelo
        if CategoriaFinanceira:
            receitas_anterior = sum(
                l.valor or Decimal('0') for l in lancamentos_anterior.filter(
                    tipo=CategoriaFinanceira.TIPO_RECEITA
                )
            )
            despesas_anterior = sum(
                l.valor or Decimal('0') for l in lancamentos_anterior.filter(
                    tipo=CategoriaFinanceira.TIPO_DESPESA
                )
            )
        else:
            receitas_anterior = sum(
                l.valor or Decimal('0') for l in lancamentos_anterior.filter(tipo='RECEITA')
            )
            despesas_anterior = sum(
                l.valor or Decimal('0') for l in lancamentos_anterior.filter(tipo='DESPESA')
            )
        saldo_anterior = receitas_anterior - despesas_anterior
        
        tendencia_receitas = receitas_mes - receitas_anterior
        tendencia_despesas = despesas_mes - despesas_anterior
        tendencia_saldo = saldo_mes - saldo_anterior
        
        percentual_receitas = (tendencia_receitas / receitas_anterior * 100) if receitas_anterior > 0 else Decimal('0')
        percentual_despesas = (tendencia_despesas / despesas_anterior * 100) if despesas_anterior > 0 else Decimal('0')
        percentual_receitas_abs = abs(percentual_receitas)
        percentual_despesas_abs = abs(percentual_despesas)
    else:
        tendencia_receitas = Decimal('0')
        tendencia_despesas = Decimal('0')
        tendencia_saldo = Decimal('0')
        percentual_receitas = Decimal('0')
        percentual_despesas = Decimal('0')
        percentual_receitas_abs = Decimal('0')
        percentual_despesas_abs = Decimal('0')
    
    # Custos operacionais - tendência (comparar com período anterior)
    if TanqueCombustivel and Funcionario and EstoqueSuplementacao:
        consumos_anterior = ConsumoCombustivel.objects.filter(
            tanque__propriedade=propriedade,
            data__gte=data_inicio_anterior,
            data__lte=data_fim_anterior
        ) if ConsumoCombustivel else []
        valor_consumo_anterior = sum(
            c.valor_total or Decimal('0') for c in consumos_anterior
        ) if consumos_anterior else Decimal('0')
        
        distribuicoes_anterior = DistribuicaoSuplementacao.objects.filter(
            estoque__propriedade=propriedade,
            data__gte=data_inicio_anterior,
            data__lte=data_fim_anterior
        ) if DistribuicaoSuplementacao else []
        valor_distribuido_anterior = sum(
            d.valor_total or Decimal('0') for d in distribuicoes_anterior
        ) if distribuicoes_anterior else Decimal('0')
        
        funcionarios_anterior = Funcionario.objects.filter(
            propriedade=propriedade,
            situacao='ATIVO'
        )
        folha_anterior = sum(f.salario_base or Decimal('0') for f in funcionarios_anterior)
        
        custos_anterior = valor_consumo_anterior + folha_anterior + valor_distribuido_anterior
        tendencia_custos = total_custos_operacionais - custos_anterior
        percentual_custos = (tendencia_custos / custos_anterior * 100) if custos_anterior > 0 else Decimal('0')
        percentual_custos_abs = abs(percentual_custos)
    else:
        tendencia_custos = Decimal('0')
        percentual_custos = Decimal('0')
        percentual_custos_abs = Decimal('0')
    
    # ========== ALERTAS CRÍTICOS ==========
    alertas_criticos = []
    total_alertas = 0
    
    # Alertas de estoque baixo
    if estoques_baixo > 0:
        alertas_criticos.append({
            'tipo': 'ESTOQUE_BAIXO',
            'titulo': f'{estoques_baixo} Estoque(s) de Suplementação Abaixo do Mínimo',
            'descricao': 'Verifique os estoques de suplementação urgentemente.',
            'prioridade': 'ALTA' if estoques_baixo >= 3 else 'MEDIA',
            'url': f'/propriedade/{propriedade.id}/nutricao/dashboard/',
            'icone': 'bi-exclamation-triangle-fill',
            'cor': 'danger' if estoques_baixo >= 3 else 'warning'
        })
        total_alertas += 1  # Corrigido: somar apenas 1 alerta, não a quantidade de estoques
    
    # Alertas de manutenção
    if manutencoes_pendentes > 0:
        alertas_criticos.append({
            'tipo': 'MANUTENCAO',
            'titulo': f'{manutencoes_pendentes} Manutenção(ões) Pendente(s)',
            'descricao': 'Equipamentos aguardando manutenção.',
            'prioridade': 'ALTA' if manutencoes_pendentes >= 5 else 'MEDIA',
            'url': f'/propriedade/{propriedade.id}/operacoes/dashboard/',
            'icone': 'bi-tools',
            'cor': 'danger' if manutencoes_pendentes >= 5 else 'warning'
        })
        total_alertas += 1  # Corrigido: somar apenas 1 alerta, não a quantidade de manutenções
    
    # Alertas financeiros
    if saldo_mes < 0:
        alertas_criticos.append({
            'tipo': 'SALDO_NEGATIVO',
            'titulo': 'Saldo Financeiro Negativo',
            'descricao': f'Saldo atual: {saldo_mes}',  # Valor será formatado no template com moeda_br
            'valor_saldo': saldo_mes,  # Adicionar valor separado para formatação
            'prioridade': 'ALTA',
            'url': f'/propriedade/{propriedade.id}/financeiro/dashboard/',
            'icone': 'bi-cash-coin',
            'cor': 'danger'
        })
        total_alertas += 1
    
    # Alertas de requisições pendentes
    if requisicoes_pendentes > 0:
        alertas_criticos.append({
            'tipo': 'REQUISICOES',
            'titulo': f'{requisicoes_pendentes} Requisição(ões) Aguardando Aprovação',
            'descricao': 'Requisições de compra precisam de atenção.',
            'prioridade': 'MEDIA',
            'url': f'/propriedade/{propriedade.id}/compras/dashboard/',
            'icone': 'bi-cart',
            'cor': 'warning'
        })
        total_alertas += requisicoes_pendentes
    
    # Alertas de IATF pendentes
    if iatfs_pendentes > 0:
        alertas_criticos.append({
            'tipo': 'IATF',
            'titulo': f'{iatfs_pendentes} IATF(s) Programada(s)',
            'descricao': 'IATFs aguardando execução.',
            'prioridade': 'MEDIA',
            'url': f'/propriedade/{propriedade.id}/reproducao/iatf/',
            'icone': 'bi-calendar-check',
            'cor': 'info'
        })
        total_alertas += iatfs_pendentes
    
    # ========== ATIVIDADES RECENTES - TIMELINE ==========
    atividades_recentes = []
    
    # Usar data_inicio já calculada acima
    data_limite = data_inicio
    
    # Pecuária - Movimentações
    if MovimentacaoIndividual:
        movimentacoes = MovimentacaoIndividual.objects.filter(
            animal__propriedade=propriedade,
            data_movimentacao__gte=data_limite
        ).select_related('animal', 'animal__categoria').order_by('-data_movimentacao')[:20]
        for mov in movimentacoes:
            atividades_recentes.append({
                'tipo': 'movimentacao',
                'modulo': 'Pecuária',
                'icone': 'bi-arrow-left-right',
                'cor': 'primary',
                'titulo': f"Movimentação: {mov.get_tipo_movimentacao_display()}",
                'descricao': f"Animal {mov.animal.numero_brinco if mov.animal else 'N/A'} - {mov.quantidade_animais or 1} animal(is)",
                'data': mov.data_movimentacao,
                'valor': mov.valor,
                'url': f'/propriedade/{propriedade.id}/pecuaria/rastreabilidade/animal/{mov.animal.id}/' if mov.animal else None
            })
    
    # Pecuária - Novos Animais
    if AnimalIndividual:
        try:
            # AnimalIndividual tem data_atualizacao e data_cadastro
            novos_animais = AnimalIndividual.objects.filter(
                propriedade=propriedade,
                data_atualizacao__date__gte=data_limite
            ).select_related('categoria').order_by('-data_atualizacao')[:10]
            
            for animal in novos_animais:
                data_animal = animal.data_atualizacao.date() if animal.data_atualizacao else date.today()
                
                atividades_recentes.append({
                    'tipo': 'animal_novo',
                    'modulo': 'Rastreabilidade',
                    'icone': 'bi-cow',
                    'cor': 'info',
                    'titulo': f"Novo Animal Cadastrado",
                    'descricao': f"Brinco: {animal.numero_brinco} - {animal.categoria.nome if animal.categoria else 'Sem categoria'}",
                    'data': data_animal,
                    'valor': None,
                    'url': f'/propriedade/{propriedade.id}/pecuaria/rastreabilidade/animal/{animal.id}/'
                })
        except Exception as e:
            logger.warning(f'Erro ao buscar novos animais: {e}', exc_info=True)
            # Continuar sem dados de novos animais
    
    # Reprodução - IATFs
    if IATF:
        iatfs_recentes = IATF.objects.filter(
            propriedade=propriedade,
            data_programada__gte=data_limite
        ).select_related('animal_individual', 'animal_individual__categoria').order_by('-data_programada')[:10]
        for iatf in iatfs_recentes:
            atividades_recentes.append({
                'tipo': 'iatf',
                'modulo': 'Reprodução',
                'icone': 'bi-calendar-check',
                'cor': 'success',
                'titulo': f"IATF {iatf.get_status_display()}",
                'descricao': f"Animal: {iatf.animal_individual.numero_brinco if iatf.animal_individual else 'N/A'} - Protocolo: {iatf.protocolo or 'N/A'}",
                'data': iatf.data_programada,
                'valor': None,
                'url': f'/propriedade/{propriedade.id}/pecuaria/reproducao/'
            })
    
    # Reprodução - Nascimentos
    if Nascimento:
        nascimentos = Nascimento.objects.filter(
            propriedade=propriedade,
            data_nascimento__gte=data_limite
        ).select_related('mae', 'mae__categoria').order_by('-data_nascimento')[:15]
        for nasc in nascimentos:
            atividades_recentes.append({
                'tipo': 'nascimento',
                'modulo': 'Reprodução',
                'icone': 'bi-heart',
                'cor': 'danger',
                'titulo': f"Nascimento Registrado",
                'descricao': f"Sexo: {nasc.get_sexo_display()} - Peso: {nasc.peso_kg or 'N/A'}kg",
                'data': nasc.data_nascimento,
                'valor': None,
                'url': f'/propriedade/{propriedade.id}/pecuaria/reproducao/'
            })
    
    # Financeiro - Lançamentos
    if LancamentoFinanceiro:
        lancamentos = LancamentoFinanceiro.objects.filter(
            propriedade=propriedade,
            data_competencia__gte=data_limite
        ).select_related('categoria').order_by('-data_competencia', '-id')[:15]
        
        # Usar constantes do modelo
        tipo_receita = CategoriaFinanceira.TIPO_RECEITA if CategoriaFinanceira else 'RECEITA'
        
        for lanc in lancamentos:
            atividades_recentes.append({
                'tipo': 'lancamento',
                'modulo': 'Financeiro',
                'icone': 'bi-cash-coin' if lanc.tipo == tipo_receita else 'bi-cash-stack',
                'cor': 'success' if lanc.tipo == tipo_receita else 'warning',
                'titulo': f"{lanc.get_tipo_display()} - {lanc.get_status_display()}",
                'descricao': f"{lanc.descricao or 'Sem descrição'} - Categoria: {lanc.categoria.nome if lanc.categoria else 'N/A'}",
                'data': lanc.data_competencia,
                'valor': lanc.valor,
                'url': f'/propriedade/{propriedade.id}/financeiro/lancamentos/'
            })
    
    # Compras - Requisições
    if RequisicaoCompra:
        try:
            # RequisicaoCompra tem criado_em
            requisicoes = RequisicaoCompra.objects.filter(
                propriedade=propriedade,
                criado_em__date__gte=data_limite
            ).order_by('-criado_em')[:10]
            
            for req in requisicoes:
                data_req = req.criado_em.date() if req.criado_em else date.today()
                
                atividades_recentes.append({
                    'tipo': 'requisicao',
                    'modulo': 'Compras',
                    'icone': 'bi-journal-plus',
                    'cor': 'primary',
                    'titulo': f"Requisição de Compra - {req.get_status_display()}",
                    'descricao': f"Setor: {req.setor.nome if hasattr(req, 'setor') and req.setor else 'N/A'}",
                    'data': data_req,
                    'valor': None,
                    'url': f'/propriedade/{propriedade.id}/compras/requisicao/{req.id}/'
                })
        except Exception as e:
            logger.warning(f'Erro ao buscar lançamentos financeiros recentes: {e}', exc_info=True)
            # Continuar sem dados de lançamentos
    
    # Compras - Ordens
    if OrdemCompra:
        ordens = OrdemCompra.objects.filter(
            propriedade=propriedade,
            data_emissao__gte=data_limite
        ).select_related('fornecedor').order_by('-data_emissao')[:10]
        for ordem in ordens:
            atividades_recentes.append({
                'tipo': 'ordem_compra',
                'modulo': 'Compras',
                'icone': 'bi-cart-check',
                'cor': 'info',
                'titulo': f"Ordem de Compra - {ordem.get_status_display()}",
                'descricao': f"Fornecedor: {ordem.fornecedor.nome if ordem.fornecedor else 'N/A'}",
                'data': ordem.data_emissao,
                'valor': ordem.valor_total,
                'url': f'/propriedade/{propriedade.id}/compras/ordem/{ordem.id}/'
            })
    
    # Nutrição - Distribuições
    if DistribuicaoSuplementacao:
        distribuicoes = DistribuicaoSuplementacao.objects.filter(
            estoque__propriedade=propriedade,
            data__gte=data_limite
        ).select_related('estoque').order_by('-data')[:10]
        for dist in distribuicoes:
            atividades_recentes.append({
                'tipo': 'distribuicao',
                'modulo': 'Nutrição',
                'icone': 'bi-arrow-down-circle',
                'cor': 'success',
                'titulo': f"Distribuição de Suplementação",
                'descricao': f"{dist.estoque.tipo_suplemento if dist.estoque else 'N/A'} - {dist.quantidade} {dist.estoque.unidade_medida if dist.estoque else ''}",
                'data': dist.data,
                'valor': dist.valor_total,
                'url': f'/propriedade/{propriedade.id}/nutricao/'
            })
    
    # Operações - Consumos de Combustível
    if ConsumoCombustivel:
        consumos = ConsumoCombustivel.objects.filter(
            tanque__propriedade=propriedade,
            data__gte=data_limite
        ).select_related('tanque').order_by('-data')[:10]
        for consumo in consumos:
            atividades_recentes.append({
                'tipo': 'consumo',
                'modulo': 'Operações',
                'icone': 'bi-fuel-pump',
                'cor': 'warning',
                'titulo': f"Consumo de Combustível",
                'descricao': f"Tanque: {consumo.tanque.nome if consumo.tanque else 'N/A'} - {consumo.quantidade_litros}L",
                'data': consumo.data,
                'valor': consumo.valor_total,
                'url': f'/propriedade/{propriedade.id}/operacoes/combustivel/'
            })
    
    # Operações - Manutenções
    if ManutencaoEquipamento:
        try:
            # Tentar filtrar por data_agendamento ou data
            manutencoes = ManutencaoEquipamento.objects.filter(
                equipamento__propriedade=propriedade
            ).select_related('equipamento')
            
            try:
                manutencoes = manutencoes.filter(data_agendamento__gte=data_limite).order_by('-data_agendamento')[:10]
            except (AttributeError, TypeError) as e:
                logger.debug(f"Campo data_agendamento não encontrado, tentando data: {e}")
                try:
                    manutencoes = manutencoes.filter(data__gte=data_limite).order_by('-data')[:10]
                except (AttributeError, TypeError) as e2:
                    logger.debug(f"Campo data também não encontrado, usando ordenação por ID: {e2}")
                    manutencoes = manutencoes.order_by('-id')[:10]
            
            for manut in manutencoes:
                try:
                    data_manut = manut.data_agendamento if manut.data_agendamento else (manut.data if manut.data else date.today())
                except (AttributeError, TypeError) as e:
                    logger.debug(f"Erro ao obter data da manutenção: {e}")
                    data_manut = date.today()
                
                atividades_recentes.append({
                    'tipo': 'manutencao',
                    'modulo': 'Operações',
                    'icone': 'bi-tools',
                    'cor': 'secondary',
                    'titulo': f"Manutenção - {manut.get_status_display() if hasattr(manut, 'get_status_display') else 'N/A'}",
                    'descricao': f"Equipamento: {manut.equipamento.nome if manut.equipamento else 'N/A'}",
                    'data': data_manut,
                    'valor': getattr(manut, 'custo_total', None),
                    'url': f'/propriedade/{propriedade.id}/operacoes/equipamentos/'
                })
        except Exception as e:
            logger.warning(f'Erro ao buscar lançamentos financeiros recentes: {e}', exc_info=True)
            # Continuar sem dados de lançamentos
    
    # Inventário - Atualizações (usando data_inventario mais recente)
    inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).order_by('-data_inventario').first()
    if inventario_recente:
        atividades_recentes.append({
            'tipo': 'inventario',
            'modulo': 'Pecuária',
            'icone': 'bi-clipboard-data',
            'cor': 'primary',
            'titulo': f"Inventário Atualizado",
            'descricao': f"Data: {inventario_recente.data_inventario.strftime('%d/%m/%Y')} - Total: {total_animais_inventario} animais",
            'data': inventario_recente.data_inventario,
            'valor': valor_total_rebanho,
            'url': f'/propriedade/{propriedade.id}/pecuaria/inventario/'
        })
    
    # Aplicar filtro por módulo se especificado
    if modulo_filtro:
        atividades_recentes = [a for a in atividades_recentes if a['modulo'].upper() == modulo_filtro]
    
    # Ordenar todas as atividades por data (mais recente primeiro)
    atividades_recentes.sort(key=lambda x: x['data'], reverse=True)
    atividades_recentes = atividades_recentes[:50]  # Limitar a 50 atividades mais recentes
    
    # Serializar dados para JSON se necessário
    if isinstance(meses_grafico, list):
        meses_grafico = json.dumps(meses_grafico)
    if isinstance(receitas_grafico, list):
        receitas_grafico = json.dumps(receitas_grafico)
    if isinstance(despesas_grafico, list):
        despesas_grafico = json.dumps(despesas_grafico)
    
    # ========== RENTABILIDADE ==========
    try:
        from .services_rentabilidade import calcular_indicadores_completos
        periodo_rentabilidade = int(request.GET.get('periodo_rentabilidade', periodo_dias))
        # Passar as datas corretas do período pesquisado
        logger.info(f"Calculando rentabilidade - Propriedade: {propriedade.id}, Período: {data_inicio} a {data_fim} ({periodo_rentabilidade} dias)")
        indicadores_rentabilidade = calcular_indicadores_completos(
            propriedade, 
            periodo_rentabilidade, 
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        logger.info(f"Resultado rentabilidade - Chaves: {list(indicadores_rentabilidade.keys()) if indicadores_rentabilidade else 'None'}")
        # Garantir que sempre retorne um dict válido mesmo se houver valores zero
        if not indicadores_rentabilidade:
            indicadores_rentabilidade = {
                'custo_por_animal': {
                    'periodo_dias': periodo_rentabilidade,
                    'total_animais': total_animais_inventario,
                    'custos_detalhados': {
                        'fixos': 0.0,
                        'variaveis': 0.0,
                        'combustivel': 0.0,
                        'folha': 0.0,
                        'manutencao': 0.0,
                        'financeiro': 0.0,
                        'nutricao': 0.0,
                        'veterinario': 0.0,
                    },
                    'custo_total': 0.0,
                    'custo_por_animal': 0.0,
                    'custo_por_animal_mes': 0.0,
                },
                'custo_por_arroba': {
                    'periodo_dias': periodo_rentabilidade,
                    'peso_total_kg': 0.0,
                    'arrobas_totais': 0.0,
                    'custo_total': 0.0,
                    'custo_por_arroba': 0.0,
                },
                'lucratividade': {
                    'periodo_dias': periodo_rentabilidade,
                    'receita_total': 0.0,
                    'custo_total': 0.0,
                    'lucro': 0.0,
                    'margem_lucro': 0.0,
                    'roi': 0.0,
                },
                'periodo_dias': periodo_rentabilidade,
            }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Erro ao calcular rentabilidade: {e}\n{error_trace}", exc_info=True)
        print(f"ERRO DETALHADO AO CALCULAR RENTABILIDADE: {e}")
        print(error_trace)
        # Criar estrutura vazia mas válida para não quebrar o template
        indicadores_rentabilidade = {
            'custo_por_animal': {
                'periodo_dias': periodo_dias,
                'total_animais': total_animais_inventario,
                'custos_detalhados': {
                    'fixos': 0.0,
                    'variaveis': 0.0,
                    'combustivel': 0.0,
                    'folha': 0.0,
                    'manutencao': 0.0,
                    'financeiro': 0.0,
                    'nutricao': 0.0,
                    'veterinario': 0.0,
                },
                'custo_total': 0.0,
                'custo_por_animal': 0.0,
                'custo_por_animal_mes': 0.0,
            },
            'custo_por_arroba': {
                'periodo_dias': periodo_dias,
                'peso_total_kg': 0.0,
                'arrobas_totais': 0.0,
                'custo_total': 0.0,
                'custo_por_arroba': 0.0,
            },
            'lucratividade': {
                'periodo_dias': periodo_dias,
                'receita_total': 0.0,
                'custo_total': 0.0,
                'lucro': 0.0,
                'margem_lucro': 0.0,
                'roi': 0.0,
            },
            'periodo_dias': periodo_dias,
        }
        periodo_rentabilidade = periodo_dias
    
    # ========== CALCULAR MÉTRICAS ADICIONAIS PARA OS CARDS ==========
    # ROI Anual - usar lucratividade real
    if indicadores_rentabilidade and indicadores_rentabilidade.get('lucratividade'):
        roi_anual = Decimal(str(indicadores_rentabilidade['lucratividade'].get('roi', 0)))
    else:
        # Calcular ROI básico: (Receitas - Despesas) / Valor do Rebanho * 100
        if valor_total_rebanho > 0:
            roi_anual = ((receitas_mes - despesas_mes) / valor_total_rebanho * 100)
        else:
            roi_anual = Decimal('0')
    
    # Receita por Animal - usar período
    receita_por_animal = (receitas_mes / total_animais_inventario) if total_animais_inventario > 0 else Decimal('0')
    
    # Custo por Animal - usar custos operacionais do período
    custo_por_animal_periodo = (total_custos_operacionais / total_animais_inventario) if total_animais_inventario > 0 else Decimal('0')
    
    # Nascimentos do período (não apenas do mês)
    if Nascimento:
        nascimentos_periodo = Nascimento.objects.filter(
            propriedade=propriedade,
            data_nascimento__gte=data_inicio,
            data_nascimento__lte=data_fim
        ).count()
    else:
        nascimentos_periodo = 0
    
    # Informações sobre módulos disponíveis
    modulos_disponiveis = {
        'reproducao': Touro is not None,
        'nutricao': EstoqueSuplementacao is not None,
        'operacoes': TanqueCombustivel is not None,
        'financeiro': LancamentoFinanceiro is not None,
        'compras': RequisicaoCompra is not None,
    }
    
    context = {
        'propriedade': propriedade,
        'modulos_disponiveis': modulos_disponiveis,
        'modulos_indisponiveis': modulos_indisponiveis,
        # Pecuária
        'inventario': inventario,
        'inventario_por_categoria': inventario_por_categoria,
        'total_animais_inventario': total_animais_inventario,
        'valor_total_rebanho': valor_total_rebanho,
        'animais_rastreados': animais_rastreados,
        'animais_por_status': animais_por_status,
        'movimentacoes_recentes': movimentacoes_recentes,
        'touros_aptos': touros_aptos,
        'estacoes_monta_ativas': estacoes_monta_ativas,
        'iatfs_pendentes': iatfs_pendentes,
        'nascimentos_mes': nascimentos_mes,
        # Nutrição
        'estoques_baixo': estoques_baixo,
        'valor_total_estoque': valor_total_estoque,
        'total_distribuido_mes': total_distribuido_mes,
        'valor_distribuido_mes': valor_distribuido_mes,
        'cochos_ativos': cochos_ativos,
        # Operações
        'estoque_total_combustivel': estoque_total_combustivel,
        'total_consumo_mes': total_consumo_mes,
        'valor_consumo_mes': valor_consumo_mes,
        'equipamentos_ativos': equipamentos_ativos,
        'manutencoes_pendentes': manutencoes_pendentes,
        'funcionarios_ativos': funcionarios_ativos,
        'folha_mensal': folha_mensal,
        # Financeiro
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes,
        'receitas_periodo': receitas_mes,  # Alias para usar no template
        'despesas_periodo': despesas_mes,  # Alias para usar no template
        'periodo_label': f"{data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}",
        'contas_ativas': contas_ativas,
        'meses_grafico': meses_grafico,
        'receitas_grafico': receitas_grafico,
        'despesas_grafico': despesas_grafico,
        # Compras
        'requisicoes_pendentes': requisicoes_pendentes,
        'ordens_pendentes': ordens_pendentes,
        'valor_ordens_pendentes': valor_ordens_pendentes,
        'total_fornecedores': total_fornecedores,
        # Bens e Patrimônio
        'total_bens': total_bens,
        'valor_total_bens': valor_total_bens,
        'valor_depreciado_bens': valor_depreciado_bens,
        # Planejamento
        'planejamentos_ativos': planejamentos_ativos,
        'total_metas_comerciais': total_metas_comerciais,
        'total_metas_financeiras': total_metas_financeiras,
        # Métricas consolidadas
        'total_custos_operacionais': total_custos_operacionais,
        'margem_lucro': margem_lucro,
        # Tendências
        'tendencia_animais': tendencia_animais,
        'percentual_animais': percentual_animais,
        'percentual_animais_abs': percentual_animais_abs,
        'tendencia_receitas': tendencia_receitas,
        'tendencia_despesas': tendencia_despesas,
        'tendencia_saldo': tendencia_saldo,
        'tendencia_custos': tendencia_custos,
        'percentual_receitas': percentual_receitas,
        'percentual_despesas': percentual_despesas,
        'percentual_custos': percentual_custos,
        'percentual_receitas_abs': percentual_receitas_abs,
        'percentual_despesas_abs': percentual_despesas_abs,
        'percentual_custos_abs': percentual_custos_abs,
        # Alertas
        'alertas_criticos': alertas_criticos,
        'total_alertas': total_alertas,
        # Atividades recentes
        'atividades_recentes': atividades_recentes,
        # Filtros aplicados
        'periodo_dias': periodo_dias,
        'modulo_filtro': modulo_filtro,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'modulos_disponiveis': modulos_disponiveis,
        # Rentabilidade
        'indicadores_rentabilidade': indicadores_rentabilidade,
        'periodo_rentabilidade': periodo_rentabilidade,
        # Métricas adicionais para cards
        'roi_anual': roi_anual,
        'receita_por_animal': receita_por_animal,
        'custo_por_animal_periodo': custo_por_animal_periodo,
        'nascimentos_periodo': nascimentos_periodo,
    }
    
    return render(request, 'gestao_rural/pecuaria_completa_dashboard.html', context)


@login_required
def dashboard_consulta_api(request, propriedade_id):
    """API para consultas dinâmicas do dashboard - analisa perguntas e retorna dados"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    data = json.loads(request.body)
    pergunta = data.get('pergunta', '').lower()

    resposta = {
        'tipo': 'dados',
        'titulo': '',
        'dados': [],
        'grafico': None,
        'insights': []
    }
    
    # Análise de palavras-chave na pergunta
    if any(palavra in pergunta for palavra in ['inventário', 'inventario', 'animais', 'rebanho', 'categoria']):
        # Dados de inventário
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        inventario_data = []
        for item in inventario:
            inventario_data.append({
                'categoria': item.categoria.nome,
                'quantidade': int(item.quantidade),
                'valor_total': float(item.valor_total or 0),
                'valor_por_cabeca': float(item.valor_por_cabeca or 0)
            })
        
        resposta['titulo'] = 'Inventário de Rebanho'
        resposta['dados'] = inventario_data
        resposta['grafico'] = {
            'tipo': 'bar',
            'eixo_x': 'categoria',
            'eixo_y': 'quantidade',
            'titulo': 'Quantidade por Categoria'
        }
        resposta['insights'].append(f'Total de {sum(i["quantidade"] for i in inventario_data)} animais')
        resposta['insights'].append(f'Valor total: R$ {sum(i["valor_total"] for i in inventario_data):,.2f}')
    
    elif any(palavra in pergunta for palavra in ['financeiro', 'receita', 'despesa', 'saldo', 'lucro']):
        # Dados financeiros
        if LancamentoFinanceiro:
            mes_atual = date.today().replace(day=1)
            lancamentos_mes = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                data_competencia__gte=mes_atual
            )
            receitas = sum(l.valor for l in lancamentos_mes.filter(tipo='RECEITA', status='QUITADO'))
            despesas = sum(l.valor for l in lancamentos_mes.filter(tipo='DESPESA', status='QUITADO'))
            
            resposta['titulo'] = 'Situação Financeira do Mês'
            resposta['dados'] = [
                {'tipo': 'Receitas', 'valor': float(receitas)},
                {'tipo': 'Despesas', 'valor': float(despesas)},
                {'tipo': 'Saldo', 'valor': float(receitas - despesas)}
            ]
            resposta['grafico'] = {
                'tipo': 'line',
                'eixo_x': 'tipo',
                'eixo_y': 'valor',
                'titulo': 'Fluxo Financeiro'
            }
            resposta['insights'].append(f'Saldo do mês: R$ {receitas - despesas:,.2f}')
            if receitas > 0:
                margem = ((receitas - despesas) / receitas * 100)
                resposta['insights'].append(f'Margem de lucro: {margem:.1f}%')
    
    elif any(palavra in pergunta for palavra in ['nutrição', 'suplementação', 'suplementacao', 'estoque', 'cocho']):
        # Dados de nutrição
        if EstoqueSuplementacao:
            estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
            estoques_data = []
            for estoque in estoques:
                estoques_data.append({
                    'tipo': estoque.tipo_suplemento,
                    'quantidade': float(estoque.quantidade_atual),
                    'minimo': float(estoque.quantidade_minima),
                    'valor': float(estoque.valor_total_estoque)
                })
            
            resposta['titulo'] = 'Estoques de Suplementação'
            resposta['dados'] = estoques_data
            resposta['grafico'] = {
                'tipo': 'bar',
                'eixo_x': 'tipo',
                'eixo_y': 'quantidade',
                'titulo': 'Estoque Atual por Tipo'
            }
            estoques_baixo = [e for e in estoques_data if e['quantidade'] <= e['minimo']]
            if estoques_baixo:
                resposta['insights'].append(f'⚠️ {len(estoques_baixo)} estoque(s) abaixo do mínimo')
    
    elif any(palavra in pergunta for palavra in ['reprodução', 'reproducao', 'iatf', 'touro', 'nascimento']):
        # Dados de reprodução
        if Touro:
            touros_aptos = Touro.objects.filter(propriedade=propriedade, status='APTO').count()
            if Nascimento:
                nascimentos_mes = Nascimento.objects.filter(
                    propriedade=propriedade,
                    data_nascimento__month=date.today().month,
                    data_nascimento__year=date.today().year
                ).count()
            else:
                nascimentos_mes = 0
            
            resposta['titulo'] = 'Situação Reprodutiva'
            resposta['dados'] = [
                {'item': 'Touros Aptos', 'valor': touros_aptos},
                {'item': 'Nascimentos (Mês)', 'valor': nascimentos_mes}
            ]
            resposta['grafico'] = {
                'tipo': 'doughnut',
                'eixo_x': 'item',
                'eixo_y': 'valor',
                'titulo': 'Reprodução'
            }
    
    elif any(palavra in pergunta for palavra in ['projeção', 'projecao', 'futuro', 'anos', 'evolução']):
        # Dados de projeção
        from .models import MovimentacaoProjetada
        movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade
        ).order_by('ano', 'mes')[:24]  # Próximos 24 meses
        
        projecao_data = {}
        for mov in movimentacoes:
            chave = f"{mov.ano}-{mov.mes:02d}"
            if chave not in projecao_data:
                projecao_data[chave] = {'periodo': chave, 'compras': 0, 'vendas': 0, 'nascimentos': 0}
            
            if mov.tipo_movimentacao == 'COMPRA':
                projecao_data[chave]['compras'] += mov.quantidade
            elif mov.tipo_movimentacao == 'VENDA':
                projecao_data[chave]['vendas'] += mov.quantidade
            elif mov.tipo_movimentacao == 'NASCIMENTO':
                projecao_data[chave]['nascimentos'] += mov.quantidade
        
        resposta['titulo'] = 'Projeção de Movimentações'
        resposta['dados'] = list(projecao_data.values())
        resposta['grafico'] = {
            'tipo': 'line',
            'eixo_x': 'periodo',
            'eixo_y': ['compras', 'vendas', 'nascimentos'],
            'titulo': 'Evolução Projetada'
        }
    
    else:
        # Resposta genérica
        # Buscar inventário mais recente
        data_inventario_recente = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).aggregate(Max('data_inventario'))['data_inventario__max']
        
        if data_inventario_recente:
            inventario = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                data_inventario=data_inventario_recente
            )
            total_animais = sum(item.quantidade for item in inventario)
        else:
            total_animais = 0
        
        resposta['titulo'] = 'Informações Gerais'
        resposta['dados'] = [{
            'item': 'Total de Animais',
            'valor': total_animais
        }]
        resposta['insights'].append('Faça perguntas específicas como: "Mostre o inventário", "Qual a situação financeira?", "Como está a nutrição?"')
    
    return JsonResponse(resposta)


def _montar_contexto_planejamento(propriedade, planejamento, cenario):
    """Monta o contexto básico para o dashboard de planejamento."""
    context = {
        'propriedade': propriedade,
        'planejamento': planejamento,
        'cenario': cenario,
    }
    
    if planejamento:
        # Adicionar dados do planejamento se existir
        try:
            context.update({
                'metas_comerciais': planejamento.metas_comerciais.all() if hasattr(planejamento, 'metas_comerciais') else [],
                'indicadores_planejados': planejamento.indicadores_planejados.all() if hasattr(planejamento, 'indicadores_planejados') else [],
                'cenarios': planejamento.cenarios.all() if hasattr(planejamento, 'cenarios') else [],
            })
        except Exception:
            pass
    
    return context


@login_required
def pecuaria_planejamento_dashboard(request, propriedade_id):
    """Dashboard estratégico do planejamento pecuário (projeções, finanças e desempenho)."""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Se for usuário demo, criar planejamento automaticamente se não existir
    if _is_usuario_demo(request.user):
        ano_atual = timezone.now().year
        planejamento_existente = PlanejamentoAnual.objects.filter(
            propriedade=propriedade,
            ano=ano_atual
        ).first()
        
        if not planejamento_existente:
            try:
                from gestao_rural.services.planejamento_helper import criar_planejamento_automatico
                planejamento_existente = criar_planejamento_automatico(propriedade, ano_atual)
                logger.info(f'✅ Planejamento criado automaticamente para usuário demo: {request.user.username}')
            except ValueError as e:
                # Se não há inventário, não criar (vai mostrar mensagem no template)
                logger.warning(f'⚠️ Não foi possível criar planejamento automático (faltando inventário): {e}')
            except Exception as e:
                logger.error(f'❌ Erro ao criar planejamento automático para demo: {e}', exc_info=True)
    
    # Criar planejamento automaticamente se solicitado
    if request.method == 'POST' and 'criar_planejamento' in request.POST:
        from gestao_rural.services.planejamento_helper import criar_planejamento_automatico
        
        ano = int(request.POST.get('ano', timezone.now().year))
        try:
            planejamento = criar_planejamento_automatico(propriedade, ano)
            messages.success(
                request, 
                f'Planejamento para {ano} criado com sucesso! '
                f'Foram criadas {planejamento.metas_comerciais.count()} metas comerciais e '
                f'{planejamento.indicadores_planejados.count()} indicadores.'
            )
            return redirect('pecuaria_planejamento_dashboard', propriedade_id=propriedade.id)
        except ValueError as e:
            messages.warning(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao criar planejamento: {str(e)}')
    
    # Sincronizar planejamento se solicitado
    if request.method == 'POST' and 'sincronizar_planejamento' in request.POST:
        from gestao_rural.services.planejamento_helper import sincronizar_planejamento_com_projecoes
        
        planejamento_id = request.POST.get('planejamento_id')
        if planejamento_id:
            try:
                planejamento = PlanejamentoAnual.objects.get(
                    id=int(planejamento_id),
                    propriedade=propriedade
                )
                sincronizar_planejamento_com_projecoes(planejamento)
                messages.success(request, 'Planejamento sincronizado com as projeções mais recentes!')
                return redirect('pecuaria_planejamento_dashboard', propriedade_id=propriedade.id)
            except PlanejamentoAnual.DoesNotExist:
                messages.error(request, 'Planejamento não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro ao sincronizar: {str(e)}')
    
    planejamento_id = request.GET.get('planejamento')
    cenario_id = request.GET.get('cenario')

    planejamento = None
    if planejamento_id:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                id=int(planejamento_id),
                propriedade=propriedade
            )
        except (PlanejamentoAnual.DoesNotExist, ValueError):
            planejamento = None
    else:
        # Se não há planejamento selecionado, tentar usar o do ano atual
        ano_atual = timezone.now().year
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade,
            ano=ano_atual
        ).first()

    cenario = None
    if cenario_id and planejamento:
        try:
            cenario = planejamento.cenarios.get(id=int(cenario_id))
        except (CenarioPlanejamento.DoesNotExist, ValueError):
            cenario = None

    context = _montar_contexto_planejamento(propriedade, planejamento, cenario)
    
    # Verificar se planejamento está desatualizado
    status_atualizacao = None
    if planejamento:
        from gestao_rural.services.planejamento_helper import verificar_planejamento_desatualizado
        status_atualizacao = verificar_planejamento_desatualizado(planejamento)
    
    context.update({
        'current_page': 'planejamento',
        'planejamento_atual': planejamento,
        'planejamentos_disponiveis': PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-ano'),
        'status_atualizacao': status_atualizacao,
    })

    return render(request, 'gestao_rural/pecuaria_planejamento_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def pecuaria_planejamentos_api(request, propriedade_id):
    """API para listar planejamentos disponíveis"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=propriedade
    ).order_by('-ano')
    
    dados = {
        'planejamentos': [
            {
                'id': p.id,
                'ano': p.ano,
                'status': p.status,
                'status_label': p.get_status_display(),
                'descricao': p.descricao or '',
            }
            for p in planejamentos
        ]
    }
    
    return JsonResponse(dados)


@login_required
@require_http_methods(["GET"])
def pecuaria_planejamento_resumo_api(request, propriedade_id, planejamento_id):
    """API para retornar resumo completo de um planejamento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    planejamento = get_object_or_404(
        PlanejamentoAnual,
        id=planejamento_id,
        propriedade=propriedade
    )
    
    cenario_id = request.GET.get('cenario')
    cenario = None
    if cenario_id:
        try:
            cenario = planejamento.cenarios.get(id=int(cenario_id))
        except (CenarioPlanejamento.DoesNotExist, ValueError):
            cenario = None
    
    # Buscar cenários
    cenarios = planejamento.cenarios.all() if hasattr(planejamento, 'cenarios') else []
    
    # Buscar metas comerciais
    metas_comerciais = []
    if hasattr(planejamento, 'metas_comerciais'):
        for meta in planejamento.metas_comerciais.all():
            metas_comerciais.append({
                'id': meta.id,
                'categoria': meta.categoria.nome if meta.categoria else 'Geral',
                'quantidade_animais': float(meta.quantidade_animais or 0),
                'arrobas_totais': float(meta.arrobas_totais or 0),
                'preco_medio_esperado': float(meta.preco_medio_esperado or 0),
                'canal_venda': meta.canal_venda or '',
            })
    
    # Buscar metas financeiras
    metas_financeiras = []
    if hasattr(planejamento, 'metas_financeiras'):
        for meta in planejamento.metas_financeiras.all():
            metas_financeiras.append({
                'id': meta.id,
                'descricao': meta.descricao,
                'tipo_custo': meta.tipo_custo,
                'tipo_custo_label': meta.get_tipo_custo_display(),
                'valor_anual_previsto': float(meta.valor_anual_previsto or 0),
                'percentual_correcao': float(meta.percentual_correcao or 0) if meta.percentual_correcao else None,
                'indice_correcao': meta.indice_correcao or '',
            })
    
    # Buscar indicadores
    indicadores = []
    if hasattr(planejamento, 'indicadores_planejados'):
        for indicador in planejamento.indicadores_planejados.all():
            indicadores.append({
                'id': indicador.id,
                'nome': indicador.nome,
                'valor_meta': float(indicador.valor_meta or 0),
                'unidade': indicador.unidade or '',
                'observacoes': indicador.observacoes or '',
            })
    
    # Buscar atividades planejadas
    atividades = []
    if hasattr(planejamento, 'atividades_planejadas'):
        atividades = list(planejamento.atividades_planejadas.all().values('id', 'descricao', 'tipo_atividade'))
    
    # Buscar inventário planejado (se houver)
    inventario = []
    # Tentar buscar inventário relacionado ao planejamento
    try:
        from .models import InventarioRebanho
        inventario_objs = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).select_related('categoria')
        
        for item in inventario_objs:
            inventario.append({
                'id': item.id,
                'categoria': item.categoria.nome if item.categoria else 'Sem categoria',
                'quantidade': float(item.quantidade or 0),
                'valor_total': float(item.valor_total or 0),
            })
    except Exception:
        pass
    
    # Montar resumo rápido
    resumo = {
        'animais_engorda': 0,
        'total_mortes': 0,
        'matrizes': 0,
    }
    
    # Calcular resumo básico (pode ser expandido)
    try:
        from .models import InventarioRebanho, CategoriaAnimal
        inventario_total = InventarioRebanho.objects.filter(propriedade=propriedade)
        resumo['matrizes'] = sum(
            item.quantidade for item in inventario_total 
            if item.categoria and 'vaca' in item.categoria.nome.lower()
        )
    except Exception:
        pass
    
    # Montar dados dos cenários
    cenarios_data = []
    for c in cenarios:
        cenarios_data.append({
            'id': c.id,
            'nome': c.nome,
            'is_baseline': getattr(c, 'is_baseline', False),
        })
    
    dados = {
        'planejamento': {
            'id': planejamento.id,
            'ano': planejamento.ano,
            'status': planejamento.status,
            'status_label': planejamento.get_status_display(),
            'cenario_atual_id': cenario.id if cenario else None,
        },
        'cenarios': cenarios_data,
        'metas_comerciais': metas_comerciais,
        'metas_financeiras': metas_financeiras,
        'indicadores': indicadores,
        'inventario': inventario,
        'atividades': atividades,
        'resumo': resumo,
    }
    
    return JsonResponse(dados)


@login_required
def reproducao_dashboard(request, propriedade_id):
    """
    Dashboard de Reprodução - Redireciona para o dashboard de IATF
    que é o módulo principal de reprodução implementado.
    """
    return redirect('iatf_dashboard', propriedade_id=propriedade_id)
