# -*- coding: utf-8 -*-
"""
Script para verificar transferências do Favo de Mel para Girassol em 2024 e 2025
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')

categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

print("=" * 80)
print("VERIFICAR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL 2024 E 2025")
print("=" * 80)

# Transferências de saída do Favo de Mel
print("\n[FAVO DE MEL - Transferencias SAIDA]")
saidas_2024 = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote,
    data_movimentacao__year=2024
).order_by('data_movimentacao')

saidas_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote,
    data_movimentacao__year=2025
).order_by('data_movimentacao')

print(f"2024: {saidas_2024.count()} transferencias")
total_2024 = sum(s.quantidade for s in saidas_2024)
for s in saidas_2024:
    print(f"  - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade}")
print(f"  Total: {total_2024}")

print(f"\n2025: {saidas_2025.count()} transferencias")
total_2025 = sum(s.quantidade for s in saidas_2025)
for s in saidas_2025:
    print(f"  - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade}")
print(f"  Total: {total_2025}")

# Transferências de entrada no Girassol
print("\n[GIRASSOL - Transferencias ENTRADA]")
entradas_2024 = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote,
    data_movimentacao__year=2024
).order_by('data_movimentacao')

entradas_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote,
    data_movimentacao__year=2025
).order_by('data_movimentacao')

print(f"2024: {entradas_2024.count()} transferencias")
total_entradas_2024 = sum(e.quantidade for e in entradas_2024)
for e in entradas_2024:
    print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")
print(f"  Total: {total_entradas_2024}")

print(f"\n2025: {entradas_2025.count()} transferencias")
total_entradas_2025 = sum(e.quantidade for e in entradas_2025)
for e in entradas_2025:
    print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")
print(f"  Total: {total_entradas_2025}")

# Verificar se estão balanceadas
print("\n[VERIFICACAO]")
if total_2024 == total_entradas_2024:
    print(f"[OK] Transferencias 2024 balanceadas: {total_2024}")
else:
    print(f"[ERRO] Transferencias 2024 desbalanceadas: SAIDA={total_2024}, ENTRADA={total_entradas_2024}")

if total_2025 == total_entradas_2025:
    print(f"[OK] Transferencias 2025 balanceadas: {total_2025}")
else:
    print(f"[ERRO] Transferencias 2025 desbalanceadas: SAIDA={total_2025}, ENTRADA={total_entradas_2025}")

print(f"\n[OK] Verificacao concluida!")










