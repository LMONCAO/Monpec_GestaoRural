# -*- coding: utf-8 -*-
"""
Script para vincular movimentações ao novo planejamento da Invernada Grande
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def aguardar_banco_livre(max_tentativas=30, intervalo=3):
    """Aguarda o banco de dados ficar livre"""
    for tentativa in range(max_tentativas):
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("ROLLBACK")
            return True
        except Exception:
            if tentativa < max_tentativas - 1:
                time.sleep(intervalo)
            else:
                return False
    return False


@transaction.atomic
def vincular_movimentacoes_novo_planejamento():
    """Vincula movimentações ao novo planejamento"""
    
    print("=" * 80)
    print("VINCULAR MOVIMENTACOES AO NOVO PLANEJAMENTO - INVERNADA GRANDE")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar planejamento mais recente
    planejamento_novo = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_novo:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento novo: {planejamento_novo.codigo}")
    
    # Buscar TODAS as movimentações sem planejamento ou em planejamentos antigos
    todas_movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada
    )
    
    print(f"\n[INFO] Total de movimentacoes: {todas_movimentacoes.count()}")
    
    # Agrupar por planejamento
    por_planejamento = {}
    for mov in todas_movimentacoes:
        codigo = mov.planejamento.codigo if mov.planejamento else 'SEM PLANEJAMENTO'
        if codigo not in por_planejamento:
            por_planejamento[codigo] = []
        por_planejamento[codigo].append(mov)
    
    print(f"\n[MOVIMENTACOES POR PLANEJAMENTO]")
    for codigo, movs in por_planejamento.items():
        print(f"  {codigo}: {len(movs)} movimentacoes")
    
    # Vincular todas as movimentações ao planejamento novo
    movimentacoes_para_vincular = todas_movimentacoes.exclude(planejamento=planejamento_novo)
    
    if movimentacoes_para_vincular.exists():
        print(f"\n[PASSO] Vinculando {movimentacoes_para_vincular.count()} movimentacoes ao planejamento novo...")
        atualizadas = movimentacoes_para_vincular.update(planejamento=planejamento_novo)
        print(f"[OK] {atualizadas} movimentacoes vinculadas")
    else:
        print(f"\n[OK] Todas as movimentacoes ja estao vinculadas ao planejamento novo")
    
    # Verificar resultado
    mov_final = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        planejamento=planejamento_novo
    )
    
    print(f"\n[VERIFICACAO FINAL]")
    print(f"  Total de movimentacoes no planejamento novo: {mov_final.count()}")
    
    # Agrupar por ano
    mov_por_ano = {}
    for mov in mov_final:
        ano = mov.data_movimentacao.year
        if ano not in mov_por_ano:
            mov_por_ano[ano] = 0
        mov_por_ano[ano] += 1
    
    for ano in sorted(mov_por_ano.keys()):
        print(f"  {ano}: {mov_por_ano[ano]} movimentacoes")
    
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        vincular_movimentacoes_novo_planejamento()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















