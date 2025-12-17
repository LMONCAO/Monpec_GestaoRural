# -*- coding: utf-8 -*-
"""
Script para verificar transferências e vendas de vacas descarte em 2023
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
invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')

categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR TRANSFERENCIAS E VENDAS 2023")
print("=" * 80)

# Transferências de saída da Canta Galo
print("\n[CANTA GALO - Transferencias SAIDA em 2023]")
saidas = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

total_saidas = sum(s.quantidade for s in saidas)
print(f"Total: {saidas.count()} transferencias, {total_saidas} vacas")
for s in saidas:
    print(f"  - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade} - {s.observacao}")

# Transferências de entrada na Invernada Grande
print("\n[INVERNADA GRANDE - Transferencias ENTRADA em 2023]")
entradas = MovimentacaoProjetada.objects.filter(
    propriedade=invernada_grande,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

total_entradas = sum(e.quantidade for e in entradas)
print(f"Total: {entradas.count()} transferencias, {total_entradas} vacas")
for e in entradas:
    print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} - {e.observacao}")

# Vendas na Invernada Grande
print("\n[INVERNADA GRANDE - Vendas em 2023]")
vendas = MovimentacaoProjetada.objects.filter(
    propriedade=invernada_grande,
    tipo_movimentacao='VENDA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

total_vendido = sum(v.quantidade for v in vendas)
print(f"Total: {vendas.count()} vendas, {total_vendido} vacas")
for v in vendas:
    print(f"  - {v.data_movimentacao.strftime('%d/%m/%Y')}: {v.quantidade} - {v.observacao}")

# Verificar saldos
print("\n[VERIFICACAO DE SALDOS]")
print(f"Transferencias SAIDA (Canta Galo): {total_saidas}")
print(f"Transferencias ENTRADA (Invernada Grande): {total_entradas}")
print(f"Vendas (Invernada Grande): {total_vendido}")

if total_saidas == total_entradas:
    print(f"[OK] Transferencias balanceadas!")
else:
    print(f"[ERRO] Transferencias desbalanceadas!")

if total_entradas == total_vendido:
    print(f"[OK] Todas as vacas foram vendidas!")
else:
    print(f"[AVISO] Faltam vender {total_entradas - total_vendido} vacas")

print(f"\n[OK] Verificacao concluida!")











