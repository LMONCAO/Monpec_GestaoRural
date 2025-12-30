# -*- coding: utf-8 -*-
"""
Script para zerar completamente o saldo da Invernada Grande em 2023
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
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada, InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
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
def zerar_saldo_2023():
    """Zera completamente o saldo da Invernada Grande em 2023"""
    
    print("=" * 80)
    print("ZERAR SALDO INVERNADA GRANDE 2023")
    print("=" * 80)
    
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar saldo final de 2023
    saldo_final_2023 = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    print(f"\n[INFO] Saldo final de 2023: {saldo_final_2023}")
    
    if saldo_final_2023 <= 0:
        print(f"[OK] Saldo ja esta zerado!")
        return
    
    # Criar vendas para zerar o saldo
    print(f"\n[INFO] Criando vendas para zerar {saldo_final_2023} vacas...")
    
    # Começar vendas em setembro/2023 (após as vendas existentes)
    data_venda = date(2023, 9, 1)
    quantidade_restante = saldo_final_2023
    vendas_criadas = 0
    
    while quantidade_restante > 0 and data_venda.year == 2023:
        quantidade_venda = min(80, quantidade_restante)
        
        # Verificar se já existe venda nesta data
        venda_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada_grande,
            tipo_movimentacao='VENDA',
            categoria=categoria_descarte,
            data_movimentacao=data_venda
        ).first()
        
        if venda_existente:
            # Usar data diferente
            data_venda = date(data_venda.year, data_venda.month, 15)
        
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(quantidade_venda))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_venda,
            tipo_movimentacao='VENDA',
            quantidade=quantidade_venda,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento,
            observacao=f'Venda para zerar saldo 2023 - {quantidade_venda} vacas descarte'
        )
        
        VendaProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda,
            quantidade=quantidade_venda,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_medio_kg * Decimal(str(quantidade_venda)),
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda + timedelta(days=30),
            observacoes=f'Venda para zerar saldo 2023'
        )
        
        print(f"   [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
        vendas_criadas += 1
        quantidade_restante -= quantidade_venda
        
        # Próxima venda: 1 mês depois
        if data_venda.month == 12:
            break
        else:
            data_venda = date(data_venda.year, data_venda.month + 1, 1)
    
    # Verificar saldo final novamente
    saldo_final_verificacao = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    print(f"\n[INFO] Saldo final apos correcoes: {saldo_final_verificacao}")
    
    if saldo_final_verificacao > 0:
        print(f"   [AVISO] Ainda ha {saldo_final_verificacao} vacas no estoque")
        print(f"   Criando venda final...")
        
        # Criar venda final em dezembro
        data_venda_final = date(2023, 12, 15)
        
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(saldo_final_verificacao))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_venda_final,
            tipo_movimentacao='VENDA',
            quantidade=saldo_final_verificacao,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento,
            observacao=f'Venda final para zerar saldo 2023 - {saldo_final_verificacao} vacas descarte'
        )
        
        VendaProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda_final,
            quantidade=saldo_final_verificacao,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_medio_kg * Decimal(str(saldo_final_verificacao)),
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda_final + timedelta(days=30),
            observacoes=f'Venda final para zerar saldo 2023'
        )
        
        print(f"   [OK] Venda final criada: {saldo_final_verificacao} em {data_venda_final.strftime('%d/%m/%Y')}")
        vendas_criadas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Vendas criadas: {vendas_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        zerar_saldo_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























