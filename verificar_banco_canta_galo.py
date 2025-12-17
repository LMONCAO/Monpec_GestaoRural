#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar dados do banco - Marcelo Sanguino e Fazenda Canta Galo"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import ProdutorRural, Propriedade, InventarioRebanho

print("="*60)
print("VERIFICANDO BANCO DE DADOS - MARCELO SANGUINO / CANTA GALO")
print("="*60)
print()

# Verificar produtores
print("=== PRODUTORES ===")
produtores = ProdutorRural.objects.all()
print(f"Total: {produtores.count()}")
for p in produtores:
    print(f"  ID {p.id}: {p.nome}")
    if 'sanguino' in p.nome.lower() or 'marcelo' in p.nome.lower():
        print(f"    *** ENCONTRADO: {p.nome} ***")
print()

# Verificar propriedades
print("=== PROPRIEDADES ===")
propriedades = Propriedade.objects.all()
print(f"Total: {propriedades.count()}")
for prop in propriedades:
    produtor_nome = prop.produtor.nome if prop.produtor else "N/A"
    print(f"  ID {prop.id}: {prop.nome_propriedade}")
    print(f"    Produtor: {produtor_nome}")
    if 'canta' in prop.nome_propriedade.lower() or 'galo' in prop.nome_propriedade.lower():
        print(f"    *** ENCONTRADO: {prop.nome_propriedade} ***")
        # Verificar inventário
        inventarios = InventarioRebanho.objects.filter(propriedade=prop)
        print(f"    Inventários: {inventarios.count()}")
        if inventarios.exists():
            total_animais = sum(inv.quantidade for inv in inventarios)
            total_valor = sum(inv.valor_total for inv in inventarios)
            print(f"    Total de animais: {total_animais:,}")
            print(f"    Valor total: R$ {total_valor:,.2f}")
print()

print("="*60)

















