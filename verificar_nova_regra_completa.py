# -*- coding: utf-8 -*-
"""
Script para verificar a nova regra completa:
1. Compras no Favo de Mel
2. Transferências para Girassol
3. Vendas de 100 em 100 após 90 dias
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from collections import defaultdict
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica a nova regra completa"""
    
    print("=" * 80)
    print("VERIFICAR NOVA REGRA COMPLETA")
    print("=" * 80)
    print("1. Compras no Favo de Mel")
    print("2. Transferências para Girassol")
    print("3. Vendas de 100 em 100 após 90 dias")
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
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # ========== 1. COMPRAS NO FAVO DE MEL ==========
    print("\n[1. COMPRAS NO FAVO DE MEL]")
    compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"  Total: {compras.count()}")
    total_compras = 0
    for compra in compras:
        valor_str = f"{compra.valor_total:,.2f}" if compra.valor_total else "0.00"
        print(f"    {compra.data_movimentacao.strftime('%d/%m/%Y')}: {compra.quantidade} garrotes - R$ {valor_str}")
        total_compras += compra.quantidade
    
    # ========== 2. TRANSFERÊNCIAS PARA GIRASSOL ==========
    print("\n[2. TRANSFERÊNCIAS FAVO DE MEL -> GIRASSOL]")
    
    # Saídas do Favo de Mel (compras transferidas)
    saidas_compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo,
        observacao__icontains='comprados'
    ).order_by('data_movimentacao')
    
    print(f"  Saídas (de compras): {saidas_compras.count()}")
    total_saidas = 0
    for saida in saidas_compras:
        print(f"    {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} garrotes")
        total_saidas += saida.quantidade
    
    # Entradas na Girassol (de compras)
    entradas_compras = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento_girassol,
        observacao__icontains='comprados'
    ).order_by('data_movimentacao')
    
    print(f"  Entradas (de compras): {entradas_compras.count()}")
    total_entradas = 0
    for entrada in entradas_compras:
        print(f"    {entrada.data_movimentacao.strftime('%d/%m/%Y')}: {entrada.quantidade} garrotes")
        total_entradas += entrada.quantidade
    
    # ========== 3. VENDAS NA GIRASSOL ==========
    print("\n[3. VENDAS NA GIRASSOL (de 100 em 100)]")
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_boi,
        tipo_movimentacao='VENDA',
        planejamento=planejamento_girassol
    ).order_by('data_movimentacao')
    
    print(f"  Total: {vendas.count()}")
    
    # Agrupar por entrada
    vendas_por_entrada = defaultdict(list)
    for venda in vendas:
        # Buscar entrada relacionada (90 dias antes)
        data_entrada_esperada = venda.data_movimentacao - timedelta(days=90)
        entrada_relacionada = entradas_compras.filter(
            data_movimentacao__gte=data_entrada_esperada - timedelta(days=5),
            data_movimentacao__lte=data_entrada_esperada + timedelta(days=5)
        ).first()
        
        if entrada_relacionada:
            vendas_por_entrada[entrada_relacionada.data_movimentacao].append(venda)
    
    total_vendido = 0
    for entrada_data, vendas_lote in sorted(vendas_por_entrada.items()):
        print(f"\n  Entrada: {entrada_data.strftime('%d/%m/%Y')}")
        entrada = entradas_compras.filter(data_movimentacao=entrada_data).first()
        if entrada:
            print(f"    Quantidade recebida: {entrada.quantidade}")
            print(f"    Vendas criadas: {len(vendas_lote)}")
            total_lote = sum(v.quantidade for v in vendas_lote)
            print(f"    Total vendido: {total_lote}")
            for venda in vendas_lote:
                print(f"      {venda.data_movimentacao.strftime('%d/%m/%Y')}: {venda.quantidade} bois")
            total_vendido += total_lote
    
    print(f"\n[RESUMO]")
    print(f"  Compras no Favo de Mel: {total_compras} garrotes")
    print(f"  Transferências para Girassol: {total_entradas} garrotes")
    print(f"  Vendas na Girassol: {total_vendido} bois")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    from datetime import timedelta
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

