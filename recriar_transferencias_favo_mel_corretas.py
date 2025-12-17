# -*- coding: utf-8 -*-
"""
Script para recriar transferências do Favo de Mel respeitando saldo disponível
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction
from datetime import date, timedelta
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual,
    InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo disponível ANTES da data de referência"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lt=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações ANTES da data (não incluir movimentações na própria data)
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lt=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)  # Não permitir saldo negativo


@transaction.atomic
def recriar():
    """Recria transferências respeitando saldo disponível"""
    
    print("=" * 80)
    print("RECRIAR TRANSFERENCIAS FAVO DE MEL CORRETAS")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamentos
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo if planejamento_favo else 'Nenhum'}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo if planejamento_girassol else 'Nenhum'}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # ========== 1. DELETAR TODAS AS TRANSFERÊNCIAS DE SAÍDA (exceto compras) ==========
    print("\n[1. DELETANDO TRANSFERENCIAS DE SAIDA EXISTENTES]")
    
    # Deletar apenas transferências regulares (480 a cada 90 dias), não as de compras
    saidas_para_deletar = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo
    ).exclude(
        observacao__icontains='comprados'
    )
    
    # Buscar entradas correspondentes na Girassol
    entradas_para_deletar = []
    for saida in saidas_para_deletar:
        entrada = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade,
            planejamento=planejamento_girassol
        ).exclude(
            observacao__icontains='comprados'
        ).first()
        
        if entrada:
            entradas_para_deletar.append(entrada)
    
    total_deletadas = saidas_para_deletar.count()
    saidas_para_deletar.delete()
    for entrada in entradas_para_deletar:
        entrada.delete()
    
    print(f"  Deletadas: {total_deletadas} transferências")
    
    # ========== 2. RECRIAR TRANSFERÊNCIAS RESPEITANDO SALDO ==========
    print("\n[2. RECRIANDO TRANSFERENCIAS COM SALDO CORRETO]")
    
    # Primeira transferência: 01/04/2022
    data_transferencia = date(2022, 4, 1)
    quantidade_por_transferencia = 480
    intervalo_meses = 3  # 90 dias
    ano_fim = 2026
    transferencias_criadas = 0
    
    while data_transferencia.year <= ano_fim:
        # Calcular saldo disponível ANTES desta transferência
        saldo_disponivel = calcular_saldo_disponivel(
            favo_mel, categoria_garrote, data_transferencia, planejamento_favo
        )
        
        if saldo_disponivel <= 0:
            print(f"  [PULAR] {data_transferencia.strftime('%d/%m/%Y')}: Sem saldo (saldo: {saldo_disponivel})")
            # Usar função adicionar_meses
            from datetime import timedelta
            data_transferencia = data_transferencia + timedelta(days=90)
            continue
        
        # Quantidade a transferir: mínimo entre 480 e saldo disponível
        quantidade_transferir = min(quantidade_por_transferencia, saldo_disponivel)
        
        if quantidade_transferir <= 0:
            print(f"  [PULAR] {data_transferencia.strftime('%d/%m/%Y')}: Quantidade zero")
            from datetime import timedelta
            data_transferencia = data_transferencia + timedelta(days=90)
            continue
        
        # Criar transferência de saída do Favo de Mel
        MovimentacaoProjetada.objects.create(
            propriedade=favo_mel,
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_favo,
            observacao=f'Transferencia para Girassol - {quantidade_transferir} garrotes (saldo disponivel: {saldo_disponivel}) - CONFIGURACAO PADRAO: 480 a cada 90 dias - SEM SALDO NEGATIVO'
        )
        
        # Criar transferência de entrada no Girassol
        MovimentacaoProjetada.objects.create(
            propriedade=girassol,
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_girassol,
            observacao=f'Transferencia de Favo de Mel - {quantidade_transferir} garrotes - CONFIGURACAO PADRAO: 480 a cada 90 dias'
        )
        
        print(f"  [OK] {data_transferencia.strftime('%d/%m/%Y')}: {quantidade_transferir} garrotes (saldo antes: {saldo_disponivel})")
        transferencias_criadas += 1
        
        # Próxima transferência: 90 dias depois (3 meses)
        from datetime import timedelta
        data_transferencia = data_transferencia + timedelta(days=90)
    
    print(f"\n[RESUMO]")
    print(f"  Transferências criadas: {transferencias_criadas}")
    
    # Aplicar configuração padrão da Girassol
    print("\n[Aplicando configuração padrão da Girassol...]")
    try:
        from gestao_rural.configuracao_padrao_girassol import aplicar_configuracao_padrao_girassol
        aplicar_configuracao_padrao_girassol(girassol, planejamento_girassol)
        print("[OK] Configuração padrão aplicada!")
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    try:
        recriar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

