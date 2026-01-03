# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, InventarioRebanho, CategoriaAnimal

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

inventario = InventarioRebanho.objects.filter(
    propriedade=girassol, 
    categoria=categoria, 
    data_inventario__year=2025
).first()

if inventario:
    print(f'Deletando inventario: {inventario.data_inventario} - {inventario.quantidade}')
    inventario.delete()
    print('Inventario deletado')
else:
    print('Inventario nao encontrado')
























