# -*- coding: utf-8 -*-
"""
Script para verificar quais anos têm projeções na Invernada Grande
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db.models import Q

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar_anos():
    """Verifica quais anos têm movimentações"""
    
    print("=" * 80)
    print("VERIFICAR ANOS COM PROJECOES - INVERNADA GRANDE")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar todos os planejamentos
    planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano')
    
    print(f"\n[INFO] Total de planejamentos: {planejamentos.count()}")
    
    for planejamento in planejamentos:
        print(f"\n[PLANEJAMENTO] {planejamento.codigo} (Ano: {planejamento.ano})")
        
        # Buscar anos com movimentações
        movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            planejamento=planejamento
        )
        
        anos_com_movimentacoes = movimentacoes.values_list('data_movimentacao__year', flat=True).distinct()
        anos_com_movimentacoes = sorted(set(anos_com_movimentacoes))
        
        print(f"  Anos com movimentacoes: {anos_com_movimentacoes}")
        
        # Contar por tipo
        for ano in [2022, 2023, 2024, 2025]:
            mov_ano = movimentacoes.filter(data_movimentacao__year=ano)
            if mov_ano.exists():
                print(f"  {ano}: {mov_ano.count()} movimentacoes")
                tipos = mov_ano.values_list('tipo_movimentacao', flat=True).distinct()
                print(f"    Tipos: {list(tipos)}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar_anos()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










