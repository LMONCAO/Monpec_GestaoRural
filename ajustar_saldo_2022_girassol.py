# -*- coding: utf-8 -*-
"""
Script para ajustar saldo de 2022 na Girassol para 300 bois
Como não há evoluções em 2022, vamos ajustar o inventário inicial
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
    Propriedade, InventarioRebanho, CategoriaAnimal
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
def ajustar_saldo_2022():
    """Ajusta saldo de 2022 para 300 bois"""
    
    print("=" * 80)
    print("AJUSTAR SALDO 2022 GIRASSOL PARA 300 BOIS")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # Buscar inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=girassol,
        categoria=categoria_boi
    ).order_by('-data_inventario').first()
    
    if inventario:
        print(f"[INFO] Inventario atual: {inventario.quantidade} bois em {inventario.data_inventario.strftime('%d/%m/%Y')}")
        
        # Atualizar quantidade para 300 e data para 2022
        inventario.quantidade = 300
        inventario.data_inventario = date(2022, 1, 1)
        inventario.save()
        
        print(f"[OK] Inventario atualizado: 300 bois em 01/01/2022")
    else:
        # Criar inventário inicial
        InventarioRebanho.objects.create(
            propriedade=girassol,
            categoria=categoria_boi,
            data_inventario=date(2022, 1, 1),
            quantidade=300
        )
        
        print(f"[OK] Inventario criado: 300 bois em 01/01/2022")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        ajustar_saldo_2022()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

