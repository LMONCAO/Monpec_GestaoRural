# -*- coding: utf-8 -*-
"""
Views Consolidadas - MÓDULO COMPRAS E ESTOQUE
Agrupa:
- Fornecedores
- Ordens de Compra
- Notas Fiscais (SEFAZ)
- Insumos/Estoque
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.forms import inlineformset_factory, formset_factory
from django import forms
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

from .models import Propriedade
from .decorators import obter_propriedade_com_permissao, bloquear_demo_cadastro
from .models_compras_financeiro import (
    Fornecedor, NotaFiscal, ItemNotaFiscal,
    OrdemCompra, ItemOrdemCompra,
    RequisicaoCompra, ItemRequisicaoCompra,
    AprovacaoRequisicaoCompra, CotacaoFornecedor,
    ItemCotacaoFornecedor, RecebimentoCompra,
    ItemRecebimentoCompra, EventoFluxoCompra,
    SetorPropriedade, ConviteCotacaoFornecedor,
    ContaPagar, OrcamentoCompraMensal, AjusteOrcamentoCompra,
    AutorizacaoExcedenteOrcamento,
    Produto, CategoriaProduto,
)
from .models_cadastros import Cliente
from .forms_completos import (
    RequisicaoCompraForm, ItemRequisicaoCompraForm,
    AprovacaoRequisicaoCompraForm, CotacaoFornecedorForm,
    ItemCotacaoFornecedorForm, RecebimentoCompraForm,
    ItemRecebimentoCompraForm, OrdemCompraForm, OrdemCompraAutorizacaoForm,
    SetorPropriedadeForm, ConviteCotacaoFornecedorForm,
    RespostaCotacaoFornecedorCabecalhoForm, RespostaItemCotacaoFornecedorForm,
    OrcamentoCompraMensalForm, AjusteOrcamentoCompraForm,
    NotaFiscalSaidaForm, ItemNotaFiscalForm,
    ProdutoForm, CategoriaProdutoForm,
)
from .services_receita_federal import (
    consultar_ncm, validar_cfop, sincronizar_produto
)
from .services import enviar_notificacao_compra


RequisicaoItemFormSet = inlineformset_factory(
    RequisicaoCompra,
    ItemRequisicaoCompra,
    form=ItemRequisicaoCompraForm,
    extra=3,
    can_delete=False
)

CotacaoItemFormSet = inlineformset_factory(
    CotacaoFornecedor,
    ItemCotacaoFornecedor,
    form=ItemCotacaoFornecedorForm,
    extra=0,
    can_delete=False
)

RecebimentoItemFormSet = inlineformset_factory(
    RecebimentoCompra,
    ItemRecebimentoCompra,
    form=ItemRecebimentoCompraForm,
    extra=0,
    can_delete=False
)


def gerar_conta_pagar_para_ordem(ordem):
    """
    Cria ou atualiza uma conta a pagar vinculada à ordem de compra.
    Gera uma previsão financeira para o valor total da OC.
    """
    data_vencimento = ordem.data_entrega_prevista or ordem.data_emissao
    descricao = f"OC {ordem.numero_ordem} - {ordem.fornecedor.nome}"
    defaults = {
        'propriedade': ordem.propriedade,
        'fornecedor': ordem.fornecedor,
        'descricao': descricao[:200],
        'categoria': str(ordem.plano_conta) if ordem.plano_conta else None,
        'valor': ordem.valor_total,
        'data_vencimento': data_vencimento,
        'forma_pagamento': ordem.forma_pagamento or ordem.condicoes_pagamento,
    }

    conta, created = ContaPagar.objects.get_or_create(
        ordem_compra=ordem,
        defaults=defaults,
    )

    if not created:
        campos_atualizados = []
        for campo, valor in defaults.items():
            if getattr(conta, campo) != valor:
                setattr(conta, campo, valor)
                campos_atualizados.append(campo)
        if campos_atualizados:
            conta.save(update_fields=campos_atualizados)
        else:
            # Força atualização do status com base na data
            conta.save()
    else:
        conta.save()

    return conta, created


def obter_historico_preco_item(ordem, item):
    """
    Retorna informações da última compra (mesmo fornecedor e geral)
    para comparação de preços.
    """
    base_qs = ItemOrdemCompra.objects.filter(
        ordem_compra__propriedade=ordem.propriedade,
        descricao__iexact=item.descricao,
    ).exclude(pk=item.pk).select_related('ordem_compra__fornecedor')

    ultimo_mesmo_fornecedor = base_qs.filter(
        ordem_compra__fornecedor=ordem.fornecedor
    ).order_by('-ordem_compra__data_emissao', '-ordem_compra__id').first()

    ultimo_geral = base_qs.order_by('-ordem_compra__data_emissao', '-ordem_compra__id').first()

    def montar_info(registro):
        if not registro:
            return None
        return {
            'valor_unitario': registro.valor_unitario,
            'data': registro.ordem_compra.data_emissao,
            'ordem': registro.ordem_compra.numero_ordem,
            'fornecedor': registro.ordem_compra.fornecedor.nome,
        }

    info_fornecedor = montar_info(ultimo_mesmo_fornecedor)
    info_geral = montar_info(ultimo_geral)

    def calcular_diferenca(valor_atual, valor_anterior):
        if valor_anterior in (None, 0):
            return None, None
        diferenca = valor_atual - valor_anterior
        percentual = (diferenca / valor_anterior) * 100 if valor_anterior else None
        return diferenca, percentual

    dif_fornecedor = (
        calcular_diferenca(item.valor_unitario, info_fornecedor['valor_unitario'])
        if info_fornecedor else (None, None)
    )
    dif_geral = (
        calcular_diferenca(item.valor_unitario, info_geral['valor_unitario'])
        if info_geral else (None, None)
    )

    return {
        'fornecedor': info_fornecedor,
        'geral': info_geral,
        'dif_fornecedor_valor': dif_fornecedor[0],
        'dif_fornecedor_percentual': dif_fornecedor[1],
        'dif_geral_valor': dif_geral[0],
        'dif_geral_percentual': dif_geral[1],
    }


def _buscar_orcamento(propriedade, setor, data_referencia):
    data_ref = data_referencia or timezone.localdate()
    qs = OrcamentoCompraMensal.objects.filter(
        propriedade=propriedade,
        ano=data_ref.year,
        mes=data_ref.month,
    )
    if setor:
        orcamento = qs.filter(setor=setor).first()
        if orcamento:
            return orcamento
    return qs.filter(setor__isnull=True).first()


def montar_contexto_orcamento(propriedade, setor, data_referencia=None, ignorar_ordem=None):
    orcamento = _buscar_orcamento(propriedade, setor, data_referencia)
    if not orcamento:
        return None

    utilizado = orcamento.valor_utilizado(ignorar_ordem=ignorar_ordem)
    return {
        'orcamento': orcamento,
        'valor_limite': orcamento.valor_limite,
        'limite_extra': orcamento.limite_extra,
        'total_limite': orcamento.total_limite,
        'valor_utilizado': utilizado,
        'saldo_disponivel': orcamento.total_limite - utilizado,
        'percentual_utilizado': orcamento.percentual_utilizado(ignorar_ordem=ignorar_ordem),
    }


def validar_orcamento_para_valor(propriedade, setor, data_emissao, valor, ignorar_ordem=None, verificar_autorizacao=True):
    """
    Valida se o valor excede o orçamento.
    Se verificar_autorizacao=True, verifica se há autorização de excedente aprovada.
    Retorna None se está OK, ou dict com informações do excedente se não está OK.
    """
    if valor <= Decimal('0.00'):
        return None

    orcamento = _buscar_orcamento(propriedade, setor, data_emissao)
    if not orcamento:
        return None

    if orcamento.excede_limite(valor, ignorar_ordem=ignorar_ordem):
        utilizado = orcamento.valor_utilizado(ignorar_ordem=ignorar_ordem)
        saldo_disponivel = orcamento.total_limite - utilizado
        valor_excedente = valor - saldo_disponivel
        
        # Verificar se há autorização de excedente
        autorizacao = None
        if verificar_autorizacao:
            autorizacao = orcamento.tem_autorizacao_excedente(valor, ignorar_ordem)
        
        return {
            'orcamento': orcamento,
            'utilizado': utilizado,
            'saldo_disponivel': saldo_disponivel,
            'valor_excedente': valor_excedente,
            'autorizacao': autorizacao,
        }
    return None


@login_required
def compras_dashboard(request, propriedade_id):
    """Dashboard consolidado de Compras"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Fornecedores
    fornecedores = Fornecedor.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True)
    ).order_by('nome')[:10]
    total_fornecedores = Fornecedor.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True)
    ).count()
    
    # Ordens de Compra
    ordens_pendentes = OrdemCompra.objects.filter(
        propriedade=propriedade,
        status__in=['RASCUNHO', 'APROVADA', 'ENVIADA']
    ).count()
    
    ordens_recentes = OrdemCompra.objects.filter(
        propriedade=propriedade
    ).select_related('fornecedor').order_by('-data_emissao')[:10]
    
    # Notas Fiscais
    mes_atual = date.today().replace(day=1)
    # Usar apenas select_related de fornecedor (cliente pode não existir se migração não aplicada)
    nfes_mes = NotaFiscal.objects.filter(
        propriedade=propriedade,
        data_emissao__gte=mes_atual
    ).select_related('fornecedor')
    valor_compras_mes = sum(nf.valor_total for nf in nfes_mes if nf.tipo == 'ENTRADA')
    
    # Orçamento Mensal - Calculado por parcelas (ContaPagar) com vencimento no mês
    hoje = date.today()
    orcamento_mes = _buscar_orcamento(propriedade, None, hoje)
    valor_orcamento_mes = Decimal('0.00')
    valor_comprometido_mes = Decimal('0.00')
    saldo_disponivel_mes = Decimal('0.00')
    percentual_utilizado_mes = 0
    
    if orcamento_mes:
        valor_orcamento_mes = orcamento_mes.total_limite
        valor_comprometido_mes = orcamento_mes.valor_utilizado()
        saldo_disponivel_mes = orcamento_mes.saldo_disponivel()
        percentual_utilizado_mes = orcamento_mes.percentual_utilizado()
    
    # Estatísticas
    nfes_pendentes = NotaFiscal.objects.filter(
        propriedade=propriedade,
        status='PENDENTE'
    ).select_related('fornecedor').count()

    setores = SetorPropriedade.objects.filter(propriedade=propriedade)
    total_setores = setores.count()
    setores_inativos = setores.filter(ativo=False).count()
    setores_sem_responsavel = setores.filter(responsavel__isnull=True).count()
    
    convites_queryset = ConviteCotacaoFornecedor.objects.filter(
        requisicao__propriedade=propriedade
    )
    timezone_now = timezone.now()
    convites_abertos = convites_queryset.filter(status='ENVIADO').count()
    convites_respondidos = convites_queryset.filter(status='RESPONDIDO').count()
    convites_expirados = convites_queryset.filter(status='EXPIRADO').count()
    convites_expirando = convites_queryset.filter(
        status='ENVIADO',
        data_expiracao__isnull=False,
        data_expiracao__gt=timezone_now,
        data_expiracao__lte=timezone_now + timedelta(days=2),
    ).count()
    convites_total = convites_queryset.count()

    requisicoes_pendentes = RequisicaoCompra.objects.filter(
        propriedade=propriedade,
        status__in=['ENVIADA', 'APROVADA_GERENCIA', 'EM_COTACAO', 'AGUARDANDO_APROVACAO_COMPRAS'],
    ).count()
    ordens_autorizacao_pendente = OrdemCompra.objects.filter(
        propriedade=propriedade,
        autorizacao_setor_status='PENDENTE',
    ).count()
    
    # Cotações recebidas
    cotacoes_recebidas = CotacaoFornecedor.objects.filter(
        requisicao__propriedade=propriedade,
        status='RECEBIDA'
    ).count()
    
    context = {
        'propriedade': propriedade,
        'fornecedores': fornecedores,
        'total_fornecedores': total_fornecedores,
        'ordens_pendentes': ordens_pendentes,
        'ordens_recentes': ordens_recentes,
        'valor_compras_mes': valor_compras_mes,
        'nfes_pendentes': nfes_pendentes,
        'total_setores': total_setores,
        'setores_inativos': setores_inativos,
        'setores_sem_responsavel': setores_sem_responsavel,
        'convites_abertos': convites_abertos,
        'convites_respondidos': convites_respondidos,
        'convites_expirados': convites_expirados,
        'convites_expirando': convites_expirando,
        'convites_total': convites_total,
        'requisicoes_pendentes': requisicoes_pendentes,
        'ordens_autorizacao_pendente': ordens_autorizacao_pendente,
        'cotacoes_recebidas': cotacoes_recebidas,
        # Informações de orçamento mensal
        'orcamento_mes': orcamento_mes,
        'valor_orcamento_mes': valor_orcamento_mes,
        'valor_comprometido_mes': valor_comprometido_mes,
        'saldo_disponivel_mes': saldo_disponivel_mes,
        'percentual_utilizado_mes': percentual_utilizado_mes,
    }
    
    return render(request, 'gestao_rural/compras_dashboard.html', context)


