# -*- coding: utf-8 -*-
"""
Script para verificar transferências da Canta Galo para Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual
)


def verificar():
    """Verifica transferências da Canta Galo para Favo de Mel"""
    
    print("=" * 80)
    print("VERIFICAR TRANSFERENCIAS CANTA GALO -> FAVO DE MEL")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar planejamentos
    planejamento_canta_galo = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        codigo='PROJ-2025-0072'
    ).first()
    
    print(f"\n[INFO] Planejamento Canta Galo: {planejamento_canta_galo.codigo if planejamento_canta_galo else 'Nenhum'}")
    print(f"[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo if planejamento_favo else 'Nenhum'}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo if planejamento_girassol else 'Nenhum'}")
    
    # ========== 1. TRANSFERÊNCIAS DE SAÍDA DA CANTA GALO ==========
    print("\n[1. TRANSFERENCIAS DE SAIDA DA CANTA GALO]")
    saidas_canta_galo = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_canta_galo
    ).order_by('data_movimentacao')
    
    print(f"  Total: {saidas_canta_galo.count()}")
    total_saidas = 0
    for saida in saidas_canta_galo:
        print(f"    {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} garrotes")
        total_saidas += saida.quantidade
    
    # ========== 2. TRANSFERÊNCIAS DE ENTRADA NO FAVO DE MEL ==========
    print("\n[2. TRANSFERENCIAS DE ENTRADA NO FAVO DE MEL]")
    entradas_favo_mel = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"  Total: {entradas_favo_mel.count()}")
    total_entradas = 0
    for entrada in entradas_favo_mel:
        print(f"    {entrada.data_movimentacao.strftime('%d/%m/%Y')}: {entrada.quantidade} garrotes")
        total_entradas += entrada.quantidade
    
    # ========== 3. TRANSFERÊNCIAS DE SAÍDA DO FAVO DE MEL PARA GIRASSOL ==========
    print("\n[3. TRANSFERENCIAS DE SAIDA DO FAVO DE MEL PARA GIRASSOL]")
    saidas_favo_mel = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo,
        observacao__icontains='Girassol'
    ).order_by('data_movimentacao')
    
    print(f"  Total: {saidas_favo_mel.count()}")
    total_saidas_favo = 0
    for saida in saidas_favo_mel:
        print(f"    {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} garrotes")
        total_saidas_favo += saida.quantidade
    
    # ========== 4. TRANSFERÊNCIAS DE ENTRADA NA GIRASSOL ==========
    print("\n[4. TRANSFERENCIAS DE ENTRADA NA GIRASSOL]")
    entradas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento_girassol
    ).order_by('data_movimentacao')
    
    print(f"  Total: {entradas_girassol.count()}")
    total_entradas_girassol = 0
    for entrada in entradas_girassol:
        print(f"    {entrada.data_movimentacao.strftime('%d/%m/%Y')}: {entrada.quantidade} garrotes")
        total_entradas_girassol += entrada.quantidade
    
    print(f"\n[RESUMO]")
    print(f"  Saídas Canta Galo: {total_saidas} garrotes")
    print(f"  Entradas Favo de Mel: {total_entradas} garrotes")
    print(f"  Saídas Favo de Mel: {total_saidas_favo} garrotes")
    print(f"  Entradas Girassol: {total_entradas_girassol} garrotes")
    
    # Verificar se há diferença
    if total_saidas > total_entradas:
        print(f"\n[AVISO] Faltam {total_saidas - total_entradas} garrotes no Favo de Mel!")
    
    if total_entradas > total_saidas_favo:
        print(f"\n[AVISO] Faltam transferir {total_entradas - total_saidas_favo} garrotes do Favo de Mel para Girassol!")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















