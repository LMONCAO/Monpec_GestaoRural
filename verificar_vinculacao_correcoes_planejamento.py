# -*- coding: utf-8 -*-
"""
Script para verificar se todas as correções estão vinculadas ao planejamento atual
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

print("=" * 80)
print("VERIFICAR VINCULACAO DAS CORRECOES AO PLANEJAMENTO")
print("=" * 80)

propriedades = Propriedade.objects.all().order_by('nome_propriedade')

for propriedade in propriedades:
    print(f"\n{'='*80}")
    print(f"FAZENDA: {propriedade.nome_propriedade}")
    print(f"{'='*80}")
    
    # Buscar planejamento mais recente
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=propriedade
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_atual:
        print(f"  [AVISO] Nenhum planejamento encontrado")
        continue
    
    print(f"  Planejamento atual: {planejamento_atual.codigo} (ano {planejamento_atual.ano})")
    
    # Verificar movimentações sem planejamento ou com planejamento diferente
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade
    )
    
    sem_planejamento = movimentacoes.filter(planejamento__isnull=True).count()
    com_planejamento_diferente = movimentacoes.exclude(
        planejamento=planejamento_atual
    ).exclude(planejamento__isnull=True).count()
    com_planejamento_correto = movimentacoes.filter(planejamento=planejamento_atual).count()
    
    print(f"  Movimentacoes sem planejamento: {sem_planejamento}")
    print(f"  Movimentacoes com planejamento diferente: {com_planejamento_diferente}")
    print(f"  Movimentacoes com planejamento correto: {com_planejamento_correto}")
    
    if sem_planejamento > 0 or com_planejamento_diferente > 0:
        print(f"  [AVISO] Ha movimentacoes que precisam ser vinculadas ao planejamento atual")

print(f"\n[OK] Verificacao concluida!")




















