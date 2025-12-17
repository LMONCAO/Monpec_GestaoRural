# -*- coding: utf-8 -*-
"""
Script para atualizar transferências de Favo de Mel para Girassol
de 350 para 480 cabeças a cada 90 dias, respeitando saldos
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


def calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo disponível considerando inventário e movimentações"""
    from gestao_rural.models import InventarioRebanho
    
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações até a data
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    while mes > 12:
        mes -= 12
        ano += 1
    while mes < 1:
        mes += 12
        ano -= 1
    
    dias_no_mes = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    if mes == 2 and (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)):
        dias_no_mes[2] = 29
    
    if dia > dias_no_mes[mes]:
        dia = dias_no_mes[mes]
    
    return date(ano, mes, dia)


@transaction.atomic
def atualizar_transferencias_para_480():
    """Atualiza transferências de 350 para 480 a cada 90 dias"""
    
    print("=" * 80)
    print("ATUALIZAR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL")
    print("CONFIGURACAO PADRAO: 480 cabecas a cada 90 dias")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar planejamentos
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_favo or not planejamento_girassol:
        print("[ERRO] Planejamentos nao encontrados")
        return
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # ========== 1. DELETAR TRANSFERÊNCIAS EXISTENTES ==========
    print("\n[PASSO 1] Deletando transferencias existentes para recriar...")
    
    saidas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo
    )
    
    entradas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento_girassol
    )
    
    total_saidas = saidas_existentes.count()
    total_entradas = entradas_existentes.count()
    
    saidas_existentes.delete()
    entradas_existentes.delete()
    
    print(f"[OK] {total_saidas} saidas e {total_entradas} entradas deletadas")
    
    # ========== 2. CRIAR NOVAS TRANSFERÊNCIAS DE 480 ==========
    print("\n[PASSO 2] Criando novas transferencias de 480 cabecas a cada 90 dias...")
    
    # Buscar entradas no Favo de Mel para calcular saldo disponível
    entradas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"[INFO] Entradas no Favo de Mel: {entradas_favo.count()}")
    
    # Primeira transferência: 01/04/2022
    data_transferencia = date(2022, 4, 1)
    quantidade_por_transferencia = 480  # CONFIGURAÇÃO PADRÃO
    intervalo_meses = 3  # 90 dias
    ano_fim = 2026
    transferencias_criadas = 0
    
    while data_transferencia.year <= ano_fim:
        # Calcular saldo disponível na data da transferência
        saldo_disponivel = calcular_saldo_disponivel(
            favo_mel, categoria_garrote, data_transferencia, planejamento_favo
        )
        
        if saldo_disponivel <= 0:
            print(f"   [AVISO] Sem saldo disponivel em {data_transferencia.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel})")
            # Pular para próxima data
            data_transferencia = adicionar_meses(data_transferencia, intervalo_meses)
            continue
        
        # Quantidade a transferir: mínimo entre 480 e saldo disponível
        quantidade_transferir = min(quantidade_por_transferencia, saldo_disponivel)
        
        # Criar transferência de saída do Favo de Mel
        MovimentacaoProjetada.objects.create(
            propriedade=favo_mel,
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_favo,
            observacao=f'Transferencia para Girassol - {quantidade_transferir} garrotes (saldo disponivel: {saldo_disponivel}) - CONFIGURACAO PADRAO: 480 a cada 90 dias'
        )
        
        # Criar transferência de entrada no Girassol
        MovimentacaoProjetada.objects.create(
            propriedade=girassol,
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_girassol,
            observacao=f'Transferencia de Favo de Mel - {quantidade_transferir} garrotes - CONFIGURACAO PADRAO: 480 a cada 90 dias'
        )
        
        print(f"   [OK] Transferencia criada: {quantidade_transferir} em {data_transferencia.strftime('%d/%m/%Y')} (saldo disponivel: {saldo_disponivel})")
        transferencias_criadas += 1
        
        # Próxima transferência: 90 dias depois (3 meses)
        data_transferencia = adicionar_meses(data_transferencia, intervalo_meses)
    
    print(f"\n[RESUMO] Transferencias criadas: {transferencias_criadas}")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Transferencias atualizadas para 480 cabecas a cada 90 dias!")
    print("=" * 80)


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        atualizar_transferencias_para_480()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











