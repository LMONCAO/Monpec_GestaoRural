#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar por que as fotos não aparecem no Google Cloud
Execute este script no container do Cloud Run ou localmente para diagnosticar o problema
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')

import django
django.setup()

from django.conf import settings
from django.contrib.staticfiles import finders

def diagnosticar_fotos():
    """Diagnostica o problema das fotos não aparecendo"""
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO: Fotos não aparecendo no Google Cloud")
    print("=" * 80)
    print()
    
    # 1. Verificar configurações
    print("1️⃣ VERIFICANDO CONFIGURAÇÕES")
    print("-" * 80)
    print(f"STATIC_URL: {getattr(settings, 'STATIC_URL', 'NÃO DEFINIDO')}")
    print(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'NÃO DEFINIDO')}")
    print(f"STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', 'NÃO DEFINIDO')}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'NÃO DEFINIDO')}")
    print(f"MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'NÃO DEFINIDO')}")
    print()
    
    # 2. Verificar se as fotos existem no diretório original
    print("2️⃣ VERIFICANDO FOTOS NO DIRETÓRIO ORIGINAL (static/site/)")
    print("-" * 80)
    static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
    fotos_encontradas_origem = []
    
    for static_dir in static_dirs:
        static_path = Path(static_dir)
        site_dir = static_path / 'site'
        print(f"Verificando: {site_dir}")
        
        if site_dir.exists():
            fotos = list(site_dir.glob('foto*.jpeg')) + list(site_dir.glob('foto*.jpg'))
            if fotos:
                print(f"✅ Encontradas {len(fotos)} fotos:")
                for foto in fotos:
                    size = foto.stat().st_size
                    print(f"   - {foto.name} ({size:,} bytes)")
                    fotos_encontradas_origem.append(foto)
            else:
                print(f"❌ Nenhuma foto encontrada em {site_dir}")
        else:
            print(f"❌ Diretório não existe: {site_dir}")
    print()
    
    # 3. Verificar se as fotos foram coletadas para STATIC_ROOT
    print("3️⃣ VERIFICANDO FOTOS COLETADAS (staticfiles/site/)")
    print("-" * 80)
    static_root = getattr(settings, 'STATIC_ROOT', None)
    fotos_encontradas_coletadas = []
    
    if static_root:
        static_root_path = Path(static_root)
        site_dir_coletado = static_root_path / 'site'
        print(f"Verificando: {site_dir_coletado}")
        
        if static_root_path.exists():
            if site_dir_coletado.exists():
                fotos_coletadas = list(site_dir_coletado.glob('foto*.jpeg')) + list(site_dir_coletado.glob('foto*.jpg'))
                if fotos_coletadas:
                    print(f"✅ Encontradas {len(fotos_coletadas)} fotos coletadas:")
                    for foto in fotos_coletadas:
                        size = foto.stat().st_size
                        print(f"   - {foto.name} ({size:,} bytes)")
                        fotos_encontradas_coletadas.append(foto)
                else:
                    print(f"❌ Nenhuma foto encontrada em {site_dir_coletado}")
            else:
                print(f"❌ Diretório não existe: {site_dir_coletado}")
                print(f"   Tentando criar...")
                try:
                    site_dir_coletado.mkdir(parents=True, exist_ok=True)
                    print(f"   ✅ Diretório criado")
                except Exception as e:
                    print(f"   ❌ Erro ao criar: {e}")
        else:
            print(f"❌ STATIC_ROOT não existe: {static_root_path}")
    else:
        print("❌ STATIC_ROOT não está configurado")
    print()
    
    # 4. Verificar WhiteNoise
    print("4️⃣ VERIFICANDO CONFIGURAÇÃO DO WHITENOISE")
    print("-" * 80)
    whitenoise_root = getattr(settings, 'WHITENOISE_ROOT', None)
    whitenoise_use_finders = getattr(settings, 'WHITENOISE_USE_FINDERS', None)
    print(f"WHITENOISE_ROOT: {whitenoise_root}")
    print(f"WHITENOISE_USE_FINDERS: {whitenoise_use_finders}")
    
    # Verificar se WhiteNoise está no middleware
    middleware = getattr(settings, 'MIDDLEWARE', [])
    whitenoise_no_middleware = any('whitenoise' in str(m).lower() for m in middleware)
    print(f"WhiteNoise no MIDDLEWARE: {'✅ Sim' if whitenoise_no_middleware else '❌ Não'}")
    print()
    
    # 5. Testar finders do Django
    print("5️⃣ TESTANDO FINDERS DO DJANGO")
    print("-" * 80)
    fotos_teste = ['site/foto1.jpeg', 'site/foto2.jpeg', 'site/foto3.jpeg']
    for foto_teste in fotos_teste:
        encontrado = finders.find(foto_teste)
        if encontrado:
            print(f"✅ {foto_teste} encontrado em: {encontrado}")
        else:
            print(f"❌ {foto_teste} NÃO encontrado pelos finders")
    print()
    
    # 6. Resumo e recomendações
    print("=" * 80)
    print("📋 RESUMO E RECOMENDAÇÕES")
    print("=" * 80)
    print()
    
    problemas = []
    solucoes = []
    
    if not fotos_encontradas_origem:
        problemas.append("❌ Fotos não encontradas no diretório original (static/site/)")
        solucoes.append("1. Verificar se as fotos existem em static/site/")
        solucoes.append("2. Adicionar as fotos se estiverem faltando")
    
    if not fotos_encontradas_coletadas:
        problemas.append("❌ Fotos não foram coletadas para STATIC_ROOT")
        solucoes.append("1. Executar: python manage.py collectstatic --settings=sistema_rural.settings_gcp")
        solucoes.append("2. Verificar se o collectstatic está sendo executado no Dockerfile")
        solucoes.append("3. Verificar logs do build do Docker para erros no collectstatic")
    
    if not whitenoise_no_middleware:
        problemas.append("⚠️ WhiteNoise não está no MIDDLEWARE")
        solucoes.append("1. Adicionar WhiteNoiseMiddleware ao MIDDLEWARE em settings_gcp.py")
    
    if problemas:
        print("PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"  {problema}")
        print()
        print("SOLUÇÕES RECOMENDADAS:")
        for i, solucao in enumerate(solucoes, 1):
            print(f"  {solucao}")
    else:
        print("✅ Todas as verificações passaram!")
        print("   Se as fotos ainda não aparecem, verifique:")
        print("   1. URLs no template estão corretas")
        print("   2. Permissões dos arquivos no servidor")
        print("   3. Headers HTTP (CORS, Content-Type)")
        print("   4. Cache do navegador (tente Ctrl+F5)")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    diagnosticar_fotos()


