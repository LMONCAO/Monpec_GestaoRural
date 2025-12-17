# -*- coding: utf-8 -*-
"""
Script para verificação final completa de todas as fazendas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, InventarioRebanho

print("=" * 80)
print("VERIFICACAO FINAL COMPLETA - TODAS AS FAZENDAS")
print("=" * 80)

# 1. Verificar saldos negativos
print("\n[1] VERIFICACAO DE SALDOS NEGATIVOS")
propriedades = Propriedade.objects.all()
categorias = CategoriaAnimal.objects.filter(ativo=True)
anos = [2022, 2023, 2024, 2025, 2026]

saldos_negativos = []
for propriedade in propriedades:
    for categoria in categorias:
        for ano in anos:
            # Calcular saldo final
            inventario = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario__lte=date(ano, 12, 31)
            ).order_by('-data_inventario').first()
            
            saldo = inventario.quantidade if inventario else 0
            
            movimentacoes = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                categoria=categoria,
                data_movimentacao__lte=date(ano, 12, 31)
            ).order_by('data_movimentacao')
            
            for mov in movimentacoes:
                if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
                    saldo += mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
                    saldo -= mov.quantidade
            
            if saldo < 0:
                saldos_negativos.append({
                    'propriedade': propriedade.nome_propriedade,
                    'categoria': categoria.nome,
                    'ano': ano,
                    'saldo': saldo
                })

if saldos_negativos:
    print(f"  [ERRO] {len(saldos_negativos)} saldos negativos encontrados")
    for s in saldos_negativos:
        print(f"    - {s['propriedade']}: {s['categoria']} em {s['ano']} = {s['saldo']}")
else:
    print(f"  [OK] Nenhum saldo negativo encontrado!")

# 2. Verificar balanceamento de transferências
print("\n[2] VERIFICACAO DE BALANCEAMENTO DE TRANSFERENCIAS")

# Canta Galo -> Invernada Grande
canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

saidas_canta_descarte = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_descarte
)
entradas_invernada_descarte = MovimentacaoProjetada.objects.filter(
    propriedade=invernada,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_descarte
)

total_saidas_descarte = sum(s.quantidade for s in saidas_canta_descarte)
total_entradas_descarte = sum(e.quantidade for e in entradas_invernada_descarte)

print(f"  Canta Galo -> Invernada Grande (Vacas Descarte):")
print(f"    Saidas: {total_saidas_descarte}, Entradas: {total_entradas_descarte}")
if total_saidas_descarte == total_entradas_descarte:
    print(f"    [OK] Balanceado!")
else:
    print(f"    [ERRO] Desbalanceado: {total_saidas_descarte - total_entradas_descarte}")

# Canta Galo -> Favo de Mel
favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

saidas_canta_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
)
entradas_favo_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
)

total_saidas_garrote = sum(s.quantidade for s in saidas_canta_garrote)
total_entradas_garrote = sum(e.quantidade for e in entradas_favo_garrote)

print(f"\n  Canta Galo -> Favo de Mel (Garrotes):")
print(f"    Saidas: {total_saidas_garrote}, Entradas: {total_entradas_garrote}")
if total_saidas_garrote == total_entradas_garrote:
    print(f"    [OK] Balanceado!")
else:
    print(f"    [ERRO] Desbalanceado: {total_saidas_garrote - total_entradas_garrote}")

# Favo de Mel -> Girassol
girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')

saidas_favo_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria_garrote
)
entradas_girassol_garrote = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
)

total_saidas_favo = sum(s.quantidade for s in saidas_favo_garrote)
total_entradas_girassol = sum(e.quantidade for e in entradas_girassol_garrote)

print(f"\n  Favo de Mel -> Girassol (Garrotes):")
print(f"    Saidas: {total_saidas_favo}, Entradas: {total_entradas_girassol}")
if total_saidas_favo == total_entradas_girassol:
    print(f"    [OK] Balanceado!")
else:
    print(f"    [ERRO] Desbalanceado: {total_saidas_favo - total_entradas_girassol}")

# 3. Verificar evoluções e vendas no Girassol
print("\n[3] VERIFICACAO DE EVOLUCOES E VENDAS NO GIRASSOL")

categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')

entradas_garrote_girassol = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria_garrote
)

evolucoes_saida = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='PROMOCAO_SAIDA',
    categoria=categoria_garrote
)

evolucoes_entrada = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    categoria=categoria_boi
)

vendas_boi = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='VENDA',
    categoria=categoria_boi
)

total_entradas_garrote = sum(e.quantidade for e in entradas_garrote_girassol)
total_evolucoes_saida = sum(e.quantidade for e in evolucoes_saida)
total_evolucoes_entrada = sum(e.quantidade for e in evolucoes_entrada)
total_vendas_boi = sum(v.quantidade for v in vendas_boi)

print(f"  Entradas de Garrotes: {total_entradas_garrote}")
print(f"  Evolucoes SAIDA (Garrote): {total_evolucoes_saida}")
print(f"  Evolucoes ENTRADA (Boi): {total_evolucoes_entrada}")
print(f"  Vendas de Bois: {total_vendas_boi}")

if total_entradas_garrote == total_evolucoes_saida == total_evolucoes_entrada:
    print(f"  [OK] Evolucoes balanceadas!")
else:
    print(f"  [AVISO] Evolucoes desbalanceadas")

if total_evolucoes_entrada == total_vendas_boi:
    print(f"  [OK] Vendas balanceadas com evolucoes!")
else:
    print(f"  [AVISO] Vendas desbalanceadas: {total_evolucoes_entrada - total_vendas_boi}")

print(f"\n[OK] Verificacao final concluida!")

