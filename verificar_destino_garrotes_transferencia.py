# -*- coding: utf-8 -*-
"""
Script para verificar para onde estão indo os garrotes (machos 12-24 meses) transferidos
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
categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

print("=" * 80)
print("VERIFICAR DESTINO DOS GARROTES (MACHOS 12-24 M) TRANSFERIDOS")
print("=" * 80)

# Buscar todas as transferências de saída de garrotes da Canta Galo
print("\n[CANTA GALO - Transferencias SAIDA de Garrotes]")
saidas = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

print(f"Total: {saidas.count()} transferencias")
total_saidas = 0
for saida in saidas:
    total_saidas += saida.quantidade
    obs_safe = saida.observacao.encode('ascii', 'ignore').decode('ascii') if saida.observacao else ''
    print(f"  - {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} - {obs_safe[:60]}")

print(f"\nTotal SAIDAS: {total_saidas}")

# Buscar todas as propriedades que receberam garrotes
print("\n[PROPRIEDADES QUE RECEBERAM GARROTES]")
entradas = MovimentacaoProjetada.objects.filter(
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
).select_related('propriedade').order_by('data_movimentacao')

print(f"Total: {entradas.count()} transferencias de entrada")

# Agrupar por propriedade
entradas_por_propriedade = {}
for entrada in entradas:
    nome_prop = entrada.propriedade.nome_propriedade
    if nome_prop not in entradas_por_propriedade:
        entradas_por_propriedade[nome_prop] = []
    entradas_por_propriedade[nome_prop].append(entrada)

for nome_prop, lista_entradas in entradas_por_propriedade.items():
    total_prop = sum(e.quantidade for e in lista_entradas)
    print(f"\n  {nome_prop}: {total_prop} garrotes ({len(lista_entradas)} transferencias)")
    for e in lista_entradas[:5]:  # Mostrar apenas as 5 primeiras
        obs_safe = e.observacao.encode('ascii', 'ignore').decode('ascii') if e.observacao else ''
        print(f"    + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} - {obs_safe[:50]}")

# Verificar correspondência
print("\n[VERIFICACAO DE CORRESPONDENCIA]")
total_entradas = sum(e.quantidade for e in entradas)
print(f"Total SAIDAS (Canta Galo): {total_saidas}")
print(f"Total ENTRADAS (todas propriedades): {total_entradas}")

if total_saidas == total_entradas:
    print("[OK] Transferencias balanceadas!")
else:
    print(f"[AVISO] Diferenca: {total_saidas - total_entradas}")

# Verificar especificamente Favo de Mel
favo_mel = Propriedade.objects.filter(nome_propriedade__icontains='Favo de Mel').first()
if favo_mel:
    entradas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    total_favo = sum(e.quantidade for e in entradas_favo)
    print(f"\n[FAVO DE MEL]")
    print(f"Total recebido: {total_favo} garrotes")
    print(f"Transferencias: {entradas_favo.count()}")
    for e in entradas_favo[:10]:  # Mostrar até 10
        obs_safe = e.observacao.encode('ascii', 'ignore').decode('ascii') if e.observacao else ''
        print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} - {obs_safe[:50]}")

print(f"\n[OK] Verificacao concluida!")




















