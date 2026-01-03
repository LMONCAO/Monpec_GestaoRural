# -*- coding: utf-8 -*-
"""
Script para vender os 10 animais restantes em 2023 na Invernada Grande
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from django.db import transaction, connection
from decimal import Decimal
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada
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


@transaction.atomic
def vender_10_animais_2023():
    """Vende os 10 animais restantes em 2023"""
    
    print("=" * 80)
    print("VENDER 10 ANIMAIS INVERNADA GRANDE - 2023")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar planejamento atual
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Verificar se já existe venda de 10 animais em 2023
    vendas_2023 = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='VENDA',
        data_movimentacao__year=2023,
        planejamento=planejamento
    )
    
    total_vendido_2023 = sum(v.quantidade for v in vendas_2023)
    print(f"\n[INFO] Vendas existentes em 2023: {total_vendido_2023} animais")
    
    # Calcular saldo disponível em 31/12/2023
    from gestao_rural.models import InventarioRebanho
    
    inventario = InventarioRebanho.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_inventario__lte=date(2023, 12, 31)
    ).order_by('-data_inventario').first()
    
    saldo_inicial = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações até 31/12/2023
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_movimentacao__lte=date(2023, 12, 31),
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    saldo_final = saldo_inicial
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo_final += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo_final -= mov.quantidade
    
    print(f"[INFO] Saldo disponivel em 31/12/2023: {saldo_final} animais")
    
    if saldo_final <= 0:
        print("[OK] Saldo ja esta zerado ou negativo")
        return
    
    # Criar venda para zerar o saldo
    quantidade_venda = saldo_final
    data_venda = date(2023, 12, 30)
    
    # Valores
    peso_medio_kg = Decimal('450.00')
    valor_por_kg = Decimal('6.50')
    valor_por_animal = valor_por_kg * peso_medio_kg
    valor_total = valor_por_animal * Decimal(str(quantidade_venda))
    peso_total = peso_medio_kg * Decimal(str(quantidade_venda))
    
    # Criar movimentação de venda
    movimentacao = MovimentacaoProjetada.objects.create(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_movimentacao=data_venda,
        tipo_movimentacao='VENDA',
        quantidade=quantidade_venda,
        valor_por_cabeca=valor_por_animal,
        valor_total=valor_total,
        planejamento=planejamento,
        observacao=f'Venda final para zerar saldo - {quantidade_venda} vacas descarte (fim de 2023)'
    )
    
    # Criar VendaProjetada
    VendaProjetada.objects.create(
        propriedade=invernada,
        categoria=categoria_descarte,
        movimentacao_projetada=movimentacao,
        planejamento=planejamento,
        data_venda=data_venda,
        quantidade=quantidade_venda,
        cliente_nome='JBS',
        peso_medio_kg=peso_medio_kg,
        peso_total_kg=peso_total,
        valor_por_kg=valor_por_kg,
        valor_por_animal=valor_por_animal,
        valor_total=valor_total,
        data_recebimento=data_venda + timedelta(days=30),
        observacoes=f'Venda final para zerar saldo - {quantidade_venda} vacas descarte (fim de 2023)'
    )
    
    print(f"\n[OK] Venda criada: {quantidade_venda} animais em {data_venda.strftime('%d/%m/%Y')}")
    
    # Verificar saldo após venda
    saldo_apos_venda = saldo_final - quantidade_venda
    print(f"[VERIFICACAO] Saldo apos venda: {saldo_apos_venda} animais")
    
    if saldo_apos_venda == 0:
        print("[OK] Saldo zerado com sucesso!")
    else:
        print(f"[AVISO] Saldo ainda nao esta zerado: {saldo_apos_venda}")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Venda criada!")
    print("=" * 80)


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        vender_10_animais_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























