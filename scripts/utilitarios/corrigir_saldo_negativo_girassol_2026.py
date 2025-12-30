# -*- coding: utf-8 -*-
"""
Script para corrigir saldo negativo de garrotes no Girassol em 2026
O problema é que as evoluções estão sendo criadas antes das transferências chegarem
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
def corrigir_saldo_negativo():
    """Corrige saldo negativo no Girassol"""
    
    print("=" * 80)
    print("CORRIGIR SALDO NEGATIVO GIRASSOL 2026")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    # Buscar evoluções de 2026 que estão causando saldo negativo
    evolucoes_2026 = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao__year=2026
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Evolucoes encontradas em 2026: {evolucoes_2026.count()}")
    
    # Verificar se há transferências correspondentes ANTES das evoluções
    for evolucao in evolucoes_2026:
        # Buscar transferências que chegaram ANTES da evolução (12 meses antes)
        data_transferencia_esperada = date(evolucao.data_movimentacao.year - 1, evolucao.data_movimentacao.month, 1)
        
        transferencia_correspondente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao__lte=evolucao.data_movimentacao,
            quantidade=evolucao.quantidade
        ).order_by('-data_movimentacao').first()
        
        if not transferencia_correspondente:
            print(f"\n[PROBLEMA] Evolucao de {evolucao.quantidade} em {evolucao.data_movimentacao.strftime('%d/%m/%Y')} sem transferencia correspondente")
            print(f"  [INFO] Deletando evolucao incorreta")
            evolucao.delete()
            
            # Deletar também a promoção de entrada correspondente
            promocao_entrada = MovimentacaoProjetada.objects.filter(
                propriedade=girassol,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                data_movimentacao=evolucao.data_movimentacao,
                quantidade=evolucao.quantidade
            ).first()
            
            if promocao_entrada:
                promocao_entrada.delete()
                print(f"  [OK] Promocao de entrada deletada")
            
            # Deletar venda correspondente se existir
            from gestao_rural.models import VendaProjetada
            venda = MovimentacaoProjetada.objects.filter(
                propriedade=girassol,
                tipo_movimentacao='VENDA',
                data_movimentacao__gte=evolucao.data_movimentacao,
                quantidade=evolucao.quantidade
            ).first()
            
            if venda:
                vendas_projetadas = VendaProjetada.objects.filter(movimentacao_projetada=venda)
                vendas_projetadas.delete()
                venda.delete()
                print(f"  [OK] Venda correspondente deletada")
        else:
            print(f"  [OK] Evolucao de {evolucao.quantidade} em {evolucao.data_movimentacao.strftime('%d/%m/%Y')} tem transferencia correspondente")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_saldo_negativo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























