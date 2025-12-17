# -*- coding: utf-8 -*-
"""
Script para limpar TODOS os caches do Django
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.cache import cache
from gestao_rural.models import Propriedade

print("=" * 80)
print("LIMPAR CACHE COMPLETO DJANGO")
print("=" * 80)

# Limpar cache de todas as fazendas
from gestao_rural.models import PlanejamentoAnual

fazendas = Propriedade.objects.all()

for fazenda in fazendas:
    # Limpar cache genérico
    cache_key = f'projecao_{fazenda.id}'
    cache.delete(cache_key)
    
    # Limpar cache específico de cada planejamento
    planejamentos = PlanejamentoAnual.objects.filter(propriedade=fazenda)
    for p in planejamentos:
        cache_key_especifico = f'projecao_{fazenda.id}_{p.id}'
        cache.delete(cache_key_especifico)
    
    print(f"[OK] Cache limpo: {fazenda.nome_propriedade}")

# Limpar todo o cache
cache.clear()
print(f"\n[OK] Cache completo do Django foi limpo!")

print(f"\n[INFO] Recarregue a pagina no navegador com Ctrl+Shift+R (forcar recarregamento)")
print(f"[INFO] Se ainda nao funcionar, feche e abra o navegador novamente")

