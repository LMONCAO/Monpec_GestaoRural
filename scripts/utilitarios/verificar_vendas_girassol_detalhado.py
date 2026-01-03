# -*- coding: utf-8 -*-
"""
Script para verificar vendas da Girassol em detalhes
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, PlanejamentoAnual
from datetime import date, timedelta

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
planejamento = PlanejamentoAnual.objects.filter(propriedade=girassol).order_by('-data_criacao', '-ano').first()

print("=" * 80)
print("VERIFICAR VENDAS GIRASSOL - DETALHADO")
print("=" * 80)

# Buscar todas as evoluções
evolucoes = MovimentacaoProjetada.objects.filter(
    propriedade=girassol,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    planejamento=planejamento
).order_by('data_movimentacao')

print(f"\n[INFO] Total de evolucoes: {evolucoes.count()}")

problemas = []

for evolucao in evolucoes:
    data_evolucao = evolucao.data_movimentacao
    quantidade_evolucao = evolucao.quantidade
    data_venda_esperada = data_evolucao + timedelta(days=90)
    
    # Buscar vendas correspondentes
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        data_movimentacao__gte=data_venda_esperada - timedelta(days=5),
        data_movimentacao__lte=data_venda_esperada + timedelta(days=5),
        planejamento=planejamento
    )
    
    total_vendido = sum(v.quantidade for v in vendas)
    
    print(f"\n[EVOLUCAO] {data_evolucao.strftime('%d/%m/%Y')}: {quantidade_evolucao} bois")
    print(f"  Venda esperada em: {data_venda_esperada.strftime('%d/%m/%Y')}")
    print(f"  Total vendido: {total_vendido}")
    
    if total_vendido < quantidade_evolucao:
        falta = quantidade_evolucao - total_vendido
        problemas.append({
            'evolucao': evolucao,
            'data_evolucao': data_evolucao,
            'quantidade': quantidade_evolucao,
            'vendido': total_vendido,
            'falta': falta,
            'data_venda_esperada': data_venda_esperada
        })
        print(f"  [PROBLEMA] Faltam {falta} bois para vender!")

if problemas:
    print(f"\n[PROBLEMAS ENCONTRADOS: {len(problemas)}]")
    for prob in problemas:
        print(f"  - {prob['data_evolucao'].strftime('%d/%m/%Y')}: {prob['falta']} bois faltando")
else:
    print(f"\n[OK] Todas as evolucoes tem vendas completas!")
























