# -*- coding: utf-8 -*-
"""
Script para verificar transferências de entrada na Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual
)


def verificar():
    """Verifica transferências de entrada na Girassol"""
    
    print("=" * 80)
    print("VERIFICAR TRANSFERENCIAS GIRASSOL")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar TODAS as transferências de entrada
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA'
    ).order_by('-data_movimentacao', '-id')
    
    print(f"\n[TRANSFERENCIAS DE ENTRADA]")
    print(f"  Total: {transferencias.count()}")
    
    # Agrupar por planejamento
    por_planejamento = {}
    for trans in transferencias:
        planejamento = trans.planejamento
        if planejamento:
            codigo = planejamento.codigo
            if codigo not in por_planejamento:
                por_planejamento[codigo] = []
            por_planejamento[codigo].append(trans)
        else:
            if 'SEM_PLANEJAMENTO' not in por_planejamento:
                por_planejamento['SEM_PLANEJAMENTO'] = []
            por_planejamento['SEM_PLANEJAMENTO'].append(trans)
    
    print(f"\n[TRANSFERENCIAS POR PLANEJAMENTO]")
    for codigo, trans_list in sorted(por_planejamento.items()):
        print(f"  {codigo}: {len(trans_list)} transferencias")
        total = sum(t.quantidade for t in trans_list)
        print(f"    Total: {total} garrotes")
    
    # Verificar planejamento PROJ-2025-0072
    planejamento_0072 = PlanejamentoAnual.objects.filter(
        codigo='PROJ-2025-0072'
    ).first()
    
    if planejamento_0072:
        transferencias_0072 = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            planejamento=planejamento_0072
        )
        print(f"\n[TRANSFERENCIAS NO PLANEJAMENTO PROJ-2025-0072]")
        print(f"  Total: {transferencias_0072.count()}")
    
    # Verificar se há transferências sem planejamento que podem ser vinculadas
    transferencias_sem_planejamento = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento__isnull=True
    )
    
    print(f"\n[TRANSFERENCIAS SEM PLANEJAMENTO]")
    print(f"  Total: {transferencias_sem_planejamento.count()}")
    
    if transferencias_sem_planejamento.exists():
        print("  [INFO] Há transferências sem planejamento que podem ser vinculadas")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
