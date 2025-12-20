# -*- coding: utf-8 -*-
"""
Script para verificar a projeção PROJ-2025-0072 da Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, PlanejamentoAnual, CategoriaAnimal
)


def verificar():
    """Verifica a projeção PROJ-2025-0072"""
    
    print("=" * 80)
    print("VERIFICAR PROJECAO GIRASSOL PROJ-2025-0072")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        codigo='PROJ-2025-0072'
    ).first()
    
    if not planejamento:
        print("\n[ERRO] Planejamento PROJ-2025-0072 não encontrado!")
        return
    
    print(f"\n[INFO] Planejamento encontrado:")
    print(f"  Código: {planejamento.codigo}")
    print(f"  Propriedade: {planejamento.propriedade.nome_propriedade}")
    print(f"  Ano: {planejamento.ano}")
    print(f"  Data criação: {planejamento.data_criacao}")
    
    # Buscar movimentações
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento=planejamento
    )
    
    print(f"\n[MOVIMENTACOES]")
    print(f"  Total: {movimentacoes.count()}")
    
    # Agrupar por tipo
    tipos = {}
    for mov in movimentacoes:
        tipo = mov.tipo_movimentacao
        if tipo not in tipos:
            tipos[tipo] = 0
        tipos[tipo] += 1
    
    print(f"\n[TIPOS DE MOVIMENTACOES]")
    for tipo, count in sorted(tipos.items()):
        print(f"  {tipo}: {count}")
    
    # Verificar se há movimentações
    if movimentacoes.count() == 0:
        print("\n[AVISO] Nenhuma movimentação encontrada para esta projeção!")
        print("  Isso explica por que a projeção não aparece na interface.")
    
    # Verificar planejamentos mais recentes
    planejamentos_recentes = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano')[:5]
    
    print(f"\n[PLANEJAMENTOS MAIS RECENTES DA GIRASSOL]")
    for p in planejamentos_recentes:
        mov_count = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            planejamento=p
        ).count()
        print(f"  {p.codigo}: {p.data_criacao.strftime('%d/%m/%Y %H:%M')} - {mov_count} movimentacoes")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























