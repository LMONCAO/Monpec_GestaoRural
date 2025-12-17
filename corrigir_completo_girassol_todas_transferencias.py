# -*- coding: utf-8 -*-
"""
Script completo para corrigir Girassol:
1. Busca TODAS as transferências (independente do planejamento)
2. Cria evoluções para todas
3. Cria vendas para todas
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
from calendar import monthrange
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal, VendaProjetada
)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    while mes > 12:
        mes -= 12
        ano += 1
    
    ultimo_dia_mes = monthrange(ano, mes)[1]
    if dia > ultimo_dia_mes:
        dia = ultimo_dia_mes
    
    return date(ano, mes, dia)


def calcular_saldo_disponivel(propriedade, categoria, data_venda):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    from gestao_rural.models import InventarioRebanho
    
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_venda
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


def criar_venda(propriedade, categoria, quantidade, data_venda, cliente_nome='Frigorifico', 
                valor_por_kg=Decimal('7.00'), peso_medio_kg=Decimal('500.00'), observacao='', planejamento=None):
    """Cria uma venda projetada"""
    peso_total = peso_medio_kg * Decimal(str(quantidade))
    valor_por_animal = valor_por_kg * peso_medio_kg
    valor_total = valor_por_animal * Decimal(str(quantidade))
    
    # Criar movimentação de venda
    movimentacao = MovimentacaoProjetada.objects.create(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao=data_venda,
        tipo_movimentacao='VENDA',
        quantidade=quantidade,
        valor_por_cabeca=valor_por_animal,
        valor_total=valor_total,
        planejamento=planejamento,
        observacao=observacao
    )
    
    # Criar venda projetada
    venda = VendaProjetada.objects.create(
        propriedade=propriedade,
        categoria=categoria,
        movimentacao_projetada=movimentacao,
        data_venda=data_venda,
        quantidade=quantidade,
        cliente_nome=cliente_nome,
        peso_medio_kg=peso_medio_kg,
        peso_total_kg=peso_total,
        valor_por_kg=valor_por_kg,
        valor_por_animal=valor_por_animal,
        valor_total=valor_total,
        data_recebimento=data_venda + timedelta(days=30),
        observacoes=observacao
    )
    
    return movimentacao, venda


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
def corrigir_completo_girassol():
    """Correção completa da Girassol"""
    
    print("=" * 60)
    print("CORRECAO COMPLETA GIRASSOL")
    print("=" * 60)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[OK] Planejamento: {planejamento.codigo}")
    
    # Buscar TODAS as transferências (independente do planejamento)
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias encontradas: {transferencias.count()}")
    
    evolucoes_criadas = 0
    vendas_criadas = 0
    
    for transferencia in transferencias:
        data_transferencia = transferencia.data_movimentacao
        quantidade = transferencia.quantidade
        
        print(f"\n[INFO] Processando transferencia de {data_transferencia.strftime('%d/%m/%Y')}: {quantidade} garrotes")
        
        # Vincular transferência ao planejamento atual
        if transferencia.planejamento != planejamento:
            transferencia.planejamento = planejamento
            transferencia.save()
        
        # Evolução acontece 12 meses após a transferência
        data_evolucao = adicionar_meses(data_transferencia, 12)
        data_evolucao = date(data_evolucao.year, data_evolucao.month, 1)
        
        # Verificar se já existe evolução
        evolucao_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='PROMOCAO_SAIDA',
            categoria=categoria_garrote,
            data_movimentacao=data_evolucao,
            quantidade=quantidade
        ).first()
        
        if not evolucao_existente:
            # Criar promoção de saída
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_garrote,
                data_movimentacao=data_evolucao,
                tipo_movimentacao='PROMOCAO_SAIDA',
                quantidade=quantidade,
                planejamento=planejamento,
                observacao=f'Evolucao de idade - {quantidade} garrotes para Boi 24-36 M (transferidos em {data_transferencia.strftime("%d/%m/%Y")})'
            )
            
            # Criar promoção de entrada
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_boi,
                data_movimentacao=data_evolucao,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                quantidade=quantidade,
                planejamento=planejamento,
                observacao=f'Evolucao de idade - {quantidade} garrotes para Boi 24-36 M (transferidos em {data_transferencia.strftime("%d/%m/%Y")})'
            )
            
            print(f"   [OK] Evolucao criada: {quantidade} em {data_evolucao.strftime('%d/%m/%Y')}")
            evolucoes_criadas += 1
        else:
            # Vincular ao planejamento se não estiver
            if evolucao_existente.planejamento != planejamento:
                MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    tipo_movimentacao__in=['PROMOCAO_SAIDA', 'PROMOCAO_ENTRADA'],
                    categoria__in=[categoria_garrote, categoria_boi],
                    data_movimentacao=data_evolucao
                ).update(planejamento=planejamento)
        
        # Criar venda 90 dias após a evolução
        data_venda = data_evolucao + timedelta(days=90)
        
        # Verificar se já existe venda
        venda_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='VENDA',
            categoria=categoria_boi,
            data_movimentacao=data_venda,
            quantidade=quantidade
        ).first()
        
        if not venda_existente:
            # Verificar saldo disponível
            saldo_disponivel = calcular_saldo_disponivel(girassol, categoria_boi, data_venda)
            
            if saldo_disponivel >= quantidade:
                observacao = f'Venda completa do lote - {quantidade} bois apos 90 dias da evolucao (evolucao em {data_evolucao.strftime("%d/%m/%Y")})'
                criar_venda(
                    propriedade=girassol,
                    categoria=categoria_boi,
                    quantidade=quantidade,
                    data_venda=data_venda,
                    observacao=observacao,
                    planejamento=planejamento
                )
                print(f"   [OK] Venda criada: {quantidade} em {data_venda.strftime('%d/%m/%Y')}")
                vendas_criadas += 1
            else:
                print(f"   [AVISO] Saldo insuficiente para venda: {saldo_disponivel} < {quantidade}")
    
    print(f"\n[OK] Concluido!")
    print(f"   Evolucoes criadas: {evolucoes_criadas}")
    print(f"   Vendas criadas: {vendas_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_completo_girassol()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











