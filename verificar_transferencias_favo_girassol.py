# -*- coding: utf-8 -*-
"""
Script para verificar transferências do Favo de Mel para Girassol
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
    """Verifica transferências do Favo de Mel para Girassol"""
    
    print("=" * 80)
    print("VERIFICAR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamentos mais recentes
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo if planejamento_favo else 'NENHUM'}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo if planejamento_girassol else 'NENHUM'}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Verificar saídas do Favo de Mel
    saidas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"\n[SAIDAS DO FAVO DE MEL]")
    print(f"  Total: {saidas_favo.count()}")
    for s in saidas_favo[:10]:
        print(f"    {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade} (Planejamento: {s.planejamento.codigo if s.planejamento else 'NENHUM'})")
    
    # Verificar entradas na Girassol
    entradas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento_girassol
    ).order_by('data_movimentacao')
    
    print(f"\n[ENTRADAS NA GIRASSOL]")
    print(f"  Total: {entradas_girassol.count()}")
    for e in entradas_girassol[:10]:
        print(f"    {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} (Planejamento: {e.planejamento.codigo if e.planejamento else 'NENHUM'})")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
