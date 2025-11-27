# -*- coding: utf-8 -*-
"""
Views para análise de cenários de planejamento
Sistema completo de gerenciamento e comparação de cenários
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, datetime

from .models import (
    Propriedade,
    PlanejamentoAnual, 
    CenarioPlanejamento,
    MovimentacaoProjetada,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada,
    VendaProjetada
)
from .services.gerar_vendas_projecao import gerar_vendas_do_cenario, gerar_vendas_todos_cenarios
from calendar import month_name
from collections import defaultdict


@login_required
def analise_cenarios(request, propriedade_id):
    """Página principal de análise de cenários"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    # Buscar por código se fornecido
    codigo_busca = request.GET.get('codigo', '').strip()
    planejamento = None
    
    if codigo_busca:
        # Buscar planejamento por código
        try:
            planejamento = PlanejamentoAnual.objects.get(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            )
            messages.success(request, f'✅ Projeção encontrada: {planejamento.codigo} - {planejamento.ano}')
        except PlanejamentoAnual.DoesNotExist:
            messages.error(request, f'❌ Nenhuma projeção encontrada com o ID: {codigo_busca.upper()}. Verifique se o ID está correto.')
            planejamento = None
        except PlanejamentoAnual.MultipleObjectsReturned:
            planejamento = PlanejamentoAnual.objects.filter(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            ).first()
            if planejamento:
                messages.success(request, f'✅ Projeção encontrada: {planejamento.codigo} - {planejamento.ano}')
    
    # Se não encontrou por código, buscar planejamento atual (ano atual ou mais recente)
    if not planejamento:
        ano_atual = timezone.now().year
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-ano').first()
        
        # Se não existe planejamento, criar um para o ano atual
        if not planejamento:
            planejamento = PlanejamentoAnual.objects.create(
                propriedade=propriedade,
                ano=ano_atual,
                descricao=f"Planejamento {ano_atual}",
                status='RASCUNHO'
            )
            # Criar cenário baseline
            CenarioPlanejamento.objects.create(
                planejamento=planejamento,
                nome="Baseline",
                descricao="Cenário base de referência",
                is_baseline=True
            )
    
    # Buscar todos os planejamentos disponíveis para seleção
    planejamentos_disponiveis = PlanejamentoAnual.objects.filter(
        propriedade=propriedade
    ).order_by('-ano', '-data_criacao')
    
    # Buscar todos os cenários do planejamento
    cenarios = planejamento.cenarios.all().order_by('-is_baseline', 'nome')
    
    # Verificar se existem vendas geradas e gerar automaticamente se não existirem
    # Isso acontece quando o usuário busca por código ou acessa a página
    if planejamento and cenarios.exists():
        # Verificar se há vendas para este planejamento
        vendas_existem = VendaProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento
        ).exists()
        
        # Verificar se existem movimentações de VENDA para gerar vendas
        # Buscar movimentações do planejamento ou do ano do planejamento
        movimentacoes_venda_query = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        )
        
        # Filtrar por planejamento se existir, senão por ano
        if planejamento:
            movimentacoes_venda_query = movimentacoes_venda_query.filter(
                Q(planejamento=planejamento) | 
                Q(planejamento__isnull=True, data_movimentacao__year=planejamento.ano)
            )
        
        movimentacoes_venda_exist = movimentacoes_venda_query.exists()
        
        # Se há movimentações de VENDA mas não há vendas geradas, gerar automaticamente
        # Isso acontece quando o usuário busca por ID ou acessa a página pela primeira vez
        if movimentacoes_venda_exist and not vendas_existem:
            try:
                # Vincular movimentações não vinculadas ao planejamento
                movimentacoes_sem_vinculo = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    tipo_movimentacao='VENDA',
                    quantidade__gt=0,
                    planejamento__isnull=True,
                    data_movimentacao__year=planejamento.ano
                )
                
                if movimentacoes_sem_vinculo.exists():
                    total_para_vincular = movimentacoes_sem_vinculo.count()
                    movimentacoes_sem_vinculo.update(planejamento=planejamento)
                    messages.info(
                        request,
                        f'ℹ️ {total_para_vincular} movimentações de VENDA foram vinculadas à projeção {planejamento.codigo}.'
                    )
                
                # Gerar vendas para todos os cenários
                vendas_geradas = gerar_vendas_todos_cenarios(propriedade, planejamento)
                total_vendas = sum(len(vendas) for vendas in vendas_geradas.values())
                
                if total_vendas > 0:
                    messages.success(
                        request,
                        f'✅ Vendas geradas automaticamente para a projeção {planejamento.codigo}! '
                        f'Total: {total_vendas} vendas criadas para {len(vendas_geradas)} cenários.'
                    )
                else:
                    # Se não gerou vendas, verificar o motivo
                    movimentacoes_vinculadas = MovimentacaoProjetada.objects.filter(
                        propriedade=propriedade,
                        planejamento=planejamento,
                        tipo_movimentacao='VENDA',
                        quantidade__gt=0
                    ).count()
                    
                    if movimentacoes_vinculadas > 0:
                        messages.warning(
                            request,
                            f'⚠️ Foram encontradas {movimentacoes_vinculadas} movimentações de VENDA, mas nenhuma venda foi gerada. '
                            f'Verifique se os valores das movimentações estão preenchidos corretamente.'
                        )
                    else:
                        messages.info(
                            request,
                            f'ℹ️ Nenhuma movimentação de VENDA encontrada para gerar vendas na projeção {planejamento.codigo}. '
                            f'Gere primeiro as projeções na página "Projeções do Rebanho".'
                        )
            except Exception as e:
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao gerar vendas automaticamente: {traceback.format_exc()}')
                messages.error(request, f'❌ Erro ao gerar vendas automaticamente: {str(e)}. Verifique os logs para mais detalhes.')
    
    # Processar dados de cada cenário
    cenarios_data = []
    for cenario in cenarios:
        dados = calcular_metricas_cenario(planejamento, cenario)
        cenarios_data.append({
            'cenario': cenario,
            'dados': dados
        })
    
    ano_atual = timezone.now().year
    
    context = {
        'propriedade': propriedade,
        'planejamento': planejamento,
        'planejamentos_disponiveis': planejamentos_disponiveis,
        'cenarios_data': cenarios_data,
        'ano_atual': ano_atual,
        'codigo_busca': codigo_busca,
    }
    
    return render(request, 'gestao_rural/analise_cenarios.html', context)


