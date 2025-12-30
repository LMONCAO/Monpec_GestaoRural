# -*- coding: utf-8 -*-
"""
Script para verificar se as movimentações de morte e venda foram criadas corretamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')

categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR MOVIMENTACOES CRIADAS 2023")
print("=" * 80)

# Girassol - Mortes
print("\n[GIRASSOL - Mortes em 2023]")
mortes = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='MORTE',
    categoria=categoria_boi,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"Total: {mortes.count()}")
for m in mortes:
    print(f"  {m.data_movimentacao.strftime('%d/%m/%Y')}: {m.quantidade} - {m.observacao}")

# Invernada Grande - Vendas
print("\n[INVERNADA GRANDE - Vendas em 2023]")
vendas = MovimentacaoProjetada.objects.filter(
    propriedade=invernada_grande,
    tipo_movimentacao='VENDA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"Total: {vendas.count()}")
total_vendido = 0
for v in vendas:
    print(f"  {v.data_movimentacao.strftime('%d/%m/%Y')}: {v.quantidade} - {v.observacao}")
    total_vendido += v.quantidade

print(f"\nTotal vendido em 2023: {total_vendido}")

print(f"\n[OK] Verificacao concluida!")
























