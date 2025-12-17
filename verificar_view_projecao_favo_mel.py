# -*- coding: utf-8 -*-
"""
Script para verificar como a view está buscando as movimentações
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
    """Verifica como a view busca movimentações"""
    
    print("=" * 80)
    print("VERIFICAR VIEW PROJECAO FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar planejamento mais recente (como a view faz)
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento mais recente: {planejamento.codigo}")
    print(f"  Data criacao: {planejamento.data_criacao}")
    print(f"  Ano: {planejamento.ano}")
    
    # Buscar movimentações como a view faz
    # Verificar se a view filtra por planejamento ou não
    movimentacoes_sem_filtro = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel
    )
    
    movimentacoes_com_filtro = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        planejamento=planejamento
    )
    
    print(f"\n[MOVIMENTACOES SEM FILTRO DE PLANEJAMENTO]")
    print(f"  Total: {movimentacoes_sem_filtro.count()}")
    
    print(f"\n[MOVIMENTACOES COM FILTRO DE PLANEJAMENTO ({planejamento.codigo})]")
    print(f"  Total: {movimentacoes_com_filtro.count()}")
    
    # Agrupar por ano
    from collections import defaultdict
    mov_por_ano = defaultdict(list)
    for mov in movimentacoes_com_filtro:
        ano = mov.data_movimentacao.year
        mov_por_ano[ano].append(mov)
    
    print(f"\n[ANOS COM MOVIMENTACOES (COM FILTRO)]")
    for ano in sorted(mov_por_ano.keys()):
        movs = mov_por_ano[ano]
        print(f"  {ano}: {len(movs)} movimentacoes")
        
        # Mostrar detalhes
        tipos = defaultdict(int)
        for m in movs:
            tipos[m.tipo_movimentacao] += 1
        print(f"    Tipos: {dict(tipos)}")
    
    # Verificar se há movimentações sem planejamento
    mov_sem_planejamento = movimentacoes_sem_filtro.filter(planejamento__isnull=True)
    print(f"\n[MOVIMENTACOES SEM PLANEJAMENTO]")
    print(f"  Total: {mov_sem_planejamento.count()}")
    
    # Verificar se há movimentações com planejamento diferente
    outros_planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).exclude(id=planejamento.id).order_by('-data_criacao', '-ano')
    
    print(f"\n[OUTROS PLANEJAMENTOS]")
    for p in outros_planejamentos[:5]:  # Mostrar apenas os 5 mais recentes
        mov_p = movimentacoes_sem_filtro.filter(planejamento=p)
        print(f"  {p.codigo}: {mov_p.count()} movimentacoes")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