# ========== REQUISIÇÕES DE COMPRA ==========

@login_required
def requisicoes_compra_lista(request, propriedade_id):
    """Lista de requisições de compra por fazenda"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    status_filtro = request.GET.get('status')

    requisicoes = RequisicaoCompra.objects.filter(
        propriedade=propriedade
    ).select_related(
        'solicitante',
        'setor',
        'equipamento',
        'centro_custo',
        'plano_conta',
    ).order_by('-criado_em')

    if status_filtro:
        requisicoes = requisicoes.filter(status=status_filtro)

    context = {
        'propriedade': propriedade,
        'requisicoes': requisicoes,
        'status_filtro': status_filtro,
        'status_choices': RequisicaoCompra.STATUS_CHOICES,
    }
    return render(request, 'gestao_rural/requisicoes_compra_lista.html', context)


@login_required
def requisicao_compra_nova(request, propriedade_id):
    """Cadastro de nova requisição (funcionário da fazenda)"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    numero_preview = RequisicaoCompra.gerar_proximo_numero(propriedade)
    data_requisicao = timezone.localdate()

    if request.method == 'POST':
        form = RequisicaoCompraForm(request.POST, propriedade=propriedade)
        formset = RequisicaoItemFormSet(request.POST, prefix='itens')

        if form.is_valid() and formset.is_valid():
            requisicao = form.save(commit=False)
            requisicao.propriedade = propriedade
            requisicao.solicitante = request.user

            acao = request.POST.get('acao', 'rascunho')
            # Validar valores permitidos para ação
            acoes_permitidas = ['rascunho', 'enviar', 'aprovar', 'rejeitar', 'cancelar']
            if acao not in acoes_permitidas:
                acao = 'rascunho'  # Valor padrão seguro
            if acao == 'enviar':
                requisicao.status = 'ENVIADA'
                requisicao.enviado_em = timezone.now()
            else:
                requisicao.status = 'RASCUNHO'

            requisicao.save()
            formset.instance = requisicao
            formset.save()

            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='CRIACAO',
                status_anterior=None,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario="Requisição criada e {}.".format(
                    'enviada para aprovação' if requisicao.status == 'ENVIADA' else 'salva como rascunho'
                )
            )

            messages.success(request, 'Requisição registrada com sucesso!')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
        else:
            messages.error(request, 'Verifique os dados informados antes de salvar a requisição.')
    else:
        form = RequisicaoCompraForm(propriedade=propriedade)
        formset = RequisicaoItemFormSet(prefix='itens')

    context = {
        'propriedade': propriedade,
        'form': form,
        'formset': formset,
        'numero_preview': numero_preview,
        'data_requisicao': data_requisicao,
    }
    return render(request, 'gestao_rural/requisicao_compra_form.html', context)


@login_required
def requisicao_compra_detalhes(request, propriedade_id, requisicao_id):
    """Detalhes e linha do tempo da requisição"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    requisicao = get_object_or_404(
        RequisicaoCompra.objects.select_related(
            'solicitante',
            'ordem_compra',
            'setor',
            'equipamento',
            'centro_custo',
            'plano_conta',
        ),
        id=requisicao_id,
        propriedade=propriedade
    )

    itens = requisicao.itens.all()
    cotacoes = list(
        requisicao.cotacoes.select_related('fornecedor').prefetch_related('itens').order_by('-criado_em')
    )
    aprovacoes = requisicao.aprovacoes.select_related('usuario').order_by('-data_decisao')
    eventos = requisicao.eventos_fluxo.select_related('usuario').order_by('-criado_em')

    for cotacao in cotacoes:
        cotacao._mapa_itens = {item.item_requisicao_id: item for item in cotacao.itens.all()}

    total_estimado = sum((item.valor_estimado_total for item in itens), Decimal('0.00'))
    melhor_total_id = None
    melhor_total_valor = None
    for cotacao in cotacoes:
        if melhor_total_valor is None or (cotacao.valor_total and cotacao.valor_total < melhor_total_valor):
            melhor_total_valor = cotacao.valor_total
            melhor_total_id = cotacao.id

    for cotacao in cotacoes:
        cotacao.is_melhor_total = cotacao.id == melhor_total_id
        cotacao.delta_total = cotacao.valor_total - total_estimado if cotacao.valor_total is not None else None

    comparativo_itens = []
    for item in itens:
        linha = {
            'item': item,
            'cotacoes': [],
        }
        melhor_unitario = None
        for cotacao in cotacoes:
            item_cotado = cotacao._mapa_itens.get(item.id)
            valor_unitario = item_cotado.valor_unitario if item_cotado else None
            valor_total_item = item_cotado.valor_total if item_cotado else None

            if valor_unitario is not None:
                if melhor_unitario is None or valor_unitario < melhor_unitario:
                    melhor_unitario = valor_unitario

            delta_unitario = None
            delta_unitario_percentual = None
            if valor_unitario is not None and item.valor_estimado_unitario:
                delta_unitario = valor_unitario - item.valor_estimado_unitario
                if item.valor_estimado_unitario != 0:
                    delta_unitario_percentual = (delta_unitario / item.valor_estimado_unitario) * Decimal('100')

            delta_total_item = None
            if valor_total_item is not None:
                delta_total_item = valor_total_item - item.valor_estimado_total

            linha['cotacoes'].append({
                'cotacao': cotacao,
                'valor_unitario': valor_unitario,
                'valor_total': valor_total_item,
                'delta_unitario': delta_unitario,
                'delta_unitario_percentual': delta_unitario_percentual,
                'delta_total': delta_total_item,
                'melhor_preco': False,
            })

        for info in linha['cotacoes']:
            if info['valor_unitario'] is not None and melhor_unitario is not None:
                info['melhor_preco'] = info['valor_unitario'] == melhor_unitario

        comparativo_itens.append(linha)

    aprovacao_form = AprovacaoRequisicaoCompraForm()
    pode_selecionar_vencedor = requisicao.status in ['EM_COTACAO', 'AGUARDANDO_APROVACAO_COMPRAS'] and len(cotacoes) > 0

    if request.method == 'POST':
        acao = request.POST.get('acao')
        comentario = request.POST.get('comentario', '').strip()
        status_anterior = requisicao.status

        def _checar_permissao(condicao, mensagem):
            if not condicao:
                messages.error(request, mensagem)
                return False
            return True

        if acao == 'enviar_aprovacao' and requisicao.status == 'RASCUNHO':
            if not _checar_permissao(
                request.user == requisicao.solicitante or request.user.is_staff or request.user.is_superuser,
                'Somente o solicitante ou um usuário com privilégios pode enviar para aprovação.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            requisicao.status = 'ENVIADA'
            requisicao.enviado_em = timezone.now()
            requisicao.save(update_fields=['status', 'enviado_em', 'atualizado_em'])
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='ENVIO',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario or 'Requisição enviada para aprovação da gerência.'
            )
            messages.success(request, 'Requisição enviada para aprovação do gerente.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        if acao in ['aprovar_gerencia', 'reprovar_gerencia'] and requisicao.status in ['ENVIADA', 'APROVADA_GERENCIA']:
            if not _checar_permissao(
                request.user.is_staff or request.user.is_superuser,
                'Somente usuários autorizados (gerência) podem registrar esta decisão.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            decisao = 'APROVADO' if acao == 'aprovar_gerencia' else 'REPROVADO'
            novo_status = 'APROVADA_GERENCIA' if acao == 'aprovar_gerencia' else 'REPROVADA_GERENCIA'
            requisicao.status = novo_status
            if novo_status == 'REPROVADA_GERENCIA':
                requisicao.concluido_em = timezone.now()
            requisicao.save(update_fields=['status', 'concluido_em', 'atualizado_em'])

            AprovacaoRequisicaoCompra.objects.create(
                requisicao=requisicao,
                etapa='GERENCIA',
                decisao=decisao,
                usuario=request.user,
                comentario=comentario or ('Aprovada' if decisao == 'APROVADO' else 'Reprovada'),
                data_decisao=timezone.now()
            )
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='APROVACAO_GERENCIA',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario
            )
            messages.success(request, 'Decisão da gerência registrada.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        if acao == 'enviar_cotacao' and requisicao.status == 'APROVADA_GERENCIA':
            if not _checar_permissao(
                request.user.is_staff or request.user.is_superuser,
                'Somente usuários de compras podem encaminhar para cotação.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            requisicao.status = 'EM_COTACAO'
            requisicao.save(update_fields=['status', 'atualizado_em'])
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='COTACAO',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario or 'Iniciando processo de cotação.'
            )
            messages.success(request, 'Requisição encaminhada para o comprador realizar cotações.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        if acao in ['aprovar_compras', 'reprovar_compras'] and requisicao.status in ['EM_COTACAO', 'AGUARDANDO_APROVACAO_COMPRAS', 'APROVADA_COMPRAS']:
            if not _checar_permissao(
                request.user.is_staff or request.user.is_superuser,
                'Somente usuários de compras podem realizar esta aprovação.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            decisao = 'APROVADO' if acao == 'aprovar_compras' else 'REPROVADO'
            novo_status = 'APROVADA_COMPRAS' if acao == 'aprovar_compras' else 'REPROVADA_COMPRAS'
            requisicao.status = novo_status
            if novo_status == 'REPROVADA_COMPRAS':
                requisicao.concluido_em = timezone.now()
            requisicao.save(update_fields=['status', 'concluido_em', 'atualizado_em'])

            AprovacaoRequisicaoCompra.objects.create(
                requisicao=requisicao,
                etapa='RESPONSAVEL_COMPRAS',
                decisao=decisao,
                usuario=request.user,
                comentario=comentario or ('Aprovada pela área de compras' if decisao == 'APROVADO' else 'Reprovada pela área de compras'),
                data_decisao=timezone.now()
            )
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='APROVACAO_COMPRAS',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario
            )
            messages.success(request, 'Decisão da área de compras registrada.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        if acao == 'marcar_ordem_emitida' and requisicao.status in ['APROVADA_COMPRAS', 'ORDEM_EMITIDA']:
            if not _checar_permissao(
                request.user.is_staff or request.user.is_superuser,
                'Somente usuários de compras podem marcar a ordem como emitida.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            requisicao.status = 'ORDEM_EMITIDA'
            requisicao.save(update_fields=['status', 'atualizado_em'])
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='EMISSAO_OC',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario or 'Ordem de compra emitida para o fornecedor.'
            )
            messages.success(request, 'Status atualizado para Ordem de Compra emitida.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        if acao == 'marcar_concluida' and requisicao.status in ['AGUARDANDO_RECEBIMENTO', 'ORDEM_EMITIDA']:
            if not _checar_permissao(
                request.user.is_staff or request.user.is_superuser,
                'Somente responsáveis de compras podem concluir a requisição.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            requisicao.status = 'CONCLUIDA'
            requisicao.concluido_em = timezone.now()
            requisicao.save(update_fields=['status', 'concluido_em', 'atualizado_em'])
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='FINANCEIRO',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario or 'Recebimento validado e encaminhado ao financeiro.'
            )
            messages.success(request, 'Requisição concluída com sucesso.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        if acao == 'cancelar' and requisicao.status not in ['CONCLUIDA', 'CANCELADA']:
            if not _checar_permissao(
                request.user == requisicao.solicitante or request.user.is_staff or request.user.is_superuser,
                'Somente o solicitante ou usuários autorizados podem cancelar a requisição.',
            ):
                return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
            requisicao.status = 'CANCELADA'
            requisicao.motivo_cancelamento = comentario
            requisicao.concluido_em = timezone.now()
            requisicao.save(update_fields=['status', 'motivo_cancelamento', 'concluido_em', 'atualizado_em'])
            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='CANCELAMENTO',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=comentario or 'Requisição cancelada.'
            )
            messages.warning(request, 'Requisição cancelada.')
            return redirect('requisicoes_compra_lista', propriedade_id=propriedade.id)

        if acao == 'selecionar_cotacao' and pode_selecionar_vencedor:
            cotacao_id = request.POST.get('cotacao_id')
            try:
                cotacao_id_int = int(cotacao_id)
            except (TypeError, ValueError):
                messages.error(request, 'Cotação selecionada não encontrada.')
            else:
                cotacao_escolhida = next((c for c in cotacoes if c.id == cotacao_id_int), None)
                if not cotacao_escolhida:
                    messages.error(request, 'Cotação selecionada não encontrada.')
                else:
                    CotacaoFornecedor.objects.filter(requisicao=requisicao).exclude(id=cotacao_escolhida.id).update(
                        status='NAO_SELECIONADA',
                        atualizado_em=timezone.now()
                    )
                    cotacao_escolhida.status = 'SELECIONADA'
                    cotacao_escolhida.save(update_fields=['status', 'atualizado_em'])

                    if requisicao.status == 'EM_COTACAO':
                        requisicao.status = 'AGUARDANDO_APROVACAO_COMPRAS'
                        requisicao.save(update_fields=['status', 'atualizado_em'])

                    EventoFluxoCompra.objects.create(
                        requisicao=requisicao,
                        etapa='APROVACAO_COMPRAS',
                        status_anterior=status_anterior,
                        status_novo=requisicao.status,
                        usuario=request.user,
                        comentario=comentario or f'Cotação selecionada: {cotacao_escolhida.fornecedor.nome}.'
                    )

                    destinatarios = [
                        requisicao.solicitante.email if requisicao.solicitante else None,
                        cotacao_escolhida.fornecedor.email,
                    ]
                    if requisicao.setor and requisicao.setor.responsavel:
                        destinatarios.append(requisicao.setor.responsavel.email)
                    email_propriedade = getattr(requisicao.propriedade, "email", None) if requisicao.propriedade else None
                    if email_propriedade:
                        destinatarios.append(email_propriedade)

                    enviar_notificacao_compra(
                        assunto=f"[Monpec] Cotação selecionada para {requisicao.numero}",
                        mensagem=(
                            f"A cotação do fornecedor {cotacao_escolhida.fornecedor.nome} foi selecionada como vencedora "
                            f"para a requisição {requisicao.numero} ({requisicao.titulo}).\n\n"
                            f"Valor total negociado: {cotacao_escolhida.valor_total}\n"
                            f"Prazo de entrega: {cotacao_escolhida.prazo_entrega_estimado or 'Não informado.'}\n"
                            f"Condições de pagamento: {cotacao_escolhida.condicoes_pagamento or 'Não informado.'}\n\n"
                            "Acesse o módulo de compras para aprovar a requisição ou gerar a ordem correspondente."
                        ),
                        destinatarios=destinatarios,
                    )
                    messages.success(request, 'Cotação selecionada como vencedora para aprovação final.')
                    return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)

        messages.error(request, 'Não foi possível processar a ação solicitada.')

    context = {
        'propriedade': propriedade,
        'requisicao': requisicao,
        'itens': itens,
        'cotacoes': cotacoes,
        'comparativo_itens': comparativo_itens,
        'total_estimado': total_estimado,
        'melhor_total_id': melhor_total_id,
        'aprovacoes': aprovacoes,
        'eventos': eventos,
        'aprovacao_form': aprovacao_form,
        'pode_selecionar_vencedor': pode_selecionar_vencedor,
    }
    return render(request, 'gestao_rural/requisicao_compra_detalhes.html', context)


@login_required
def setores_compra_lista(request, propriedade_id):
    """Listagem de setores responsáveis por autorizações de compra"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    mostrar_inativos = request.GET.get('mostrar') == 'inativos'

    setores = SetorPropriedade.objects.filter(
        propriedade=propriedade
    ).select_related('responsavel')
    if not mostrar_inativos:
        setores = setores.filter(ativo=True)

    setores = setores.annotate(
        total_requisicoes=Count('requisicoes', distinct=True)
    ).order_by('nome')

    context = {
        'propriedade': propriedade,
        'setores': setores,
        'mostrar_inativos': mostrar_inativos,
    }
    return render(request, 'gestao_rural/setores_compra_lista.html', context)


