# -*- coding: utf-8 -*-
"""
Script para corrigir transferências desbalanceadas
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
    """Corrige transferências desbalanceadas"""
    
    print("=" * 80)
    print("CORRIGIR TRANSFERENCIAS DESBALANCEADAS")
    print("=" * 80)
    
    # 1. Canta Galo -> Invernada Grande (512 vacas descarte em 2022)
    print("\n[1] Corrigindo Canta Galo -> Invernada Grande (2022)")
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao=date(2022, 1, 15)
    ).first()
    
    entrada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao=date(2022, 1, 15)
    ).first()
    
    if saida and not entrada:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=invernada
        ).order_by('-data_criacao', '-ano').first()
        
        MovimentacaoProjetada.objects.create(
            propriedade=invernada,
            categoria=categoria_descarte,
            data_movimentacao=date(2022, 1, 15),
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=512,
            planejamento=planejamento,
            observacao='Transferencia de Canta Galo - 512 vacas descarte (ano 2022)'
        )
        print("  [OK] Entrada criada: 512 vacas descarte em 15/01/2022")
    elif entrada:
        print("  [INFO] Entrada ja existe")
    else:
        print("  [AVISO] Saida nao encontrada")
    
    # 2. Invernada Grande (10 vacas descarte em 2025 - transferência incorreta)
    print("\n[2] Verificando Invernada Grande (2025)")
    
    saida_incorreta = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao=date(2025, 1, 15),
        quantidade=10
    ).first()
    
    if saida_incorreta:
        entrada_correspondente = MovimentacaoProjetada.objects.filter(
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=date(2025, 1, 15),
            quantidade=10
        ).exclude(propriedade=invernada).first()
        
        if not entrada_correspondente:
            print(f"  [OK] Deletando transferencia incorreta: {saida_incorreta.quantidade} em {saida_incorreta.data_movimentacao.strftime('%d/%m/%Y')}")
            saida_incorreta.delete()
            print("  [OK] Transferencia deletada")
        else:
            print(f"  [INFO] Entrada correspondente encontrada em {entrada_correspondente.propriedade.nome_propriedade}")
    else:
        print("  [INFO] Transferencia nao encontrada")
    
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










