# -*- coding: utf-8 -*-
"""
Script para vincular movimentações de 2022-2024 da Invernada Grande ao planejamento atual
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
def vincular_movimentacoes():
    """Vincula movimentações de 2022-2024 ao planejamento atual"""
    
    print("=" * 80)
    print("VINCULAR MOVIMENTACOES 2022-2024 INVERNADA GRANDE")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar planejamento atual (mais recente)
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_atual:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento atual: {planejamento_atual.codigo}")
    
    # Buscar movimentações de 2022-2024 sem planejamento ou em planejamentos antigos
    movimentacoes_2022_2024 = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        data_movimentacao__year__in=[2022, 2023, 2024]
    )
    
    print(f"\n[INFO] Movimentacoes encontradas (2022-2024): {movimentacoes_2022_2024.count()}")
    
    # Agrupar por ano
    for ano in [2022, 2023, 2024]:
        mov_ano = movimentacoes_2022_2024.filter(data_movimentacao__year=ano)
        print(f"\n[ANO {ano}]")
        print(f"  Total: {mov_ano.count()} movimentacoes")
        
        if mov_ano.exists():
            # Verificar quantas já estão no planejamento atual
            no_planejamento_atual = mov_ano.filter(planejamento=planejamento_atual)
            print(f"  No planejamento atual: {no_planejamento_atual.count()}")
            
            # Vincular as que não estão
            para_vincular = mov_ano.exclude(planejamento=planejamento_atual)
            if para_vincular.exists():
                print(f"  Para vincular: {para_vincular.count()}")
                atualizadas = para_vincular.update(planejamento=planejamento_atual)
                print(f"  [OK] {atualizadas} movimentacoes vinculadas ao planejamento atual")
            else:
                print(f"  [OK] Todas ja estao vinculadas")
        else:
            print(f"  [AVISO] Nenhuma movimentacao encontrada para {ano}")
    
    # Verificar resultado final
    print(f"\n[VERIFICACAO FINAL]")
    mov_final = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        planejamento=planejamento_atual
    )
    
    for ano in [2022, 2023, 2024, 2025]:
        mov_ano = mov_final.filter(data_movimentacao__year=ano)
        if mov_ano.exists():
            print(f"  {ano}: {mov_ano.count()} movimentacoes")
    
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        vincular_movimentacoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























