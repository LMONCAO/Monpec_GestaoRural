# -*- coding: utf-8 -*-
"""
Script para verificar saldo de bois em 2025
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual, InventarioRebanho
from datetime import date

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
planejamento = PlanejamentoAnual.objects.filter(propriedade=girassol).order_by('-data_criacao', '-ano').first()

print("=" * 80)
print("VERIFICAR SALDO BOIS 2025")
print("=" * 80)

# Inventário inicial
inventario = InventarioRebanho.objects.filter(
    propriedade=girassol,
    categoria=categoria_boi
).order_by('-data_inventario').first()

saldo = inventario.quantidade if inventario else 0
print(f"\nInventario inicial: {saldo}")

# Movimentações de 2025
movimentacoes_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    categoria=categoria_boi,
    data_movimentacao__year=2025,
    planejamento=planejamento
).order_by('data_movimentacao')

print(f"\nMovimentacoes em 2025:")
for mov in movimentacoes_2025:
    if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA']:
        saldo += mov.quantidade
        sinal = '+'
    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
        saldo -= mov.quantidade
        sinal = '-'
    else:
        sinal = '?'
    
    print(f"  {sinal} {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.quantidade} - {mov.tipo_movimentacao} (saldo: {saldo})")

print(f"\nSaldo final 2025: {saldo}")

# Verificar evoluções e vendas
evolucoes_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    categoria=categoria_boi,
    data_movimentacao__year=2025,
    planejamento=planejamento
)

vendas_2025 = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='VENDA',
    categoria=categoria_boi,
    data_movimentacao__year=2025,
    planejamento=planejamento
)

total_evolucoes = sum(e.quantidade for e in evolucoes_2025)
total_vendas = sum(v.quantidade for v in vendas_2025)

print(f"\nTotal evolucoes 2025: {total_evolucoes}")
print(f"Total vendas 2025: {total_vendas}")
print(f"Diferenca: {total_evolucoes - total_vendas}")
























