# -*- coding: utf-8 -*-
"""
Serviço para integrar vendas projetadas com o módulo financeiro
"""
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum, Q
from django.db import transaction
from django.utils import timezone

from .models import VendaProjetada, Propriedade
from .models_financeiro import ReceitaAnual, LancamentoFinanceiro, CategoriaFinanceira, ContaFinanceira


def sincronizar_receitas_anuais_vendas(propriedade, anos=None):
    """
    Sincroniza receitas anuais baseadas nas vendas projetadas.
    
    Args:
        propriedade: Propriedade
        anos: Lista de anos para sincronizar (None = todos os anos com vendas)
    
    Returns:
        dict: Resumo da sincronização
    """
    # Buscar todos os anos com vendas projetadas
    from django.db.models.functions import ExtractYear
    
    vendas_por_ano = VendaProjetada.objects.filter(
        propriedade=propriedade
    ).annotate(
        ano_venda=ExtractYear('data_venda')
    ).values('ano_venda').annotate(
        total=Sum('valor_total')
    ).order_by('ano_venda')
    
    if anos:
        vendas_por_ano = vendas_por_ano.filter(ano_venda__in=anos)
    
    receitas_criadas = 0
    receitas_atualizadas = 0
    total_receitas = Decimal('0.00')
    
    for item in vendas_por_ano:
        ano = item['ano_venda']
        valor_total = item['total'] or Decimal('0.00')
        
        # Buscar ou criar receita anual
        receita, created = ReceitaAnual.objects.get_or_create(
            propriedade=propriedade,
            ano=ano,
            defaults={
                'valor_receita': valor_total,
                'descricao': f'Receita consolidada das vendas projetadas do ano {ano}'
            }
        )
        
        if created:
            receitas_criadas += 1
        else:
            # Atualizar valor se já existir
            receita.valor_receita = valor_total
            receita.descricao = f'Receita consolidada das vendas projetadas do ano {ano}'
            receita.save()
            receitas_atualizadas += 1
        
        total_receitas += valor_total
    
    return {
        'receitas_criadas': receitas_criadas,
        'receitas_atualizadas': receitas_atualizadas,
        'total_receitas': total_receitas,
        'anos_processados': len(vendas_por_ano)
    }


def calcular_saldos_anuais_consolidados(propriedade, anos=None):
    """
    Calcula saldos consolidados ano a ano considerando receitas e despesas.
    
    Args:
        propriedade: Propriedade
        anos: Lista de anos para calcular (None = todos os anos com receitas)
    
    Returns:
        list: Lista de dicionários com dados ano a ano
    """
    from .models_financeiro import DespesaConfigurada
    
    # Buscar receitas anuais
    receitas = ReceitaAnual.objects.filter(propriedade=propriedade)
    if anos:
        receitas = receitas.filter(ano__in=anos)
    receitas = receitas.order_by('ano')
    
    saldos_anuais = []
    saldo_acumulado = Decimal('0.00')
    
    for receita in receitas:
        ano = receita.ano
        valor_receita = receita.valor_receita
        
        # Calcular despesas totais do ano
        despesas = DespesaConfigurada.objects.filter(
            propriedade=propriedade,
            ativo=True
        )
        total_despesas = Decimal('0.00')
        for despesa in despesas:
            total_despesas += despesa.calcular_valor_anual(valor_receita)
        
        # Calcular saldo do ano
        saldo_ano = valor_receita - total_despesas
        saldo_acumulado += saldo_ano
        
        # Calcular margem
        margem_percentual = (saldo_ano / valor_receita * 100) if valor_receita > 0 else Decimal('0.00')
        
        saldos_anuais.append({
            'ano': ano,
            'receita': valor_receita,
            'despesas': total_despesas,
            'saldo_ano': saldo_ano,
            'saldo_acumulado': saldo_acumulado,
            'margem_percentual': margem_percentual,
        })
    
    return saldos_anuais


