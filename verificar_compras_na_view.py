# -*- coding: utf-8 -*-
"""
Script para verificar como a view busca as compras
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica como a view busca as compras"""
    
    print("=" * 80)
    print("VERIFICAR COMPRAS NA VIEW")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Simular o que a view faz
    planejamento_recente = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[PLANEJAMENTO MAIS RECENTE: {planejamento_recente.codigo}]")
    
    # Buscar movimentações como a view faz
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        planejamento=planejamento_recente
    ).order_by('data_movimentacao')
    
    print(f"\n[MOVIMENTACOES NO PLANEJAMENTO]")
    print(f"  Total: {movimentacoes.count()}")
    
    # Agrupar por tipo
    tipos = {}
    for mov in movimentacoes:
        tipo = mov.tipo_movimentacao
        if tipo not in tipos:
            tipos[tipo] = 0
        tipos[tipo] += 1
    
    print(f"\n[TIPOS DE MOVIMENTACOES]")
    for tipo, count in sorted(tipos.items()):
        print(f"  {tipo}: {count}")
    
    # Buscar compras especificamente
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    compras = movimentacoes.filter(
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA'
    )
    
    print(f"\n[COMPRAS DE GARROTES]")
    print(f"  Total: {compras.count()}")
    
    for compra in compras:
        print(f"    {compra.data_movimentacao.strftime('%d/%m/%Y')}: {compra.quantidade} garrotes - R$ {compra.valor_total:,.2f if compra.valor_total else 0}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











