# -*- coding: utf-8 -*-
"""
Script para verificar vendas na Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal
from datetime import date

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')

print("=" * 80)
print("VERIFICAR VENDAS GIRASSOL")
print("=" * 80)

anos = [2022, 2023, 2024, 2025, 2026]

for ano in anos:
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi,
        data_movimentacao__year=ano
    ).order_by('data_movimentacao')
    
    total_vendido = sum(v.quantidade for v in vendas)
    
    print(f"\n[ANO {ano}]")
    print(f"  Vendas encontradas: {vendas.count()}")
    print(f"  Total vendido: {total_vendido}")
    
    if vendas.exists():
        for venda in vendas:
            print(f"    - {venda.data_movimentacao.strftime('%d/%m/%Y')}: {venda.quantidade} bois")
























