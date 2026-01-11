#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar acesso ao servidor Django
"""

import urllib.request
import urllib.error
import socket

def testar_url(url):
    """Testa se uma URL está acessível"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200 or response.status == 302
    except (urllib.error.URLError, socket.timeout) as e:
        print(f"    ❌ {url} - Erro: {e}")
        return False
    except Exception as e:
        print(f"    ❌ {url} - Erro inesperado: {e}")
        return False

def main():
    print("🔍 TESTANDO ACESSO AO SISTEMA MONPEC")
    print("=" * 50)

    urls_para_testar = [
        "http://localhost:8000/",
        "http://127.0.0.1:8000/",
        "http://0.0.0.0:8000/"
    ]

    print("Testando URLs disponíveis:")
    print()

    acessivel = False
    for url in urls_para_testar:
        print(f"Testando {url}...")
        if testar_url(url):
            print(f"    ✅ {url} - ACESSÍVEL!")
            acessivel = True
        else:
            print(f"    ❌ {url} - NÃO ACESSÍVEL")

    print()
    if acessivel:
        print("🎉 SERVIDOR RESPONDENDO!")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Abra seu navegador")
        print("2. Digite uma das URLs acima (apenas HTTP)")
        print("3. Login: admin / L6171r12@@")
        print()
        print("💡 DICAS:")
        print("• Use HTTP (não HTTPS)")
        print("• Tente navegador diferente se necessário")
        print("• Limpe cache: Ctrl+Shift+Delete")
    else:
        print("⚠️  SERVIDOR NÃO ESTÁ RODANDO!")
        print()
        print("📋 PARA INICIAR:")
        print("1. Execute: iniciar_servidor_monpec_oficial.bat")
        print("2. Ou execute: python manage.py runserver 0.0.0.0:8000")
        print("3. Aguarde aparecer 'Starting development server'")
        print("4. Execute este script novamente")

if __name__ == '__main__':
    main()




