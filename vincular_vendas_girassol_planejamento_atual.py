# -*- coding: utf-8 -*-
"""
Script para vincular todas as vendas da Girassol ao planejamento atual
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import Propriedade, MovimentacaoProjetada, PlanejamentoAnual


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
def vincular_vendas():
    """Vincula todas as vendas ao planejamento atual"""
    
    print("=" * 80)
    print("VINCULAR VENDAS GIRASSOL AO PLANEJAMENTO ATUAL")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_atual:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento atual: {planejamento_atual.codigo}")
    
    # Buscar todas as vendas
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA'
    )
    
    print(f"\n[INFO] Total de vendas encontradas: {vendas.count()}")
    
    # Vincular ao planejamento atual
    vendas_atualizadas = vendas.update(planejamento=planejamento_atual)
    
    print(f"[OK] Vendas vinculadas: {vendas_atualizadas}")
    
    # Verificar também evoluções e transferências
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol
    )
    
    movimentacoes_atualizadas = movimentacoes.update(planejamento=planejamento_atual)
    
    print(f"[OK] Total de movimentacoes vinculadas: {movimentacoes_atualizadas}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        vincular_vendas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