@login_required
def criar_cenario(request, propriedade_id):
    """Criar novo cenário"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    planejamento_id = request.POST.get('planejamento_id')
    planejamento = get_object_or_404(PlanejamentoAnual, id=planejamento_id, propriedade=propriedade)
    
    nome = request.POST.get('nome', '').strip()
    if not nome:
        messages.error(request, 'Nome do cenário é obrigatório')
        return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    descricao = request.POST.get('descricao', '').strip()
    is_baseline = request.POST.get('is_baseline') == 'on'
    
    # Se marcar como baseline, desmarcar outros
    if is_baseline:
        CenarioPlanejamento.objects.filter(planejamento=planejamento, is_baseline=True).update(is_baseline=False)
    
    # Ajustes percentuais
    ajuste_preco = Decimal(request.POST.get('ajuste_preco_percentual', '0') or '0')
    ajuste_custo = Decimal(request.POST.get('ajuste_custo_percentual', '0') or '0')
    ajuste_producao = Decimal(request.POST.get('ajuste_producao_percentual', '0') or '0')
    ajuste_taxas = Decimal(request.POST.get('ajuste_taxas_percentual', '0') or '0')
    
    cenario = CenarioPlanejamento.objects.create(
        planejamento=planejamento,
        nome=nome,
        descricao=descricao,
        is_baseline=is_baseline,
        ajuste_preco_percentual=ajuste_preco,
        ajuste_custo_percentual=ajuste_custo,
        ajuste_producao_percentual=ajuste_producao,
        ajuste_taxas_percentual=ajuste_taxas
    )
    
    messages.success(request, f'Cenário "{nome}" criado com sucesso!')
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def editar_cenario(request, propriedade_id, cenario_id):
    """Editar cenário existente"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    cenario = get_object_or_404(
        CenarioPlanejamento, 
        id=cenario_id,
        planejamento__propriedade=propriedade
    )
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        if not nome:
            messages.error(request, 'Nome do cenário é obrigatório')
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
        
        cenario.nome = nome
        cenario.descricao = request.POST.get('descricao', '').strip()
        is_baseline = request.POST.get('is_baseline') == 'on'
        
        # Se marcar como baseline, desmarcar outros
        if is_baseline and not cenario.is_baseline:
            CenarioPlanejamento.objects.filter(
                planejamento=cenario.planejamento, 
                is_baseline=True
            ).exclude(id=cenario.id).update(is_baseline=False)
        
        cenario.is_baseline = is_baseline
        cenario.ajuste_preco_percentual = Decimal(request.POST.get('ajuste_preco_percentual', '0') or '0')
        cenario.ajuste_custo_percentual = Decimal(request.POST.get('ajuste_custo_percentual', '0') or '0')
        cenario.ajuste_producao_percentual = Decimal(request.POST.get('ajuste_producao_percentual', '0') or '0')
        cenario.ajuste_taxas_percentual = Decimal(request.POST.get('ajuste_taxas_percentual', '0') or '0')
        cenario.save()
        
        messages.success(request, f'Cenário "{nome}" atualizado com sucesso!')
        return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    # GET - retornar dados do cenário em JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'id': cenario.id,
            'nome': cenario.nome,
            'descricao': cenario.descricao or '',
            'is_baseline': cenario.is_baseline,
            'ajuste_preco_percentual': str(cenario.ajuste_preco_percentual),
            'ajuste_custo_percentual': str(cenario.ajuste_custo_percentual),
            'ajuste_producao_percentual': str(cenario.ajuste_producao_percentual),
            'ajuste_taxas_percentual': str(cenario.ajuste_taxas_percentual),
        })
    
    # GET normal - redirecionar para a página principal
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def excluir_cenario(request, propriedade_id, cenario_id):
    """Excluir cenário"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    cenario = get_object_or_404(
        CenarioPlanejamento, 
        id=cenario_id,
        planejamento__propriedade=propriedade
    )
    
    # Não permitir excluir baseline se for o único cenário
    if cenario.is_baseline:
        total_cenarios = CenarioPlanejamento.objects.filter(planejamento=cenario.planejamento).count()
        if total_cenarios == 1:
            messages.error(request, 'Não é possível excluir o cenário baseline se for o único cenário.')
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    nome = cenario.nome
    cenario.delete()
    
    messages.success(request, f'Cenário "{nome}" excluído com sucesso!')
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def comparar_cenarios_api(request, propriedade_id):
    """API para comparar cenários"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id, 
        produtor__usuario_responsavel=request.user
    )
    
    planejamento_id = request.GET.get('planejamento_id')
    if not planejamento_id:
        return JsonResponse({'erro': 'planejamento_id é obrigatório'}, status=400)
    
    planejamento = get_object_or_404(PlanejamentoAnual, id=planejamento_id, propriedade=propriedade)
    
    cenarios_ids = request.GET.getlist('cenarios_ids[]')
    if not cenarios_ids:
        cenarios = planejamento.cenarios.all()
    else:
        cenarios = CenarioPlanejamento.objects.filter(
            id__in=cenarios_ids,
            planejamento=planejamento
        )
    
    dados_comparacao = []
    for cenario in cenarios:
        metricas = calcular_metricas_cenario(planejamento, cenario)
        dados_comparacao.append({
            'id': cenario.id,
            'nome': cenario.nome,
            'is_baseline': cenario.is_baseline,
            'metricas': metricas
        })
    
    return JsonResponse({
        'cenarios': dados_comparacao
    })


def calcular_metricas_cenario(planejamento, cenario):
    """Calcula métricas financeiras e operacionais de um cenário"""
    # Buscar metas comerciais
    metas_comerciais = MetaComercialPlanejada.objects.filter(planejamento=planejamento)
    
    # Calcular receitas projetadas com ajuste de preço
    receitas_totais = Decimal('0')
    quantidade_animais = 0
    arrobas_totais = Decimal('0')
    
    for meta in metas_comerciais:
        preco_ajustado = meta.preco_medio_esperado * (1 + cenario.ajuste_preco_percentual / 100)
        quantidade_ajustada = int(meta.quantidade_animais * (1 + cenario.ajuste_producao_percentual / 100))
        
        receita_meta = preco_ajustado * quantidade_ajustada
        if meta.arrobas_totais:
            receita_meta = preco_ajustado * meta.arrobas_totais * (1 + cenario.ajuste_producao_percentual / 100)
        
        receitas_totais += receita_meta
        quantidade_animais += quantidade_ajustada
        if meta.arrobas_totais:
            arrobas_totais += meta.arrobas_totais * (1 + cenario.ajuste_producao_percentual / 100)
    
    # Buscar metas financeiras (custos)
    metas_financeiras = MetaFinanceiraPlanejada.objects.filter(planejamento=planejamento)
    
    custos_totais = Decimal('0')
    for meta in metas_financeiras:
        custo_ajustado = meta.valor_anual_previsto * (1 + cenario.ajuste_custo_percentual / 100)
        custos_totais += custo_ajustado
    
    # Calcular lucro
    lucro = receitas_totais - custos_totais
    
    # Calcular margem
    margem = (lucro / receitas_totais * 100) if receitas_totais > 0 else Decimal('0')
    
    return {
        'receitas_totais': float(receitas_totais),
        'custos_totais': float(custos_totais),
        'lucro': float(lucro),
        'margem': float(margem),
        'quantidade_animais': quantidade_animais,
        'arrobas_totais': float(arrobas_totais),
    }