@login_required
def setor_compra_novo(request, propriedade_id):
    """Cadastro de novo setor de compras"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)

    if request.method == 'POST':
        form = SetorPropriedadeForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            setor = form.save(commit=False)
            setor.propriedade = propriedade
            setor.save()
            messages.success(request, 'Setor cadastrado com sucesso.')
            return redirect('setores_compra_lista', propriedade_id=propriedade.id)
        messages.error(request, 'Não foi possível salvar o setor. Verifique os dados informados.')
    else:
        form = SetorPropriedadeForm(propriedade=propriedade)

    context = {
        'propriedade': propriedade,
        'form': form,
        'modo': 'novo',
    }
    return render(request, 'gestao_rural/setor_compra_form.html', context)


@login_required
def setor_compra_editar(request, propriedade_id, setor_id):
    """Edição de setor de compras"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    setor = get_object_or_404(SetorPropriedade, id=setor_id, propriedade=propriedade)

    if request.method == 'POST':
        form = SetorPropriedadeForm(request.POST, instance=setor, propriedade=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do setor atualizados com sucesso.')
            return redirect('setores_compra_lista', propriedade_id=propriedade.id)
        messages.error(request, 'Não foi possível atualizar o setor. Verifique os dados informados.')
    else:
        form = SetorPropriedadeForm(instance=setor, propriedade=propriedade)

    context = {
        'propriedade': propriedade,
        'form': form,
        'setor': setor,
        'modo': 'editar',
    }
    return render(request, 'gestao_rural/setor_compra_form.html', context)


@login_required
def setor_compra_alterar_status(request, propriedade_id, setor_id):
    """Ativa ou inativa um setor"""
    if request.method != 'POST':
        messages.error(request, 'Ação inválida.')
        return redirect('setores_compra_lista', propriedade_id=propriedade_id)

    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    setor = get_object_or_404(SetorPropriedade, id=setor_id, propriedade=propriedade)
    setor.ativo = not setor.ativo
    setor.save(update_fields=['ativo'])

    status_label = 'ativado' if setor.ativo else 'inativado'
    messages.success(request, f'Setor {status_label} com sucesso.')
    return redirect('setores_compra_lista', propriedade_id=propriedade.id)


@login_required
def convites_cotacao_lista(request, propriedade_id):
    """Lista convites de cotação enviados aos fornecedores."""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    status_filtro = request.GET.get('status')

    convites = ConviteCotacaoFornecedor.objects.filter(
        requisicao__propriedade=propriedade
    ).select_related('fornecedor', 'requisicao', 'enviado_por').order_by('-criado_em')

    if status_filtro:
        convites = convites.filter(status=status_filtro)

    context = {
        'propriedade': propriedade,
        'convites': convites,
        'status_filtro': status_filtro,
        'status_choices': ConviteCotacaoFornecedor.STATUS_CHOICES,
    }
    return render(request, 'gestao_rural/convites_cotacao_lista.html', context)


@login_required
def convite_cotacao_novo(request, propriedade_id):
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    requisicao_id = request.GET.get('requisicao') or request.POST.get('requisicao_id')

    if not requisicao_id:
        messages.error(request, 'Selecione uma requisição para gerar convites.')
        return redirect('requisicoes_compra_lista', propriedade_id=propriedade.id)

    requisicao = get_object_or_404(
        RequisicaoCompra.objects.select_related('propriedade'),
        id=requisicao_id,
        propriedade=propriedade
    )

    if request.method == 'POST':
        form = ConviteCotacaoFornecedorForm(request.POST, requisicao=requisicao)
        if form.is_valid():
            convite = form.save(commit=False)
            convite.requisicao = requisicao
            if not convite.data_expiracao:
                convite.data_expiracao = timezone.now() + timedelta(days=7)
            convite.save()
            convite.marcar_enviado(request.user)
            messages.success(
                request,
                f'Convite gerado para o fornecedor {convite.fornecedor.nome}. Compartilhe o link com o fornecedor.'
            )
            return redirect('convites_cotacao_lista', propriedade_id=propriedade.id)
        messages.error(request, 'Não foi possível gerar o convite. Verifique os dados informados.')
    else:
        initial = {}
        fornecedor_param = request.GET.get('fornecedor')
        if fornecedor_param:
            initial['fornecedor'] = fornecedor_param
            fornecedor_ref = Fornecedor.objects.filter(id=fornecedor_param).first()
            if fornecedor_ref and fornecedor_ref.email:
                initial['email_destinatario'] = fornecedor_ref.email
        form = ConviteCotacaoFornecedorForm(initial=initial, requisicao=requisicao)

    context = {
        'propriedade': propriedade,
        'requisicao': requisicao,
        'form': form,
    }
    return render(request, 'gestao_rural/convite_cotacao_form.html', context)


@login_required
def convite_cotacao_cancelar(request, propriedade_id, convite_id):
    if request.method != 'POST':
        messages.error(request, 'Ação inválida.')
        return redirect('convites_cotacao_lista', propriedade_id=propriedade_id)

    convite = get_object_or_404(
        ConviteCotacaoFornecedor.objects.select_related('requisicao__propriedade'),
        id=convite_id,
        requisicao__propriedade__id=propriedade_id
    )
    convite.cancelar()
    messages.success(request, 'Convite cancelado com sucesso.')
    return redirect('convites_cotacao_lista', propriedade_id=propriedade_id)


def cotacao_fornecedor_responder_token(request, token):
    """Portal público para fornecedores responderem uma cotação via link seguro."""
    convite = get_object_or_404(
        ConviteCotacaoFornecedor.objects.select_related('requisicao__propriedade', 'fornecedor'),
        token=token
    )
    requisicao = convite.requisicao
    itens_requisicao = list(requisicao.itens.all())

    ItemRespostaFormSet = formset_factory(RespostaItemCotacaoFornecedorForm, extra=0)

    if request.method == 'POST' and convite.pode_responder():
        cabecalho_form = RespostaCotacaoFornecedorCabecalhoForm(request.POST, request.FILES)
        formset = ItemRespostaFormSet(request.POST, prefix='itens')

        if cabecalho_form.is_valid() and formset.is_valid():
            cotacao, _created = CotacaoFornecedor.objects.get_or_create(
                requisicao=requisicao,
                fornecedor=convite.fornecedor,
                defaults={'status': 'RECEBIDA'}
            )

            cabecalho = cabecalho_form.cleaned_data
            cotacao.prazo_entrega_estimado = cabecalho.get('prazo_entrega_estimado')
            cotacao.condicoes_pagamento = cabecalho.get('condicoes_pagamento')
            cotacao.valor_frete = cabecalho.get('valor_frete') or Decimal('0.00')
            cotacao.observacoes = cabecalho.get('observacoes')
            if cabecalho.get('anexo_proposta'):
                cotacao.anexo_proposta = cabecalho['anexo_proposta']
            cotacao.status = 'RECEBIDA'
            cotacao.valor_total = Decimal('0.00')
            cotacao.save()
            cotacao.itens.all().delete()

            for item_form, item_req in zip(formset.forms, itens_requisicao):
                valor_unitario = item_form.cleaned_data.get('valor_unitario')
                if valor_unitario is None:
                    continue
                valor_total = valor_unitario * item_req.quantidade
                ItemCotacaoFornecedor.objects.create(
                    cotacao=cotacao,
                    item_requisicao=item_req,
                    descricao=item_req.descricao,
                    unidade_medida=item_req.unidade_medida,
                    quantidade=item_req.quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total
                )
                cotacao.valor_total += valor_total

            cotacao.valor_total += cotacao.valor_frete
            cotacao.save(update_fields=['valor_total', 'prazo_entrega_estimado', 'condicoes_pagamento', 'valor_frete', 'observacoes', 'status', 'anexo_proposta'])

            convite.marcar_respondido(cabecalho.get('observacoes', ''))

            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='COTACAO',
                status_anterior=requisicao.status,
                status_novo=requisicao.status,
                usuario=None,
                comentario=f"Cotação recebida via portal do fornecedor {convite.fornecedor.nome}."
            )

            destinatarios = [
                requisicao.solicitante.email if requisicao.solicitante else None,
            ]
            if requisicao.setor and requisicao.setor.responsavel:
                destinatarios.append(requisicao.setor.responsavel.email)
            email_propriedade = getattr(requisicao.propriedade, "email", None) if requisicao.propriedade else None
            if email_propriedade:
                destinatarios.append(email_propriedade)

            enviar_notificacao_compra(
                assunto=f"[Monpec] Cotação respondida por {convite.fornecedor.nome}",
                mensagem=(
                    f"A requisição {requisicao.numero} recebeu uma cotação do fornecedor "
                    f"{convite.fornecedor.nome}.\n\n"
                    f"Prazo informado: {cotacao.prazo_entrega_estimado or 'Não informado.'}\n"
                    f"Valor total: {cotacao.valor_total}\n"
                    f"Condições de pagamento: {cotacao.condicoes_pagamento or 'Não informado.'}\n\n"
                    "Acesse o módulo de compras para analisar os valores e avançar com o processo."
                ),
                destinatarios=destinatarios,
            )

            return render(
                request,
                'gestao_rural/cotacao_fornecedor_token.html',
                {
                    'convite': convite,
                    'requisicao': requisicao,
                    'fornecedor': convite.fornecedor,
                    'sucesso': True,
                }
            )
    else:
        cabecalho_form = RespostaCotacaoFornecedorCabecalhoForm()
        formset = ItemRespostaFormSet(
            prefix='itens',
            initial=[{'valor_unitario': None} for _ in itens_requisicao]
        )

    if not convite.pode_responder():
        return render(
            request,
            'gestao_rural/cotacao_fornecedor_token.html',
            {
                'convite': convite,
                'requisicao': requisicao,
                'fornecedor': convite.fornecedor,
                'invalido': True,
            }
        )

    itens_com_form = list(zip(itens_requisicao, formset.forms))

    context = {
        'convite': convite,
        'requisicao': requisicao,
        'fornecedor': convite.fornecedor,
        'cabecalho_form': cabecalho_form,
        'formset': formset,
        'itens_com_form': itens_com_form,
    }
    return render(request, 'gestao_rural/cotacao_fornecedor_token.html', context)


