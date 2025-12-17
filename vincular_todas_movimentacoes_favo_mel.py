# -*- coding: utf-8 -*-
"""
Script para vincular todas as movimentações do Favo de Mel ao planejamento atual
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
    """Vincula todas as movimentações ao planejamento atual"""
    
    print("=" * 80)
    print("VINCULAR TODAS MOVIMENTACOES FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar planejamento mais recente
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_atual:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento atual: {planejamento_atual.codigo}")
    
    # Buscar TODAS as movimentações (de qualquer planejamento)
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel
    )
    
    print(f"\n[INFO] Total de movimentacoes encontradas: {movimentacoes.count()}")
    
    # Contar por tipo
    tipos = movimentacoes.values_list('tipo_movimentacao', flat=True).distinct()
    for tipo in tipos:
        count = movimentacoes.filter(tipo_movimentacao=tipo).count()
        total = sum(m.quantidade for m in movimentacoes.filter(tipo_movimentacao=tipo))
        print(f"  {tipo}: {count} movimentacoes, {total} animais")
    
    # Vincular todas ao planejamento atual
    movimentacoes_atualizadas = movimentacoes.update(planejamento=planejamento_atual)
    
    print(f"\n[OK] Movimentacoes vinculadas: {movimentacoes_atualizadas}")
    
    # Verificar por ano
    from datetime import date
    anos = [2022, 2023, 2024, 2025, 2026]
    
    print(f"\n[VERIFICACAO POR ANO]")
    for ano in anos:
        movs_ano = movimentacoes.filter(data_movimentacao__year=ano)
        if movs_ano.exists():
            total = sum(m.quantidade for m in movs_ano)
            print(f"  {ano}: {movs_ano.count()} movimentacoes, {total} animais")
    
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











