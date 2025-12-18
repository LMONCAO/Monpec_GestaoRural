# -*- coding: utf-8 -*-
"""
Script para verificar o que aconteceu com as vacas descarte na Canta Galo em 2023
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    InventarioRebanho
)

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

print("=" * 80)
print("VERIFICAR VACAS DESCARTE CANTA GALO 2023")
print("=" * 80)

# Verificar inventário inicial
inventarios = InventarioRebanho.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte
).order_by('data_inventario')

print(f"\n[INFO] Inventarios iniciais:")
for inv in inventarios:
    print(f"   {inv.data_inventario.strftime('%d/%m/%Y')}: {inv.quantidade}")

# Verificar todas as movimentações de vacas descarte na Canta Galo
print(f"\n[INFO] Todas as movimentacoes de Vacas Descarte na Canta Galo:")
movimentacoes = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte
).order_by('data_movimentacao')

for mov in movimentacoes:
    sinal = '+' if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA'] else '-'
    print(f"   {sinal} {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.quantidade} - {mov.tipo_movimentacao}")

# Calcular saldo em 15/01/2023
print(f"\n[INFO] Calculando saldo em 15/01/2023...")

inventario_inicial = InventarioRebanho.objects.filter(
    propriedade=canta_galo,
    data_inventario__lte=date(2023, 1, 15)
).order_by('-data_inventario').first()

saldo = 0
if inventario_inicial:
    inventarios = InventarioRebanho.objects.filter(
        propriedade=canta_galo,
        data_inventario=inventario_inicial.data_inventario,
        categoria=categoria_descarte
    )
    saldo = sum(inv.quantidade for inv in inventarios)
    print(f"   Inventario inicial: {saldo}")

movimentacoes_ate_2023 = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte,
    data_movimentacao__lte=date(2023, 1, 15)
).order_by('data_movimentacao')

for mov in movimentacoes_ate_2023:
    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
        saldo += mov.quantidade
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
        saldo -= mov.quantidade
        if saldo < 0:
            saldo = 0

print(f"   Saldo em 15/01/2023: {saldo}")

# Verificar se há promoções de vacas em reprodução para descarte em 2023
print(f"\n[INFO] Verificando promocoes de vacas em reproducao para descarte em 2023...")
categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')

promocoes_entrada = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    categoria=categoria_descarte,
    data_movimentacao__year=2023
).order_by('data_movimentacao')

print(f"   Promocoes ENTRADA (descarte) em 2023: {promocoes_entrada.count()}")
for p in promocoes_entrada:
    print(f"      + {p.data_movimentacao.strftime('%d/%m/%Y')}: {p.quantidade}")

if promocoes_entrada.exists():
    print(f"\n[INFO] Ha promocoes em 2023! Pode haver estoque disponivel apos as promocoes")

print(f"\n[OK] Verificacao concluida!")




















