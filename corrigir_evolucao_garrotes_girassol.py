# -*- coding: utf-8 -*-
"""
Script para corrigir evolução de garrotes na Fazenda Girassol.
Os garrotes transferidos devem evoluir para "Boi 24-36 M" após 12 meses.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction, connection
import time
from calendar import monthrange
from collections import defaultdict

from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada, 
    VendaProjetada, InventarioRebanho, PlanejamentoAnual
)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    # Ajustar ano e mês
    while mes > 12:
        mes -= 12
        ano += 1
    
    # Ajustar dia se o mês não tiver esse dia
    ultimo_dia_mes = monthrange(ano, mes)[1]
    if dia > ultimo_dia_mes:
        dia = ultimo_dia_mes
    
    return date(ano, mes, dia)


def calcular_rebanho_por_movimentacoes(propriedade, data_referencia):
    """Calcula o rebanho atual baseado no inventário inicial + movimentações projetadas."""
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldos = defaultdict(int)
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario
        ).select_related('categoria')
        
        for inv in inventarios:
            saldos[inv.categoria.nome] = inv.quantidade
    
    filtro_data = {}
    if data_inventario:
        filtro_data = {'data_movimentacao__gt': data_inventario}
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__lte=data_referencia,
        **filtro_data
    ).select_related('categoria').order_by('data_movimentacao')
    
    for mov in movimentacoes:
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldos[categoria] += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldos[categoria] -= mov.quantidade
            if saldos[categoria] < 0:
                saldos[categoria] = 0
    
    return dict(saldos)


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
                print(f"[AVISO] Banco bloqueado, aguardando {intervalo}s... (tentativa {tentativa + 1}/{max_tentativas})")
                time.sleep(intervalo)
            else:
                print("[ERRO] Nao foi possivel acessar o banco de dados apos varias tentativas")
                return False
    return False


@transaction.atomic
def corrigir_evolucao_garrotes_girassol():
    """Corrige a evolução de garrotes para Boi 24-36 M na Fazenda Girassol"""
    
    # Buscar propriedade
    try:
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        print(f"[OK] Propriedade encontrada: {girassol.nome_propriedade}")
    except Propriedade.DoesNotExist:
        print("[ERRO] Propriedade 'Girassol' nao encontrada")
        return
    except Propriedade.MultipleObjectsReturned:
        girassol = Propriedade.objects.filter(nome_propriedade__icontains='Girassol').first()
        print(f"[AVISO] Multiplas propriedades encontradas, usando: {girassol.nome_propriedade}")
    
    # Buscar categorias
    try:
        categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
        print(f"[OK] Categoria origem encontrada: {categoria_garrote.nome}")
    except:
        categoria_garrote = CategoriaAnimal.objects.filter(nome__icontains='Garrote').first()
        if not categoria_garrote:
            print("[ERRO] Categoria 'Garrote' nao encontrada")
            return
        print(f"[OK] Categoria origem encontrada: {categoria_garrote.nome}")
    
    try:
        categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
        print(f"[OK] Categoria destino encontrada: {categoria_boi.nome}")
    except:
        categoria_boi = CategoriaAnimal.objects.filter(nome__icontains='Boi').exclude(nome__icontains='+36').first()
        if not categoria_boi:
            print("[ERRO] Categoria 'Boi 24-36 M' nao encontrada")
            return
        print(f"[OK] Categoria destino encontrada: {categoria_boi.nome}")
    
    # Buscar transferências de entrada de garrotes em 2022 e 2023
    transferencias_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2022, 2023]
    ).order_by('data_movimentacao')
    
    if not transferencias_entrada.exists():
        print("[ERRO] Nenhuma transferencia de entrada de garrotes encontrada")
        return
    
    print(f"\n[INFO] Transferencias de entrada encontradas: {transferencias_entrada.count()}")
    for t in transferencias_entrada:
        print(f"   - {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade} {t.categoria.nome}")
    
    # Verificar evoluções existentes
    evolucoes_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2022, 2023, 2024]
    )
    
    print(f"\n[INFO] Evolucoes existentes: {evolucoes_existentes.count()}")
    for e in evolucoes_existentes:
        print(f"   - {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade} {e.categoria.nome}")
    
    # Criar evoluções para cada transferência (12 meses após a transferência)
    evolucoes_criadas = 0
    
    for transferencia in transferencias_entrada:
        data_transferencia = transferencia.data_movimentacao
        quantidade = transferencia.quantidade
        
        # Evolução acontece 12 meses após a transferência
        data_evolucao = adicionar_meses(data_transferencia, 12)
        # Ajustar para o primeiro dia do mês
        data_evolucao = date(data_evolucao.year, data_evolucao.month, 1)
        
        # Verificar se já existe evolução para esta transferência
        evolucao_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='PROMOCAO_SAIDA',
            categoria=categoria_garrote,
            data_movimentacao=data_evolucao,
            quantidade=quantidade
        ).first()
        
        if evolucao_existente:
            print(f"\n[INFO] Evolucao ja existe para {data_transferencia.strftime('%d/%m/%Y')} -> {data_evolucao.strftime('%d/%m/%Y')}")
            continue
        
        # Verificar estoque disponível antes de criar evolução
        saldos = calcular_rebanho_por_movimentacoes(girassol, data_evolucao)
        estoque_garrote = saldos.get(categoria_garrote.nome, 0)
        
        if estoque_garrote < quantidade:
            print(f"\n[AVISO] Estoque insuficiente em {data_evolucao.strftime('%d/%m/%Y')}")
            print(f"   Estoque disponivel: {estoque_garrote}")
            print(f"   Quantidade desejada: {quantidade}")
            quantidade = min(quantidade, estoque_garrote)
            
            if quantidade <= 0:
                print(f"   Pulando esta evolucao (sem estoque)")
                continue
        
        # Criar promoção de saída (garrote)
        MovimentacaoProjetada.objects.create(
            propriedade=girassol,
            categoria=categoria_garrote,
            data_movimentacao=data_evolucao,
            tipo_movimentacao='PROMOCAO_SAIDA',
            quantidade=quantidade,
            observacao=f'Evolucao de idade - {quantidade} garrotes para Boi 24-36 M (transferidos em {data_transferencia.strftime("%d/%m/%Y")})'
        )
        
        # Criar promoção de entrada (boi)
        MovimentacaoProjetada.objects.create(
            propriedade=girassol,
            categoria=categoria_boi,
            data_movimentacao=data_evolucao,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            quantidade=quantidade,
            observacao=f'Evolucao de idade - {quantidade} garrotes para Boi 24-36 M (transferidos em {data_transferencia.strftime("%d/%m/%Y")})'
        )
        
        print(f"   [OK] Evolucao criada: {quantidade} cabecas em {data_evolucao.strftime('%d/%m/%Y')} (transferidos em {data_transferencia.strftime('%d/%m/%Y')})")
        evolucoes_criadas += 1
    
    print(f"\n[OK] Concluido!")
    print(f"   Total de evolucoes criadas: {evolucoes_criadas}")


if __name__ == '__main__':
    print("=" * 60)
    print("CORRECAO DE EVOLUCAO - GARROTES GIRASSOL")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Buscar transferencias de garrotes para Girassol")
    print("2. Criar evolucoes (Garrote 12-24 M -> Boi 24-36 M) apos 12 meses")
    print("3. Garantir que as evolucoes acontecem antes das vendas")
    print("\n" + "=" * 60 + "\n")
    
    # Aguardar banco ficar livre
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_evolucao_garrotes_girassol()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















