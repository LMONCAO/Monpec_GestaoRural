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
categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')

print("Vendas de vacas em reproducao em 2023:")
vendas = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='VENDA',
    categoria=categoria_reproducao,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"Total: {vendas.count()}")
for v in vendas:
    print(f"  {v.data_movimentacao.strftime('%d/%m/%Y')}: {v.quantidade}")

# Verificar se essas vendas têm promoções para descarte
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("\nPromocoes de reproducao para descarte em 2023:")
promocoes_saida = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='PROMOCAO_SAIDA',
    categoria=categoria_reproducao,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

promocoes_entrada = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"Promocoes SAIDA (reproducao): {promocoes_saida.count()}")
for p in promocoes_saida:
    print(f"  - {p.data_movimentacao.strftime('%d/%m/%Y')}: {p.quantidade}")

print(f"\nPromocoes ENTRADA (descarte): {promocoes_entrada.count()}")
for p in promocoes_entrada:
    print(f"  + {p.data_movimentacao.strftime('%d/%m/%Y')}: {p.quantidade}")

total_promocoes = sum(p.quantidade for p in promocoes_entrada)
print(f"\nTotal promovido para descarte em 2023: {total_promocoes}")











