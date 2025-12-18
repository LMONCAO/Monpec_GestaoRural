# -*- coding: utf-8 -*-
"""
Script para verificar por que o estoque da Girassol está crescendo tanto
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')

print("=" * 60)
print("VERIFICAR CRESCIMENTO ESTOQUE GIRASSOL")
print("=" * 60)

# Verificar transferências de entrada (garrotes)
print(f"\n[INFO] Transferencias de ENTRADA (Garrotes):")
entradas = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

total_entradas = 0
for e in entradas:
    total_entradas += e.quantidade
    print(f"   + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} (ano {e.data_movimentacao.year})")
print(f"   Total ENTRADA: {total_entradas}")

# Verificar evoluções (garrotes -> bois)
print(f"\n[INFO] Evolucoes (Garrotes -> Bois):")
evolucoes_saida = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='PROMOCAO_SAIDA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

evolucoes_entrada = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    categoria=categoria_boi
).order_by('data_movimentacao')

total_evolucoes = 0
for e in evolucoes_entrada:
    total_evolucoes += e.quantidade
    print(f"   -> {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} garrotes evoluem para bois (ano {e.data_movimentacao.year})")
print(f"   Total EVOLUCOES: {total_evolucoes}")

# Verificar vendas de bois
print(f"\n[INFO] Vendas de BOIS:")
vendas_bois = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='VENDA',
    categoria=categoria_boi
).order_by('data_movimentacao')

total_vendas_bois = 0
for v in vendas_bois:
    total_vendas_bois += v.quantidade
    print(f"   - {v.data_movimentacao.strftime('%d/%m/%Y')}: {v.quantidade} bois vendidos (ano {v.data_movimentacao.year})")
print(f"   Total VENDAS BOIS: {total_vendas_bois}")

# Verificar vendas de garrotes
print(f"\n[INFO] Vendas de GARROTES:")
vendas_garrotes = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='VENDA',
    categoria=categoria_garrote
).order_by('data_movimentacao')

total_vendas_garrotes = 0
for v in vendas_garrotes:
    total_vendas_garrotes += v.quantidade
    print(f"   - {v.data_movimentacao.strftime('%d/%m/%Y')}: {v.quantidade} garrotes vendidos (ano {v.data_movimentacao.year})")
print(f"   Total VENDAS GARROTES: {total_vendas_garrotes}")

# Resumo por ano
print(f"\n[INFO] Resumo por ano:")

anos = [2022, 2023, 2024, 2025, 2026]
for ano in anos:
    entradas_ano = sum(e.quantidade for e in entradas if e.data_movimentacao.year == ano)
    evolucoes_ano = sum(e.quantidade for e in evolucoes_entrada if e.data_movimentacao.year == ano)
    vendas_bois_ano = sum(v.quantidade for v in vendas_bois if v.data_movimentacao.year == ano)
    vendas_garrotes_ano = sum(v.quantidade for v in vendas_garrotes if v.data_movimentacao.year == ano)
    
    if entradas_ano > 0 or evolucoes_ano > 0 or vendas_bois_ano > 0 or vendas_garrotes_ano > 0:
        print(f"\n   {ano}:")
        print(f"      Entradas: +{entradas_ano}")
        print(f"      Evolucoes: {evolucoes_ano} garrotes -> bois")
        print(f"      Vendas bois: -{vendas_bois_ano}")
        print(f"      Vendas garrotes: -{vendas_garrotes_ano}")
        print(f"      Saldo liquido: +{entradas_ano} -{vendas_bois_ano} -{vendas_garrotes_ano} = {entradas_ano - vendas_bois_ano - vendas_garrotes_ano}")

# Diagnóstico
print(f"\n[DIAGNOSTICO]")
print(f"   Total entradas: {total_entradas}")
print(f"   Total evolucoes: {total_evolucoes}")
print(f"   Total vendas bois: {total_vendas_bois}")
print(f"   Total vendas garrotes: {total_vendas_garrotes}")

if total_evolucoes > total_vendas_bois:
    diferenca = total_evolucoes - total_vendas_bois
    print(f"\n   [PROBLEMA] Evolucoes ({total_evolucoes}) > Vendas bois ({total_vendas_bois})")
    print(f"   Diferenca: {diferenca} bois nao foram vendidos")
    print(f"   Isso explica o crescimento do estoque!")

if total_entradas > total_evolucoes + total_vendas_garrotes:
    diferenca = total_entradas - (total_evolucoes + total_vendas_garrotes)
    print(f"\n   [PROBLEMA] Entradas ({total_entradas}) > Evolucoes+Vendas ({total_evolucoes + total_vendas_garrotes})")
    print(f"   Diferenca: {diferenca} garrotes nao foram processados")
    print(f"   Isso explica o crescimento do estoque de garrotes!")

print(f"\n[OK] Verificacao concluida!")




















