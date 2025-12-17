# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("Promocoes de vacas em reproducao para descarte em 2023:")
promocoes = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"Total: {promocoes.count()}")
for p in promocoes:
    print(f"  {p.data_movimentacao.strftime('%d/%m/%Y')}: {p.quantidade}")

# Verificar saldo final de 2022
print("\nSaldo final de 2022:")
from gestao_rural.models import InventarioRebanho

inventario = InventarioRebanho.objects.filter(
    propriedade=canta_galo,
    data_inventario__lte=date(2022, 12, 31)
).order_by('-data_inventario').first()

saldo = 0
if inventario:
    invs = InventarioRebanho.objects.filter(
        propriedade=canta_galo,
        data_inventario=inventario.data_inventario,
        categoria=categoria_descarte
    )
    saldo = sum(inv.quantidade for inv in invs)

movs_2022 = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte,
    data_movimentacao__year=2022
).order_by('data_movimentacao')

for mov in movs_2022:
    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo += mov.quantidade
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
        saldo -= mov.quantidade

print(f"Saldo final 2022: {saldo}")










