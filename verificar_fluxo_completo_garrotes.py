# -*- coding: utf-8 -*-
"""
Script para verificar o fluxo completo dos garrotes: Canta Galo -> Favo de Mel -> Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')

categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

print("=" * 80)
print("FLUXO COMPLETO DOS GARROTES")
print("=" * 80)

# 1. Canta Galo -> Favo de Mel
print("\n[1] CANTA GALO -> FAVO DE MEL")
saidas_canta = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

entradas_favo = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

total_saidas_canta = sum(s.quantidade for s in saidas_canta)
total_entradas_favo = sum(e.quantidade for e in entradas_favo)

print(f"  Saidas (Canta Galo): {total_saidas_canta}")
print(f"  Entradas (Favo de Mel): {total_entradas_favo}")
if total_saidas_canta == total_entradas_favo:
    print(f"  [OK] Balanceado!")
else:
    print(f"  [ERRO] Desbalanceado: {total_saidas_canta - total_entradas_favo}")

# 2. Favo de Mel -> Girassol
print("\n[2] FAVO DE MEL -> GIRASSOL")
saidas_favo = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

entradas_girassol = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

total_saidas_favo = sum(s.quantidade for s in saidas_favo)
total_entradas_girassol = sum(e.quantidade for e in entradas_girassol)

print(f"  Saidas (Favo de Mel): {total_saidas_favo}")
print(f"  Entradas (Girassol): {total_entradas_girassol}")
if total_saidas_favo == total_entradas_girassol:
    print(f"  [OK] Balanceado!")
else:
    print(f"  [ERRO] Desbalanceado: {total_saidas_favo - total_entradas_girassol}")

# Resumo
print("\n[RESUMO DO FLUXO]")
print(f"  Canta Galo -> Favo de Mel: {total_saidas_canta} garrotes")
print(f"  Favo de Mel -> Girassol: {total_saidas_favo} garrotes")
print(f"  Saldo no Favo de Mel: {total_entradas_favo - total_saidas_favo} garrotes")

print(f"\n[OK] Verificacao concluida!")











