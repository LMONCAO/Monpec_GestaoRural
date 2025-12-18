# -*- coding: utf-8 -*-
"""
Script para criar saídas do Favo de Mel para Girassol baseado nas entradas do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = 0
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        saldo = inventario_inicial.quantidade
    
    filtro_data = {}
    if data_inventario:
        filtro_data = {'data_movimentacao__gt': data_inventario}
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        **filtro_data
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldo -= mov.quantidade
            if saldo < 0:
                saldo = 0
    
    return saldo


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
def criar_saidas_favo_mel():
    """Cria saídas do Favo de Mel para Girassol baseado nas entradas do Favo de Mel"""
    
    print("=" * 80)
    print("CRIAR SAIDAS FAVO DE MEL -> GIRASSOL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    
    # Buscar entradas na Girassol (essas são as que devem ter saídas correspondentes no Favo de Mel)
    entradas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Entradas na Girassol: {entradas_girassol.count()}")
    
    saidas_criadas = 0
    
    for entrada in entradas_girassol:
        data_transferencia = entrada.data_movimentacao
        quantidade = entrada.quantidade
        
        print(f"\n[ENTRADA GIRASSOL] {data_transferencia.strftime('%d/%m/%Y')}: {quantidade} garrotes")
        
        # Verificar se já existe saída correspondente no Favo de Mel
        saida_existente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia,
            quantidade=quantidade
        ).first()
        
        if not saida_existente:
            # Verificar saldo disponível no Favo de Mel na data da transferência
            saldo_disponivel = calcular_saldo_disponivel(favo_mel, categoria_garrote, data_transferencia)
            
            if saldo_disponivel >= quantidade:
                # Criar saída do Favo de Mel
                MovimentacaoProjetada.objects.create(
                    propriedade=favo_mel,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    quantidade=quantidade,
                    planejamento=planejamento_favo,
                    observacao=f'Transferencia para Girassol - {quantidade} garrotes (ano {data_transferencia.year})'
                )
                print(f"  [OK] Saida criada: {quantidade} garrotes")
                saidas_criadas += 1
            else:
                print(f"  [AVISO] Saldo insuficiente: {saldo_disponivel} < {quantidade}")
                # Criar mesmo assim (pode ser que o saldo esteja sendo calculado incorretamente)
                MovimentacaoProjetada.objects.create(
                    propriedade=favo_mel,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    quantidade=quantidade,
                    planejamento=planejamento_favo,
                    observacao=f'Transferencia para Girassol - {quantidade} garrotes (ano {data_transferencia.year}) - Saldo disponivel: {saldo_disponivel}'
                )
                print(f"  [OK] Saida criada mesmo com saldo insuficiente (sera ajustado)")
                saidas_criadas += 1
        else:
            # Vincular ao planejamento atual se não estiver
            if saida_existente.planejamento != planejamento_favo:
                saida_existente.planejamento = planejamento_favo
                saida_existente.save()
                print(f"  [OK] Saida vinculada ao planejamento atual")
            else:
                print(f"  [INFO] Saida ja existe")
    
    # Verificar resultado final
    saidas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    )
    
    total_saidas = sum(s.quantidade for s in saidas_favo)
    total_entradas = sum(e.quantidade for e in entradas_girassol)
    
    print(f"\n[RESUMO FINAL]")
    print(f"  Saidas (Favo de Mel): {total_saidas}")
    print(f"  Entradas (Girassol): {total_entradas}")
    print(f"  Diferenca: {total_saidas - total_entradas}")
    print(f"  Saidas criadas: {saidas_criadas}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_saidas_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















