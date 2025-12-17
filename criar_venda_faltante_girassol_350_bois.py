# -*- coding: utf-8 -*-
"""
Script para criar a venda faltante de 350 bois no Girassol
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada, InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_venda):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_venda
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
        data_movimentacao__lte=data_venda,
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
def criar_venda_faltante():
    """Cria a venda faltante de 350 bois"""
    
    print("=" * 80)
    print("CRIAR VENDA FALTANTE - 350 BOIS GIRASSOL")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar evolução de 01/10/2025
    evolucao = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi,
        data_movimentacao=date(2025, 10, 1),
        quantidade=350
    ).first()
    
    if not evolucao:
        print("[ERRO] Evolucao nao encontrada")
        return
    
    print(f"[INFO] Evolucao encontrada: {evolucao.quantidade} bois em {evolucao.data_movimentacao.strftime('%d/%m/%Y')}")
    
    # Data da venda: 90 dias após a evolução (30/12/2025)
    data_venda = date(2025, 12, 30)
    
    # Verificar saldo disponível
    saldo_disponivel = calcular_saldo_disponivel(girassol, categoria_boi, data_venda)
    print(f"[INFO] Saldo disponivel em {data_venda.strftime('%d/%m/%Y')}: {saldo_disponivel}")
    
    if saldo_disponivel < 350:
        print(f"[AVISO] Saldo insuficiente: {saldo_disponivel} < 350")
        print(f"[INFO] Criando venda com saldo disponivel: {saldo_disponivel}")
        quantidade_venda = saldo_disponivel
    else:
        quantidade_venda = 350
    
    # Verificar se já existe venda
    venda_existente = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi,
        data_movimentacao=data_venda,
        quantidade=quantidade_venda
    ).first()
    
    if venda_existente:
        print(f"[INFO] Venda ja existe: {venda_existente.quantidade}")
        return
    
    # Criar venda
    valor_por_kg = Decimal('7.00')
    peso_medio_kg = Decimal('500.00')
    valor_por_animal = valor_por_kg * peso_medio_kg
    valor_total = valor_por_animal * Decimal(str(quantidade_venda))
    
    movimentacao = MovimentacaoProjetada.objects.create(
        propriedade=girassol,
        categoria=categoria_boi,
        data_movimentacao=data_venda,
        tipo_movimentacao='VENDA',
        quantidade=quantidade_venda,
        planejamento=planejamento,
        observacao=f'Venda de {quantidade_venda} bois - 90 dias apos evolucao de 01/10/2025'
    )
    
    from datetime import timedelta
    
    peso_total = peso_medio_kg * Decimal(str(quantidade_venda))
    
    VendaProjetada.objects.create(
        propriedade=girassol,
        categoria=categoria_boi,
        movimentacao_projetada=movimentacao,
        data_venda=data_venda,
        quantidade=quantidade_venda,
        cliente_nome='Frigorifico',
        peso_medio_kg=peso_medio_kg,
        peso_total_kg=peso_total,
        valor_por_kg=valor_por_kg,
        valor_por_animal=valor_por_animal,
        valor_total=valor_total,
        data_recebimento=data_venda + timedelta(days=30),
        observacoes=f'Venda de {quantidade_venda} bois - 90 dias apos evolucao de 01/10/2025'
    )
    
    print(f"[OK] Venda criada: {quantidade_venda} bois em {data_venda.strftime('%d/%m/%Y')}")
    print(f"[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_venda_faltante()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

