# -*- coding: utf-8 -*-
"""
Script para verificar projeções da Invernada Grande
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, PlanejamentoAnual
from datetime import date

invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')

print("=" * 80)
print("VERIFICAR PROJECOES INVERNADA GRANDE")
print("=" * 80)

# Verificar planejamentos
planejamentos = PlanejamentoAnual.objects.filter(propriedade=invernada).order_by('ano')
print(f"\n[INFO] Planejamentos encontrados: {planejamentos.count()}")
for p in planejamentos:
    print(f"  - {p.codigo} (ano {p.ano})")

# Verificar movimentações por ano
anos = [2022, 2023, 2024, 2025]
for ano in anos:
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        data_movimentacao__year=ano
    )
    print(f"\n[ANO {ano}]")
    print(f"  Movimentacoes: {movimentacoes.count()}")
    if movimentacoes.exists():
        tipos = movimentacoes.values_list('tipo_movimentacao', flat=True).distinct()
        for tipo in tipos:
            qtd = movimentacoes.filter(tipo_movimentacao=tipo).count()
            print(f"    {tipo}: {qtd}")











