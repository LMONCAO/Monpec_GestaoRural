# -*- coding: utf-8 -*-
"""
Script para vender os 10 animais do inventário inicial em 2023
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
    PlanejamentoAnual, VendaProjetada, InventarioRebanho
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
def vender_10_animais_inventario_2023():
    """Vende os 10 animais do inventário inicial em 2023"""
    
    print("=" * 80)
    print("VENDER 10 ANIMAIS DO INVENTARIO INICIAL - 2023")
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
    
    # Buscar inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte
    ).order_by('-data_inventario').first()
    
    if not inventario:
        print("[ERRO] Nenhum inventario encontrado")
        return
    
    print(f"[INFO] Inventario: {inventario.data_inventario.strftime('%d/%m/%Y')} - {inventario.quantidade} animais")
    
    # Verificar se já existe venda de 10 animais em 2023
    vendas_2023 = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='VENDA',
        data_movimentacao__year=2023,
        planejamento=planejamento
    )
    
    if vendas_2023.exists():
        print(f"[INFO] Ja existem {vendas_2023.count()} vendas em 2023")
        total_vendido = sum(v.quantidade for v in vendas_2023)
        print(f"[INFO] Total vendido em 2023: {total_vendido} animais")
        
        # Deletar vendas existentes para recriar
        print("[INFO] Deletando vendas existentes...")
        vendas_2023.delete()
        print("[OK] Vendas deletadas")
    
    # Criar venda para os 10 animais do inventário
    quantidade_venda = 10
    data_venda = date(2023, 1, 15)  # Vender no início de 2023
    
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
        observacao=f'Venda dos 10 animais do inventario inicial - {quantidade_venda} vacas descarte (inicio de 2023)'
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
        observacoes=f'Venda dos 10 animais do inventario inicial - {quantidade_venda} vacas descarte (inicio de 2023)'
    )
    
    print(f"\n[OK] Venda criada: {quantidade_venda} animais em {data_venda.strftime('%d/%m/%Y')}")
    print(f"[OK] Valor total: R$ {valor_total:,.2f}")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Venda criada! Saldo sera zerado em 2023, 2024 e 2025")
    print("=" * 80)


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        vender_10_animais_inventario_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











