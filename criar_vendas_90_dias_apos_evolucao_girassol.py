# -*- coding: utf-8 -*-
"""
Script para criar vendas de Boi 24-36 M na Fazenda Girassol.
As vendas devem ocorrer a cada 90 dias após a evolução (não após a entrada).
Garante que o saldo não fique negativo.
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
from collections import defaultdict
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal, VendaProjetada, InventarioRebanho
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
def criar_vendas_90_dias_apos_evolucao():
    """Cria vendas a cada 90 dias após a evolução dos garrotes"""
    
    try:
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        print(f"[OK] Propriedade encontrada: {girassol.nome_propriedade}")
    except:
        print("[ERRO] Propriedade 'Girassol' nao encontrada")
        return
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[OK] Planejamento: {planejamento.codigo} (ano {planejamento.ano})")
    
    # Buscar categorias
    try:
        categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
        print(f"[OK] Categoria encontrada: {categoria_boi.nome}")
    except:
        print("[ERRO] Categoria 'Boi 24-36 M' nao encontrada")
        return
    
    # Buscar evoluções (PROMOCAO_ENTRADA de Boi 24-36 M)
    evolucoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi,
        data_movimentacao__year__in=[2023, 2024]
    ).order_by('data_movimentacao')
    
    if not evolucoes.exists():
        print("[ERRO] Nenhuma evolucao encontrada")
        print("   Execute primeiro o script de criacao de evolucoes")
        return
    
    print(f"\n[INFO] Evolucoes encontradas: {evolucoes.count()}")
    for e in evolucoes:
        print(f"   - {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} {e.categoria.nome}")
    
    # Verificar vendas existentes
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi,
        data_movimentacao__year__in=[2023, 2024]
    )
    
    print(f"\n[INFO] Vendas existentes: {vendas_existentes.count()}")
    
    # Perguntar se deve excluir vendas existentes
    excluir_existentes = True
    print(f"\n   -> Excluindo vendas existentes e recriando...")
    
    if excluir_existentes:
        # Excluir vendas projetadas associadas
        vendas_projetadas = VendaProjetada.objects.filter(
            movimentacao_projetada__in=vendas_existentes
        )
        print(f"   Excluindo {vendas_projetadas.count()} vendas projetadas...")
        vendas_projetadas.delete()
        
        # Excluir movimentações de venda
        print(f"   Excluindo {vendas_existentes.count()} movimentacoes de venda...")
        vendas_existentes.delete()
    
    # Criar vendas a cada 90 dias após cada evolução
    vendas_criadas = 0
    
    for evolucao in evolucoes:
        data_evolucao = evolucao.data_movimentacao
        quantidade_lote = evolucao.quantidade
        
        print(f"\n[INFO] Processando evolucao de {data_evolucao.strftime('%d/%m/%Y')}: {quantidade_lote} cabecas")
        
        # Primeira venda: 90 dias após a evolução
        data_primeira_venda = data_evolucao + timedelta(days=90)
        
        # Vender TODO o lote após 90 dias da evolução
        data_venda = data_primeira_venda
        
        # Verificar saldo disponível antes de criar venda
        saldo_disponivel = calcular_saldo_disponivel(girassol, categoria_boi, data_venda)
        
        if saldo_disponivel < quantidade_lote:
            print(f"   [AVISO] Saldo insuficiente em {data_venda.strftime('%d/%m/%Y')}")
            print(f"   Estoque disponivel: {saldo_disponivel}, Quantidade desejada: {quantidade_lote}")
            quantidade_venda = min(quantidade_lote, saldo_disponivel)
            
            if quantidade_venda <= 0:
                print(f"   Pulando esta venda (sem estoque)")
                continue
        else:
            quantidade_venda = quantidade_lote
        
        # Criar venda do lote completo
        observacao = f'Venda completa do lote - {quantidade_venda} bois apos 90 dias da evolucao (evolucao em {data_evolucao.strftime("%d/%m/%Y")})'
        movimentacao, venda = criar_venda(
            propriedade=girassol,
            categoria=categoria_boi,
            quantidade=quantidade_venda,
            data_venda=data_venda,
            cliente_nome='Frigorifico',
            valor_por_kg=Decimal('7.00'),
            peso_medio_kg=Decimal('500.00'),
            observacao=observacao,
            planejamento=planejamento
        )
        
        print(f"   [OK] Venda: {quantidade_venda} cabecas em {data_venda.strftime('%d/%m/%Y')} - R$ {venda.valor_total:,.2f}")
        vendas_criadas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de vendas criadas: {vendas_criadas}")


if __name__ == '__main__':
    print("=" * 60)
    print("CRIAR VENDAS A CADA 90 DIAS APOS EVOLUCAO - GIRASSOL")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Buscar evolucoes de garrotes para Boi 24-36 M")
    print("2. Criar vendas a cada 90 dias apos cada evolucao")
    print("3. Garantir que o saldo nao fique negativo")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_vendas_90_dias_apos_evolucao()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