@login_required
def gerar_vendas_cenario(request, propriedade_id, cenario_id):
    """Gerar vendas projetadas para um cenário específico"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    cenario = get_object_or_404(
        CenarioPlanejamento,
        id=cenario_id,
        planejamento__propriedade=propriedade
    )
    
    try:
        # Verificar se há movimentações antes de tentar gerar
        movimentacoes_venda = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=cenario.planejamento,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        )
        total_movimentacoes = movimentacoes_venda.count()
        
        if total_movimentacoes == 0:
            messages.warning(
                request,
                f'⚠️ Nenhuma movimentação de VENDA encontrada para o planejamento {cenario.planejamento.codigo}. '
                f'É necessário gerar primeiro as projeções na página "Projeções do Rebanho".'
            )
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
        
        vendas_criadas = gerar_vendas_do_cenario(propriedade, cenario)
        
        if len(vendas_criadas) > 0:
            messages.success(
                request,
                f'✅ Vendas geradas com sucesso! Total: {len(vendas_criadas)} vendas criadas para o cenário "{cenario.nome}".'
            )
        else:
            # Verificar se já existem vendas
            vendas_existentes = VendaProjetada.objects.filter(
                propriedade=propriedade,
                cenario=cenario
            ).count()
            
            if vendas_existentes > 0:
                messages.info(
                    request,
                    f'ℹ️ Todas as vendas já estão geradas para o cenário "{cenario.nome}". '
                    f'Total: {vendas_existentes} vendas existentes.'
                )
            else:
                messages.warning(
                    request,
                    f'⚠️ Nenhuma venda foi gerada. Foram encontradas {total_movimentacoes} movimentações de VENDA, '
                    f'mas nenhuma venda foi criada. Verifique os logs para mais detalhes.'
                )
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar vendas: {traceback.format_exc()}')
        messages.error(
            request, 
            f'❌ Erro ao gerar vendas: {str(e)}. '
            f'Verifique os logs para mais detalhes.'
        )
    
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def gerar_vendas_todos_cenarios_view(request, propriedade_id):
    """Gerar vendas para todos os cenários do planejamento atual"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    # Buscar planejamento atual - pode vir da URL como parâmetro (codigo ou planejamento_id)
    planejamento = None
    codigo_busca = request.GET.get('codigo', '').strip()
    planejamento_id = request.GET.get('planejamento_id')
    
    # PRIORIDADE 1: Buscar por código (mais específico) - PROJEÇÃO SELECIONADA PELO USUÁRIO
    if codigo_busca:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            )
            messages.info(request, f'✅ Gerando vendas para a projeção selecionada: {planejamento.codigo}')
        except PlanejamentoAnual.DoesNotExist:
            messages.error(request, f'❌ Nenhuma projeção encontrada com o código: {codigo_busca.upper()}')
            planejamento = None
        except PlanejamentoAnual.MultipleObjectsReturned:
            planejamento = PlanejamentoAnual.objects.filter(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            ).order_by('-data_criacao').first()
            if planejamento:
                messages.info(request, f'✅ Gerando vendas para a projeção selecionada: {planejamento.codigo}')
    
    # PRIORIDADE 2: Buscar por ID
    if not planejamento and planejamento_id:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                id=planejamento_id,
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            planejamento = None
    
    # PRIORIDADE 3: Buscar o planejamento mais recente por data de criação
    if not planejamento:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        messages.error(request, 'Nenhum planejamento encontrado. Crie um planejamento primeiro gerando uma projeção na página "Projeções do Rebanho".')
        return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    # Buscar o planejamento mais recente que tem movimentações de VENDA
    # Isso garante que usamos o planejamento correto mesmo quando há múltiplos no mesmo ano
    planejamento_com_movimentacoes = PlanejamentoAnual.objects.filter(
        propriedade=propriedade,
        movimentacoes_planejadas__tipo_movimentacao='VENDA',
        movimentacoes_planejadas__quantidade__gt=0
    ).distinct().order_by('-data_criacao').first()
    
    # Se encontrou um planejamento com movimentações, sempre usar o mais recente
    if planejamento_com_movimentacoes:
        # Verificar se o planejamento atual tem movimentações
        movimentacoes_atual = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            quantidade__gt=0,
            planejamento=planejamento
        ).count()
        
        # Se o planejamento com movimentações é mais recente ou o atual não tem movimentações, usar ele
        if planejamento_com_movimentacoes.data_criacao > planejamento.data_criacao or movimentacoes_atual == 0:
            planejamento = planejamento_com_movimentacoes
    
    # Verificar se há movimentações de VENDA antes de tentar gerar
    # IMPORTANTE: Buscar TODAS as movimentações do planejamento (incluindo múltiplos anos)
    movimentacoes_venda = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        tipo_movimentacao='VENDA',
        quantidade__gt=0
    )
    
    # Filtrar por planejamento - buscar todas vinculadas ao planejamento
    total_movimentacoes = 0
    if planejamento:
        movimentacoes_venda = movimentacoes_venda.filter(planejamento=planejamento)
        total_movimentacoes = movimentacoes_venda.count()
        
        # Se não encontrou, tentar vincular movimentações sem planejamento
        # OU movimentações vinculadas a outros planejamentos recentes do mesmo período
        if total_movimentacoes == 0:
            # Buscar movimentações sem planejamento que podem pertencer a este
            anos_busca = [planejamento.ano + i for i in range(-2, 6)]
            movimentacoes_sem_planejamento = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='VENDA',
                quantidade__gt=0,
                planejamento__isnull=True,
                data_movimentacao__year__in=anos_busca
            )
            
            total_sem_planejamento = movimentacoes_sem_planejamento.count()
            if total_sem_planejamento > 0:
                # Vincular ao planejamento
                movimentacoes_sem_planejamento.update(planejamento=planejamento)
                messages.info(
                    request,
                    f'ℹ️ {total_sem_planejamento} movimentações de VENDA foram vinculadas ao planejamento {planejamento.codigo}.'
                )
                total_movimentacoes = total_sem_planejamento
                # Recarregar a query após vincular
                movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    tipo_movimentacao='VENDA',
                    quantidade__gt=0,
                    planejamento=planejamento
                )
            
            # Se ainda não encontrou, tentar buscar movimentações de planejamentos recentes do mesmo período
            if total_movimentacoes == 0:
                from datetime import timedelta
                # Buscar planejamentos criados recentemente (últimas 24 horas)
                data_limite = timezone.now() - timedelta(hours=24)
                planejamentos_recentes = PlanejamentoAnual.objects.filter(
                    propriedade=propriedade,
                    data_criacao__gte=data_limite
                ).order_by('-data_criacao')
                
                for plan_recente in planejamentos_recentes:
                    movimentacoes_outro_planejamento = MovimentacaoProjetada.objects.filter(
                        propriedade=propriedade,
                        tipo_movimentacao='VENDA',
                        quantidade__gt=0,
                        planejamento=plan_recente
                    ).count()
                    
                    if movimentacoes_outro_planejamento > 0:
                        # Se o planejamento recente tem movimentações e é mais recente, usar ele
                        if plan_recente.data_criacao > planejamento.data_criacao:
                            planejamento = plan_recente
                            movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                                propriedade=propriedade,
                                tipo_movimentacao='VENDA',
                                quantidade__gt=0,
                                planejamento=planejamento
                            )
                            total_movimentacoes = movimentacoes_venda.count()
                            messages.info(
                                request,
                                f'ℹ️ Usando o planejamento mais recente {planejamento.codigo} que possui {total_movimentacoes} movimentações de VENDA.'
                            )
                        else:
                            # Transferir movimentações do outro planejamento para este
                            MovimentacaoProjetada.objects.filter(
                                propriedade=propriedade,
                                tipo_movimentacao='VENDA',
                                quantidade__gt=0,
                                planejamento=plan_recente
                            ).update(planejamento=planejamento)
                            
                            messages.info(
                                request,
                                f'ℹ️ {movimentacoes_outro_planejamento} movimentações de VENDA foram transferidas do planejamento {plan_recente.codigo} para {planejamento.codigo}.'
                            )
                            total_movimentacoes = movimentacoes_outro_planejamento
                            # Recarregar a query após transferir
                            movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                                propriedade=propriedade,
                                tipo_movimentacao='VENDA',
                                quantidade__gt=0,
                                planejamento=planejamento
                            )
                        break
    
    if total_movimentacoes == 0:
        # Verificar se há movimentações de VENDA em geral para esta propriedade
        total_vendas_geral = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        ).count()
        
        if total_vendas_geral == 0:
            messages.warning(
                request,
                f'⚠️ Nenhuma movimentação de VENDA encontrada para esta propriedade. '
                f'É necessário gerar primeiro as projeções na página "Projeções do Rebanho" '
                f'para criar movimentações de venda que possam ser convertidas em vendas projetadas.'
            )
        else:
            # Buscar TODAS as movimentações de VENDA (vinculadas a qualquer planejamento ou sem planejamento)
            # e transferir para o planejamento atual
            movimentacoes_todas = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='VENDA',
                quantidade__gt=0
            )
            
            # Buscar movimentações de outros planejamentos recentes (últimos 7 dias)
            from datetime import timedelta
            data_limite = timezone.now() - timedelta(days=7)
            planejamentos_com_movimentacoes = PlanejamentoAnual.objects.filter(
                propriedade=propriedade,
                movimentacoes_planejadas__tipo_movimentacao='VENDA',
                movimentacoes_planejadas__quantidade__gt=0
            ).distinct().order_by('-data_criacao')
            
            total_transferidas = 0
            planejamento_origem = None
            
            # Se encontrou planejamentos com movimentações, transferir do mais recente
            if planejamentos_com_movimentacoes.exists():
                planejamento_origem = planejamentos_com_movimentacoes.first()
                movimentacoes_para_transferir = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    tipo_movimentacao='VENDA',
                    quantidade__gt=0,
                    planejamento=planejamento_origem
                )
                total_transferidas = movimentacoes_para_transferir.count()
                
                if total_transferidas > 0:
                    # Transferir todas as movimentações para o planejamento atual
                    movimentacoes_para_transferir.update(planejamento=planejamento)
                    messages.success(
                        request,
                        f'✅ {total_transferidas} movimentações de VENDA foram transferidas do planejamento {planejamento_origem.codigo} para {planejamento.codigo}. '
                        f'As vendas serão geradas agora.'
                    )
                    # Recarregar a query após transferir
                    movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                        propriedade=propriedade,
                        tipo_movimentacao='VENDA',
                        quantidade__gt=0,
                        planejamento=planejamento
                    )
                    total_movimentacoes = movimentacoes_venda.count()
                else:
                    # Tentar vincular movimentações sem planejamento
                    ano_atual = timezone.now().year
                    anos_busca = list(range(planejamento.ano - 2, planejamento.ano + 6))
                    
                    movimentacoes_para_vincular = MovimentacaoProjetada.objects.filter(
                        propriedade=propriedade,
                        tipo_movimentacao='VENDA',
                        quantidade__gt=0,
                        planejamento__isnull=True,
                        data_movimentacao__year__in=anos_busca
                    )
                    
                    total_para_vincular = movimentacoes_para_vincular.count()
                    
                    if total_para_vincular > 0:
                        # Vincular automaticamente
                        movimentacoes_para_vincular.update(planejamento=planejamento)
                        messages.success(
                            request,
                            f'✅ {total_para_vincular} movimentações de VENDA foram vinculadas ao planejamento {planejamento.codigo}. '
                            f'As vendas serão geradas agora.'
                        )
                        movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                            propriedade=propriedade,
                            tipo_movimentacao='VENDA',
                            quantidade__gt=0,
                            planejamento=planejamento
                        )
                        total_movimentacoes = movimentacoes_venda.count()
                    else:
                        messages.warning(
                            request,
                            f'⚠️ Nenhuma movimentação de VENDA encontrada para a projeção {planejamento.codigo} (ano {planejamento.ano}). '
                            f'Foram encontradas {total_vendas_geral} movimentações de VENDA na propriedade, '
                            f'mas nenhuma está no período de busca ({anos_busca[0]}-{anos_busca[-1]}). '
                            f'Verifique se as movimentações foram geradas corretamente.'
                        )
                        return redirect('analise_cenarios', propriedade_id=propriedade.id)
            else:
                # Tentar vincular movimentações sem planejamento
                ano_atual = timezone.now().year
                anos_busca = list(range(planejamento.ano - 2, planejamento.ano + 6))
                
                movimentacoes_para_vincular = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    tipo_movimentacao='VENDA',
                    quantidade__gt=0,
                    planejamento__isnull=True,
                    data_movimentacao__year__in=anos_busca
                )
                
                total_para_vincular = movimentacoes_para_vincular.count()
                
                if total_para_vincular > 0:
                    # Vincular automaticamente
                    movimentacoes_para_vincular.update(planejamento=planejamento)
                    messages.success(
                        request,
                        f'✅ {total_para_vincular} movimentações de VENDA foram vinculadas ao planejamento {planejamento.codigo}. '
                        f'As vendas serão geradas agora.'
                    )
                    movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                        propriedade=propriedade,
                        tipo_movimentacao='VENDA',
                        quantidade__gt=0,
                        planejamento=planejamento
                    )
                    total_movimentacoes = movimentacoes_venda.count()
                else:
                    messages.warning(
                        request,
                        f'⚠️ Nenhuma movimentação de VENDA encontrada para a projeção {planejamento.codigo} (ano {planejamento.ano}). '
                        f'Foram encontradas {total_vendas_geral} movimentações de VENDA na propriedade, '
                        f'mas nenhuma está no período de busca ({anos_busca[0]}-{anos_busca[-1]}). '
                        f'Verifique se as movimentações foram geradas corretamente.'
                    )
                    return redirect('analise_cenarios', propriedade_id=propriedade.id)
        
        # Se ainda não tem movimentações após tentar transferir/vincular, retornar
        if total_movimentacoes == 0:
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    try:
        # Verificar quantas vendas já existem antes de gerar
        vendas_existentes_antes = VendaProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento
        ).count()
        
        # Verificar se há movimentações antes de tentar gerar
        movimentacoes_finais = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            quantidade__gt=0,
            planejamento=planejamento
        ).count()
        
        if movimentacoes_finais == 0:
            messages.error(
                request,
                f'❌ Não foi possível gerar vendas. Nenhuma movimentação de VENDA encontrada vinculada ao planejamento {planejamento.codigo}. '
                f'Verifique se as movimentações foram transferidas corretamente.'
            )
            return redirect('analise_cenarios', propriedade_id=propriedade.id)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Iniciando geração de vendas para planejamento {planejamento.codigo} com {movimentacoes_finais} movimentações")
        
        # Verificar se há cenários, se não houver, criar um baseline automaticamente
        total_cenarios = planejamento.cenarios.count()
        if total_cenarios == 0:
            logger.info(f"Nenhum cenário encontrado. Criando cenário Baseline automaticamente...")
            cenario_baseline = CenarioPlanejamento.objects.create(
                planejamento=planejamento,
                nome="Baseline",
                descricao="Cenário base criado automaticamente para geração de vendas",
                is_baseline=True
            )
            messages.info(
                request,
                f'ℹ️ Um cenário "Baseline" foi criado automaticamente para a projeção {planejamento.codigo}.'
            )
            logger.info(f"Cenário Baseline criado: {cenario_baseline.id}")
        
        vendas_geradas = gerar_vendas_todos_cenarios(propriedade, planejamento)
        total_vendas = sum(len(vendas) for vendas in vendas_geradas.values())
        
        # Verificar quantas vendas existem agora
        vendas_existentes_agora = VendaProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento
        ).count()
        
        logger.info(f"Vendas geradas: {total_vendas} novas, {vendas_existentes_agora} total")
        
        if total_vendas > 0:
            messages.success(
                request,
                f'✅ Vendas geradas com sucesso para a projeção {planejamento.codigo}! '
                f'Total: {total_vendas} novas vendas criadas para {len(vendas_geradas)} cenários. '
                f'Total geral de vendas: {vendas_existentes_agora}'
            )
        else:
            # Verificar quantos cenários têm vendas
            cenarios_com_vendas = VendaProjetada.objects.filter(
                propriedade=propriedade,
                planejamento=planejamento
            ).values('cenario').distinct().count()
            
            total_cenarios = planejamento.cenarios.count()
            
            if vendas_existentes_agora > 0:
                messages.info(
                    request,
                    f'ℹ️ Todas as vendas já estão geradas! '
                    f'Total: {vendas_existentes_agora} vendas para {cenarios_com_vendas} cenários. '
                    f'Foram encontradas {movimentacoes_finais} movimentações de VENDA, '
                    f'e todas já possuem vendas projetadas geradas.'
                )
            else:
                # Verificar se há cenários no planejamento
                if total_cenarios == 0:
                    messages.warning(
                        request,
                        f'⚠️ Nenhum cenário encontrado no planejamento {planejamento.codigo}. '
                        f'Crie pelo menos um cenário antes de gerar vendas.'
                    )
                else:
                    messages.warning(
                        request,
                        f'⚠️ Nenhuma venda foi gerada. Foram encontradas {movimentacoes_finais} movimentações de VENDA, '
                        f'mas nenhuma venda foi criada. Verifique os logs para mais detalhes. '
                        f'Total de cenários: {total_cenarios}'
                    )
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar vendas: {traceback.format_exc()}')
        messages.error(
            request, 
            f'❌ Erro ao gerar vendas: {str(e)}. '
            f'Foram encontradas {total_movimentacoes} movimentações de VENDA. '
            f'Verifique os logs para mais detalhes.'
        )
    
    return redirect('analise_cenarios', propriedade_id=propriedade.id)


