# -*- coding: utf-8 -*-
"""
Script para limpar cache de todas as fazendas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.cache import cache
from gestao_rural.models import Propriedade

fazendas = Propriedade.objects.all()

print("=" * 80)
print("LIMPAR CACHE TODAS AS FAZENDAS")
print("=" * 80)

for fazenda in fazendas:
    cache_key = f'projecao_{fazenda.id}'
    cache.delete(cache_key)
    print(f"[OK] Cache limpo: {fazenda.nome_propriedade}")

print(f"\n[OK] Cache de todas as fazendas foi limpo!")
print(f"[INFO] Recarregue as paginas no navegador para ver as atualizacoes")
























