"""
Script para testar se a URL v3 está sendo carregada pelo servidor Django
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.urls import get_resolver, reverse, NoReverseMatch

print("=" * 60)
print("TESTANDO URL CURRAL V3 NO SERVIDOR")
print("=" * 60)
print()

# Tentar resolver a URL
try:
    url = reverse('curral_dashboard_v3', args=[1])
    print(f"[OK] URL resolvida: {url}")
    print(f"[OK] URL completa: http://localhost:8000{url}")
except NoReverseMatch as e:
    print(f"[ERRO] URL nao encontrada: {e}")
    print()

# Verificar no resolver
resolver = get_resolver()
print(f"[INFO] Total de padroes no resolver: {len(resolver.url_patterns)}")
print()

# Procurar por padroes curral
curral_patterns = []
def find_patterns(url_patterns, prefix=''):
    for pattern in url_patterns:
        if hasattr(pattern, 'pattern'):
            pattern_str = str(pattern.pattern)
            if 'curral' in pattern_str:
                curral_patterns.append(f"{prefix}{pattern_str}")
        elif hasattr(pattern, 'url_patterns'):
            find_patterns(pattern.url_patterns, prefix)

find_patterns(resolver.url_patterns)

print(f"[INFO] Padroes curral encontrados: {len(curral_patterns)}")
v3_patterns = [p for p in curral_patterns if 'v3' in p]
if v3_patterns:
    print(f"[OK] Padroes com v3: {len(v3_patterns)}")
    for p in v3_patterns:
        print(f"  - {p}")
else:
    print("[ERRO] Nenhum padrao com v3 encontrado!")
    print()
    print("Primeiros 10 padroes curral:")
    for i, p in enumerate(curral_patterns[:10]):
        print(f"  {i+1}. {p}")

print()
print("=" * 60)


