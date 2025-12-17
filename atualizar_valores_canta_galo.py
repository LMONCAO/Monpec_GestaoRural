# -*- coding: utf-8 -*-
"""
Script para atualizar valores de vacas em reprodução e machos na Canta Galo
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction
from decimal import Decimal
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho
)


@transaction.atomic
def atualizar_valores():
    """Atualiza valores de vacas em reprodução e machos na Canta Galo"""
    
    print("=" * 80)
    print("ATUALIZAR VALORES CANTA GALO")
    print("=" * 80)
    print("Vacas em Reprodução: R$ 5.500,00 por cabeça (todos os anos)")
    print("Machos: R$ 3.000,00 por cabeça (todos os anos)")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    
    # Buscar categorias
    categoria_vacas_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
    
    # Buscar categorias de machos (pode haver várias)
    from django.db.models import Q
    categorias_machos = CategoriaAnimal.objects.filter(
        Q(nome__icontains='Garrote') | Q(nome__icontains='Boi') | Q(nome__icontains='Touro')
    )
    
    print(f"\n[INFO] Fazenda: {canta_galo.nome_propriedade}")
    print(f"[INFO] Categoria Vacas em Reprodução: {categoria_vacas_reproducao.nome}")
    print(f"[INFO] Categorias de Machos: {[c.nome for c in categorias_machos]}")
    
    # Valores novos
    valor_vaca_reproducao = Decimal('5500.00')
    valor_macho = Decimal('3000.00')
    
    # ========== 1. ATUALIZAR INVENTÁRIO ==========
    print("\n[1. ATUALIZANDO INVENTARIO]")
    
    # Vacas em reprodução
    inventarios_vacas = InventarioRebanho.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_vacas_reproducao
    )
    
    atualizados = 0
    for inv in inventarios_vacas:
        if inv.valor_por_cabeca != valor_vaca_reproducao:
            inv.valor_por_cabeca = valor_vaca_reproducao
            inv.save()
            atualizados += 1
    
    print(f"  Inventários de vacas em reprodução atualizados: {atualizados}")
    
    # Machos
    inventarios_machos = InventarioRebanho.objects.filter(
        propriedade=canta_galo,
        categoria__in=categorias_machos
    )
    
    atualizados = 0
    for inv in inventarios_machos:
        if inv.valor_por_cabeca != valor_macho:
            inv.valor_por_cabeca = valor_macho
            inv.save()
            atualizados += 1
    
    print(f"  Inventários de machos atualizados: {atualizados}")
    
    # ========== 2. ATUALIZAR MOVIMENTAÇÕES ==========
    print("\n[2. ATUALIZANDO MOVIMENTACOES]")
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("  [AVISO] Nenhum planejamento encontrado")
    else:
        print(f"  Planejamento: {planejamento.codigo}")
        
        # Vacas em reprodução
        movimentacoes_vacas = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_vacas_reproducao,
            planejamento=planejamento
        )
        
        atualizadas = 0
        for mov in movimentacoes_vacas:
            if mov.valor_por_cabeca != valor_vaca_reproducao:
                mov.valor_por_cabeca = valor_vaca_reproducao
                if mov.quantidade:
                    mov.valor_total = mov.quantidade * valor_vaca_reproducao
                mov.save()
                atualizadas += 1
        
        print(f"  Movimentações de vacas em reprodução atualizadas: {atualizadas}")
        
        # Machos
        movimentacoes_machos = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria__in=categorias_machos,
            planejamento=planejamento
        )
        
        atualizadas = 0
        for mov in movimentacoes_machos:
            if mov.valor_por_cabeca != valor_macho:
                mov.valor_por_cabeca = valor_macho
                if mov.quantidade:
                    mov.valor_total = mov.quantidade * valor_macho
                mov.save()
                atualizadas += 1
        
        print(f"  Movimentações de machos atualizadas: {atualizadas}")
    
    # ========== 3. ATUALIZAR TODAS AS MOVIMENTAÇÕES (TODOS OS PLANEJAMENTOS) ==========
    print("\n[3. ATUALIZANDO TODAS AS MOVIMENTACOES (TODOS OS PLANEJAMENTOS)]")
    
    # Vacas em reprodução
    todas_mov_vacas = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_vacas_reproducao
    )
    
    atualizadas = 0
    for mov in todas_mov_vacas:
        if mov.valor_por_cabeca != valor_vaca_reproducao:
            mov.valor_por_cabeca = valor_vaca_reproducao
            if mov.quantidade:
                mov.valor_total = mov.quantidade * valor_vaca_reproducao
            mov.save()
            atualizadas += 1
    
    print(f"  Total de movimentações de vacas em reprodução atualizadas: {atualizadas}")
    
    # Machos
    todas_mov_machos = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria__in=categorias_machos
    )
    
    atualizadas = 0
    for mov in todas_mov_machos:
        if mov.valor_por_cabeca != valor_macho:
            mov.valor_por_cabeca = valor_macho
            if mov.quantidade:
                mov.valor_total = mov.quantidade * valor_macho
            mov.save()
            atualizadas += 1
    
    print(f"  Total de movimentações de machos atualizadas: {atualizadas}")
    
    print("\n[OK] Valores atualizados com sucesso!")


if __name__ == '__main__':
    try:
        atualizar_valores()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

