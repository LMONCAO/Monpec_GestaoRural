# -*- coding: utf-8 -*-
"""
Script para verificar inventários iniciais
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import Propriedade, InventarioRebanho, CategoriaAnimal

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')

categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR INVENTARIOS INICIAIS")
print("=" * 80)

# Girassol
print("\n[GIRASSOL]")
inventarios_girassol = InventarioRebanho.objects.filter(
    propriedade=girassol,
    categoria=categoria_boi
).order_by('data_inventario')

print(f"Inventarios de Boi 24-36 M: {inventarios_girassol.count()}")
for inv in inventarios_girassol:
    print(f"  {inv.data_inventario.strftime('%d/%m/%Y')}: {inv.quantidade}")

# Invernada Grande
print("\n[INVERNADA GRANDE]")
inventarios_invernada = InventarioRebanho.objects.filter(
    propriedade=invernada_grande,
    categoria=categoria_descarte
).order_by('data_inventario')

print(f"Inventarios de Vacas Descarte: {inventarios_invernada.count()}")
for inv in inventarios_invernada:
    print(f"  {inv.data_inventario.strftime('%d/%m/%Y')}: {inv.quantidade}")

# Verificar saldo considerando inventário inicial
print("\n[VERIFICACAO DE SALDO COM INVENTARIO]")

# Girassol - saldo em 31/12/2023
inventario_girassol = InventarioRebanho.objects.filter(
    propriedade=girassol,
    data_inventario__lte=date(2023, 12, 31),
    categoria=categoria_boi
).order_by('-data_inventario').first()

saldo_girassol = 0
if inventario_girassol:
    saldo_girassol = inventario_girassol.quantidade
    print(f"Girassol - Inventario inicial: {saldo_girassol}")

from gestao_rural.models import MovimentacaoProjetada
movs_girassol = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    categoria=categoria_boi,
    data_movimentacao__lte=date(2023, 12, 31)
).order_by('data_movimentacao')

for mov in movs_girassol:
    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo_girassol += mov.quantidade
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
        saldo_girassol -= mov.quantidade

print(f"Girassol - Saldo final (com movimentacoes): {saldo_girassol}")

# Invernada Grande - saldo em 31/12/2023
inventario_invernada = InventarioRebanho.objects.filter(
    propriedade=invernada_grande,
    data_inventario__lte=date(2023, 12, 31),
    categoria=categoria_descarte
).order_by('-data_inventario').first()

saldo_invernada = 0
if inventario_invernada:
    saldo_invernada = inventario_invernada.quantidade
    print(f"Invernada Grande - Inventario inicial: {saldo_invernada}")

movs_invernada = MovimentacaoProjetada.objects.filter(
    propriedade=invernada_grande,
    categoria=categoria_descarte,
    data_movimentacao__lte=date(2023, 12, 31)
).order_by('data_movimentacao')

for mov in movs_invernada:
    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo_invernada += mov.quantidade
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
        saldo_invernada -= mov.quantidade

print(f"Invernada Grande - Saldo final (com movimentacoes): {saldo_invernada}")

print(f"\n[OK] Verificacao concluida!")
























