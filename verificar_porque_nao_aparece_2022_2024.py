# -*- coding: utf-8 -*-
"""
Script para verificar por que 2022-2024 não aparecem após nova geração
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
    """Verifica movimentações por ano e planejamento"""
    
    print("=" * 80)
    print("VERIFICAR POR QUE 2022-2024 NAO APARECEM")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar TODAS as movimentações
    todas_movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Total de movimentacoes (todas): {todas_movimentacoes.count()}")
    
    # Agrupar por ano
    movimentacoes_por_ano = defaultdict(list)
    for mov in todas_movimentacoes:
        ano = mov.data_movimentacao.year
        movimentacoes_por_ano[ano].append(mov)
    
    print(f"\n[ANOS COM MOVIMENTACOES]")
    for ano in sorted(movimentacoes_por_ano.keys()):
        movs = movimentacoes_por_ano[ano]
        print(f"  {ano}: {len(movs)} movimentacoes")
        
        # Mostrar planejamentos
        planejamentos = set(m.planejamento.codigo if m.planejamento else 'SEM PLANEJAMENTO' for m in movs)
        print(f"    Planejamentos: {list(planejamentos)}")
    
    # Verificar planejamento mais recente
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if planejamento_atual:
        print(f"\n[PLANEJAMENTO ATUAL: {planejamento_atual.codigo}]")
        mov_planejamento = todas_movimentacoes.filter(planejamento=planejamento_atual)
        print(f"  Total: {mov_planejamento.count()} movimentacoes")
        
        mov_por_ano = defaultdict(list)
        for mov in mov_planejamento:
            ano = mov.data_movimentacao.year
            mov_por_ano[ano].append(mov)
        
        for ano in sorted(mov_por_ano.keys()):
            print(f"  {ano}: {len(mov_por_ano[ano])} movimentacoes")
    
    # Verificar se a função gerar_resumo_projecao_por_ano está sendo chamada corretamente
    print(f"\n[PROBLEMA IDENTIFICADO]")
    print(f"  A funcao gerar_resumo_projecao_por_ano so processa anos que TEM movimentacoes")
    print(f"  Se nao houver movimentacoes em 2022-2024, esses anos nao aparecerao")
    print(f"  Solucao: Criar movimentacoes para todos os anos OU modificar a funcao")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











