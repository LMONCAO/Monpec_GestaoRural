# -*- coding: utf-8 -*-
"""
Script para verificar se as correções ainda existem e garantir que estejam vinculadas ao planejamento.
Se não existirem, recria as correções.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction, connection
from datetime import date
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
def verificar_e_garantir_correcoes():
    """Verifica e garante que as correções existam e estejam vinculadas"""
    
    # Buscar propriedades
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
        categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
        categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    except:
        print("[ERRO] Categorias nao encontradas")
        return
    
    # Verificar transferências de entrada de garrotes
    transferencias = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        data_movimentacao__year__in=[2022, 2023]
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias encontradas: {transferencias.count()}")
    
    if transferencias.count() == 0:
        print("[AVISO] Nenhuma transferencia encontrada. As correcoes podem ter sido apagadas.")
        return
    
    # Verificar evoluções para cada transferência
    evolucoes_criadas = 0
    
    for transferencia in transferencias:
        data_transferencia = transferencia.data_movimentacao
        quantidade = transferencia.quantidade
        
        # Evolução acontece 12 meses após
        data_evolucao = adicionar_meses(data_transferencia, 12)
        data_evolucao = date(data_evolucao.year, data_evolucao.month, 1)
        
        # Verificar se já existe evolução
        evolucao_saida = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='PROMOCAO_SAIDA',
            categoria=categoria_garrote,
            data_movimentacao=data_evolucao,
            quantidade=quantidade
        ).first()
        
        if not evolucao_saida:
            print(f"\n[AVISO] Evolucao faltando para transferencia de {data_transferencia.strftime('%d/%m/%Y')}")
            print(f"   Criando evolucao para {data_evolucao.strftime('%d/%m/%Y')}...")
            
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
            
            evolucoes_criadas += 1
            print(f"   [OK] Evolucao criada e vinculada ao planejamento")
        else:
            # Verificar se está vinculada ao planejamento
            if evolucao_saida.planejamento != planejamento:
                print(f"\n[INFO] Vinculando evolucao existente ao planejamento {planejamento.codigo}...")
                MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    tipo_movimentacao__in=['PROMOCAO_SAIDA', 'PROMOCAO_ENTRADA'],
                    categoria__in=[categoria_garrote, categoria_boi],
                    data_movimentacao=data_evolucao
                ).update(planejamento=planejamento)
                print(f"   [OK] Evolucao vinculada")
    
    # Vincular transferências ao planejamento se não estiverem
    transferencias_sem_planejamento = transferencias.filter(planejamento__isnull=True)
    if transferencias_sem_planejamento.exists():
        total = transferencias_sem_planejamento.count()
        transferencias_sem_planejamento.update(planejamento=planejamento)
        print(f"\n[OK] {total} transferencias vinculadas ao planejamento")
    
    print(f"\n[OK] Concluido!")
    if evolucoes_criadas > 0:
        print(f"   Evolucoes criadas: {evolucoes_criadas}")


if __name__ == '__main__':
    print("=" * 60)
    print("VERIFICAR E GARANTIR CORRECOES - GIRASSOL")
    print("=" * 60)
    print()
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_e_garantir_correcoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























