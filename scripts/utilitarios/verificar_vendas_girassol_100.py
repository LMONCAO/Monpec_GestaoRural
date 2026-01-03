# -*- coding: utf-8 -*-
"""
Script para verificar vendas de 100 em 100 na Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from collections import defaultdict
from datetime import timedelta
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica vendas de 100 em 100 na Girassol"""
    
    print("=" * 80)
    print("VERIFICAR VENDAS GIRASSOL (100 EM 100)")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Buscar categoria
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # Buscar vendas
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_boi,
        tipo_movimentacao='VENDA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[VENDAS DE BOIS GORDOS]")
    print(f"  Total: {vendas.count()}")
    
    # Agrupar por ano
    vendas_por_ano = defaultdict(list)
    for venda in vendas:
        ano = venda.data_movimentacao.year
        vendas_por_ano[ano].append(venda)
    
    total_vendido = 0
    for ano in sorted(vendas_por_ano.keys()):
        vendas_ano = vendas_por_ano[ano]
        print(f"\n  [{ano}]")
        print(f"    Total de vendas: {len(vendas_ano)}")
        
        for venda in vendas_ano:
            print(f"      {venda.data_movimentacao.strftime('%d/%m/%Y')}: {venda.quantidade} bois")
            total_vendido += venda.quantidade
        
        total_ano = sum(v.quantidade for v in vendas_ano)
        print(f"    Total do ano: {total_ano} bois")
    
    print(f"\n[RESUMO]")
    print(f"  Total vendido: {total_vendido} bois")
    print(f"  Total de vendas: {vendas.count()}")
    
    # Verificar se há vendas de 100
    vendas_100 = [v for v in vendas if v.quantidade == 100]
    print(f"  Vendas de exatamente 100: {len(vendas_100)}")
    
    # Verificar outras quantidades
    outras_quantidades = defaultdict(int)
    for venda in vendas:
        outras_quantidades[venda.quantidade] += 1
    
    print(f"\n[QUANTIDADES POR VENDA]")
    for qtd, count in sorted(outras_quantidades.items()):
        print(f"  {qtd} bois: {count} vendas")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























