# -*- coding: utf-8 -*-
"""
Script para criar evoluções para TODOS os lotes de garrotes que entraram na Girassol
O problema é que apenas o primeiro lote (2022) teve evoluções criadas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from django.db import transaction, connection
from calendar import monthrange
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal
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
def criar_evolucoes_todos_lotes():
    """Cria evoluções para todos os lotes de garrotes"""
    
    print("=" * 60)
    print("CRIAR EVOLUCOES TODOS OS LOTES - GIRASSOL")
    print("=" * 60)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[OK] Planejamento: {planejamento.codigo}")
    
    # Buscar todas as transferências de entrada
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias encontradas: {transferencias.count()}")
    
    evolucoes_criadas = 0
    
    for transferencia in transferencias:
        data_transferencia = transferencia.data_movimentacao
        quantidade = transferencia.quantidade
        
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
            
            print(f"   [OK] Evolucao criada: {quantidade} em {data_evolucao.strftime('%d/%m/%Y')} (transferencia em {data_transferencia.strftime('%d/%m/%Y')})")
            evolucoes_criadas += 1
        else:
            # Verificar se está vinculada ao planejamento
            if evolucao_existente.planejamento != planejamento:
                MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    tipo_movimentacao__in=['PROMOCAO_SAIDA', 'PROMOCAO_ENTRADA'],
                    categoria__in=[categoria_garrote, categoria_boi],
                    data_movimentacao=data_evolucao
                ).update(planejamento=planejamento)
                print(f"   [OK] Evolucao vinculada ao planejamento")
    
    print(f"\n[OK] Concluido!")
    print(f"   Evolucoes criadas: {evolucoes_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_evolucoes_todos_lotes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























