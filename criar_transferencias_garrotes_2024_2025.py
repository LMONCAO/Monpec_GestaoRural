# -*- coding: utf-8 -*-
"""
Script para criar transferências de garrotes da Canta Galo para Favo de Mel em 2024 e 2025
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
def criar_transferencias_garrotes_2024_2025():
    """Cria transferências de garrotes da Canta Galo para Favo de Mel em 2024 e 2025"""
    
    print("=" * 80)
    print("CRIAR TRANSFERENCIAS GARROTES 2024 E 2025")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    anos = [2024, 2025]
    transferencias_criadas = 0
    
    for ano in anos:
        print(f"\n[ANO {ano}]")
        
        # Data da transferência: 15 de janeiro
        data_transferencia = date(ano, 1, 15)
        
        # Verificar saldo disponível na Canta Galo
        saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_garrote, data_transferencia)
        
        print(f"   [INFO] Saldo disponivel em {data_transferencia.strftime('%d/%m/%Y')}: {saldo_disponivel}")
        
        if saldo_disponivel <= 0:
            print(f"   [AVISO] Sem saldo disponivel para transferir")
            continue
        
        # Verificar se já existe transferência
        saida_existente = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia
        ).first()
        
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=data_transferencia
        ).first()
        
        if saida_existente and entrada_existente:
            print(f"   [INFO] Transferencia ja existe: {saida_existente.quantidade} garrotes")
            continue
        
        # Quantidade a transferir: usar o saldo disponível
        quantidade_transferir = saldo_disponivel
        
        # Criar transferência de saída da Canta Galo
        if not saida_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_garrote,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=quantidade_transferir,
                planejamento=planejamento_canta,
                observacao=f'Transferencia para Favo de Mel - {quantidade_transferir} garrotes (ano {ano})'
            )
            print(f"   [OK] Transferencia SAIDA criada: {quantidade_transferir} em {data_transferencia.strftime('%d/%m/%Y')}")
        
        # Criar transferência de entrada no Favo de Mel
        if not entrada_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade_transferir,
                planejamento=planejamento_favo,
                observacao=f'Transferencia de Canta Galo - {quantidade_transferir} garrotes (ano {ano})'
            )
            print(f"   [OK] Transferencia ENTRADA criada: {quantidade_transferir} em {data_transferencia.strftime('%d/%m/%Y')}")
        
        transferencias_criadas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias criadas: {transferencias_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_transferencias_garrotes_2024_2025()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










