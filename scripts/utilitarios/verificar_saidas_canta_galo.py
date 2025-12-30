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

print("SAIDAS da Canta Galo (todas):")
saidas = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    tipo_movimentacao='TRANSFERENCIA_SAIDA',
    categoria=categoria
).order_by('data_movimentacao')

print(f"Total: {saidas.count()}")
for s in saidas:
    obs = s.observacao[:80] if s.observacao else 'Sem obs'
    print(f"  {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade} - {obs}")

print("\nENTRADAS no Favo de Mel:")
entradas = MovimentacaoProjetada.objects.filter(
    propriedade=favo_mel,
    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
    categoria=categoria
).order_by('data_movimentacao')

print(f"Total: {entradas.count()}")
for e in entradas:
    print(f"  {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")

# Verificar correspondências
print("\nVerificando correspondencias:")
for entrada in entradas:
    saida_correspondente = saidas.filter(
        data_movimentacao=entrada.data_movimentacao,
        quantidade=entrada.quantidade
    ).first()
    
    if saida_correspondente:
        print(f"  [OK] {entrada.data_movimentacao.strftime('%d/%m/%Y')}: {entrada.quantidade} - TEM saida correspondente")
    else:
        print(f"  [FALTA] {entrada.data_movimentacao.strftime('%d/%m/%Y')}: {entrada.quantidade} - SEM saida correspondente")
























