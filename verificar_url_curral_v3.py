"""
Script para verificar se a URL curral/v3 está configurada corretamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.conf import settings

print("=" * 60)
print("VERIFICANDO URL CURRAL V3")
print("=" * 60)
print()

# Verificar se a URL está definida
try:
    url = reverse('curral_dashboard_v3', args=[1])
    print(f"[OK] URL encontrada: {url}")
    print(f"[OK] URL completa: http://localhost:8000{url}")
except NoReverseMatch as e:
    print(f"[ERRO] URL nao encontrada: {e}")
    print()
    print("Verificando URLs do gestao_rural...")
    
    # Tentar importar diretamente
    try:
        from gestao_rural import urls as gestao_urls
        print(f"[INFO] Total de URLs em gestao_rural: {len(gestao_urls.urlpatterns)}")
        
        # Procurar pela URL curral/v3
        for pattern in gestao_urls.urlpatterns:
            if hasattr(pattern, 'pattern'):
                pattern_str = str(pattern.pattern)
                if 'curral/v3' in pattern_str or 'curral_dashboard_v3' in str(pattern):
                    print(f"[OK] URL encontrada no padrao: {pattern_str}")
                    if hasattr(pattern, 'name') and pattern.name:
                        print(f"[OK] Nome da URL: {pattern.name}")
    except Exception as e:
        print(f"[ERRO] Erro ao verificar URLs: {e}")

print()
print("=" * 60)
print("INSTRUCOES:")
print("=" * 60)
print("1. Pare o servidor Django (Ctrl+C)")
print("2. Reinicie o servidor: python311\\python.exe manage.py runserver")
print("3. Acesse: http://localhost:8000/propriedade/1/curral/v3/")
print("=" * 60)


