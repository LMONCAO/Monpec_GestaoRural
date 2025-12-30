# -*- coding: utf-8 -*-
"""
Script para garantir que todas as vendas da Girassol estejam visíveis na projeção
Vincula todas as vendas ao planejamento mais recente
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
def garantir_vendas_visiveis():
    """Garante que todas as vendas estejam visíveis"""
    
    print("=" * 80)
    print("GARANTIR VENDAS VISIVEIS GIRASSOL")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento mais recente
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
    
    # Vincular todas as vendas ao planejamento atual
    vendas_atualizadas = vendas.update(planejamento=planejamento_atual)
    
    print(f"[OK] Vendas vinculadas ao planejamento atual: {vendas_atualizadas}")
    
    # Verificar também todas as movimentações (transferências, evoluções, etc)
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol
    )
    
    movimentacoes_atualizadas = movimentacoes.update(planejamento=planejamento_atual)
    
    print(f"[OK] Total de movimentacoes vinculadas: {movimentacoes_atualizadas}")
    
    # Verificar vendas por ano
    from datetime import date
    anos = [2022, 2023, 2024, 2025, 2026]
    
    print(f"\n[VERIFICACAO POR ANO]")
    for ano in anos:
        vendas_ano = vendas.filter(data_movimentacao__year=ano)
        total = sum(v.quantidade for v in vendas_ano)
        print(f"  {ano}: {vendas_ano.count()} vendas, {total} bois")
    
    print(f"\n[OK] Concluido!")
    print(f"\n[NOTA] Em 2022 nao ha vendas porque:")
    print(f"  - As transferencias chegaram em 2022")
    print(f"  - As evolucoes acontecem 12 meses depois (2023)")
    print(f"  - As vendas acontecem 90 dias apos a evolucao (2023)")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        garantir_vendas_visiveis()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























