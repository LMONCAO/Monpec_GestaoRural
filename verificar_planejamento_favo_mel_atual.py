# -*- coding: utf-8 -*-
"""
Script para verificar o planejamento atual do Favo de Mel
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
    """Verifica o planejamento atual do Favo de Mel"""
    
    print("=" * 80)
    print("VERIFICAR PLANEJAMENTO ATUAL FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar TODOS os planejamentos
    planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano')
    
    print(f"\n[TODOS OS PLANEJAMENTOS]")
    for p in planejamentos[:5]:  # Mostrar os 5 mais recentes
        mov_count = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            planejamento=p
        ).count()
        print(f"  {p.codigo}: {p.data_criacao.strftime('%d/%m/%Y %H:%M')} - {mov_count} movimentacoes")
    
    # Buscar planejamento mais recente
    planejamento = planejamentos.first()
    
    print(f"\n[PLANEJAMENTO MAIS RECENTE: {planejamento.codigo}]")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar compras
    compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"  Compras: {compras.count()}")
    
    # Buscar transferências
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao__in=['TRANSFERENCIA_ENTRADA', 'TRANSFERENCIA_SAIDA'],
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"  Transferencias: {transferencias.count()}")
    
    # Total de movimentações
    total = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        planejamento=planejamento
    ).count()
    
    print(f"  Total de movimentacoes: {total}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















