# -*- coding: utf-8 -*-
"""
Script para verificar movimentações por planejamento na Invernada Grande
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db.models import Count

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar_movimentacoes():
    """Verifica movimentações por planejamento"""
    
    print("=" * 80)
    print("VERIFICAR MOVIMENTACOES POR PLANEJAMENTO - INVERNADA GRANDE")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar planejamento mais recente
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_atual:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento atual: {planejamento_atual.codigo}")
    
    # Buscar TODAS as movimentações (com e sem planejamento)
    todas_movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada
    )
    
    print(f"\n[INFO] Total de movimentacoes (todas): {todas_movimentacoes.count()}")
    
    # Agrupar por ano
    for ano in [2022, 2023, 2024, 2025]:
        mov_ano = todas_movimentacoes.filter(data_movimentacao__year=ano)
        print(f"\n[ANO {ano}]")
        print(f"  Total: {mov_ano.count()} movimentacoes")
        
        if mov_ano.exists():
            # Agrupar por planejamento
            por_planejamento = mov_ano.values('planejamento__codigo').annotate(
                total=Count('id')
            ).order_by('planejamento__codigo')
            
            for item in por_planejamento:
                codigo = item['planejamento__codigo'] or 'SEM PLANEJAMENTO'
                total = item['total']
                print(f"    {codigo}: {total} movimentacoes")
            
            # Tipos de movimentação
            tipos = mov_ano.values_list('tipo_movimentacao', flat=True).distinct()
            print(f"    Tipos: {list(tipos)}")
            
            # Movimentações sem planejamento
            sem_planejamento = mov_ano.filter(planejamento__isnull=True)
            if sem_planejamento.exists():
                print(f"    [AVISO] {sem_planejamento.count()} movimentacoes SEM planejamento")
        else:
            print(f"  [AVISO] Nenhuma movimentacao encontrada para {ano}")
    
    # Verificar movimentações do planejamento atual
    print(f"\n[PLANEJAMENTO ATUAL: {planejamento_atual.codigo}]")
    mov_planejamento = todas_movimentacoes.filter(planejamento=planejamento_atual)
    print(f"  Total: {mov_planejamento.count()} movimentacoes")
    
    for ano in [2022, 2023, 2024, 2025]:
        mov_ano = mov_planejamento.filter(data_movimentacao__year=ano)
        if mov_ano.exists():
            print(f"  {ano}: {mov_ano.count()} movimentacoes")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar_movimentacoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










