# -*- coding: utf-8 -*-
"""
Script para verificar a projeção da Girassol
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
    """Verifica a projeção da Girassol"""
    
    print("=" * 80)
    print("VERIFICAR PROJECAO GIRASSOL")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    print(f"  Data criacao: {planejamento.data_criacao}")
    
    # Buscar TODAS as movimentações
    todas_movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol
    )
    
    print(f"\n[INFO] Total de movimentacoes (todas): {todas_movimentacoes.count()}")
    
    # Verificar movimentações do planejamento atual
    mov_planejamento = todas_movimentacoes.filter(planejamento=planejamento)
    print(f"\n[PLANEJAMENTO ATUAL: {planejamento.codigo}]")
    print(f"  Total: {mov_planejamento.count()} movimentacoes")
    
    # Agrupar por ano
    mov_por_ano = defaultdict(list)
    for mov in mov_planejamento:
        ano = mov.data_movimentacao.year
        mov_por_ano[ano].append(mov)
    
    print(f"\n[ANOS COM MOVIMENTACOES]")
    for ano in sorted(mov_por_ano.keys()):
        movs = mov_por_ano[ano]
        print(f"  {ano}: {len(movs)} movimentacoes")
        
        # Mostrar tipos
        tipos = defaultdict(int)
        for m in movs:
            tipos[m.tipo_movimentacao] += 1
        print(f"    Tipos: {dict(tipos)}")
    
    # Verificar entradas
    entradas = mov_planejamento.filter(tipo_movimentacao='TRANSFERENCIA_ENTRADA')
    print(f"\n[ENTRADAS]")
    print(f"  Total: {entradas.count()}")
    for e in entradas[:5]:
        print(f"    {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} {e.categoria.nome}")
    
    # Verificar vendas
    vendas = mov_planejamento.filter(tipo_movimentacao='VENDA')
    print(f"\n[VENDAS]")
    print(f"  Total: {vendas.count()}")
    for v in vendas[:5]:
        print(f"    {v.data_movimentacao.strftime('%d/%m/%Y')}: {v.quantidade} {v.categoria.nome}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























