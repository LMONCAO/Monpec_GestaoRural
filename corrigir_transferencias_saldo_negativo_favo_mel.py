# -*- coding: utf-8 -*-
"""
Script para corrigir transferências com saldo negativo no Favo de Mel
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
    """Calcula saldo disponível considerando inventário e movimentações"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações até a data
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return saldo


@transaction.atomic
def corrigir():
    """Corrige transferências com saldo negativo"""
    
    print("=" * 80)
    print("CORRIGIR TRANSFERENCIAS COM SALDO NEGATIVO FAVO DE MEL")
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
    
    # Buscar TODAS as transferências de saída
    saidas = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao', 'id')
    
    print(f"\n[TRANSFERENCIAS DE SAIDA]")
    print(f"  Total: {saidas.count()}")
    
    transferencias_corrigidas = 0
    transferencias_deletadas = 0
    
    for saida in saidas:
        # Calcular saldo disponível ANTES desta transferência
        data_verificacao = saida.data_movimentacao - timedelta(days=1)
        saldo_disponivel = calcular_saldo_disponivel(
            favo_mel, categoria_garrote, data_verificacao, planejamento_favo
        )
        
        if saldo_disponivel < saida.quantidade:
            # Saldo insuficiente - ajustar ou deletar
            if saldo_disponivel > 0:
                # Ajustar quantidade
                quantidade_ajustada = saldo_disponivel
                print(f"  [AJUSTE] {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} -> {quantidade_ajustada} (saldo: {saldo_disponivel})")
                
                # Atualizar saída
                saida.quantidade = quantidade_ajustada
                saida.observacao = f'{saida.observacao} - AJUSTADO: quantidade reduzida para respeitar saldo'
                saida.save()
                
                # Atualizar entrada correspondente na Girassol
                entrada_girassol = MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    categoria=categoria_garrote,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    data_movimentacao=saida.data_movimentacao,
                    planejamento=planejamento_girassol
                ).first()
                
                if entrada_girassol:
                    entrada_girassol.quantidade = quantidade_ajustada
                    entrada_girassol.save()
                
                transferencias_corrigidas += 1
            else:
                # Saldo zero ou negativo - deletar transferência
                print(f"  [DELETAR] {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} (saldo: {saldo_disponivel})")
                
                # Deletar entrada correspondente na Girassol
                entrada_girassol = MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    categoria=categoria_garrote,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    data_movimentacao=saida.data_movimentacao,
                    planejamento=planejamento_girassol
                ).first()
                
                if entrada_girassol:
                    entrada_girassol.delete()
                
                # Deletar saída
                saida.delete()
                transferencias_deletadas += 1
    
    print(f"\n[RESUMO]")
    print(f"  Transferências corrigidas: {transferencias_corrigidas}")
    print(f"  Transferências deletadas: {transferencias_deletadas}")
    
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    try:
        corrigir()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