@login_required
def cotacao_fornecedor_nova(request, propriedade_id, requisicao_id):
    """Registro de cotação para uma requisição aprovada"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    requisicao = get_object_or_404(
        RequisicaoCompra.objects.select_related('propriedade'),
        id=requisicao_id,
        propriedade=propriedade
    )

    # Ajustar quantidade de formulários conforme quantidade de itens da requisição
    quantidade_itens = max(1, requisicao.itens.count())
    CotacaoFormSetDynamic = inlineformset_factory(
        CotacaoFornecedor,
        ItemCotacaoFornecedor,
        form=ItemCotacaoFornecedorForm,
        extra=quantidade_itens,
        can_delete=False
    )

    if request.method == 'POST':
        form = CotacaoFornecedorForm(request.POST, request.FILES)
        formset = CotacaoFormSetDynamic(request.POST, prefix='itens')

        if form.is_valid() and formset.is_valid():
            cotacao = form.save(commit=False)
            cotacao.requisicao = requisicao
            cotacao.comprador = request.user
            cotacao.save()
            formset.instance = cotacao
            formset.save()

            status_anterior = requisicao.status
            if status_anterior == 'EM_COTACAO':
                requisicao.status = 'AGUARDANDO_APROVACAO_COMPRAS'
                requisicao.save(update_fields=['status', 'atualizado_em'])
            else:
                requisicao.save(update_fields=['atualizado_em'])

            EventoFluxoCompra.objects.create(
                requisicao=requisicao,
                etapa='COTACAO',
                status_anterior=status_anterior,
                status_novo=requisicao.status,
                usuario=request.user,
                comentario=f"Cotação registrada para o fornecedor {cotacao.fornecedor.nome}"
            )

            messages.success(request, 'Cotação registrada com sucesso.')
            return redirect('requisicao_compra_detalhes', propriedade_id=propriedade.id, requisicao_id=requisicao.id)
        else:
            messages.error(request, 'Revise os dados da cotação.')
    else:
        form = CotacaoFornecedorForm()
        formset = CotacaoFormSetDynamic(prefix='itens')

        itens_requisicao = list(requisicao.itens.all())
        for idx, form_item in enumerate(formset.forms):
            if idx < len(itens_requisicao):
                item = itens_requisicao[idx]
                form_item.initial.update({
                    'item_requisicao': item,
                    'descricao': item.descricao,
                    'unidade_medida': item.unidade_medida,
                    'quantidade': item.quantidade,
                    'valor_unitario': item.valor_estimado_unitario,
                })

    context = {
        'propriedade': propriedade,
        'requisicao': requisicao,
        'form': form,
        'formset': formset,
    }
    return render(request, 'gestao_rural/cotacao_fornecedor_form.html', context)


@login_required
def recebimento_compra_novo(request, propriedade_id, ordem_id):
    """Registro do recebimento físico vinculado à OC"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    ordem = get_object_or_404(
        OrdemCompra.objects.select_related('propriedade', 'fornecedor'),
        id=ordem_id,
        propriedade=propriedade
    )

    requisicao_origem = ordem.requisicoes_origem.first()

    quantidade_itens = max(1, ordem.itens.count())
    RecebimentoFormSetDynamic = inlineformset_factory(
        RecebimentoCompra,
        ItemRecebimentoCompra,
        form=ItemRecebimentoCompraForm,
        extra=quantidade_itens,
        can_delete=False
    )

    if request.method == 'POST':
        form = RecebimentoCompraForm(request.POST, request.FILES)
        formset = RecebimentoFormSetDynamic(request.POST, prefix='itens')

        if form.is_valid() and formset.is_valid():
            recebimento = form.save(commit=False)
            recebimento.ordem_compra = ordem
            recebimento.responsavel = request.user
            if recebimento.status == 'RECEBIDO' and not recebimento.data_recebimento:
                recebimento.data_recebimento = date.today()
            recebimento.save()
            formset.instance = recebimento
            formset.save()

            if recebimento.status == 'RECEBIDO':
                ordem.status = 'RECEBIDA'
            elif recebimento.status == 'DIVERGENCIA':
                ordem.status = 'PARCIAL'
            ordem.save(update_fields=['status'])

            if requisicao_origem:
                status_anterior = requisicao_origem.status
                if recebimento.status == 'RECEBIDO':
                    requisicao_origem.status = 'CONCLUIDA'
                    requisicao_origem.concluido_em = timezone.now()
                else:
                    requisicao_origem.status = 'AGUARDANDO_RECEBIMENTO'
                requisicao_origem.save(update_fields=['status', 'concluido_em', 'atualizado_em'])

                EventoFluxoCompra.objects.create(
                    requisicao=requisicao_origem,
                    etapa='RECEBIMENTO',
                    status_anterior=status_anterior,
                    status_novo=requisicao_origem.status,
                    usuario=request.user,
                    comentario=f"Recebimento registrado para a OC {ordem.numero_ordem}."
                )

            messages.success(request, 'Recebimento registrado com sucesso.')
            return redirect('ordem_compra_detalhes', propriedade_id=propriedade.id, ordem_id=ordem.id)
        else:
            messages.error(request, 'Revise os dados do recebimento.')
    else:
        form = RecebimentoCompraForm(initial={
            'status': 'RECEBIDO' if ordem.status == 'RECEBIDA' else 'PENDENTE',
            'data_prevista': ordem.data_entrega_prevista
        })
        formset = RecebimentoFormSetDynamic(prefix='itens')

        itens_ordem = list(ordem.itens.all())
        for idx, form_item in enumerate(formset.forms):
            if idx < len(itens_ordem):
                item = itens_ordem[idx]
                form_item.initial.update({
                    'item_requisicao': item,
                    'descricao': item.descricao,
                    'unidade_medida': item.unidade_medida,
                    'quantidade': item.quantidade,
                    'valor_unitario': item.valor_estimado_unitario,
                })

    context = {
        'propriedade': propriedade,
        'ordem': ordem,
        'itens': itens_ordem,
        'form': form,
        'formset': formset,
    }
    return render(request, 'gestao_rural/recebimento_compra_form.html', context)


# ========== FORNECEDORES ==========

