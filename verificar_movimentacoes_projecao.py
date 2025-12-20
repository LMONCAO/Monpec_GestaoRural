# -*- coding: utf-8 -*-
"""
Script para verificar se as movimentações de projeção estão sendo salvas corretamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, PlanejamentoAnual
)

# Buscar propriedade Invernada Grande
try:
    propriedade = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    print(f"Propriedade encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
except Propriedade.DoesNotExist:
    print("ERRO: Propriedade Invernada Grande não encontrada")
    sys.exit(1)

# Buscar planejamento mais recente
planejamento = PlanejamentoAnual.objects.filter(
    propriedade=propriedade
).order_by('-data_criacao', '-ano').first()

if planejamento:
    print(f"\nPlanejamento mais recente: {planejamento.codigo} (ID: {planejamento.id})")
    print(f"Data de criação: {planejamento.data_criacao}")
    print(f"Ano: {planejamento.ano}")
    
    # Buscar movimentações do planejamento
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        planejamento=planejamento
    ).select_related('categoria').order_by('data_movimentacao')
    
    print(f"\nMovimentações encontradas no planejamento: {movimentacoes.count()}")
    
    if movimentacoes.exists():
        print("\nPrimeiras 10 movimentações:")
        for i, mov in enumerate(movimentacoes[:10], 1):
            print(f"  {i}. {mov.data_movimentacao.strftime('%d/%m/%Y')} - {mov.tipo_movimentacao} - {mov.categoria.nome} - {mov.quantidade} cabeças")
    else:
        print("\nNENHUMA MOVIMENTAÇÃO ENCONTRADA NO PLANEJAMENTO!")
        
        # Verificar se há movimentações sem planejamento
        mov_sem_planejamento = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento__isnull=True
        ).count()
        print(f"Movimentações sem planejamento: {mov_sem_planejamento}")
        
        # Verificar todas as movimentações da propriedade
        todas_mov = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade
        ).count()
        print(f"Total de movimentações da propriedade: {todas_mov}")
        
        if todas_mov > 0:
            print("\nÚltimas 5 movimentações (de qualquer planejamento):")
            ultimas = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade
            ).select_related('categoria', 'planejamento').order_by('-data_movimentacao')[:5]
            for mov in ultimas:
                planejamento_info = mov.planejamento.codigo if mov.planejamento else "SEM PLANEJAMENTO"
                print(f"  - {mov.data_movimentacao.strftime('%d/%m/%Y')} - {mov.tipo_movimentacao} - {mov.categoria.nome} - {mov.quantidade} - Planejamento: {planejamento_info}")
else:
    print("\nERRO: Nenhum planejamento encontrado para a propriedade")
























