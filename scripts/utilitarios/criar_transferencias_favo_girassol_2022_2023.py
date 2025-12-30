# -*- coding: utf-8 -*-
"""
Script para criar transferências do Favo de Mel para Girassol em 2022 e 2023
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
def criar_transferencias_2022_2023():
    """Cria transferências do Favo de Mel para Girassol em 2022 e 2023"""
    
    print("=" * 80)
    print("CRIAR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL 2022 E 2023")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    anos = [2022, 2023]
    transferencias_criadas = 0
    
    for ano in anos:
        print(f"\n[ANO {ano}]")
        
        # Datas de transferência: 01/04, 01/07, 01/10, 01/01 (do ano seguinte)
        datas_transferencia = [
            date(ano, 4, 1),
            date(ano, 7, 1),
            date(ano, 10, 1),
            date(ano + 1, 1, 1)  # Janeiro do ano seguinte
        ]
        
        # Buscar entradas no Favo de Mel neste ano
        entradas_ano = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao__year=ano
        ).order_by('data_movimentacao')
        
        total_entradas = sum(e.quantidade for e in entradas_ano)
        print(f"   [INFO] Total de entradas no Favo de Mel em {ano}: {total_entradas}")
        
        # Verificar saldo disponível no início do ano
        saldo_inicial = calcular_saldo_disponivel(favo_mel, categoria_garrote, date(ano, 1, 1))
        print(f"   [INFO] Saldo inicial em 01/01/{ano}: {saldo_inicial}")
        
        # Calcular saldo total disponível (incluindo entradas do ano)
        saldo_total_disponivel = saldo_inicial + total_entradas
        print(f"   [INFO] Saldo total disponivel (inicial + entradas): {saldo_total_disponivel}")
        
        # Quantidade por transferência: 350 cabeças
        quantidade_por_transferencia = 350
        
        # Criar transferências trimestrais
        quantidade_restante = saldo_total_disponivel
        lote = 1
        
        for data_transferencia in datas_transferencia:
            if quantidade_restante <= 0:
                break
            
            # Verificar saldo disponível na data da transferência
            saldo_disponivel = calcular_saldo_disponivel(favo_mel, categoria_garrote, data_transferencia)
            
            if saldo_disponivel <= 0:
                print(f"   [AVISO] Sem saldo disponivel em {data_transferencia.strftime('%d/%m/%Y')}")
                continue
            
            # Quantidade a transferir: mínimo entre 350 e o saldo disponível
            quantidade_a_transferir = min(quantidade_por_transferencia, saldo_disponivel, quantidade_restante)
            
            # Verificar se já existe transferência
            saida_existente = MovimentacaoProjetada.objects.filter(
                propriedade=favo_mel,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                categoria=categoria_garrote,
                data_movimentacao=data_transferencia
            ).first()
            
            entrada_existente = MovimentacaoProjetada.objects.filter(
                propriedade=girassol,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=categoria_garrote,
                data_movimentacao=data_transferencia
            ).first()
            
            if saida_existente and entrada_existente:
                print(f"   [INFO] Transferencia ja existe: {saida_existente.quantidade} em {data_transferencia.strftime('%d/%m/%Y')}")
                quantidade_restante -= saida_existente.quantidade
                continue
            
            # Criar transferência de saída do Favo de Mel
            if not saida_existente:
                MovimentacaoProjetada.objects.create(
                    propriedade=favo_mel,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    quantidade=quantidade_a_transferir,
                    planejamento=planejamento_favo,
                    observacao=f'Transferencia para Girassol - {quantidade_a_transferir} garrotes (lote {lote}, ano {ano})'
                )
                print(f"   [OK] Transferencia SAIDA criada: {quantidade_a_transferir} em {data_transferencia.strftime('%d/%m/%Y')}")
            
            # Criar transferência de entrada no Girassol
            if not entrada_existente:
                MovimentacaoProjetada.objects.create(
                    propriedade=girassol,
                    categoria=categoria_garrote,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    quantidade=quantidade_a_transferir,
                    planejamento=planejamento_girassol,
                    observacao=f'Entrada de {quantidade_a_transferir} garrotes de {favo_mel.nome_propriedade} (transferencia de {data_transferencia.strftime("%d/%m/%Y")})'
                )
                print(f"   [OK] Transferencia ENTRADA criada no Girassol: {quantidade_a_transferir}")
            
            quantidade_restante -= quantidade_a_transferir
            lote += 1
            transferencias_criadas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias criadas: {transferencias_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_transferencias_2022_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