@login_required
def fornecedores_lista(request, propriedade_id):
    """Lista de fornecedores"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    fornecedores = Fornecedor.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True)
    ).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'fornecedores': fornecedores,
    }
    
    return render(request, 'gestao_rural/fornecedores_lista.html', context)


@login_required
@bloquear_demo_cadastro
def fornecedor_novo(request, propriedade_id):
    """Cadastrar novo fornecedor"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        fornecedor = Fornecedor()
        fornecedor.propriedade = propriedade
        fornecedor.nome = request.POST.get('nome')
        fornecedor.nome_fantasia = request.POST.get('nome_fantasia', '')
        fornecedor.cpf_cnpj = request.POST.get('cpf_cnpj')
        fornecedor.tipo = request.POST.get('tipo')
        fornecedor.telefone = request.POST.get('telefone', '')
        fornecedor.email = request.POST.get('email', '')
        fornecedor.endereco = request.POST.get('endereco', '')
        fornecedor.cidade = request.POST.get('cidade', '')
        fornecedor.estado = request.POST.get('estado', '')
        fornecedor.observacoes = request.POST.get('observacoes', '')
        
        try:
            fornecedor.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('fornecedores_lista', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar fornecedor: {str(e)}')
    
    return render(request, 'gestao_rural/fornecedor_form.html', {
        'propriedade': propriedade,
        'form_type': 'novo'
    })


# ========== ORDENS DE COMPRA ==========

@login_required
def ordens_compra_lista(request, propriedade_id):
    """Lista de ordens de compra"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    ordens = OrdemCompra.objects.filter(propriedade=propriedade).select_related(
        'fornecedor',
        'setor',
        'plano_conta',
        'centro_custo',
        'requisicao_origem',
        'autorizacao_setor_usuario'
    ).order_by('-data_emissao')
    
    context = {
        'propriedade': propriedade,
        'ordens': ordens,
    }
    
    return render(request, 'gestao_rural/ordens_compra_lista.html', context)


@login_required
def orcamentos_compra_lista(request, propriedade_id):
    """Configuração de orçamento mensal por propriedade e setor."""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    ano_atual = timezone.now().year
    try:
        ano_filtro = int(request.GET.get('ano', ano_atual))
    except ValueError:
        ano_filtro = ano_atual

    orcamentos_qs = OrcamentoCompraMensal.objects.filter(
        propriedade=propriedade,
        ano=ano_filtro,
    ).select_related('setor').order_by('-mes', 'setor__nome')

    orcamentos_dados = []
    for orcamento in orcamentos_qs:
        utilizado = orcamento.valor_utilizado()
        saldo = orcamento.total_limite - utilizado
        orcamentos_dados.append({
            'obj': orcamento,
            'utilizado': utilizado,
            'saldo': saldo,
            'percentual': orcamento.percentual_utilizado(),
            'ajustes': orcamento.ajustes.all()[:5],
        })

    form = OrcamentoCompraMensalForm(
        propriedade=propriedade,
        initial={'ano': ano_filtro, 'mes': timezone.now().month},
    )
    ajuste_form = AjusteOrcamentoCompraForm()

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'definir_orcamento':
            form = OrcamentoCompraMensalForm(request.POST, propriedade=propriedade)
            if form.is_valid():
                setor = form.cleaned_data.get('setor')
                mes = form.cleaned_data['mes']
                ano = form.cleaned_data['ano']
                valor_limite = form.cleaned_data['valor_limite']
                observacoes = form.cleaned_data.get('observacoes')

                orcamento, criado = OrcamentoCompraMensal.objects.get_or_create(
                    propriedade=propriedade,
                    setor=setor,
                    ano=ano,
                    mes=mes,
                )
                orcamento.valor_limite = valor_limite
                orcamento.observacoes = observacoes
                if criado and not orcamento.criado_por_id:
                    orcamento.criado_por = request.user
                else:
                    orcamento.atualizado_por = request.user
                orcamento.save()

                messages.success(request, 'Orçamento mensal salvo com sucesso.')
                return redirect('orcamentos_compra_lista', propriedade_id=propriedade.id)
            else:
                messages.error(request, 'Não foi possível salvar o orçamento. Verifique os dados informados.')
        elif acao == 'ajuste_orcamento':
            ajuste_form = AjusteOrcamentoCompraForm(request.POST)
            if ajuste_form.is_valid():
                try:
                    orcamento_id = int(request.POST.get('orcamento_id'))
                except (TypeError, ValueError):
                    orcamento_id = None
                orcamento = get_object_or_404(
                    OrcamentoCompraMensal,
                    id=orcamento_id,
                    propriedade=propriedade,
                )
                valor = ajuste_form.cleaned_data['valor']
                justificativa = ajuste_form.cleaned_data['justificativa']
                AjusteOrcamentoCompra.objects.create(
                    orcamento=orcamento,
                    valor=valor,
                    justificativa=justificativa,
                    criado_por=request.user,
                )
                orcamento.limite_extra = (orcamento.limite_extra or Decimal('0.00')) + valor
                orcamento.atualizado_por = request.user
                orcamento.save(update_fields=['limite_extra', 'atualizado_por', 'atualizado_em'])

                messages.success(request, 'Limite extra emergencial adicionado com sucesso.')
                return redirect('orcamentos_compra_lista', propriedade_id=propriedade.id)
            else:
                messages.error(request, 'Informe um valor e uma justificativa válidos para o ajuste.')
        else:
            messages.error(request, 'Ação inválida para orçamento de compras.')

    context = {
        'propriedade': propriedade,
        'ano_filtro': ano_filtro,
        'orcamentos': orcamentos_dados,
        'orcamentos_objs': [item['obj'] for item in orcamentos_dados],
        'form': form,
        'ajuste_form': ajuste_form,
        'anos_disponiveis': range(ano_atual - 2, ano_atual + 3),
    }
    return render(request, 'gestao_rural/orcamentos_compra_lista.html', context)


@login_required
def ordem_compra_nova(request, propriedade_id):
    """Criar nova ordem de compra"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    requisicao_id = request.GET.get('requisicao') or request.POST.get('requisicao_id')
    requisicao = None
    if requisicao_id:
        try:
            requisicao = RequisicaoCompra.objects.get(id=requisicao_id, propriedade=propriedade)
        except RequisicaoCompra.DoesNotExist:
            requisicao = None
            messages.warning(request, 'Requisição informada não foi encontrada para esta propriedade.')

    setor_contexto = requisicao.setor if requisicao else None
    data_contexto = timezone.localdate()

    if request.method == 'POST':
        form = OrdemCompraForm(request.POST, propriedade=propriedade, requisicao=requisicao)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.propriedade = propriedade
            ordem.criado_por = request.user
            if requisicao:
                ordem.requisicao_origem = requisicao
                if requisicao.setor and not ordem.setor:
                    ordem.setor = requisicao.setor
                if requisicao.plano_conta and not ordem.plano_conta:
                    ordem.plano_conta = requisicao.plano_conta
                if requisicao.centro_custo and not ordem.centro_custo:
                    ordem.centro_custo = requisicao.centro_custo
                if requisicao.centro_custo_descricao and not ordem.centro_custo_descricao:
                    ordem.centro_custo_descricao = requisicao.centro_custo_descricao

            valor_previsto = (ordem.valor_produtos or Decimal('0.00')) + (ordem.valor_frete or Decimal('0.00'))
            if valor_previsto <= Decimal('0.00') and requisicao:
                valor_previsto = requisicao.total_estimado

            setor_validacao = ordem.setor or (requisicao.setor if requisicao else None)
            data_emissao = form.cleaned_data.get('data_emissao') or timezone.localdate()
            
            # Verificar se há autorização de excedente informada no formulário
            autorizacao_id = request.POST.get('autorizacao_excedente_id')
            autorizacao_excedente = None
            if autorizacao_id:
                try:
                    from .models_compras_financeiro import AutorizacaoExcedenteOrcamento
                    autorizacao_excedente = AutorizacaoExcedenteOrcamento.objects.get(
                        id=autorizacao_id,
                        status='APROVADA'
                    )
                except:
                    autorizacao_excedente = None
            
            validacao = validar_orcamento_para_valor(
                propriedade,
                setor_validacao,
                data_emissao,
                valor_previsto,
                verificar_autorizacao=True,
            )

            if validacao:
                orcamento = validacao['orcamento']
                saldo_disponivel = validacao['saldo_disponivel']
                valor_excedente = validacao.get('valor_excedente', Decimal('0.00'))
                autorizacao = validacao.get('autorizacao') or autorizacao_excedente
                
                # Se não tem autorização, bloquear
                if not autorizacao:
                    if saldo_disponivel < Decimal('0.00'):
                        saldo_disponivel = Decimal('0.00')
                    mensagem = (
                        f"Orçamento mensal excedido para {orcamento.get_mes_display()}/{orcamento.ano}. "
                        f"Disponível: R$ {saldo_disponivel:.2f}. "
                        f"Excedente: R$ {valor_excedente:.2f}. "
                        f"É necessário solicitar autorização da gerência para prosseguir."
                    )
                    form.add_error(None, mensagem)
                    setor_contexto = setor_validacao
                    data_contexto = data_emissao
                else:
                    # Tem autorização, pode prosseguir
                    ordem.save()
                    # Vincular autorização à ordem se ainda não estiver vinculada
                    if autorizacao and not autorizacao.ordem_compra:
                        autorizacao.ordem_compra = ordem
                        autorizacao.save(update_fields=['ordem_compra'])
                    # Gerar conta a pagar para a ordem
                    gerar_conta_pagar_para_ordem(ordem)
                    
                    if requisicao:
                        requisicao.ordem_compra = ordem
                        status_anterior = requisicao.status
                        requisicao.status = 'ORDEM_EMITIDA'
                        requisicao.save(update_fields=['ordem_compra', 'status', 'atualizado_em'])
                        EventoFluxoCompra.objects.create(
                            requisicao=requisicao,
                            etapa='EMISSAO_OC',
                            status_anterior=status_anterior,
                            status_novo=requisicao.status,
                            usuario=request.user,
                            comentario=f"Ordem {ordem.numero_ordem} emitida a partir da requisição."
                        )
                    messages.success(request, 'Ordem de compra criada com sucesso!')
                    return redirect('ordem_compra_detalhes', propriedade_id=propriedade.id, ordem_id=ordem.id)
            else:
                ordem.save()
                # Gerar conta a pagar para a ordem
                gerar_conta_pagar_para_ordem(ordem)

                if requisicao:
                    requisicao.ordem_compra = ordem
                    status_anterior = requisicao.status
                    requisicao.status = 'ORDEM_EMITIDA'
                    requisicao.save(update_fields=['ordem_compra', 'status', 'atualizado_em'])
                    EventoFluxoCompra.objects.create(
                        requisicao=requisicao,
                        etapa='EMISSAO_OC',
                        status_anterior=status_anterior,
                        status_novo=requisicao.status,
                        usuario=request.user,
                        comentario=f"Ordem {ordem.numero_ordem} emitida a partir da requisição."
                    )

                messages.success(request, 'Ordem de compra criada com sucesso!')
                return redirect('ordem_compra_detalhes', propriedade_id=propriedade.id, ordem_id=ordem.id)
        else:
            setor_id = request.POST.get('setor')
            if setor_id:
                try:
                    setor_contexto = SetorPropriedade.objects.get(id=setor_id, propriedade=propriedade)
                except (SetorPropriedade.DoesNotExist, ValueError):
                    setor_contexto = requisicao.setor if requisicao else None
            data_str = request.POST.get('data_emissao')
            if data_str:
                try:
                    data_contexto = datetime.strptime(data_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    data_contexto = timezone.localdate()
    else:
        form = OrdemCompraForm(propriedade=propriedade, requisicao=requisicao)
        data_inicial = form.initial.get('data_emissao')
        if isinstance(data_inicial, str):
            try:
                data_contexto = datetime.strptime(data_inicial, '%Y-%m-%d').date()
            except ValueError:
                data_contexto = timezone.localdate()
        elif data_inicial:
            data_contexto = data_inicial

    if not setor_contexto and requisicao:
        setor_contexto = requisicao.setor

    orcamento_info = montar_contexto_orcamento(propriedade, setor_contexto, data_contexto)

    return render(request, 'gestao_rural/ordem_compra_form.html', {
        'propriedade': propriedade,
        'requisicao': requisicao,
        'form': form,
        'orcamento_info': orcamento_info,
    })


@login_required
def ordem_compra_detalhes(request, propriedade_id, ordem_id):
    """Detalhes completos da ordem de compra"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    ordem = get_object_or_404(
        OrdemCompra.objects.select_related(
            'fornecedor',
            'nota_fiscal',
            'criado_por',
            'aprovado_por',
            'setor',
            'plano_conta',
            'centro_custo',
            'requisicao_origem',
            'autorizacao_setor_usuario',
        ),
        id=ordem_id,
        propriedade=propriedade
    )
    itens = ordem.itens.all()
    recebimentos = ordem.recebimentos.select_related('responsavel').order_by('-criado_em')
    requisicao = ordem.requisicao_origem or ordem.requisicoes_origem.select_related('solicitante').first()
    responsavel_setor = ordem.setor.responsavel if ordem.setor and hasattr(ordem.setor, "responsavel") else None
    pode_autorizar = (
        ordem.setor is not None
        and (
            request.user == responsavel_setor
            or request.user.is_superuser
            or request.user.is_staff
        )
    )
    autorizacao_form = OrdemCompraAutorizacaoForm()

    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'autorizacao_setor':
            if not pode_autorizar:
                messages.error(request, 'Você não possui permissão para autorizar esta ordem.')
            else:
                autorizacao_form = OrdemCompraAutorizacaoForm(request.POST)
                if autorizacao_form.is_valid():
                    decisao = autorizacao_form.cleaned_data['decisao']
                    observacoes = autorizacao_form.cleaned_data['observacoes']
                    ordem.autorizacao_setor_status = decisao
                    ordem.autorizacao_setor_usuario = request.user
                    ordem.autorizacao_setor_data = timezone.now()
                    ordem.autorizacao_setor_observacoes = observacoes
                    ordem.save(update_fields=[
                        'autorizacao_setor_status',
                        'autorizacao_setor_usuario',
                        'autorizacao_setor_data',
                        'autorizacao_setor_observacoes',
                        'atualizado_em'
                    ])

                    if requisicao:
                        EventoFluxoCompra.objects.create(
                            requisicao=requisicao,
                            etapa='AUTORIZACAO_SETOR',
                            status_anterior=requisicao.status,
                            status_novo=requisicao.status,
                            usuario=request.user,
                            comentario=observacoes or f'Autorização do setor registrada como {ordem.get_autorizacao_setor_status_display()}.'
                        )

                    conta_pagar = None
                    if decisao == 'AUTORIZADA':
                        conta_pagar, conta_criada = gerar_conta_pagar_para_ordem(ordem)
                        if requisicao:
                            EventoFluxoCompra.objects.create(
                                requisicao=requisicao,
                                etapa='FINANCEIRO',
                                status_anterior=requisicao.status,
                                status_novo=requisicao.status,
                                usuario=request.user,
                                comentario='Conta a pagar gerada a partir da autorização da OC.'
                            )
                        mensagem = 'Ordem autorizada pelo responsável do setor.'
                        if conta_criada:
                            mensagem += ' Conta a pagar criada automaticamente.'
                        else:
                            mensagem += ' Conta a pagar atualizada.'
                        destinatarios = [
                            ordem.criado_por.email if ordem.criado_por else None,
                            getattr(ordem.fornecedor, "email", None),
                        ]
                        if ordem.setor and ordem.setor.responsavel:
                            destinatarios.append(ordem.setor.responsavel.email)
                        email_propriedade = getattr(ordem.propriedade, "email", None) if ordem.propriedade else None
                        if email_propriedade:
                            destinatarios.append(email_propriedade)

                        enviar_notificacao_compra(
                            assunto=f"[Monpec] Ordem {ordem.numero_ordem} autorizada pelo setor",
                            mensagem=(
                                f"A ordem de compra {ordem.numero_ordem} foi autorizada pelo setor "
                                f"{ordem.setor.nome if ordem.setor else 'responsável'}.\n\n"
                                f"Valor total: {ordem.valor_total}\n"
                                f"Condições de pagamento: {ordem.condicoes_pagamento or 'Não informado.'}\n\n"
                                "Acesse o módulo de compras para prosseguir com o envio ao fornecedor ou demais etapas."
                            ),
                            destinatarios=destinatarios,
                        )
                        messages.success(request, mensagem)
                    else:
                        messages.warning(request, 'Ordem marcada como negada pelo setor. Ajustes podem ser necessários.')
                        destinatarios = [
                            ordem.criado_por.email if ordem.criado_por else None,
                        ]
                        if ordem.setor and ordem.setor.responsavel:
                            destinatarios.append(ordem.setor.responsavel.email)

                        enviar_notificacao_compra(
                            assunto=f"[Monpec] Ordem {ordem.numero_ordem} negada pelo setor",
                            mensagem=(
                                f"A ordem de compra {ordem.numero_ordem} foi marcada como NEGADA pelo setor "
                                f"{ordem.setor.nome if ordem.setor else 'responsável'}.\n\n"
                                "Revise as observações adicionadas e realize os ajustes necessários antes de reenviar."
                            ),
                            destinatarios=destinatarios,
                        )
                    return redirect('ordem_compra_detalhes', propriedade_id=propriedade.id, ordem_id=ordem.id)
                else:
                    messages.error(request, 'Não foi possível registrar a decisão. Verifique os dados informados.')

    conta_pagar_vinculada = ordem.contas_pagar.select_related('fornecedor').order_by('data_vencimento').first()
    for item in itens:
        item.historico = obter_historico_preco_item(ordem, item)

    context = {
        'propriedade': propriedade,
        'ordem': ordem,
        'itens': itens,
        'recebimentos': recebimentos,
        'requisicao': requisicao,
        'autorizacao_form': autorizacao_form,
        'pode_autorizar_setor': pode_autorizar,
        'conta_pagar': conta_pagar_vinculada,
    }
    return render(request, 'gestao_rural/ordem_compra_detalhes.html', context)


# ========== NOTAS FISCAIS ==========

@login_required
def notas_fiscais_lista(request, propriedade_id):
    """Lista de notas fiscais"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    notas = NotaFiscal.objects.filter(propriedade=propriedade).select_related(
        'fornecedor', 'cliente'
    ).order_by('-data_emissao')
    
    context = {
        'propriedade': propriedade,
        'notas': notas,
    }
    
    return render(request, 'gestao_rural/notas_fiscais_lista.html', context)


@login_required
def nota_fiscal_upload(request, propriedade_id):
    """Upload de Nota Fiscal (XML)"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    fornecedores = Fornecedor.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True),
        ativo=True
    ).order_by('nome')
    
    if request.method == 'POST' and request.FILES.get('arquivo_xml'):
        try:
            arquivo_xml = request.FILES['arquivo_xml']
            
            # Parse do XML
            tree = ET.parse(arquivo_xml)
            root = tree.getroot()
            
            # Namespace NFe
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Extrair dados da NF-e
            inf_nfe = root.find('.//nfe:infNFe', ns)
            if inf_nfe is None:
                messages.error(request, 'Arquivo XML inválido ou não é uma NF-e')
                return render(request, 'gestao_rural/nota_fiscal_upload.html', {
                    'propriedade': propriedade,
                    'fornecedores': fornecedores
                })
            
            # Chave de acesso
            chave_acesso = inf_nfe.get('Id', '').replace('NFe', '')
            
            # Verificar se já existe
            if NotaFiscal.objects.filter(chave_acesso=chave_acesso).exists():
                messages.warning(request, 'Esta NF-e já foi importada!')
                return redirect('notas_fiscais_lista', propriedade_id=propriedade.id)
            
            # Dados da NF
            ide = inf_nfe.find('.//nfe:ide', ns)
            if ide is None:
                messages.error(request, 'Estrutura XML inválida: elemento "ide" não encontrado')
                return render(request, 'gestao_rural/nota_fiscal_upload.html', {
                    'propriedade': propriedade,
                    'fornecedores': fornecedores
                })
            
            numero_elem = ide.find('nfe:nNF', ns)
            numero = numero_elem.text if numero_elem is not None and numero_elem.text else ''
            
            serie_elem = ide.find('nfe:serie', ns)
            serie = serie_elem.text if serie_elem is not None and serie_elem.text else '1'
            
            dh_emi_elem = ide.find('nfe:dhEmi', ns)
            if dh_emi_elem is not None and dh_emi_elem.text:
                try:
                    # Formato: 2024-01-15T10:30:00-03:00
                    data_emissao_str = dh_emi_elem.text[:10]
                    data_emissao = data_emissao_str
                except (ValueError, IndexError):
                    data_emissao = date.today().isoformat()
            else:
                data_emissao = date.today().isoformat()
            
            # Emitente
            emit = inf_nfe.find('.//nfe:emit', ns)
            if emit is None:
                messages.error(request, 'Estrutura XML inválida: elemento "emit" não encontrado')
                return render(request, 'gestao_rural/nota_fiscal_upload.html', {
                    'propriedade': propriedade,
                    'fornecedores': fornecedores
                })
            
            cnpj_elem = emit.find('nfe:CNPJ', ns)
            cnpj_emitente = cnpj_elem.text if cnpj_elem is not None and cnpj_elem.text else ''
            
            nome_elem = emit.find('nfe:xNome', ns)
            nome_emitente = nome_elem.text if nome_elem is not None and nome_elem.text else ''
            
            if not cnpj_emitente:
                messages.error(request, 'CNPJ do emitente não encontrado no XML')
                return render(request, 'gestao_rural/nota_fiscal_upload.html', {
                    'propriedade': propriedade,
                    'fornecedores': fornecedores
                })
            
            # Buscar ou criar fornecedor
            fornecedor, _ = Fornecedor.objects.get_or_create(
                cpf_cnpj=cnpj_emitente,
                defaults={'nome': nome_emitente, 'propriedade': propriedade}
            )
            
            # Valores
            total = inf_nfe.find('.//nfe:total/nfe:ICMSTot', ns)
            if total is None:
                messages.error(request, 'Estrutura XML inválida: valores totais não encontrados')
                return render(request, 'gestao_rural/nota_fiscal_upload.html', {
                    'propriedade': propriedade,
                    'fornecedores': fornecedores
                })
            
            v_prod_elem = total.find('nfe:vProd', ns)
            valor_produtos = Decimal(v_prod_elem.text) if v_prod_elem is not None and v_prod_elem.text else Decimal('0')
            
            v_nf_elem = total.find('nfe:vNF', ns)
            valor_total = Decimal(v_nf_elem.text) if v_nf_elem is not None and v_nf_elem.text else Decimal('0')
            
            # Criar Nota Fiscal
            nota = NotaFiscal(
                propriedade=propriedade,
                fornecedor=fornecedor,
                tipo='ENTRADA',
                numero=numero,
                serie=serie,
                chave_acesso=chave_acesso,
                data_emissao=datetime.strptime(data_emissao, '%Y-%m-%d').date(),
                valor_produtos=valor_produtos,
                valor_total=valor_total,
                status='AUTORIZADA',
                arquivo_xml=arquivo_xml,
                importado_por=request.user
            )
            nota.save()
            
            # Processar itens
            dets = inf_nfe.findall('.//nfe:det', ns)
            itens_processados = 0
            for det in dets:
                try:
                    prod = det.find('nfe:prod', ns)
                    if prod is None:
                        continue
                    
                    c_prod_elem = prod.find('nfe:cProd', ns)
                    codigo_produto = c_prod_elem.text if c_prod_elem is not None and c_prod_elem.text else ''
                    
                    x_prod_elem = prod.find('nfe:xProd', ns)
                    descricao = x_prod_elem.text if x_prod_elem is not None and x_prod_elem.text else ''
                    
                    ncm_elem = prod.find('nfe:NCM', ns)
                    ncm = ncm_elem.text if ncm_elem is not None and ncm_elem.text else ''
                    
                    u_com_elem = prod.find('nfe:uCom', ns)
                    unidade_medida = u_com_elem.text if u_com_elem is not None and u_com_elem.text else 'UN'
                    
                    q_com_elem = prod.find('nfe:qCom', ns)
                    quantidade = Decimal(q_com_elem.text) if q_com_elem is not None and q_com_elem.text else Decimal('1')
                    
                    v_un_com_elem = prod.find('nfe:vUnCom', ns)
                    valor_unitario = Decimal(v_un_com_elem.text) if v_un_com_elem is not None and v_un_com_elem.text else Decimal('0')
                    
                    item = ItemNotaFiscal(
                        nota_fiscal=nota,
                        codigo_produto=codigo_produto,
                        descricao=descricao,
                        ncm=ncm,
                        unidade_medida=unidade_medida,
                        quantidade=quantidade,
                        valor_unitario=valor_unitario,
                    )
                    item.save()
                    itens_processados += 1
                except Exception as e:
                    # Continuar processando outros itens mesmo se um falhar
                    import logging
                    logging.warning(f"Erro ao processar item da NF-e {numero}: {str(e)}")
                    continue
            
            if itens_processados == 0:
                messages.warning(request, f'NF-e importada, mas nenhum item foi processado. Verifique a estrutura do XML.')

            vinculada_ordem = False
            ordem_associada = None
            ordens_possiveis = OrdemCompra.objects.filter(
                propriedade=propriedade,
                fornecedor=fornecedor,
                nota_fiscal__isnull=True
            ).order_by('-data_emissao')

            tolerancia_minima = Decimal('1.00')
            tolerancia_percentual = Decimal('0.05')

            for ordem_candidata in ordens_possiveis:
                if ordem_candidata.valor_total:
                    diferenca = abs(ordem_candidata.valor_total - nota.valor_total)
                    tolerancia = max(tolerancia_minima, ordem_candidata.valor_total * tolerancia_percentual)
                    if diferenca <= tolerancia:
                        ordem_associada = ordem_candidata
                        break

            if ordem_associada:
                ordem_associada.nota_fiscal = nota
                ordem_associada.status = 'RECEBIDA'
                ordem_associada.data_recebimento = nota.data_emissao
                ordem_associada.save(update_fields=['nota_fiscal', 'status', 'data_recebimento'])
                conta_pagar, _ = gerar_conta_pagar_para_ordem(ordem_associada)
                conta_pagar.nota_fiscal = nota
                conta_pagar.valor = nota.valor_total
                conta_pagar.fornecedor = fornecedor
                conta_pagar.save(update_fields=['nota_fiscal', 'valor', 'fornecedor'])
                if ordem_associada.requisicao_origem:
                    EventoFluxoCompra.objects.create(
                        requisicao=ordem_associada.requisicao_origem,
                        etapa='FINANCEIRO',
                        status_anterior=ordem_associada.requisicao_origem.status,
                        status_novo=ordem_associada.requisicao_origem.status,
                        usuario=request.user,
                        comentario=f'NF-e {nota.numero} vinculada automaticamente à ordem {ordem_associada.numero_ordem}.'
                    )
                vinculada_ordem = True

            mensagem_sucesso = f'NF-e {numero} importada com sucesso!'
            if vinculada_ordem and ordem_associada:
                mensagem_sucesso += f' Vinculada à ordem {ordem_associada.numero_ordem}.'
            messages.success(request, mensagem_sucesso)
            return redirect('nota_fiscal_detalhes', propriedade_id=propriedade.id, nota_id=nota.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao processar XML: {str(e)}')
    
    return render(request, 'gestao_rural/nota_fiscal_upload.html', {
        'propriedade': propriedade,
        'fornecedores': fornecedores
    })


@login_required
def nota_fiscal_detalhes(request, propriedade_id, nota_id):
    """Detalhes da nota fiscal"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    nota = get_object_or_404(NotaFiscal, id=nota_id, propriedade=propriedade)
    itens = ItemNotaFiscal.objects.filter(nota_fiscal=nota)
    ordens = nota.ordens_compra.select_related('fornecedor').all() if nota.tipo == 'ENTRADA' else []
    contas_pagar = nota.contas_pagar.select_related('fornecedor', 'ordem_compra').all() if nota.tipo == 'ENTRADA' else []
    
    context = {
        'propriedade': propriedade,
        'nota': nota,
        'itens': itens,
        'ordens': ordens,
        'contas_pagar': contas_pagar,
    }
    
    return render(request, 'gestao_rural/nota_fiscal_detalhes.html', context)


@login_required
def nota_fiscal_emitir(request, propriedade_id):
    """Emitir NF-e de saída (venda)"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Buscar próximo número de NF-e
    ultima_nota = NotaFiscal.objects.filter(
        propriedade=propriedade,
        tipo='SAIDA',
        serie='1'
    ).order_by('-numero').first()
    
    proximo_numero = 1
    if ultima_nota and ultima_nota.numero:
        try:
            proximo_numero = int(ultima_nota.numero) + 1
        except (ValueError, TypeError):
            pass
    
    # Verificar se o modelo Produto existe (migration aplicada)
    try:
        from .models_compras_financeiro import Produto
        # Se chegou aqui, o modelo existe - usar formulário completo
        ItemNotaFiscalFormSet = inlineformset_factory(
            NotaFiscal,
            ItemNotaFiscal,
            form=ItemNotaFiscalForm,
            extra=1,
            can_delete=True,
            min_num=1,
            validate_min=True
        )
    except (ImportError, Exception) as e:
        # Se o modelo não existe ou há erro, criar formset sem o campo produto
        logger.warning(f'Modelo Produto não disponível, usando formulário simplificado: {str(e)}')
        class ItemNotaFiscalFormSemProduto(forms.ModelForm):
            """Formulário para itens da NF-e sem campo produto (fallback)"""
            class Meta:
                model = ItemNotaFiscal
                fields = [
                    'codigo_produto', 'descricao', 'ncm', 'cfop',
                    'unidade_medida', 'quantidade', 'valor_unitario'
                ]
                widgets = {
                    'codigo_produto': forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Código do produto'
                    }),
                    'descricao': forms.TextInput(attrs={
                        'class': 'form-control',
                        'required': True,
                        'placeholder': 'Descrição do produto/serviço'
                    }),
                    'ncm': forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'NCM (ex: 0102.29.00)'
                    }),
                    'cfop': forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'CFOP (ex: 5102)'
                    }),
                    'unidade_medida': forms.TextInput(attrs={
                        'class': 'form-control',
                        'value': 'UN',
                        'placeholder': 'UN, KG, etc.'
                    }),
                    'quantidade': forms.NumberInput(attrs={
                        'class': 'form-control',
                        'step': '0.001',
                        'min': '0.001',
                        'required': True
                    }),
                    'valor_unitario': forms.NumberInput(attrs={
                        'class': 'form-control',
                        'step': '0.01',
                        'min': '0.01',
                        'required': True
                    }),
                }
        
        ItemNotaFiscalFormSet = inlineformset_factory(
            NotaFiscal,
            ItemNotaFiscal,
            form=ItemNotaFiscalFormSemProduto,
            extra=1,
            can_delete=True,
            min_num=1,
            validate_min=True
        )
    
    if request.method == 'POST':
        form = NotaFiscalSaidaForm(request.POST, propriedade=propriedade)
        formset = ItemNotaFiscalFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            nota = form.save(commit=False)
            nota.propriedade = propriedade
            nota.tipo = 'SAIDA'
            nota.numero = str(proximo_numero)
            nota.status = 'PENDENTE'
            
            # Calcular valor total dos produtos
            if not nota.valor_produtos:
                nota.valor_produtos = Decimal('0.00')
            
            nota.save()
            
            # Salvar itens
            formset.instance = nota
            itens = formset.save()
            
            # Recalcular valor total dos produtos baseado nos itens
            valor_total_itens = sum(item.valor_total for item in itens)
            if valor_total_itens > 0:
                nota.valor_produtos = valor_total_itens
                nota.save()
            
            # Tentar emitir NF-e via API ou diretamente com SEFAZ (se configurado)
            try:
                from .services_nfe import emitir_nfe
                resultado = emitir_nfe(nota)
                if resultado.get('sucesso'):
                    nota.status = 'AUTORIZADA'
                    nota.chave_acesso = resultado.get('chave_acesso', '')
                    nota.protocolo_autorizacao = resultado.get('protocolo', '')
                    nota.data_autorizacao = timezone.now()
                    if resultado.get('xml'):
                        # Salvar XML retornado
                        from django.core.files.base import ContentFile
                        nota.arquivo_xml.save(f'nfe_{nota.numero}.xml', ContentFile(resultado['xml']), save=False)
                    nota.save()
                    messages.success(request, f'NF-e {nota.numero} emitida e autorizada com sucesso!')
                else:
                    nota.status = 'REJEITADA'
                    nota.save()
                    erro_msg = resultado.get("erro", "Erro desconhecido")
                    messages.warning(request, f'NF-e {nota.numero} criada, mas não foi autorizada: {erro_msg}')
            except ImportError:
                # Serviço de NF-e não configurado - apenas salvar como pendente
                messages.info(
                    request, 
                    f'NF-e {nota.numero} criada com status PENDENTE. '
                    'Configure NFE_SEFAZ (emissão direta) ou API_NFE (API terceira) nas settings para emissão automática.'
                )
            except Exception as e:
                logger.error(f'Erro ao emitir NF-e: {str(e)}', exc_info=True)
                messages.warning(request, f'NF-e {nota.numero} criada, mas houve erro na emissão: {str(e)}')
            
            return redirect('nota_fiscal_detalhes', propriedade_id=propriedade.id, nota_id=nota.id)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = NotaFiscalSaidaForm(propriedade=propriedade)
        formset = ItemNotaFiscalFormSet(instance=NotaFiscal())
    
    clientes = Cliente.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True),
        ativo=True
    ).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'formset': formset,
        'clientes': clientes,
        'proximo_numero': proximo_numero,
    }
    
    return render(request, 'gestao_rural/nota_fiscal_emitir.html', context)


@login_required
def sincronizar_nfe_recebidas(request, propriedade_id):
    """Sincronizar NFe recebidas automaticamente"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Verificar se a propriedade tem CPF/CNPJ configurado
    cpf_cnpj = propriedade.produtor.cpf_cnpj if hasattr(propriedade, 'produtor') and propriedade.produtor else None
    
    if not cpf_cnpj:
        messages.warning(
            request,
            'CPF/CNPJ não configurado para esta propriedade. Configure no cadastro do produtor.'
        )
        return redirect('compras_dashboard', propriedade_id=propriedade.id)
    
    # Verificar configuração da API
    from django.conf import settings
    api_nfe = getattr(settings, 'API_NFE', None)
    if not api_nfe:
        messages.error(
            request,
            'API de NF-e não configurada. Configure API_NFE nas settings do sistema.'
        )
        return redirect('compras_dashboard', propriedade_id=propriedade.id)
    
    if request.method == 'POST':
        from datetime import date, timedelta
        from gestao_rural.services_nfe_consulta import (
            consultar_nfe_recebidas,
            baixar_xml_nfe,
            baixar_pdf_nfe,
            importar_nfe_do_xml
        )
        from gestao_rural.models_compras_financeiro import NotaFiscal
        
        # Obter parâmetros
        dias = int(request.POST.get('dias', 30))
        limite = int(request.POST.get('limite', 100))
        baixar_pdf = request.POST.get('baixar_pdf') == 'on'
        
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)
        
        try:
            # Consultar NFe recebidas
            resultado = consultar_nfe_recebidas(
                propriedade=propriedade,
                data_inicio=data_inicio,
                data_fim=data_fim,
                limite=limite
            )
            
            if not resultado['sucesso']:
                messages.error(
                    request,
                    f'Erro ao consultar NFe: {resultado.get("erro", "Erro desconhecido")}'
                )
                return redirect('sincronizar_nfe_recebidas', propriedade_id=propriedade.id)
            
            notas_encontradas = resultado.get('notas', [])
            total_encontrado = resultado.get('total_encontrado', 0)
            
            if not notas_encontradas:
                messages.info(request, 'Nenhuma nota fiscal encontrada no período informado.')
                return redirect('notas_fiscais_lista', propriedade_id=propriedade.id)
            
            # Processar cada nota
            notas_importadas = 0
            notas_ja_existentes = 0
            erros = []
            
            for nota_data in notas_encontradas:
                chave_acesso = nota_data.get('chave_acesso', '')
                
                if not chave_acesso:
                    continue
                
                # Verificar se já existe
                if NotaFiscal.objects.filter(chave_acesso=chave_acesso).exists():
                    notas_ja_existentes += 1
                    continue
                
                try:
                    # Baixar XML
                    resultado_xml = baixar_xml_nfe(chave_acesso, api_nfe)
                    
                    if not resultado_xml['sucesso']:
                        erros.append(f'Nota {chave_acesso[:20]}...: Erro ao baixar XML')
                        continue
                    
                    xml_content = resultado_xml.get('xml')
                    if not xml_content:
                        erros.append(f'Nota {chave_acesso[:20]}...: XML vazio')
                        continue
                    
                    # Importar NFe do XML
                    resultado_importacao = importar_nfe_do_xml(
                        xml_content=xml_content,
                        propriedade=propriedade,
                        usuario=request.user
                    )
                    
                    if not resultado_importacao['sucesso']:
                        erros.append(
                            f'Nota {chave_acesso[:20]}...: {resultado_importacao.get("erro", "Erro desconhecido")}'
                        )
                        continue
                    
                    nota_fiscal = resultado_importacao['nota_fiscal']
                    
                    # Baixar PDF se solicitado
                    if baixar_pdf:
                        resultado_pdf = baixar_pdf_nfe(chave_acesso, api_nfe)
                        if resultado_pdf['sucesso']:
                            from django.core.files.base import ContentFile
                            nota_fiscal.arquivo_pdf.save(
                                f'nfe_{chave_acesso}.pdf',
                                ContentFile(resultado_pdf['pdf']),
                                save=True
                            )
                    
                    # Tentar vincular a ordem de compra
                    _vincular_ordem_compra_automatico(nota_fiscal, propriedade)
                    
                    notas_importadas += 1
                
                except Exception as e:
                    erros.append(f'Nota {chave_acesso[:20]}...: {str(e)}')
                    continue
            
            # Mensagens de resultado
            if notas_importadas > 0:
                messages.success(
                    request,
                    f'{notas_importadas} nota(s) fiscal(is) importada(s) com sucesso!'
                )
            
            if notas_ja_existentes > 0:
                messages.info(
                    request,
                    f'{notas_ja_existentes} nota(s) já estavam cadastrada(s) no sistema.'
                )
            
            if erros:
                messages.warning(
                    request,
                    f'{len(erros)} erro(s) durante a importação. Verifique os logs para detalhes.'
                )
            
            return redirect('notas_fiscais_lista', propriedade_id=propriedade.id)
        
        except Exception as e:
            messages.error(request, f'Erro ao sincronizar NFe: {str(e)}')
            logger.error(f'Erro ao sincronizar NFe: {str(e)}', exc_info=True)
    
    # Estatísticas
    from datetime import date, timedelta
    mes_atual = date.today().replace(day=1)
    nfes_mes = NotaFiscal.objects.filter(
        propriedade=propriedade,
        data_emissao__gte=mes_atual,
        tipo='ENTRADA'
    ).count()
    
    context = {
        'propriedade': propriedade,
        'cpf_cnpj': cpf_cnpj,
        'nfes_mes': nfes_mes,
    }
    
    return render(request, 'gestao_rural/sincronizar_nfe_recebidas.html', context)


