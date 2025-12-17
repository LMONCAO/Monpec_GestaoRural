# -*- coding: utf-8 -*-
"""
Script para recriar transferências corretas de vacas descarte (apenas 2022 e 2023)
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
    InventarioRebanho, PlanejamentoAnual
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
def recriar_transferencias_corretas():
    """Recria transferências corretas de vacas descarte (apenas 2022 e 2023)"""
    
    print("=" * 80)
    print("RECRIAR TRANSFERENCIAS CORRETAS - VACAS DESCARTE (2022-2023)")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    anos = [2022, 2023]
    transferencias_criadas = 0
    
    for ano in anos:
        print(f"\n[ANO {ano}]")
        
        data_transferencia = date(ano, 1, 15)
        
        # Verificar saldo disponível
        saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
        
        print(f"  [INFO] Saldo disponivel em {data_transferencia.strftime('%d/%m/%Y')}: {saldo_disponivel}")
        
        if saldo_disponivel <= 0:
            print(f"  [AVISO] Sem saldo disponivel para transferir")
            continue
        
        # Verificar se já existe transferência
        saida_existente = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia
        ).first()
        
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada_grande,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia
        ).first()
        
        if saida_existente and entrada_existente:
            print(f"  [INFO] Transferencia ja existe: {saida_existente.quantidade}")
            continue
        
        # Quantidade a transferir: mínimo entre 512 e saldo disponível
        quantidade_transferir = min(512, saldo_disponivel)
        
        # Criar transferência de saída
        if not saida_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=quantidade_transferir,
                planejamento=planejamento_canta,
                observacao=f'Transferencia para Invernada Grande - {quantidade_transferir} vacas descarte (ano {ano})'
            )
            print(f"  [OK] Transferencia SAIDA criada: {quantidade_transferir}")
        
        # Criar transferência de entrada
        if not entrada_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade_transferir,
                planejamento=planejamento_invernada,
                observacao=f'Transferencia de Canta Galo - {quantidade_transferir} vacas descarte (ano {ano})'
            )
            print(f"  [OK] Transferencia ENTRADA criada: {quantidade_transferir}")
        
        transferencias_criadas += 1
    
    # Verificar saldos finais
    print(f"\n[VERIFICACAO DE SALDOS FINAIS]")
    for ano in anos:
        saldo_final = calcular_saldo_disponivel(canta_galo, categoria_descarte, date(ano, 12, 31))
        print(f"  {ano}: Saldo final = {saldo_final}")
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias criadas/verificadas: {transferencias_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        recriar_transferencias_corretas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










