# -*- coding: utf-8 -*-
"""
Script para vincular todas as movimentações da Girassol ao planejamento mais recente
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
def vincular_movimentacoes():
    """Vincula todas as movimentações ao planejamento mais recente"""
    
    print("=" * 80)
    print("VINCULAR MOVIMENTACOES GIRASSOL AO PLANEJAMENTO MAIS RECENTE")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento mais recente
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_atual:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento mais recente: {planejamento_atual.codigo}")
    print(f"[INFO] Data de criacao: {planejamento_atual.data_criacao}")
    
    # Buscar todas as movimentações da Girassol
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol
    )
    
    print(f"\n[INFO] Total de movimentacoes encontradas: {movimentacoes.count()}")
    
    # Contar movimentações por tipo
    tipos = movimentacoes.values_list('tipo_movimentacao', flat=True).distinct()
    for tipo in tipos:
        count = movimentacoes.filter(tipo_movimentacao=tipo).count()
        print(f"  {tipo}: {count}")
    
    # Vincular todas as movimentações ao planejamento mais recente
    movimentacoes_atualizadas = movimentacoes.update(planejamento=planejamento_atual)
    
    print(f"\n[OK] Movimentacoes vinculadas: {movimentacoes_atualizadas}")
    
    # Verificar movimentações por ano
    from datetime import date
    anos = [2022, 2023, 2024, 2025, 2026]
    
    print(f"\n[VERIFICACAO POR ANO]")
    for ano in anos:
        movs_ano = movimentacoes.filter(data_movimentacao__year=ano)
        print(f"  {ano}: {movs_ano.count()} movimentacoes")
        
        # Verificar vendas
        vendas = movs_ano.filter(tipo_movimentacao='VENDA')
        if vendas.exists():
            total_vendido = sum(v.quantidade for v in vendas)
            print(f"    Vendas: {vendas.count()} vendas, {total_vendido} bois")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        vincular_movimentacoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