def _vincular_ordem_compra_automatico(nota_fiscal, propriedade):
    """
    Tenta vincular automaticamente a nota fiscal a uma ordem de compra
    """
    try:
        from decimal import Decimal
        
        # Buscar ordens de compra do mesmo fornecedor sem nota fiscal
        ordens_possiveis = OrdemCompra.objects.filter(
            propriedade=propriedade,
            fornecedor=nota_fiscal.fornecedor,
            nota_fiscal__isnull=True,
            status__in=['ENVIADA', 'APROVADA', 'RECEBIDA']
        ).order_by('-data_emissao')
        
        tolerancia_minima = Decimal('1.00')
        tolerancia_percentual = Decimal('0.05')
        
        for ordem_candidata in ordens_possiveis:
            if ordem_candidata.valor_total:
                diferenca = abs(ordem_candidata.valor_total - nota_fiscal.valor_total)
                tolerancia = max(tolerancia_minima, ordem_candidata.valor_total * tolerancia_percentual)
                
                if diferenca <= tolerancia:
                    # Vincular
                    ordem_candidata.nota_fiscal = nota_fiscal
                    ordem_candidata.status = 'RECEBIDA'
                    ordem_candidata.data_recebimento = nota_fiscal.data_emissao
                    ordem_candidata.save(update_fields=['nota_fiscal', 'status', 'data_recebimento'])
                    
                    # Gerar conta a pagar
                    conta_pagar, _ = gerar_conta_pagar_para_ordem(ordem_candidata)
                    conta_pagar.nota_fiscal = nota_fiscal
                    conta_pagar.valor = nota_fiscal.valor_total
                    conta_pagar.save(update_fields=['nota_fiscal', 'valor'])
                    
                    return True
        
        return False
    except Exception as e:
        logger.warning(f'Erro ao vincular ordem de compra: {str(e)}')
        return False


