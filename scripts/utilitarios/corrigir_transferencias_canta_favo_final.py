# -*- coding: utf-8 -*-
"""
Script para criar as transferências de saída da Canta Galo para Favo de Mel
baseado nas entradas existentes no Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

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
def corrigir_transferencias_canta_favo():
    """Cria transferências de saída da Canta Galo baseado nas entradas do Favo de Mel"""
    
    print("=" * 80)
    print("CORRIGIR TRANSFERENCIAS CANTA GALO -> FAVO DE MEL")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar entradas no Favo de Mel
    entradas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Entradas no Favo de Mel: {entradas_favo.count()}")
    
    # Buscar todas as saídas da Canta Galo
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria
    )
    
    saidas_criadas = 0
    
    for entrada in entradas_favo:
        # Verificar se já existe saída correspondente
        saida_existente = saidas_canta.filter(
            data_movimentacao=entrada.data_movimentacao,
            quantidade=entrada.quantidade
        ).first()
        
        if not saida_existente:
            # Criar saída correspondente
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria,
                data_movimentacao=entrada.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=entrada.quantidade,
                planejamento=planejamento_canta,
                observacao=f'Transferencia para Favo de Mel - {entrada.quantidade} garrotes'
            )
            print(f"   [OK] Saida criada: {entrada.quantidade} em {entrada.data_movimentacao.strftime('%d/%m/%Y')}")
            saidas_criadas += 1
    
    print(f"\n[OK] {saidas_criadas} saidas criadas")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencias_canta_favo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























