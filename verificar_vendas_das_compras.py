# -*- coding: utf-8 -*-
"""
Script para verificar vendas das compras específicas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import timedelta
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica vendas das compras específicas"""
    
    print("=" * 80)
    print("VERIFICAR VENDAS DAS COMPRAS")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamentos
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # Buscar compras
    compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"\n[COMPRAS E SUAS VENDAS]")
    
    for compra in compras:
        data_compra = compra.data_movimentacao
        quantidade_compra = compra.quantidade
        
        # Data esperada da primeira venda: 90 dias após compra
        data_primeira_venda_esperada = data_compra + timedelta(days=90)
        
        print(f"\n  Compra: {data_compra.strftime('%d/%m/%Y')} - {quantidade_compra} garrotes")
        print(f"    Primeira venda esperada: {data_primeira_venda_esperada.strftime('%d/%m/%Y')}")
        
        # Buscar vendas relacionadas (após 90 dias da compra)
        vendas_relacionadas = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_boi,
            tipo_movimentacao='VENDA',
            planejamento=planejamento_girassol,
            data_movimentacao__gte=data_primeira_venda_esperada - timedelta(days=10),
            data_movimentacao__lte=data_primeira_venda_esperada + timedelta(days=365)  # Até 1 ano depois
        ).order_by('data_movimentacao')
        
        print(f"    Vendas encontradas: {vendas_relacionadas.count()}")
        
        total_vendido = 0
        for venda in vendas_relacionadas:
            print(f"      {venda.data_movimentacao.strftime('%d/%m/%Y')}: {venda.quantidade} bois")
            total_vendido += venda.quantidade
        
        print(f"    Total vendido: {total_vendido} de {quantidade_compra}")
        
        if total_vendido < quantidade_compra:
            print(f"    ⚠️ FALTAM {quantidade_compra - total_vendido} bois para vender!")
        elif total_vendido == quantidade_compra:
            print(f"    ✅ Todos os animais foram vendidos!")
        else:
            print(f"    ⚠️ Vendeu mais do que recebeu ({total_vendido} > {quantidade_compra})")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