# ============================================================================
# VIEWS - PRODUTOS (CADASTRO FISCAL)
# ============================================================================

@login_required
def produtos_lista(request, propriedade_id):
    """Lista de produtos cadastrados"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    # Filtros
    busca = request.GET.get('busca', '')
    categoria_id = request.GET.get('categoria', '')
    ativo = request.GET.get('ativo', '')
    
    produtos = Produto.objects.all()
    
    if busca:
        produtos = produtos.filter(
            Q(codigo__icontains=busca) |
            Q(descricao__icontains=busca) |
            Q(ncm__icontains=busca)
        )
    
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    
    if ativo == '1':
        produtos = produtos.filter(ativo=True)
    elif ativo == '0':
        produtos = produtos.filter(ativo=False)
    
    produtos = produtos.select_related('categoria', 'usuario_cadastro').order_by('categoria', 'descricao')
    
    categorias = CategoriaProduto.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'produtos': produtos,
        'categorias': categorias,
        'busca': busca,
        'categoria_id': categoria_id,
        'ativo': ativo,
    }
    
    return render(request, 'gestao_rural/produtos_lista.html', context)


@login_required
def produto_novo(request, propriedade_id):
    """Cadastrar novo produto"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.usuario_cadastro = request.user
            
            # Tentar sincronizar com Receita Federal
            try:
                resultado = sincronizar_produto(produto)
                if resultado.get('sucesso'):
                    messages.success(request, 'Produto cadastrado e sincronizado com a Receita Federal!')
                else:
                    messages.warning(request, f'Produto cadastrado, mas houve avisos na sincronização: {resultado.get("erro", "Erro desconhecido")}')
            except Exception as e:
                logger.error(f'Erro ao sincronizar produto: {str(e)}')
                messages.warning(request, 'Produto cadastrado, mas não foi possível sincronizar com a Receita Federal.')
            
            produto.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produtos_lista', propriedade_id=propriedade.id)
    else:
        form = ProdutoForm()
    
    categorias = CategoriaProduto.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'categorias': categorias,
    }
    
    return render(request, 'gestao_rural/produto_form.html', context)


