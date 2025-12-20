# -*- coding: utf-8 -*-
"""
Script para corrigir desbalanceamentos restantes
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
def corrigir_desbalanceamentos():
    """Corrige desbalanceamentos restantes"""
    
    print("=" * 80)
    print("CORRIGIR DESBALANCEAMENTOS RESTANTES")
    print("=" * 80)
    
    # 1. Favo de Mel -> Girassol (25 garrotes em 15/01/2025)
    print("\n[1] Corrigindo Favo de Mel -> Girassol (25 garrotes)")
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    saida_25 = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote,
        data_movimentacao=date(2025, 1, 15),
        quantidade=25
    ).first()
    
    if saida_25:
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=date(2025, 1, 15),
            quantidade=25
        ).first()
        
        if not entrada_existente:
            planejamento_girassol = PlanejamentoAnual.objects.filter(
                propriedade=girassol
            ).order_by('-data_criacao', '-ano').first()
            
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_garrote,
                data_movimentacao=date(2025, 1, 15),
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=25,
                planejamento=planejamento_girassol,
                observacao=f'Transferencia de Favo de Mel - 25 garrotes (ano 2025)'
            )
            print(f"  [OK] Entrada criada: 25 garrotes em 15/01/2025")
        else:
            print(f"  [INFO] Entrada ja existe")
    else:
        print(f"  [INFO] Saida nao encontrada")
    
    # 2. Invernada Grande (10 vacas descarte em 15/01/2025)
    print("\n[2] Verificando Invernada Grande (10 vacas descarte)")
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    saida_10 = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao=date(2025, 1, 15),
        quantidade=10
    ).first()
    
    if saida_10:
        print(f"  [INFO] Transferencia de saida encontrada: {saida_10.quantidade} em {saida_10.data_movimentacao.strftime('%d/%m/%Y')}")
        obs_safe = saida_10.observacao.encode('ascii', 'ignore').decode('ascii') if saida_10.observacao else ''
        print(f"  Observacao: {obs_safe[:60]}")
        
        # Verificar se deveria ter entrada correspondente ou se é uma saída para outra propriedade
        # Se não houver entrada correspondente e não for uma saída esperada, deletar
        entrada_correspondente = MovimentacaoProjetada.objects.filter(
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=date(2025, 1, 15),
            quantidade=10
        ).exclude(propriedade=invernada).first()
        
        if not entrada_correspondente:
            # Se não há entrada correspondente e não deveria haver (Invernada Grande não recebe vacas descarte), deletar
            saida_10.delete()
            print(f"  [OK] Transferencia de saida deletada (sem entrada correspondente)")
        else:
            print(f"  [INFO] Entrada correspondente encontrada em {entrada_correspondente.propriedade.nome_propriedade}")
    else:
        print(f"  [INFO] Saida nao encontrada")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_desbalanceamentos()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