def criar_lancamentos_financeiros_vendas(propriedade, ano=None, conta_destino=None, categoria_receita=None):
    """
    Cria lançamentos financeiros baseados nas vendas projetadas.
    
    Args:
        propriedade: Propriedade
        ano: Ano específico (None = todos os anos)
        conta_destino: ContaFinanceira para recebimento (None = primeira conta ativa)
        categoria_receita: CategoriaFinanceira para receitas (None = primeira categoria de receita)
    
    Returns:
        dict: Resumo dos lançamentos criados
    """
    # Buscar conta destino padrão se não fornecida
    if not conta_destino:
        conta_destino = ContaFinanceira.objects.filter(
            propriedade=propriedade,
            ativa=True
        ).first()
        if not conta_destino:
            return {
                'erro': 'Nenhuma conta financeira ativa encontrada. Crie uma conta primeiro.',
                'lancamentos_criados': 0
            }
    
    # Buscar categoria de receita padrão se não fornecida
    if not categoria_receita:
        categoria_receita = CategoriaFinanceira.objects.filter(
            propriedade=propriedade,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            ativa=True
        ).first()
        if not categoria_receita:
            # Criar categoria padrão se não existir
            categoria_receita = CategoriaFinanceira.objects.create(
                propriedade=propriedade,
                nome='Vendas de Animais',
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao='Receitas provenientes de vendas de animais',
                ativa=True
            )
    
    # Buscar vendas projetadas
    from django.db.models.functions import ExtractYear
    
    vendas = VendaProjetada.objects.filter(propriedade=propriedade)
    if ano:
        vendas = vendas.annotate(ano_venda=ExtractYear('data_venda')).filter(ano_venda=ano)
    
    lancamentos_criados = 0
    lancamentos_duplicados = 0
    
    with transaction.atomic():
        for venda in vendas:
            # Verificar se já existe lançamento para esta venda
            lancamento_existente = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                descricao__icontains=f"Venda {venda.data_venda.strftime('%d/%m/%Y')}",
                valor=venda.valor_total,
                data_competencia=venda.data_recebimento or venda.data_venda
            ).first()
            
            if lancamento_existente:
                lancamentos_duplicados += 1
                continue
            
            # Criar lançamento financeiro
            data_recebimento = venda.data_recebimento or venda.data_venda
            data_vencimento = data_recebimento
            
            LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria_receita,
                conta_destino=conta_destino,
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao=f"Venda {venda.data_venda.strftime('%d/%m/%Y')} - {venda.quantidade} {venda.categoria.nome} - {venda.cliente_nome or 'Cliente não definido'}",
                valor=venda.valor_total,
                data_competencia=venda.data_venda,
                data_vencimento=data_vencimento,
                data_quitacao=data_recebimento if data_recebimento <= timezone.localdate() else None,
                forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                status=LancamentoFinanceiro.STATUS_QUITADO if data_recebimento <= timezone.localdate() else LancamentoFinanceiro.STATUS_PENDENTE,
                documento_referencia=f"Venda Projetada ID: {venda.id}",
                observacoes=f"Gerado automaticamente da venda projetada. Cliente: {venda.cliente_nome or 'Não definido'}"
            )
            lancamentos_criados += 1
    
    return {
        'lancamentos_criados': lancamentos_criados,
        'lancamentos_duplicados': lancamentos_duplicados,
        'conta_destino': conta_destino.nome,
        'categoria_receita': categoria_receita.nome
    }


def obter_resumo_financeiro_por_ano(propriedade, anos=None):
    """
    Obtém resumo financeiro completo por ano (receitas, despesas, saldos).
    
    Args:
        propriedade: Propriedade
        anos: Lista de anos (None = todos)
    
    Returns:
        dict: Resumo completo
    """
    saldos_anuais = calcular_saldos_anuais_consolidados(propriedade, anos)
    
    # Calcular totais
    total_receitas = sum(item['receita'] for item in saldos_anuais)
    total_despesas = sum(item['despesas'] for item in saldos_anuais)
    total_saldo = sum(item['saldo_ano'] for item in saldos_anuais)
    
    # Saldo acumulado final
    saldo_acumulado_final = saldos_anuais[-1]['saldo_acumulado'] if saldos_anuais else Decimal('0.00')
    
    return {
        'saldos_anuais': saldos_anuais,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'total_saldo': total_saldo,
        'saldo_acumulado_final': saldo_acumulado_final,
        'anos_analisados': len(saldos_anuais)
    }

