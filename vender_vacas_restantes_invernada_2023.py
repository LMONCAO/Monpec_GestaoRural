# -*- coding: utf-8 -*-
"""
Script para vender as 10 vacas restantes na Invernada Grande em 2023
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
    PlanejamentoAnual, VendaProjetada
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    from gestao_rural.models import InventarioRebanho
    
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria
    ).order_by('-data_inventario').first()
    
    saldo = 0
    if inventario_inicial:
        saldo = inventario_inicial.quantidade
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia
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
def vender_vacas_restantes():
    """Vende as vacas restantes na Invernada Grande"""
    
    print("=" * 80)
    print("VENDER VACAS RESTANTES INVERNADA GRANDE 2023")
    print("=" * 80)
    
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar saldo final
    saldo_final = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    print(f"\n[INFO] Saldo final em 2023: {saldo_final}")
    
    if saldo_final > 0:
        # Criar venda final em dezembro/2023
        data_venda_final = date(2023, 12, 25)
        
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(saldo_final))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_venda_final,
            tipo_movimentacao='VENDA',
            quantidade=saldo_final,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento,
            observacao=f'Venda final para zerar saldo 2023 - {saldo_final} vacas descarte (inventario inicial)'
        )
        
        VendaProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda_final,
            quantidade=saldo_final,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_medio_kg * Decimal(str(saldo_final)),
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda_final + timedelta(days=30),
            observacoes=f'Venda final para zerar saldo 2023 (inventario inicial)'
        )
        
        print(f"   [OK] Venda criada: {saldo_final} vacas em {data_venda_final.strftime('%d/%m/%Y')} - R$ {valor_total:.2f}")
    else:
        print(f"   [OK] Saldo ja esta zerado!")
    
    # Verificar saldo final novamente
    saldo_final_verificacao = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    print(f"\n[INFO] Saldo final apos correcao: {saldo_final_verificacao}")
    
    if saldo_final_verificacao == 0:
        print(f"   [OK] Saldo zerado com sucesso!")
    else:
        print(f"   [AVISO] Ainda ha {saldo_final_verificacao} vacas")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        vender_vacas_restantes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










