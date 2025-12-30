# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, InventarioRebanho
from datetime import date

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

inventario = InventarioRebanho.objects.filter(
    propriedade=girassol, 
    categoria=categoria
).order_by('-data_inventario').first()

print(f'Inventario inicial: {inventario.quantidade if inventario else 0} em {inventario.data_inventario if inventario else "N/A"}')

saldo = inventario.quantidade if inventario else 0

movs_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=girassol, 
    categoria=categoria, 
    data_movimentacao__year=2025
).order_by('data_movimentacao')

print(f'\nMovimentacoes 2025: {movs_2025.count()}')
for mov in movs_2025:
    print(f'{mov.data_movimentacao}: {mov.tipo_movimentacao} {mov.quantidade}')
    if mov.tipo_movimentacao in ['TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo += mov.quantidade
    elif mov.tipo_movimentacao in ['TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA', 'VENDA', 'MORTE']:
        saldo -= mov.quantidade

print(f'\nSaldo final 2025: {saldo}')

# Verificar se há inventário para 2026
inventario_2026 = InventarioRebanho.objects.filter(
    propriedade=girassol, 
    categoria=categoria,
    data_inventario__year=2026
).first()

print(f'\nInventario 2026: {inventario_2026.quantidade if inventario_2026 else "Nao existe"}')
























