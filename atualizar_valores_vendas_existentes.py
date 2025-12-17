# -*- coding: utf-8 -*-
"""
Script para atualizar valores das vendas existentes conforme configuração por ano
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
    Propriedade, MovimentacaoProjetada, VendaProjetada, CategoriaAnimal
)


@transaction.atomic
def atualizar_valores():
    """Atualiza valores das vendas existentes"""
    
    print("=" * 80)
    print("ATUALIZAR VALORES DAS VENDAS EXISTENTES")
    print("=" * 80)
    
    # Valores por ano
    valores_bezerras = {
        2022: Decimal('1900.00'),
        2023: Decimal('1600.00'),
        2024: Decimal('1875.00'),
        2025: Decimal('2100.00'),
    }
    
    valores_garrotes = {
        2022: Decimal('2300.00'),
        2023: Decimal('2000.00'),
        2024: Decimal('2280.00'),
        2025: Decimal('2350.00'),
    }
    
    valores_boi_gordo = {
        2022: Decimal('5700.00'),
        2023: Decimal('4950.00'),
        2024: Decimal('5890.00'),
        2025: Decimal('6032.00'),
    }
    
    # Buscar categorias
    categoria_bezerra = CategoriaAnimal.objects.get(nome__icontains='Bezerro(a) 0-12 F')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # ========== 1. ATUALIZAR VENDAS DE BEZERRAS ==========
    print("\n[1. ATUALIZAR VENDAS DE BEZERRAS]")
    vendas_bezerras = MovimentacaoProjetada.objects.filter(
        categoria=categoria_bezerra,
        tipo_movimentacao='VENDA'
    )
    
    atualizadas = 0
    for venda in vendas_bezerras:
        ano = venda.data_movimentacao.year
        valor_por_cabeca = valores_bezerras.get(ano, Decimal('1600.00'))
        valor_total = valor_por_cabeca * Decimal(str(venda.quantidade))
        
        venda.valor_por_cabeca = valor_por_cabeca
        venda.valor_total = valor_total
        venda.save()
        atualizadas += 1
    
    print(f"  Vendas atualizadas: {atualizadas}")
    
    # ========== 2. ATUALIZAR COMPRAS DE GARROTES ==========
    print("\n[2. ATUALIZAR COMPRAS DE GARROTES]")
    compras_garrotes = MovimentacaoProjetada.objects.filter(
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA'
    )
    
    atualizadas = 0
    for compra in compras_garrotes:
        ano = compra.data_movimentacao.year
        valor_por_cabeca = valores_garrotes.get(ano, Decimal('2300.00'))
        valor_total = valor_por_cabeca * Decimal(str(compra.quantidade))
        
        compra.valor_por_cabeca = valor_por_cabeca
        compra.valor_total = valor_total
        compra.save()
        atualizadas += 1
    
    print(f"  Compras atualizadas: {atualizadas}")
    
    # ========== 3. ATUALIZAR VENDAS DE BOI GORDO ==========
    print("\n[3. ATUALIZAR VENDAS DE BOI GORDO]")
    vendas_boi = MovimentacaoProjetada.objects.filter(
        categoria=categoria_boi,
        tipo_movimentacao='VENDA'
    )
    
    atualizadas = 0
    for venda in vendas_boi:
        ano = venda.data_movimentacao.year
        valor_total_boi = valores_boi_gordo.get(ano, Decimal('5700.00'))
        peso_medio = Decimal('500.00')
        valor_por_kg = valor_total_boi / peso_medio
        valor_total = valor_total_boi * Decimal(str(venda.quantidade))
        
        # Atualizar MovimentacaoProjetada
        venda.valor_por_cabeca = valor_total_boi
        venda.valor_total = valor_total
        venda.save()
        
        # Atualizar ou criar VendaProjetada
        venda_projetada = VendaProjetada.objects.filter(
            movimentacao_projetada=venda
        ).first()
        
        if venda_projetada:
            venda_projetada.valor_por_kg = valor_por_kg
            venda_projetada.peso_medio_kg = peso_medio
            venda_projetada.valor_total = valor_total
            venda_projetada.save()
        else:
            # Criar VendaProjetada se não existir
            from gestao_rural.models import Propriedade
            propriedade = venda.propriedade
            VendaProjetada.objects.create(
                propriedade=propriedade,
                movimentacao_projetada=venda,
                data_venda=venda.data_movimentacao,
                categoria=categoria_boi,
                quantidade=venda.quantidade,
                cliente_nome='Frigorífico',
                valor_por_kg=valor_por_kg,
                peso_medio_kg=peso_medio,
                valor_total=valor_total
            )
        
        atualizadas += 1
    
    print(f"  Vendas atualizadas: {atualizadas}")
    
    print("\n[OK] Valores atualizados com sucesso!")


if __name__ == '__main__':
    try:
        atualizar_valores()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

