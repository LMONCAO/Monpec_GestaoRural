# -*- coding: utf-8 -*-
"""
Script para verificar movimentações da Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, PlanejamentoAnual

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
planejamento = PlanejamentoAnual.objects.filter(propriedade=girassol).order_by('-data_criacao', '-ano').first()

print("=" * 80)
print("VERIFICAR MOVIMENTACOES GIRASSOL")
print("=" * 80)

print(f"\nPlanejamento: {planejamento.codigo}")

movimentacoes = MovimentacaoProjetada.objects.filter(propriedade=girassol, planejamento=planejamento)

print(f"Total de movimentacoes: {movimentacoes.count()}")

print(f"\nPor tipo:")
print(f"  TRANSFERENCIA_ENTRADA: {movimentacoes.filter(tipo_movimentacao='TRANSFERENCIA_ENTRADA').count()}")
print(f"  PROMOCAO_ENTRADA: {movimentacoes.filter(tipo_movimentacao='PROMOCAO_ENTRADA').count()}")
print(f"  PROMOCAO_SAIDA: {movimentacoes.filter(tipo_movimentacao='PROMOCAO_SAIDA').count()}")
print(f"  VENDA: {movimentacoes.filter(tipo_movimentacao='VENDA').count()}")

print(f"\nPor ano:")
from datetime import date
anos = [2022, 2023, 2024, 2025, 2026]
for ano in anos:
    movs_ano = movimentacoes.filter(data_movimentacao__year=ano)
    if movs_ano.exists():
        print(f"  {ano}: {movs_ano.count()} movimentacoes")
        vendas = movs_ano.filter(tipo_movimentacao='VENDA')
        if vendas.exists():
            total = sum(v.quantidade for v in vendas)
            print(f"    Vendas: {vendas.count()} vendas, {total} bois")