@login_required
def relatorio_vendas_projecao(request, propriedade_id):
    """Relatório de vendas da projeção - página principal"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    # Buscar planejamento - pode vir da URL como parâmetro (codigo ou planejamento_id)
    planejamento = None
    codigo_busca = request.GET.get('codigo', '').strip()
    planejamento_id = request.GET.get('planejamento_id')
    
    # PRIORIDADE 1: Buscar por código (projeção selecionada pelo usuário)
    if codigo_busca:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            messages.error(request, f'❌ Nenhuma projeção encontrada com o código: {codigo_busca.upper()}')
            planejamento = None
        except PlanejamentoAnual.MultipleObjectsReturned:
            planejamento = PlanejamentoAnual.objects.filter(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            ).order_by('-data_criacao').first()
    
    # PRIORIDADE 2: Buscar por ID
    if not planejamento and planejamento_id:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                id=planejamento_id,
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            planejamento = None
    
    # PRIORIDADE 3: Buscar o planejamento mais recente por data de criação
    if not planejamento:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        messages.warning(request, 'Nenhum planejamento encontrado. Crie um planejamento primeiro gerando uma projeção na página "Projeções do Rebanho".')
        return redirect('analise_cenarios', propriedade_id=propriedade.id)
    
    # Filtros
    cenario_id = request.GET.get('cenario')
    ano = request.GET.get('ano')  # Removido default - se não informado, mostra todos os anos
    mes = request.GET.get('mes')
    tipo_relatorio = request.GET.get('tipo', 'geral')  # geral, mensal, anual
    
    # Buscar vendas - TODAS do planejamento (pode incluir múltiplos anos da projeção)
    vendas_query = VendaProjetada.objects.filter(
        propriedade=propriedade,
        planejamento=planejamento
    )
    
    if cenario_id:
        vendas_query = vendas_query.filter(cenario_id=cenario_id)
    
    # Filtrar por ano apenas se especificado (se não informado, mostra todos os anos)
    if ano:
        vendas_query = vendas_query.filter(data_venda__year=int(ano))
    
    if mes:
        vendas_query = vendas_query.filter(data_venda__month=int(mes))
    
    vendas = vendas_query.order_by('-data_venda', 'categoria')
    
    # Debug: Log para entender o que está sendo buscado
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"DEBUG relatorio_vendas_projecao - Planejamento: {planejamento.codigo if planejamento else 'None'}")
    logger.info(f"DEBUG relatorio_vendas_projecao - Planejamento ID: {planejamento.id if planejamento else 'None'}")
    logger.info(f"DEBUG relatorio_vendas_projecao - Total de vendas encontradas: {vendas.count()}")
    
    # Verificar se há vendas no banco de dados para este planejamento (sem filtros)
    vendas_totais_planejamento = VendaProjetada.objects.filter(
        propriedade=propriedade,
        planejamento=planejamento
    ).count()
    logger.info(f"DEBUG relatorio_vendas_projecao - Total de vendas no banco para este planejamento: {vendas_totais_planejamento}")
    
    # Se não há vendas, verificar se há movimentações
    if vendas_totais_planejamento == 0:
        movimentacoes_count = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        ).count()
        logger.info(f"DEBUG relatorio_vendas_projecao - Movimentações VENDA encontradas: {movimentacoes_count}")
        
        cenarios_count = planejamento.cenarios.count()
        logger.info(f"DEBUG relatorio_vendas_projecao - Cenários encontrados: {cenarios_count}")
        
        if movimentacoes_count > 0 and cenarios_count == 0:
            messages.warning(
                request,
                f'⚠️ Nenhuma venda encontrada para a projeção {planejamento.codigo}. '
                f'Foram encontradas {movimentacoes_count} movimentações de VENDA, mas não há cenários. '
                f'Clique em "Gerar Vendas" para criar um cenário automaticamente e gerar as vendas.'
            )
        elif movimentacoes_count == 0:
            messages.warning(
                request,
                f'⚠️ Nenhuma movimentação de VENDA encontrada para a projeção {planejamento.codigo}. '
                f'É necessário gerar primeiro as projeções na página "Projeções do Rebanho".'
            )
    
    # Buscar range de anos disponíveis nas vendas/movimentações para exibir no filtro
    # Primeiro tenta buscar das vendas, se não houver, busca das movimentações
    if vendas.exists():
        anos_disponiveis = list(vendas.values_list('data_venda__year', flat=True).distinct().order_by('data_venda__year'))
        logger.info(f"DEBUG relatorio_vendas_projecao - Anos encontrados nas vendas: {anos_disponiveis}")
    else:
        # Buscar anos das movimentações projetadas vinculadas ao planejamento
        anos_disponiveis = list(MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        ).values_list('data_movimentacao__year', flat=True).distinct().order_by('data_movimentacao__year'))
    
    if not anos_disponiveis:
        anos_disponiveis = [planejamento.ano]
    
    # Se não houver vendas e houver movimentações de VENDA, gerar automaticamente
    if not vendas.exists():
        # Verificar se existem movimentações de VENDA para gerar vendas
        # Buscar com planejamento ou sem planejamento (apenas por propriedade e ano)
        movimentacoes_venda = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        )
        
        # Filtrar por planejamento - buscar TODAS as movimentações do planejamento (todos os anos)
        if planejamento:
            movimentacoes_venda = movimentacoes_venda.filter(planejamento=planejamento)
        elif ano:
            movimentacoes_venda = movimentacoes_venda.filter(data_movimentacao__year=ano)
        
        if movimentacoes_venda.exists():
            # Gerar vendas para todos os cenários do planejamento
            from .services.gerar_vendas_projecao import gerar_vendas_todos_cenarios
            try:
                gerar_vendas_todos_cenarios(propriedade, planejamento)
                # Recarregar vendas
                vendas_query = VendaProjetada.objects.filter(
                    propriedade=propriedade
                )
                if planejamento:
                    vendas_query = vendas_query.filter(planejamento=planejamento)
                if cenario_id:
                    vendas_query = vendas_query.filter(cenario_id=cenario_id)
                if ano:
                    vendas_query = vendas_query.filter(data_venda__year=ano)
                if mes:
                    vendas_query = vendas_query.filter(data_venda__month=mes)
                vendas = vendas_query.order_by('-data_venda', 'categoria')
                messages.info(request, f'Vendas geradas automaticamente! Total: {vendas.count()} vendas criadas.')
            except Exception as e:
                import traceback
                messages.warning(request, f'Erro ao gerar vendas automaticamente: {str(e)}')
                # Log do erro para debug
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao gerar vendas: {traceback.format_exc()}')
    
    # Buscar cenários disponíveis
    cenarios = planejamento.cenarios.all().order_by('-is_baseline', 'nome')
    
    # Se não há cenários mas há movimentações, criar um cenário padrão automaticamente
    if not cenarios.exists():
        movimentacoes_existem = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        ).exists()
        
        if movimentacoes_existem:
            # Criar cenário baseline automaticamente
            cenario_baseline = CenarioPlanejamento.objects.create(
                planejamento=planejamento,
                nome="Baseline",
                descricao="Cenário base criado automaticamente",
                is_baseline=True
            )
            cenarios = planejamento.cenarios.all().order_by('-is_baseline', 'nome')
            messages.info(request, f'ℹ️ Um cenário "Baseline" foi criado automaticamente para a projeção {planejamento.codigo}.')
    
    # Converter queryset para lista para melhor renderização no template
    vendas_lista = list(vendas)
    
    # Estatísticas gerais
    total_vendas = len(vendas_lista)
    total_quantidade = sum(v.quantidade for v in vendas_lista)
    total_valor = sum(v.valor_total or Decimal('0') for v in vendas_lista)
    total_peso = sum(v.peso_total_kg or Decimal('0') for v in vendas_lista)
    
    logger.info(f"DEBUG relatorio_vendas_projecao - Estatísticas: Total={total_vendas}, Quantidade={total_quantidade}, Valor={total_valor}, Peso={total_peso}")
    
    # Agrupar por ANO primeiro
    vendas_por_ano = defaultdict(lambda: {
        'vendas': [],
        'total_quantidade': 0,
        'total_valor': Decimal('0'),
        'total_peso': Decimal('0'),
        'meses': defaultdict(lambda: {
            'vendas': [],
            'total_quantidade': 0,
            'total_valor': Decimal('0'),
            'total_peso': Decimal('0')
        })
    })
    
    for venda in vendas_lista:
        ano = venda.data_venda.year
        mes_num = venda.data_venda.month
        mes_ano = f"{ano}-{mes_num:02d}"
        
        # Agrupar por ano
        vendas_por_ano[ano]['vendas'].append(venda)
        vendas_por_ano[ano]['total_quantidade'] += venda.quantidade
        vendas_por_ano[ano]['total_valor'] += venda.valor_total or Decimal('0')
        if venda.peso_total_kg:
            vendas_por_ano[ano]['total_peso'] += venda.peso_total_kg
        
        # Agrupar por mês dentro do ano
        vendas_por_ano[ano]['meses'][mes_num]['vendas'].append(venda)
        vendas_por_ano[ano]['meses'][mes_num]['total_quantidade'] += venda.quantidade
        vendas_por_ano[ano]['meses'][mes_num]['total_valor'] += venda.valor_total or Decimal('0')
        if venda.peso_total_kg:
            vendas_por_ano[ano]['meses'][mes_num]['total_peso'] += venda.peso_total_kg
    
    # Converter para lista ordenada por ano
    vendas_por_ano_lista = []
    for ano in sorted(vendas_por_ano.keys(), reverse=True):
        dados_ano = vendas_por_ano[ano]
        meses_lista = []
        for mes_num in sorted(dados_ano['meses'].keys()):
            meses_lista.append({
                'mes': mes_num,
                'mes_nome': month_name[mes_num],
                **dados_ano['meses'][mes_num]
            })
        
        vendas_por_ano_lista.append({
            'ano': ano,
            'total_quantidade': dados_ano['total_quantidade'],
            'total_valor': dados_ano['total_valor'],
            'total_peso': dados_ano['total_peso'],
            'vendas': dados_ano['vendas'],
            'meses': meses_lista
        })
    
    # Manter também agrupamento mensal para compatibilidade
    vendas_por_mes = defaultdict(lambda: {
        'vendas': [],
        'total_quantidade': 0,
        'total_valor': Decimal('0'),
        'total_peso': Decimal('0')
    })
    
    for venda in vendas:
        mes_ano = f"{venda.data_venda.year}-{venda.data_venda.month:02d}"
        vendas_por_mes[mes_ano]['vendas'].append(venda)
        vendas_por_mes[mes_ano]['total_quantidade'] += venda.quantidade
        vendas_por_mes[mes_ano]['total_valor'] += venda.valor_total
        if venda.peso_total_kg:
            vendas_por_mes[mes_ano]['total_peso'] += venda.peso_total_kg
    
    # Converter para lista ordenada
    vendas_por_mes_lista = []
    for mes_ano in sorted(vendas_por_mes.keys(), reverse=True):
        ano_mes, mes_num = mes_ano.split('-')
        vendas_por_mes_lista.append({
            'mes_ano': mes_ano,
            'ano': int(ano_mes),
            'mes': int(mes_num),
            'mes_nome': month_name[int(mes_num)],
            **vendas_por_mes[mes_ano]
        })
    
    # Agrupar por categoria
    vendas_por_categoria = defaultdict(lambda: {
        'vendas': [],
        'total_quantidade': 0,
        'total_valor': Decimal('0'),
        'total_peso': Decimal('0')
    })
    
    for venda in vendas_lista:
        cat_nome = venda.categoria.nome
        vendas_por_categoria[cat_nome]['vendas'].append(venda)
        vendas_por_categoria[cat_nome]['total_quantidade'] += venda.quantidade
        vendas_por_categoria[cat_nome]['total_valor'] += venda.valor_total or Decimal('0')
        if venda.peso_total_kg:
            vendas_por_categoria[cat_nome]['total_peso'] += venda.peso_total_kg
    
    # Agrupar por cliente
    vendas_por_cliente = defaultdict(lambda: {
        'vendas': [],
        'total_quantidade': 0,
        'total_valor': Decimal('0'),
        'total_peso': Decimal('0')
    })
    
    for venda in vendas_lista:
        cliente_nome = venda.cliente_nome or "Cliente não definido"
        vendas_por_cliente[cliente_nome]['vendas'].append(venda)
        vendas_por_cliente[cliente_nome]['total_quantidade'] += venda.quantidade
        vendas_por_cliente[cliente_nome]['total_valor'] += venda.valor_total
        if venda.peso_total_kg:
            vendas_por_cliente[cliente_nome]['total_peso'] += venda.peso_total_kg
    
    context = {
        'propriedade': propriedade,
        'planejamento': planejamento,
        'cenarios': cenarios,
        'cenario_selecionado': int(cenario_id) if cenario_id else None,
        'ano_selecionado': int(ano) if ano else None,
        'mes_selecionado': int(mes) if mes else None,
        'tipo_relatorio': tipo_relatorio,
        'vendas': vendas_lista,
        'total_vendas': total_vendas,
        'total_quantidade': total_quantidade,
        'total_valor': float(total_valor),
        'total_peso': float(total_peso),
        'vendas_por_mes': vendas_por_mes_lista,
        'vendas_por_ano': vendas_por_ano_lista,
        'vendas_por_categoria': dict(vendas_por_categoria),
        'vendas_por_cliente': dict(vendas_por_cliente),
        'anos_disponiveis': anos_disponiveis,
        'anos_choices': range(min(anos_disponiveis) if anos_disponiveis else planejamento.ano - 5,
                             max(anos_disponiveis) + 1 if anos_disponiveis else planejamento.ano + 5),
    }
    
    return render(request, 'gestao_rural/relatorio_vendas_projecao.html', context)


@login_required
def relatorio_vendas_mensal(request, propriedade_id, ano, mes):
    """Relatório mensal detalhado de vendas"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    # Buscar planejamento - pode vir da URL como parâmetro (codigo ou planejamento_id)
    planejamento = None
    codigo_busca = request.GET.get('codigo', '').strip()
    planejamento_id = request.GET.get('planejamento_id')
    
    # PRIORIDADE 1: Buscar por código (projeção selecionada pelo usuário)
    if codigo_busca:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            messages.error(request, f'❌ Nenhuma projeção encontrada com o código: {codigo_busca.upper()}')
            planejamento = None
        except PlanejamentoAnual.MultipleObjectsReturned:
            planejamento = PlanejamentoAnual.objects.filter(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            ).order_by('-data_criacao').first()
    
    # PRIORIDADE 2: Buscar por ID
    if not planejamento and planejamento_id:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                id=planejamento_id,
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            planejamento = None
    
    # PRIORIDADE 3: Buscar o planejamento mais recente por data de criação
    if not planejamento:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        messages.warning(request, f'Nenhum planejamento encontrado.')
        return redirect('relatorio_vendas_projecao', propriedade_id=propriedade.id)
    
    cenario_id = request.GET.get('cenario')
    
    # Buscar vendas do mês
    vendas_query = VendaProjetada.objects.filter(
        propriedade=propriedade,
        planejamento=planejamento,
        data_venda__year=ano,
        data_venda__month=mes
    )
    
    if cenario_id:
        vendas_query = vendas_query.filter(cenario_id=cenario_id)
    
    vendas = vendas_query.order_by('data_venda', 'categoria')
    
    # Estatísticas do mês
    total_quantidade = sum(v.quantidade for v in vendas)
    total_valor = sum(v.valor_total for v in vendas)
    total_peso = sum(v.peso_total_kg or Decimal('0') for v in vendas)
    
    # Agrupar por categoria
    vendas_por_categoria = defaultdict(lambda: {
        'vendas': [],
        'quantidade': 0,
        'valor': Decimal('0'),
        'peso': Decimal('0')
    })
    
    for venda in vendas:
        cat_nome = venda.categoria.nome
        vendas_por_categoria[cat_nome]['vendas'].append(venda)
        vendas_por_categoria[cat_nome]['quantidade'] += venda.quantidade
        vendas_por_categoria[cat_nome]['valor'] += venda.valor_total
        if venda.peso_total_kg:
            vendas_por_categoria[cat_nome]['peso'] += venda.peso_total_kg
    
    context = {
        'propriedade': propriedade,
        'planejamento': planejamento,
        'ano': ano,
        'mes': mes,
        'mes_nome': month_name[mes],
        'vendas': vendas_lista,
        'vendas_por_categoria': dict(vendas_por_categoria),
        'total_quantidade': total_quantidade,
        'total_valor': float(total_valor),
        'total_peso': float(total_peso),
        'cenario_selecionado': int(cenario_id) if cenario_id else None,
    }
    
    return render(request, 'gestao_rural/relatorio_vendas_mensal.html', context)


