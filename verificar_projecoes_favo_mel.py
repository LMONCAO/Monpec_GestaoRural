# -*- coding: utf-8 -*-
"""
Script para verificar projeções do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, PlanejamentoAnual
from datetime import date

favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')

print("=" * 80)
print("VERIFICAR PROJECOES FAVO DE MEL")
print("=" * 80)

# Verificar planejamentos
planejamentos = PlanejamentoAnual.objects.filter(propriedade=favo_mel).order_by('ano')
print(f"\n[INFO] Planejamentos encontrados: {planejamentos.count()}")
for p in planejamentos:
    print(f"  - {p.codigo} (ano {p.ano})")

# Verificar movimentações por ano
anos = [2022, 2023, 2024, 2025, 2026]
for ano in anos:
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        data_movimentacao__year=ano
    )
    print(f"\n[ANO {ano}]")
    print(f"  Movimentacoes: {movimentacoes.count()}")
    if movimentacoes.exists():
        tipos = movimentacoes.values_list('tipo_movimentacao', flat=True).distinct()
        for tipo in tipos:
            qtd = movimentacoes.filter(tipo_movimentacao=tipo).count()
            total = sum(m.quantidade for m in movimentacoes.filter(tipo_movimentacao=tipo))
            print(f"    {tipo}: {qtd} movimentacoes, {total} animais")




















