# -*- coding: utf-8 -*-
"""
Script para verificar para onde estão indo as 512 vacas descarte em 2023
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
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR DESTINO DAS 512 VACAS DESCARTE 2023")
print("=" * 80)

# Buscar transferências de saída da Canta Galo em 2023
print("\n[CANTA GALO - Transferencias SAIDA de Vacas Descarte em 2023]")
saidas_2023 = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"Total: {saidas_2023.count()} transferencias")
for saida in saidas_2023:
    print(f"  - {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} - {saida.observacao}")
    print(f"    Planejamento: {saida.planejamento.codigo if saida.planejamento else 'Nenhum'}")

# Buscar todas as propriedades que receberam vacas descarte em 2023
print("\n[PROPRIEDADES QUE RECEBERAM VACAS DESCARTE EM 2023]")
entradas_2023 = MovimentacaoProjetada.objects.filter(
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).select_related('propriedade').order_by('data_movimentacao')

print(f"Total: {entradas_2023.count()} transferencias de entrada")
for entrada in entradas_2023:
    print(f"  + {entrada.propriedade.nome_propriedade}: {entrada.quantidade} em {entrada.data_movimentacao.strftime('%d/%m/%Y')}")
    print(f"    Observacao: {entrada.observacao}")
    print(f"    Planejamento: {entrada.planejamento.codigo if entrada.planejamento else 'Nenhum'}")

# Verificar se há correspondência entre saídas e entradas
print("\n[VERIFICACAO DE CORRESPONDENCIA]")
total_saidas = sum(s.quantidade for s in saidas_2023)
total_entradas = sum(e.quantidade for e in entradas_2023)

print(f"Total SAIDAS (Canta Galo): {total_saidas}")
print(f"Total ENTRADAS (todas propriedades): {total_entradas}")

if total_saidas == total_entradas:
    print("[OK] Transferencias balanceadas!")
else:
    print(f"[AVISO] Diferenca: {total_saidas - total_entradas}")

# Verificar especificamente Invernada Grande
invernada_grande = Propriedade.objects.filter(nome_propriedade__icontains='Invernada Grande').first()
if invernada_grande:
    entradas_invernada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year=2023
    )
    total_invernada = sum(e.quantidade for e in entradas_invernada)
    print(f"\n[INVERNADA GRANDE]")
    print(f"Total recebido em 2023: {total_invernada}")
    for e in entradas_invernada:
        print(f"  + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")

print(f"\n[OK] Verificacao concluida!")











