# -*- coding: utf-8 -*-
"""
Script para copiar todas as movimentações da Girassol para o planejamento mais recente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import Propriedade, MovimentacaoProjetada, PlanejamentoAnual, VendaProjetada


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
def copiar_movimentacoes():
    """Copia todas as movimentações para o planejamento mais recente"""
    
    print("=" * 80)
    print("COPIAR MOVIMENTACOES GIRASSOL PARA PLANEJAMENTO NOVO")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento mais recente
    planejamento_novo = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_novo:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento novo: {planejamento_novo.codigo}")
    
    # Buscar todas as movimentações da Girassol (de qualquer planejamento)
    movimentacoes_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol
    ).exclude(planejamento=planejamento_novo)
    
    print(f"\n[INFO] Movimentacoes existentes (outros planejamentos): {movimentacoes_existentes.count()}")
    
    if movimentacoes_existentes.count() == 0:
        print("[AVISO] Nenhuma movimentacao existente encontrada")
        return
    
    # Verificar movimentações já vinculadas ao novo planejamento
    movimentacoes_ja_vinculadas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento=planejamento_novo
    )
    
    print(f"[INFO] Movimentacoes ja vinculadas ao novo planejamento: {movimentacoes_ja_vinculadas.count()}")
    
    # Opção 1: Vincular movimentações existentes ao novo planejamento (mais rápido)
    print(f"\n[OPCAO 1] Vinculando movimentacoes existentes ao novo planejamento...")
    movimentacoes_atualizadas = movimentacoes_existentes.update(planejamento=planejamento_novo)
    
    print(f"[OK] Movimentacoes vinculadas: {movimentacoes_atualizadas}")
    
    # Verificar vendas e vincular também
    vendas_existentes = VendaProjetada.objects.filter(
        movimentacao_projetada__propriedade=girassol
    ).exclude(movimentacao_projetada__planejamento=planejamento_novo)
    
    print(f"[INFO] Vendas existentes (outros planejamentos): {vendas_existentes.count()}")
    
    # As vendas serão automaticamente vinculadas quando as movimentações forem vinculadas
    
    # Verificar resultado final
    movimentacoes_finais = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento=planejamento_novo
    )
    
    print(f"\n[RESULTADO FINAL]")
    print(f"  Total de movimentacoes no novo planejamento: {movimentacoes_finais.count()}")
    
    # Contar por tipo
    tipos = movimentacoes_finais.values_list('tipo_movimentacao', flat=True).distinct()
    for tipo in tipos:
        count = movimentacoes_finais.filter(tipo_movimentacao=tipo).count()
        print(f"    {tipo}: {count}")
    
    # Verificar por ano
    from datetime import date
    anos = [2022, 2023, 2024, 2025, 2026]
    
    print(f"\n[VERIFICACAO POR ANO]")
    for ano in anos:
        movs_ano = movimentacoes_finais.filter(data_movimentacao__year=ano)
        if movs_ano.exists():
            print(f"  {ano}: {movs_ano.count()} movimentacoes")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        copiar_movimentacoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











