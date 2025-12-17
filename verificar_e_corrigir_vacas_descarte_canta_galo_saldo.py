# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir Vacas Descarte na Canta Galo
Garantindo que transferências só ocorram se houver saldo disponível
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
def verificar_e_corrigir():
    """Verifica e corrige transferências de Vacas Descarte"""
    
    print("=" * 80)
    print("VERIFICAR E CORRIGIR VACAS DESCARTE CANTA GALO")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento: {planejamento.codigo}")
    
    # Buscar todas as transferências de saída de Vacas Descarte
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias encontradas: {transferencias.count()}")
    
    transferencias_corrigidas = 0
    transferencias_deletadas = 0
    
    for transferencia in transferencias:
        print(f"\n[TRANSFERENCIA] {transferencia.data_movimentacao.strftime('%d/%m/%Y')}: {transferencia.quantidade} vacas descarte")
        
        # Calcular saldo disponível ATÉ o dia da transferência (incluindo promoções do mesmo dia)
        saldo_disponivel = calcular_saldo_disponivel(
            canta_galo, 
            categoria_descarte, 
            transferencia.data_movimentacao,
            planejamento
        )
        
        # Subtrair a própria transferência do cálculo
        saldo_antes_transferencia = saldo_disponivel + transferencia.quantidade
        
        print(f"  Saldo disponivel antes da transferencia: {saldo_antes_transferencia}")
        
        if saldo_antes_transferencia < transferencia.quantidade:
            # Não há saldo suficiente
            print(f"  [PROBLEMA] Saldo insuficiente! Faltam {transferencia.quantidade - saldo_antes_transferencia} vacas")
            
            # Verificar se há promoções no mesmo dia ou antes
            promocoes_antes = MovimentacaoProjetada.objects.filter(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                data_movimentacao__lte=transferencia.data_movimentacao,
                planejamento=planejamento
            )
            
            total_promocoes = sum(p.quantidade for p in promocoes_antes)
            saldo_com_promocoes = saldo_antes_transferencia
            
            print(f"  Promocoes antes ou no mesmo dia: {total_promocoes}, Saldo com promocoes: {saldo_com_promocoes}")
            
            if saldo_com_promocoes < transferencia.quantidade:
                # Não há saldo suficiente mesmo com promoções
                # Deletar transferência se não há saldo
                print(f"  [DELETANDO] Transferencia deletada (sem saldo disponivel)")
                transferencia.delete()
                transferencias_deletadas += 1
            else:
                # Há promoções suficientes, verificar se estão antes da transferência
                promocao_mais_recente = promocoes_antes.order_by('-data_movimentacao').first()
                if promocao_mais_recente and promocao_mais_recente.data_movimentacao >= transferencia.data_movimentacao:
                    # Ajustar data da promoção para antes da transferência
                    promocao_mais_recente.data_movimentacao = transferencia.data_movimentacao - timedelta(days=1)
                    promocao_mais_recente.save()
                    print(f"  [OK] Data da promocao ajustada para antes da transferencia")
        else:
            print(f"  [OK] Saldo suficiente")
    
    print(f"\n[RESUMO]")
    print(f"  Transferencias corrigidas: {transferencias_corrigidas}")
    print(f"  Transferencias deletadas: {transferencias_deletadas}")
    
    # Verificar saldo final por ano
    print(f"\n[VERIFICACAO FINAL POR ANO]")
    anos = [2022, 2023, 2024, 2025, 2026]
    
    for ano in anos:
        data_fim_ano = date(ano, 12, 31)
        saldo_final = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_fim_ano, planejamento)
        print(f"  {ano}: Saldo final = {saldo_final}")
        if saldo_final < 0:
            print(f"    [ERRO] Saldo negativo!")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_corrigir()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

