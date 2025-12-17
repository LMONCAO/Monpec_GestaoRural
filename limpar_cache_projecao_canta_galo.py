# -*- coding: utf-8 -*-
"""
Script para limpar o cache da projeção da Canta Galo
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.cache import cache
from gestao_rural.models import Propriedade

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')

print("=" * 80)
print("LIMPAR CACHE PROJECAO CANTA GALO")
print("=" * 80)

cache_key = f'projecao_{canta_galo.id}'
cache.delete(cache_key)

print(f"[OK] Cache limpo: {cache_key}")
print(f"[INFO] Recarregue a pagina no navegador para ver as movimentacoes")










