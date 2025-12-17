# -*- coding: utf-8 -*-
"""
Script para verificar saldo de transferências do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
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


def verificar():
    """Verifica saldo de transferências do Favo de Mel"""
    
    print("=" * 80)
    print("VERIFICAR SALDO TRANSFERENCIAS FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar planejamento
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento: {planejamento_favo.codigo if planejamento_favo else 'Nenhum'}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar TODAS as movimentações de garrotes no Favo de Mel
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        planejamento=planejamento_favo
    ).order_by('data_movimentacao', 'id')
    
    print(f"\n[MOVIMENTACOES DE GARROTES NO FAVO DE MEL]")
    print(f"  Total: {movimentacoes.count()}")
    
    # Agrupar por data e calcular saldo
    print(f"\n[ANALISE DETALHADA POR DATA]")
    
    saldo_atual = 0
    datas_processadas = set()
    
    for mov in movimentacoes:
        data_mov = mov.data_movimentacao
        
        if data_mov not in datas_processadas:
            # Calcular saldo até esta data
            saldo_ate_data = calcular_saldo_disponivel(favo_mel, categoria_garrote, data_mov, planejamento_favo)
            
            # Buscar todas as movimentações nesta data
            movs_data = movimentacoes.filter(data_movimentacao=data_mov)
            
            print(f"\n  [{data_mov.strftime('%d/%m/%Y')}]")
            print(f"    Saldo antes das movimentações: {saldo_ate_data}")
            
            for m in movs_data:
                if m.tipo_movimentacao in ['TRANSFERENCIA_ENTRADA', 'COMPRA']:
                    print(f"      +{m.quantidade} ({m.tipo_movimentacao}) - {m.observacao[:50] if m.observacao else ''}")
                    saldo_ate_data += m.quantidade
                elif m.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                    print(f"      -{m.quantidade} ({m.tipo_movimentacao}) - Saldo antes: {saldo_ate_data}")
                    if saldo_ate_data < m.quantidade:
                        print(f"      [ERRO] Saldo insuficiente! Tentando transferir {m.quantidade} mas só tem {saldo_ate_data}")
                    saldo_ate_data -= m.quantidade
                    print(f"      Saldo após: {saldo_ate_data}")
            
            print(f"    Saldo final do dia: {saldo_ate_data}")
            datas_processadas.add(data_mov)
    
    # Verificar 2022 especificamente
    print(f"\n[ANALISE ESPECIFICA 2022]")
    
    # Entradas em 2022
    entradas_2022 = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao__in=['TRANSFERENCIA_ENTRADA', 'COMPRA'],
        data_movimentacao__year=2022,
        planejamento=planejamento_favo
    )
    
    print(f"  Entradas em 2022:")
    total_entradas = 0
    for entrada in entradas_2022:
        print(f"    {entrada.data_movimentacao.strftime('%d/%m/%Y')}: +{entrada.quantidade} ({entrada.tipo_movimentacao})")
        total_entradas += entrada.quantidade
    
    print(f"  Total de entradas: {total_entradas}")
    
    # Saídas em 2022
    saidas_2022 = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        data_movimentacao__year=2022,
        planejamento=planejamento_favo
    )
    
    print(f"  Saídas em 2022:")
    total_saidas = 0
    for saida in saidas_2022:
        print(f"    {saida.data_movimentacao.strftime('%d/%m/%Y')}: -{saida.quantidade}")
        total_saidas += saida.quantidade
    
    print(f"  Total de saídas: {total_saidas}")
    print(f"  Diferença: {total_entradas - total_saidas}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











