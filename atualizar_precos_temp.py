#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script temporário para atualizar preços dos planos
"""
import os
import sys
import django

# Configurar o ambiente Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import PlanoAssinatura
from decimal import Decimal

# Atualizar preços
preco = Decimal('99.90')
print(f"Atualizando planos para R$ {preco}...")

planos = PlanoAssinatura.objects.filter(ativo=True)

if not planos.exists():
    print('⚠️ Nenhum plano ativo encontrado.')
    sys.exit(0)

atualizados = 0
for plano in planos:
    plano.preco_mensal_referencia = preco
    plano.save()
    atualizados += 1
    print(f'✓ Plano "{plano.nome}" atualizado para R$ {preco}')

print(f'\n✅ {atualizados} plano(s) atualizado(s) com sucesso!')










