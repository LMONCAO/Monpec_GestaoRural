# -*- coding: utf-8 -*-
"""
Script para limpar cache específico do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.cache import cache
from gestao_rural.models import Propriedade, PlanejamentoAnual

def limpar_cache_favo_mel():
    """Limpa cache específico do Favo de Mel"""
    
    print("=" * 80)
    print("LIMPAR CACHE ESPECIFICO FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar todos os planejamentos
    planejamentos = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano')
    
    print(f"\n[INFO] Encontrados {planejamentos.count()} planejamentos")
    
    # Limpar cache para cada planejamento
    for p in planejamentos:
        cache_key = f'projecao_{favo_mel.id}_{p.id}'
        cache.delete(cache_key)
        print(f"  [OK] Cache limpo: {cache_key} (Planejamento: {p.codigo})")
    
    # Limpar cache genérico também
    cache_key_generico = f'projecao_{favo_mel.id}'
    cache.delete(cache_key_generico)
    print(f"  [OK] Cache genérico limpo: {cache_key_generico}")
    
    # Limpar todos os caches relacionados
    cache.delete_pattern(f'projecao_{favo_mel.id}*')
    print(f"  [OK] Todos os caches com padrão 'projecao_{favo_mel.id}*' foram limpos")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Cache limpo!")
    print("=" * 80)


if __name__ == '__main__':
    try:
        limpar_cache_favo_mel()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










