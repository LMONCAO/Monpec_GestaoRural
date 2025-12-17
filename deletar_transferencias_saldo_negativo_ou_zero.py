# -*- coding: utf-8 -*-
"""
Script para deletar TODAS as transferências que resultam em saldo negativo ou zero
REGRA SIMPLES: Se saldo antes da transferência <= 0, deleta a transferência
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


def calcular_saldo_antes_transferencia(fazenda, categoria, data_transferencia, planejamento):
    """Calcula saldo disponível ANTES de uma transferência específica"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=fazenda,
        categoria=categoria,
        data_inventario__lt=data_transferencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Adicionar todas as movimentações ANTES desta transferência
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        categoria=categoria,
        data_movimentacao__lt=data_transferencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    # Adicionar promoções do mesmo dia ANTES da transferência (verificar por ID)
    promocoes_mesmo_dia = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        categoria=categoria,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        data_movimentacao=data_transferencia,
        planejamento=planejamento
    )
    
    # Buscar ID da transferência
    transferencia_obj = MovimentacaoProjetada.objects.filter(
        propriedade=fazenda,
        categoria=categoria,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        data_movimentacao=data_transferencia,
        planejamento=planejamento
    ).order_by('id').first()
    
    if transferencia_obj:
        # Adicionar apenas promoções criadas antes desta transferência (ID menor)
        promocoes_antes = promocoes_mesmo_dia.filter(id__lt=transferencia_obj.id)
        saldo += sum(p.quantidade for p in promocoes_antes)
    
    return saldo


@transaction.atomic
def deletar_transferencias_saldo_negativo_ou_zero():
    """Deleta TODAS as transferências quando saldo <= 0"""
    
    print("=" * 80)
    print("DELETAR TRANSFERENCIAS COM SALDO NEGATIVO OU ZERO")
    print("REGRA SIMPLES: Se saldo antes da transferencia <= 0, deleta")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar TODOS os planejamentos
    planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano')
    
    print(f"\n[INFO] Total de planejamentos: {planejamentos.count()}")
    
    total_deletadas = 0
    
    for planejamento in planejamentos:
        print(f"\n[PLANEJAMENTO] {planejamento.codigo}")
        
        # Buscar TODAS as transferências de saída
        transferencias = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            planejamento=planejamento
        ).order_by('data_movimentacao', 'id')
        
        print(f"  Transferencias encontradas: {transferencias.count()}")
        
        for transferencia in transferencias:
            # Calcular saldo disponível ANTES desta transferência
            saldo_antes = calcular_saldo_antes_transferencia(
                canta_galo, 
                categoria_descarte, 
                transferencia.data_movimentacao,
                planejamento
            )
            
            print(f"    {transferencia.data_movimentacao.strftime('%d/%m/%Y')}: {transferencia.quantidade} vacas - Saldo antes: {saldo_antes}")
            
            # REGRA SIMPLES: Se saldo <= 0, deleta
            if saldo_antes <= 0:
                print(f"      [DELETANDO] Saldo negativo ou zero (saldo: {saldo_antes})")
                transferencia.delete()
                total_deletadas += 1
            elif saldo_antes < transferencia.quantidade:
                print(f"      [DELETANDO] Saldo insuficiente (saldo: {saldo_antes}, precisa: {transferencia.quantidade})")
                transferencia.delete()
                total_deletadas += 1
            else:
                print(f"      [OK] Saldo suficiente")
    
    print(f"\n" + "=" * 80)
    print(f"[RESUMO FINAL]")
    print(f"  Total de transferencias deletadas: {total_deletadas}")
    
    # Verificar estado final
    planejamento_atual = planejamentos.first()
    transferencias_restantes = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_atual
    ).order_by('data_movimentacao', 'id')
    
    print(f"  Transferencias restantes no planejamento atual ({planejamento_atual.codigo}): {transferencias_restantes.count()}")
    
    if transferencias_restantes.exists():
        print(f"\n  [TRANSFERENCIAS RESTANTES]")
        for t in transferencias_restantes:
            saldo_antes = calcular_saldo_antes_transferencia(
                canta_galo, 
                categoria_descarte, 
                t.data_movimentacao,
                planejamento_atual
            )
            status = "OK" if saldo_antes > 0 and saldo_antes >= t.quantidade else "PROBLEMA"
            print(f"    {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} vacas (saldo antes: {saldo_antes}) [{status}]")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        deletar_transferencias_saldo_negativo_ou_zero()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











