# -*- coding: utf-8 -*-
"""
Script para limpar o cache da projeção do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.cache import cache
from gestao_rural.models import Propriedade

favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')

print("=" * 80)
print("LIMPAR CACHE PROJECAO FAVO DE MEL")
print("=" * 80)

cache_key = f'projecao_{favo_mel.id}'
cache.delete(cache_key)

print(f"[OK] Cache limpo: {cache_key}")
print(f"[INFO] Recarregue a pagina no navegador para ver as movimentacoes")




















