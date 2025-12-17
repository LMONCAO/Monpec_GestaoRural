# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')

print('Transferencias SAIDA da Canta Galo:')
saidas = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo, 
    tipo_movimentacao='TRANSFERENCIA_SAIDA', 
    categoria=categoria
).order_by('data_movimentacao')
for s in saidas[:10]:
    print(f'  {s.data_movimentacao.strftime("%d/%m/%Y")}: {s.quantidade}')

print('\nTransferencias ENTRADA no Favo de Mel:')
entradas = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel, 
    tipo_movimentacao='TRANSFERENCIA_ENTRADA', 
    categoria=categoria
).order_by('data_movimentacao')
for e in entradas[:10]:
    print(f'  {e.data_movimentacao.strftime("%d/%m/%Y")}: {e.quantidade}')
