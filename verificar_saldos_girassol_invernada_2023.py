# -*- coding: utf-8 -*-
"""
Script para verificar saldos detalhados na Girassol e Invernada Grande em 2023
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    InventarioRebanho
)

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')

categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR SALDOS GIRASSOL E INVERNADA GRANDE 2023")
print("=" * 80)

# ========== GIRASSOL ==========
print("\n[GIRASSOL - Boi 24-36 M]")
print("-" * 80)

# Inventário inicial
inventario = InventarioRebanho.objects.filter(
    propriedade=girassol,
    data_inventario__lte=date(2023, 12, 31)
).order_by('-data_inventario').first()

if inventario:
    invs = InventarioRebanho.objects.filter(
        propriedade=girassol,
        data_inventario=inventario.data_inventario,
        categoria=categoria_boi
    )
    saldo_inicial = sum(inv.quantidade for inv in invs)
    print(f"Inventario inicial ({inventario.data_inventario.strftime('%d/%m/%Y')}): {saldo_inicial}")
else:
    saldo_inicial = 0
    print("Sem inventario inicial")

# Todas as movimentações
movimentacoes = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    categoria=categoria_boi,
    data_movimentacao__year__lte=2023
).order_by('data_movimentacao')

print(f"\nMovimentacoes em 2023:")
saldo = saldo_inicial
for mov in movimentacoes:
    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo += mov.quantidade
        sinal = '+'
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
        saldo -= mov.quantidade
        sinal = '-'
    else:
        sinal = '?'
    
    print(f"  {sinal} {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.quantidade} - {mov.tipo_movimentacao} (saldo: {saldo})")

print(f"\nSaldo final: {saldo}")

# ========== INVERNADA GRANDE ==========
print("\n[INVERNADA GRANDE - Vacas Descarte +36 M]")
print("-" * 80)

# Inventário inicial
inventario = InventarioRebanho.objects.filter(
    propriedade=invernada_grande,
    data_inventario__lte=date(2023, 12, 31)
).order_by('-data_inventario').first()

if inventario:
    invs = InventarioRebanho.objects.filter(
        propriedade=invernada_grande,
        data_inventario=inventario.data_inventario,
        categoria=categoria_descarte
    )
    saldo_inicial = sum(inv.quantidade for inv in invs)
    print(f"Inventario inicial ({inventario.data_inventario.strftime('%d/%m/%Y')}): {saldo_inicial}")
else:
    saldo_inicial = 0
    print("Sem inventario inicial")

# Todas as movimentações
movimentacoes = MovimentacaoProjetada.objects.filter(
    propriedade=invernada_grande,
    categoria=categoria_descarte,
    data_movimentacao__year__lte=2023
).order_by('data_movimentacao')

print(f"\nMovimentacoes em 2023:")
saldo = saldo_inicial
for mov in movimentacoes:
    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo += mov.quantidade
        sinal = '+'
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
        saldo -= mov.quantidade
        sinal = '-'
    else:
        sinal = '?'
    
    print(f"  {sinal} {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.quantidade} - {mov.tipo_movimentacao} (saldo: {saldo})")

print(f"\nSaldo final: {saldo}")

print(f"\n[OK] Verificacao concluida!")











