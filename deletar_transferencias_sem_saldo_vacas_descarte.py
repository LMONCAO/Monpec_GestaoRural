# -*- coding: utf-8 -*-
"""
Script para deletar TODAS as transferências de Vacas Descarte sem saldo
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho
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


def calcular_saldo_disponivel(fazenda, categoria, data_referencia, planejamento):
    """Calcula saldo disponível até uma data específica"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=fazenda,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Adicionar todas as movimentações até a data de referência
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return saldo


@transaction.atomic
def deletar_transferencias_sem_saldo():
    """Deleta todas as transferências sem saldo"""
    
    print("=" * 80)
    print("DELETAR TRANSFERENCIAS SEM SALDO - VACAS DESCARTE")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar TODOS os planejamentos
    planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano')
    
    print(f"\n[INFO] Planejamentos encontrados: {planejamentos.count()}")
    
    total_deletadas = 0
    
    for planejamento in planejamentos:
        print(f"\n[PLANEJAMENTO] {planejamento.codigo}")
        
        # Buscar todas as transferências de saída
        transferencias = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            planejamento=planejamento
        ).order_by('data_movimentacao')
        
        print(f"  Transferencias encontradas: {transferencias.count()}")
        
        for transferencia in transferencias:
            # Calcular saldo disponível ANTES desta transferência
            saldo_antes = calcular_saldo_disponivel(
                canta_galo, 
                categoria_descarte, 
                transferencia.data_movimentacao - timedelta(days=1),
                planejamento
            )
            
            print(f"  {transferencia.data_movimentacao.strftime('%d/%m/%Y')}: {transferencia.quantidade} vacas - Saldo antes: {saldo_antes}")
            
            if saldo_antes < transferencia.quantidade:
                print(f"    [DELETANDO] Sem saldo suficiente")
                transferencia.delete()
                total_deletadas += 1
            else:
                print(f"    [OK] Saldo suficiente")
    
    print(f"\n[RESUMO]")
    print(f"  Total de transferencias deletadas: {total_deletadas}")
    
    # Verificar estado final
    planejamento_atual = planejamentos.first()
    transferencias_restantes = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_atual
    ).count()
    
    print(f"  Transferencias restantes no planejamento atual: {transferencias_restantes}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        deletar_transferencias_sem_saldo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