@login_required
def produto_editar(request, propriedade_id, produto_id):
    """Editar produto existente"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            produto = form.save()
            
            # Sincronizar novamente com Receita Federal
            try:
                resultado = sincronizar_produto(produto)
                if resultado.get('sucesso'):
                    messages.success(request, 'Produto atualizado e sincronizado com a Receita Federal!')
            except Exception as e:
                logger.error(f'Erro ao sincronizar produto: {str(e)}')
            
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('produtos_lista', propriedade_id=propriedade.id)
    else:
        form = ProdutoForm(instance=produto)
    
    categorias = CategoriaProduto.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'produto': produto,
        'categorias': categorias,
    }
    
    return render(request, 'gestao_rural/produto_form.html', context)


@login_required
def produto_sincronizar(request, propriedade_id, produto_id):
    """Sincronizar produto com Receita Federal"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    produto = get_object_or_404(Produto, id=produto_id)
    
    try:
        resultado = sincronizar_produto(produto)
        if resultado.get('sucesso'):
            messages.success(request, 'Produto sincronizado com a Receita Federal!')
        else:
            messages.error(request, f'Erro ao sincronizar: {resultado.get("erro", "Erro desconhecido")}')
    except Exception as e:
        logger.error(f'Erro ao sincronizar produto: {str(e)}')
        messages.error(request, f'Erro ao sincronizar produto: {str(e)}')
    
    return redirect('produtos_lista', propriedade_id=propriedade.id)


@login_required
def categorias_produto_lista(request, propriedade_id):
    """Lista de categorias de produtos"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    categorias = CategoriaProduto.objects.all().annotate(
        total_produtos=Count('produtos')
    ).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'categorias': categorias,
    }
    
    return render(request, 'gestao_rural/categorias_produto_lista.html', context)


@login_required
def categoria_produto_nova(request, propriedade_id):
    """Cadastrar nova categoria de produto"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        form = CategoriaProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria cadastrada com sucesso!')
            return redirect('categorias_produto_lista', propriedade_id=propriedade.id)
    else:
        form = CategoriaProdutoForm()
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/categoria_produto_form.html', context)


@login_required
def consultar_ncm_ajax(request):
    """Consulta NCM via AJAX"""
    ncm = request.GET.get('ncm', '')
    
    if not ncm:
        return JsonResponse({'sucesso': False, 'erro': 'NCM não informado'})
    
    resultado = consultar_ncm(ncm)
    return JsonResponse(resultado)


@login_required
def validar_cfop_ajax(request):
    """Valida CFOP via AJAX"""
    cfop = request.GET.get('cfop', '')
    tipo_operacao = request.GET.get('tipo', 'SAIDA')
    
    if not cfop:
        return JsonResponse({'sucesso': False, 'erro': 'CFOP não informado'})
    
    resultado = validar_cfop(cfop, tipo_operacao)
    return JsonResponse(resultado)


@login_required
def autorizacao_excedente_solicitar(request, propriedade_id):
    """Solicitar autorização para exceder orçamento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        orcamento_id = request.POST.get('orcamento_id')
        valor_total = Decimal(request.POST.get('valor_total', '0'))
        justificativa = request.POST.get('justificativa', '')
        ordem_id = request.POST.get('ordem_id')
        
        try:
            orcamento = OrcamentoCompraMensal.objects.get(id=orcamento_id, propriedade=propriedade)
            ordem = None
            if ordem_id:
                ordem = OrdemCompra.objects.get(id=ordem_id, propriedade=propriedade)
            
            utilizado = orcamento.valor_utilizado(ignorar_ordem=ordem)
            saldo = orcamento.total_limite - utilizado
            valor_excedente = valor_total - saldo if valor_total > saldo else Decimal('0.00')
            
            if valor_excedente <= Decimal('0.00'):
                messages.error(request, 'Não há excedente de orçamento para autorizar.')
                return redirect('compras_dashboard', propriedade_id=propriedade.id)
            
            autorizacao = AutorizacaoExcedenteOrcamento.objects.create(
                orcamento=orcamento,
                ordem_compra=ordem,
                valor_excedente=valor_excedente,
                valor_total_compra=valor_total,
                justificativa=justificativa,
                status='PENDENTE',
                solicitado_por=request.user,
            )
            
            messages.success(request, 'Solicitação de autorização enviada com sucesso! Aguarde aprovação da gerência.')
            if ordem:
                return redirect('ordem_compra_detalhes', propriedade_id=propriedade.id, ordem_id=ordem.id)
            return redirect('compras_dashboard', propriedade_id=propriedade.id)
        except (OrcamentoCompraMensal.DoesNotExist, OrdemCompra.DoesNotExist, ValueError) as e:
            messages.error(request, 'Erro ao processar solicitação de autorização.')
            return redirect('compras_dashboard', propriedade_id=propriedade.id)
    
    return redirect('compras_dashboard', propriedade_id=propriedade.id)


@login_required
def autorizacao_excedente_aprovar(request, propriedade_id, autorizacao_id):
    """Aprovar ou reprovar autorização de excedente"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    try:
        autorizacao = AutorizacaoExcedenteOrcamento.objects.get(
            id=autorizacao_id,
            orcamento__propriedade=propriedade,
            status='PENDENTE'
        )
    except AutorizacaoExcedenteOrcamento.DoesNotExist:
        messages.error(request, 'Autorização não encontrada ou já processada.')
        return redirect('compras_dashboard', propriedade_id=propriedade.id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        observacoes = request.POST.get('observacoes', '')
        
        if acao == 'aprovar':
            autorizacao.status = 'APROVADA'
            autorizacao.aprovado_por = request.user
            autorizacao.data_aprovacao = timezone.now()
            autorizacao.observacoes_aprovacao = observacoes
            autorizacao.save()
            
            messages.success(request, 'Autorização de excedente aprovada com sucesso!')
        elif acao == 'reprovar':
            autorizacao.status = 'REPROVADA'
            autorizacao.aprovado_por = request.user
            autorizacao.data_aprovacao = timezone.now()
            autorizacao.observacoes_aprovacao = observacoes
            autorizacao.save()
            
            messages.success(request, 'Autorização de excedente reprovada.')
        else:
            messages.error(request, 'Ação inválida.')
            return redirect('compras_dashboard', propriedade_id=propriedade.id)
        
        if autorizacao.ordem_compra:
            return redirect('ordem_compra_detalhes', propriedade_id=propriedade.id, ordem_id=autorizacao.ordem_compra.id)
        return redirect('compras_dashboard', propriedade_id=propriedade.id)
    
    context = {
        'propriedade': propriedade,
        'autorizacao': autorizacao,
    }
    return render(request, 'gestao_rural/autorizacao_excedente_aprovar.html', context)


@login_required
def buscar_produtos_ajax(request):
    """Busca produtos via AJAX para autocomplete"""
    termo = request.GET.get('termo', '')
    
    if len(termo) < 2:
        return JsonResponse({'produtos': []})
    
    produtos = Produto.objects.filter(
        Q(ativo=True) &
        (Q(codigo__icontains=termo) |
         Q(descricao__icontains=termo) |
         Q(ncm__icontains=termo))
    ).select_related('categoria')[:20]
    
    resultados = []
    for produto in produtos:
        resultados.append({
            'id': produto.id,
            'codigo': produto.codigo,
            'descricao': produto.descricao,
            'ncm': produto.ncm,
            'ncm_descricao': produto.ncm_descricao or '',
            'cfop_entrada': produto.cfop_entrada or '',
            'cfop_saida_estadual': produto.cfop_saida_estadual or '',
            'cfop_saida_interestadual': produto.cfop_saida_interestadual or '',
            'unidade_medida': produto.unidade_medida,
            'preco_venda': str(produto.preco_venda),
            'categoria': produto.categoria.nome if produto.categoria else '',
        })
    
    return JsonResponse({'produtos': resultados})


@login_required
def cadastro_rapido_setor(request, propriedade_id):
    """Cadastro rápido de setor via AJAX"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        codigo = request.POST.get('codigo', '').strip() or None
        descricao = request.POST.get('descricao', '').strip() or None
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome do setor é obrigatório'}, status=400)
        
        try:
            setor = SetorPropriedade.objects.create(
                propriedade=propriedade,
                nome=nome,
                codigo=codigo,
                descricao=descricao,
                ativo=True
            )
            return JsonResponse({
                'success': True,
                'id': setor.id,
                'nome': setor.nome
            })
        except Exception as e:
            logger.error(f'Erro ao criar setor: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def cadastro_rapido_equipamento(request, propriedade_id):
    """Cadastro rápido de equipamento via AJAX"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    try:
        from .models_operacional import Equipamento, TipoEquipamento
    except ImportError:
        return JsonResponse({'success': False, 'error': 'Módulo de equipamentos não disponível'}, status=400)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip() or None
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome do equipamento é obrigatório'}, status=400)
        
        try:
            # Criar ou obter tipo padrão
            tipo_default, _ = TipoEquipamento.objects.get_or_create(
                nome='Diversos',
                defaults={'descricao': 'Equipamentos diversos', 'ativo': True}
            )
            
            equipamento = Equipamento.objects.create(
                propriedade=propriedade,
                nome=nome,
                descricao=descricao,
                tipo=tipo_default,
                ativo=True
            )
            return JsonResponse({
                'success': True,
                'id': equipamento.id,
                'nome': equipamento.nome
            })
        except Exception as e:
            logger.error(f'Erro ao criar equipamento: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def cadastro_rapido_centro_custo(request, propriedade_id):
    """Cadastro rápido de centro de custo via AJAX"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    try:
        from .models_financeiro import CentroCusto
    except ImportError:
        return JsonResponse({'success': False, 'error': 'Módulo financeiro não disponível'}, status=400)
    
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        tipo = request.POST.get('tipo', CentroCusto.TIPO_OPERACIONAL)
        descricao = request.POST.get('descricao', '').strip() or None
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome do centro de custo é obrigatório'}, status=400)
        
        try:
            centro_custo = CentroCusto.objects.create(
                propriedade=propriedade,
                nome=nome,
                tipo=tipo,
                descricao=descricao,
                ativo=True
            )
            return JsonResponse({
                'success': True,
                'id': centro_custo.id,
                'nome': centro_custo.nome
            })
        except Exception as e:
            logger.error(f'Erro ao criar centro de custo: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def cadastro_rapido_plano_conta(request, propriedade_id):
    """Cadastro rápido de plano de conta via AJAX"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    try:
        from .models_financeiro import PlanoConta
    except ImportError:
        return JsonResponse({'success': False, 'error': 'Módulo financeiro não disponível'}, status=400)
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        nome = request.POST.get('nome', '').strip()
        tipo = request.POST.get('tipo', PlanoConta.TIPO_DESPESA)
        descricao = request.POST.get('descricao', '').strip() or None
        
        if not codigo or not nome:
            return JsonResponse({'success': False, 'error': 'Código e nome são obrigatórios'}, status=400)
        
        try:
            plano_conta = PlanoConta.objects.create(
                propriedade=propriedade,
                codigo=codigo,
                nome=nome,
                tipo=tipo,
                descricao=descricao,
                ativo=True
            )
            return JsonResponse({
                'success': True,
                'id': plano_conta.id,
                'codigo': plano_conta.codigo,
                'nome': plano_conta.nome
            })
        except Exception as e:
            logger.error(f'Erro ao criar plano de conta: {e}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

