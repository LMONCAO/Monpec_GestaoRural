# -*- coding: utf-8 -*-
"""
Script para verificar promoções em 2023 e criar transferência correta de vacas descarte
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
def verificar_e_criar_transferencia_2023():
    """Verifica promoções em 2023 e cria transferência correta"""
    
    print("=" * 80)
    print("VERIFICAR E CRIAR TRANSFERENCIA 2023 - VACAS DESCARTE")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar promoções de vacas em reprodução para descarte em 2023
    promocoes_2023 = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year=2023
    ).order_by('data_movimentacao')
    
    total_promovido = sum(p.quantidade for p in promocoes_2023)
    print(f"\n[INFO] Promocoes para descarte em 2023: {promocoes_2023.count()}")
    print(f"[INFO] Total promovido: {total_promovido}")
    
    if total_promovido > 0:
        # Data da transferência: após a última promoção
        ultima_promocao = promocoes_2023.last()
        data_transferencia = ultima_promocao.data_movimentacao
        
        # Verificar saldo disponível na data da transferência
        saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
        
        print(f"\n[INFO] Saldo disponivel em {data_transferencia.strftime('%d/%m/%Y')}: {saldo_disponivel}")
        
        if saldo_disponivel > 0:
            # Verificar se já existe transferência
            saida_existente = MovimentacaoProjetada.objects.filter(
                propriedade=canta_galo,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                categoria=categoria_descarte,
                data_movimentacao__year=2023
            ).first()
            
            if not saida_existente:
                quantidade_transferir = min(975, saldo_disponivel)
                
                # Criar transferência de saída
                MovimentacaoProjetada.objects.create(
                    propriedade=canta_galo,
                    categoria=categoria_descarte,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    quantidade=quantidade_transferir,
                    planejamento=planejamento_canta,
                    observacao=f'Transferencia para Invernada Grande - {quantidade_transferir} vacas descarte (ano 2023)'
                )
                print(f"  [OK] Transferencia SAIDA criada: {quantidade_transferir}")
                
                # Criar transferência de entrada
                MovimentacaoProjetada.objects.create(
                    propriedade=invernada_grande,
                    categoria=categoria_descarte,
                    data_movimentacao=data_transferencia,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    quantidade=quantidade_transferir,
                    planejamento=planejamento_invernada,
                    observacao=f'Transferencia de Canta Galo - {quantidade_transferir} vacas descarte (ano 2023)'
                )
                print(f"  [OK] Transferencia ENTRADA criada: {quantidade_transferir}")
            else:
                print(f"  [INFO] Transferencia ja existe: {saida_existente.quantidade}")
        else:
            print(f"  [AVISO] Sem saldo disponivel para transferir")
    else:
        print(f"  [INFO] Nenhuma promocao encontrada em 2023")
    
    # Verificar saldo final
    saldo_final_2023 = calcular_saldo_disponivel(canta_galo, categoria_descarte, date(2023, 12, 31))
    print(f"\n[INFO] Saldo final 2023: {saldo_final_2023}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_criar_transferencia_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











