# -*- coding: utf-8 -*-
"""
Script para verificar a projeção do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from collections import defaultdict

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica a projeção do Favo de Mel"""
    
    print("=" * 80)
    print("VERIFICAR PROJECAO FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Buscar TODAS as movimentações
    todas_movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel
    )
    
    print(f"\n[INFO] Total de movimentacoes (todas): {todas_movimentacoes.count()}")
    
    # Agrupar por ano
    mov_por_ano = defaultdict(list)
    for mov in todas_movimentacoes:
        ano = mov.data_movimentacao.year
        mov_por_ano[ano].append(mov)
    
    print(f"\n[ANOS COM MOVIMENTACOES]")
    for ano in sorted(mov_por_ano.keys()):
        movs = mov_por_ano[ano]
        print(f"  {ano}: {len(movs)} movimentacoes")
        
        # Mostrar tipos
        tipos = set(m.tipo_movimentacao for m in movs)
        print(f"    Tipos: {list(tipos)}")
    
    # Verificar movimentações do planejamento atual
    mov_planejamento = todas_movimentacoes.filter(planejamento=planejamento)
    print(f"\n[PLANEJAMENTO ATUAL: {planejamento.codigo}]")
    print(f"  Total: {mov_planejamento.count()} movimentacoes")
    
    for ano in sorted(set(m.data_movimentacao.year for m in mov_planejamento)):
        mov_ano = mov_planejamento.filter(data_movimentacao__year=ano)
        print(f"  {ano}: {len(mov_ano)} movimentacoes")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















