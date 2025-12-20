# -*- coding: utf-8 -*-
"""
Script para criar transferências de entrada correspondentes de garrotes no Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
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
def criar_entradas_favo_mel():
    """Cria transferências de entrada correspondentes no Favo de Mel"""
    
    print("=" * 80)
    print("CRIAR ENTRADAS GARROTES FAVO DE MEL")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar todas as transferências de saída da Canta Galo
    saidas = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de saida encontradas: {saidas.count()}")
    
    entradas_criadas = 0
    
    for saida in saidas:
        # Verificar se já existe entrada correspondente
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade
        ).first()
        
        if entrada_existente:
            print(f"  [INFO] Entrada ja existe: {saida.data_movimentacao.strftime('%d/%m/%Y')} - {saida.quantidade}")
            continue
        
        # Criar transferência de entrada
        MovimentacaoProjetada.objects.create(
            propriedade=favo_mel,
            categoria=categoria_garrote,
            data_movimentacao=saida.data_movimentacao,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=saida.quantidade,
            planejamento=planejamento_favo,
            observacao=f'Transferencia de Canta Galo - {saida.quantidade} garrotes (ano {saida.data_movimentacao.year})'
        )
        
        print(f"  [OK] Entrada criada: {saida.data_movimentacao.strftime('%d/%m/%Y')} - {saida.quantidade}")
        entradas_criadas += 1
    
    # Verificar se está balanceado
    total_saidas = sum(s.quantidade for s in saidas)
    total_entradas = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).aggregate(total=models.Sum('quantidade'))['total'] or 0
    
    print(f"\n[VERIFICACAO]")
    print(f"Total SAIDAS (Canta Galo): {total_saidas}")
    print(f"Total ENTRADAS (Favo de Mel): {total_entradas}")
    
    if total_saidas == total_entradas:
        print(f"[OK] Transferencias balanceadas!")
    else:
        print(f"[AVISO] Diferenca: {total_saidas - total_entradas}")
    
    print(f"\n[OK] Concluido!")
    print(f"   Entradas criadas: {entradas_criadas}")


if __name__ == '__main__':
    from django.db import models
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_entradas_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