@login_required
def relatorio_vendas_anual(request, propriedade_id, ano):
    """Relatório anual consolidado de vendas"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    # Buscar planejamento - pode vir da URL como parâmetro (codigo ou planejamento_id)
    planejamento = None
    codigo_busca = request.GET.get('codigo', '').strip()
    planejamento_id = request.GET.get('planejamento_id')
    
    # PRIORIDADE 1: Buscar por código (projeção selecionada pelo usuário)
    if codigo_busca:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            messages.error(request, f'❌ Nenhuma projeção encontrada com o código: {codigo_busca.upper()}')
            planejamento = None
        except PlanejamentoAnual.MultipleObjectsReturned:
            planejamento = PlanejamentoAnual.objects.filter(
                codigo=codigo_busca.upper(),
                propriedade=propriedade
            ).order_by('-data_criacao').first()
    
    # PRIORIDADE 2: Buscar por ID
    if not planejamento and planejamento_id:
        try:
            planejamento = PlanejamentoAnual.objects.get(
                id=planejamento_id,
                propriedade=propriedade
            )
        except PlanejamentoAnual.DoesNotExist:
            planejamento = None
    
    # PRIORIDADE 3: Buscar o planejamento mais recente por data de criação
    if not planejamento:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        messages.warning(request, f'Nenhum planejamento encontrado.')
        return redirect('relatorio_vendas_projecao', propriedade_id=propriedade.id)
    
    cenario_id = request.GET.get('cenario')
    
    # Buscar vendas do ano - TODAS do planejamento (pode incluir múltiplos anos da projeção)
    vendas_query = VendaProjetada.objects.filter(
        propriedade=propriedade,
        planejamento=planejamento,
        data_venda__year=ano
    )
    
    if cenario_id:
        vendas_query = vendas_query.filter(cenario_id=cenario_id)
    
    vendas = vendas_query.order_by('data_venda', 'categoria')
    
    # Converter queryset para lista para melhor renderização no template
    vendas_lista = list(vendas)
    
    # Estatísticas do ano
    total_quantidade = sum(v.quantidade for v in vendas_lista)
    total_valor = sum(v.valor_total or Decimal('0') for v in vendas_lista)
    total_peso = sum(v.peso_total_kg or Decimal('0') for v in vendas_lista)
    
    # Agrupar por mês
    vendas_por_mes = defaultdict(lambda: {
        'vendas': [],
        'quantidade': 0,
        'valor': Decimal('0'),
        'peso': Decimal('0')
    })
    
    for venda in vendas_lista:
        mes_num = venda.data_venda.month
        vendas_por_mes[mes_num]['vendas'].append(venda)
        vendas_por_mes[mes_num]['quantidade'] += venda.quantidade
        vendas_por_mes[mes_num]['valor'] += venda.valor_total or Decimal('0')
        if venda.peso_total_kg:
            vendas_por_mes[mes_num]['peso'] += venda.peso_total_kg
    
    # Converter para lista ordenada
    vendas_por_mes_lista = []
    for mes_num in sorted(vendas_por_mes.keys()):
        vendas_por_mes_lista.append({
            'mes': mes_num,
            'mes_nome': month_name[mes_num],
            **vendas_por_mes[mes_num]
        })
    
    # Agrupar por categoria
    vendas_por_categoria = defaultdict(lambda: {
        'quantidade': 0,
        'valor': Decimal('0'),
        'peso': Decimal('0')
    })
    
    for venda in vendas_lista:
        cat_nome = venda.categoria.nome
        vendas_por_categoria[cat_nome]['quantidade'] += venda.quantidade
        vendas_por_categoria[cat_nome]['valor'] += venda.valor_total or Decimal('0')
        if venda.peso_total_kg:
            vendas_por_categoria[cat_nome]['peso'] += venda.peso_total_kg
    
    context = {
        'propriedade': propriedade,
        'planejamento': planejamento,
        'ano': ano,
        'vendas': vendas_lista,
        'vendas_por_mes': vendas_por_mes_lista,
        'vendas_por_categoria': dict(vendas_por_categoria),
        'total_quantidade': total_quantidade,
        'total_valor': float(total_valor),
        'total_peso': float(total_peso),
        'cenario_selecionado': int(cenario_id) if cenario_id else None,
    }
    
    return render(request, 'gestao_rural/relatorio_vendas_anual.html', context)
