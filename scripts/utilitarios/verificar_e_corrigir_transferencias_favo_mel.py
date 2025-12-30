# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir transferências de saída do Favo de Mel.
O problema é que estão saindo mais animais do que entram, causando saldos negativos.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction, connection
from collections import defaultdict
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal
)


def calcular_saldo_por_data(propriedade, categoria, data_referencia):
    """Calcula o saldo de uma categoria em uma data específica"""
    from gestao_rural.models import InventarioRebanho
    
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = 0
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario,
            categoria=categoria
        )
        saldo = sum(inv.quantidade for inv in inventarios)
    
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
def verificar_e_corrigir_transferencias_favo_mel():
    """Verifica e corrige transferências de saída do Favo de Mel"""
    
    try:
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        print(f"[OK] Propriedade encontrada: {favo_mel.nome_propriedade}")
    except:
        print("[ERRO] Propriedade 'Favo de Mel' nao encontrada")
        return
    
    # Buscar categoria garrote
    try:
        categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
        print(f"[OK] Categoria encontrada: {categoria_garrote.nome}")
    except:
        categoria_garrote = CategoriaAnimal.objects.filter(nome__icontains='Garrote').first()
        if not categoria_garrote:
            print("[ERRO] Categoria 'Garrote' nao encontrada")
            return
        print(f"[OK] Categoria encontrada: {categoria_garrote.nome}")
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[AVISO] Nenhum planejamento encontrado")
    else:
        print(f"[OK] Planejamento: {planejamento.codigo}")
    
    # Buscar transferências de entrada
    transferencias_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2022, 2023, 2024]
    ).order_by('data_movimentacao')
    
    total_entrada = sum(t.quantidade for t in transferencias_entrada)
    print(f"\n[INFO] Transferencias de ENTRADA encontradas: {transferencias_entrada.count()}")
    for t in transferencias_entrada:
        print(f"   + {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome}")
    print(f"   Total ENTRADA: {total_entrada} cabecas")
    
    # Buscar transferências de saída
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2022, 2023, 2024]
    ).order_by('data_movimentacao')
    
    total_saida = sum(t.quantidade for t in transferencias_saida)
    print(f"\n[INFO] Transferencias de SAIDA encontradas: {transferencias_saida.count()}")
    for t in transferencias_saida:
        print(f"   - {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome}")
    print(f"   Total SAIDA: {total_saida} cabecas")
    
    print(f"\n[INFO] Saldo liquido: {total_entrada - total_saida} cabecas")
    
    if total_saida > total_entrada:
        print(f"\n[ERRO] Problema detectado: Saem mais animais ({total_saida}) do que entram ({total_entrada})!")
        print(f"   Diferenca: {total_saida - total_entrada} cabecas a mais saindo")
        
        # Excluir transferências de saída excessivas
        print(f"\n[INFO] Excluindo transferencias de saida excessivas...")
        
        # Manter apenas as transferências corretas (350 a cada 3 meses)
        # Primeiro, excluir todas as transferências de saída
        transferencias_saida.delete()
        
        # Recriar apenas as transferências corretas
        print(f"[INFO] Recriando transferencias de saida corretas...")
        
        # Buscar Girassol
        try:
            girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        except:
            print("[ERRO] Propriedade 'Girassol' nao encontrada")
            return
        
        # Recriar transferências: 350 a cada 3 meses a partir de abril/2022
        datas_transferencia = [
            date(2022, 4, 1),   # 350
            date(2022, 7, 1),   # 350
            date(2022, 10, 1),  # 350
            date(2023, 1, 1),   # 130
        ]
        quantidades = [350, 350, 350, 130]
        
        transferencias_criadas = 0
        
        for data_transf, quantidade in zip(datas_transferencia, quantidades):
            # Verificar saldo disponível antes de criar transferência
            saldo_disponivel = calcular_saldo_por_data(favo_mel, categoria_garrote, data_transf)
            
            if saldo_disponivel < quantidade:
                print(f"   [AVISO] Saldo insuficiente em {data_transf.strftime('%d/%m/%Y')}")
                print(f"   Estoque disponivel: {saldo_disponivel}, Quantidade desejada: {quantidade}")
                quantidade = min(quantidade, saldo_disponivel)
                
                if quantidade <= 0:
                    print(f"   Pulando esta transferencia (sem estoque)")
                    continue
            
            # Saída do Favo de Mel
            MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                data_movimentacao=data_transf,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=quantidade,
                planejamento=planejamento,
                observacao=f'Transferencia para Girassol - lote de {quantidade} (corrigido)'
            )
            
            # Entrada no Girassol (se não existir)
            entrada_existente = MovimentacaoProjetada.objects.filter(
                propriedade=girassol,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=categoria_garrote,
                data_movimentacao=data_transf,
                quantidade=quantidade
            ).first()
            
            if not entrada_existente:
                MovimentacaoProjetada.objects.create(
                    propriedade=girassol,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transf,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    quantidade=quantidade,
                    planejamento=planejamento,
                    observacao=f'Transferencia de Favo de Mel - lote de {quantidade} (corrigido)'
                )
            
            print(f"   [OK] Transferencia criada: {quantidade} cabecas em {data_transf.strftime('%d/%m/%Y')}")
            transferencias_criadas += 1
        
        print(f"\n[OK] {transferencias_criadas} transferencias de saida recriadas")
    else:
        print(f"\n[OK] Transferencias estao corretas (saida <= entrada)")


if __name__ == '__main__':
    print("=" * 60)
    print("VERIFICAR E CORRIGIR TRANSFERENCIAS - FAVO DE MEL")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Verificar transferencias de entrada e saida")
    print("2. Corrigir se estiverem saindo mais animais do que entram")
    print("3. Recriar transferencias de saida corretas (350 a cada 3 meses)")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_corrigir_transferencias_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























