# -*- coding: utf-8 -*-
"""
Script para verificar transferências de garrotes em 2024 e 2025
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')

categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

print("=" * 80)
print("VERIFICAR TRANSFERENCIAS GARROTES 2024 E 2025")
print("=" * 80)

# Transferências de saída da Canta Galo
print("\n[CANTA GALO - Transferencias SAIDA]")
saidas_2024 = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote,
    data_movimentacao__year=2024
).order_by('data_movimentacao')

saidas_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote,
    data_movimentacao__year=2025
).order_by('data_movimentacao')

print(f"2024: {saidas_2024.count()} transferencias")
for s in saidas_2024:
    print(f"  - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade}")

print(f"\n2025: {saidas_2025.count()} transferencias")
for s in saidas_2025:
    print(f"  - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade}")

# Transferências de entrada no Favo de Mel
print("\n[FAVO DE MEL - Transferencias ENTRADA]")
entradas_2024 = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote,
    data_movimentacao__year=2024
).order_by('data_movimentacao')

entradas_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote,
    data_movimentacao__year=2025
).order_by('data_movimentacao')

print(f"2024: {entradas_2024.count()} transferencias")
for e in entradas_2024:
    print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")

print(f"\n2025: {entradas_2025.count()} transferencias")
for e in entradas_2025:
    print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")

print(f"\n[OK] Verificacao concluida!")










