# -*- coding: utf-8 -*-
"""
Script para vincular TODAS as correções da Fazenda Girassol ao planejamento mais recente.
Inclui evoluções, vendas e transferências.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada
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
def vincular_todas_correcoes_girassol():
    """Vincula todas as correções da Fazenda Girassol ao planejamento mais recente"""
    
    try:
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        print(f"[OK] Propriedade encontrada: {girassol.nome_propriedade}")
    except:
        print("[ERRO] Propriedade 'Girassol' nao encontrada")
        return
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[OK] Planejamento encontrado: {planejamento.codigo} (ano {planejamento.ano})")
    
    # Buscar TODAS as movimentações de 2022 e 2023 que são correções
    # Inclui evoluções, vendas ajustadas e transferências
    movimentacoes_sem_planejamento = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento__isnull=True,
        data_movimentacao__year__in=[2022, 2023, 2024]
    )
    
    total = movimentacoes_sem_planejamento.count()
    print(f"\n[INFO] Movimentacoes sem planejamento encontradas: {total}")
    
    if total > 0:
        # Agrupar por tipo
        tipos = {}
        for mov in movimentacoes_sem_planejamento:
            tipo = mov.tipo_movimentacao
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        print(f"   Detalhamento por tipo:")
        for tipo, quantidade in tipos.items():
            print(f"      - {tipo}: {quantidade}")
        
        # Vincular todas ao planejamento
        movimentacoes_sem_planejamento.update(planejamento=planejamento)
        print(f"\n[OK] {total} movimentacoes vinculadas ao planejamento {planejamento.codigo}")
    else:
        print("[INFO] Nenhuma movimentacao para vincular")
    
    # Verificar também movimentações que podem estar em outros planejamentos
    movimentacoes_outros_planejamentos = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        planejamento__isnull=False,
        data_movimentacao__year__in=[2022, 2023, 2024]
    ).exclude(planejamento=planejamento)
    
    total_outros = movimentacoes_outros_planejamentos.count()
    if total_outros > 0:
        print(f"\n[INFO] Encontradas {total_outros} movimentacoes em outros planejamentos")
        resposta = input("   Deseja transferir para o planejamento atual? (s/n): ").lower()
        if resposta == 's':
            movimentacoes_outros_planejamentos.update(planejamento=planejamento)
            print(f"[OK] {total_outros} movimentacoes transferidas")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    print("=" * 60)
    print("VINCULAR TODAS AS CORRECOES - GIRASSOL")
    print("=" * 60)
    print()
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        vincular_todas_correcoes_girassol()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










