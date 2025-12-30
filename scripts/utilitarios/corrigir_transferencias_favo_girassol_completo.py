# -*- coding: utf-8 -*-
"""
Script para corrigir transferências do Favo de Mel para Girassol
Garante que todas as saídas do Favo de Mel tenham entradas correspondentes na Girassol
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
def corrigir_transferencias():
    """Corrige transferências do Favo de Mel para Girassol"""
    
    print("=" * 80)
    print("CORRIGIR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # Buscar TODAS as saídas do Favo de Mel (de qualquer planejamento)
    saidas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Total de saidas do Favo de Mel: {saidas_favo.count()}")
    
    entradas_criadas = 0
    
    for saida in saidas_favo:
        print(f"\n[SAIDA] {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} garrotes")
        
        # Verificar se já existe entrada correspondente na Girassol
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade
        ).first()
        
        if not entrada_existente:
            # Criar entrada correspondente
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_garrote,
                data_movimentacao=saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=saida.quantidade,
                planejamento=planejamento_girassol,
                observacao=f'Entrada de {saida.quantidade} garrotes de {favo_mel.nome_propriedade} (transferencia de {saida.data_movimentacao.strftime("%d/%m/%Y")})'
            )
            print(f"  [OK] Entrada criada: {saida.quantidade} garrotes")
            entradas_criadas += 1
        else:
            # Vincular ao planejamento atual se não estiver
            if entrada_existente.planejamento != planejamento_girassol:
                entrada_existente.planejamento = planejamento_girassol
                entrada_existente.save()
                print(f"  [OK] Entrada vinculada ao planejamento atual")
            else:
                print(f"  [INFO] Entrada ja existe")
    
    # Verificar entradas na Girassol que não têm saída correspondente
    print(f"\n[VERIFICAR ENTRADAS SEM SAIDA CORRESPONDENTE]")
    
    entradas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote,
        planejamento=planejamento_girassol
    ).order_by('data_movimentacao')
    
    entradas_orfas = []
    
    for entrada in entradas_girassol:
        saida_correspondente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            categoria=categoria_garrote,
            data_movimentacao=entrada.data_movimentacao,
            quantidade=entrada.quantidade
        ).first()
        
        if not saida_correspondente:
            entradas_orfas.append(entrada)
            print(f"  [AVISO] Entrada de {entrada.quantidade} em {entrada.data_movimentacao.strftime('%d/%m/%Y')} sem saida correspondente")
    
    # Resumo final
    total_saidas = sum(s.quantidade for s in saidas_favo)
    total_entradas = sum(e.quantidade for e in entradas_girassol)
    
    print(f"\n[RESUMO FINAL]")
    print(f"  Saidas (Favo de Mel): {total_saidas}")
    print(f"  Entradas (Girassol): {total_entradas}")
    print(f"  Diferenca: {total_saidas - total_entradas}")
    print(f"  Entradas criadas: {entradas_criadas}")
    
    if entradas_orfas:
        print(f"\n[AVISO] {len(entradas_orfas)} entradas sem saida correspondente")
        print(f"  Essas entradas podem ter sido criadas manualmente ou de outra origem")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencias()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























