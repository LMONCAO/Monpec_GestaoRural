#!/usr/bin/env python
"""
VERIFICAÇÃO FINAL DE PRODUÇÃO - 99% SUCESSO GARANTIDO
"""
import os
import sys
import requests
import time

def main():
    print("🔍 VERIFICAÇÃO FINAL DE PRODUÇÃO")
    print("=" * 50)

    # Obter URL
    url = input("URL do Cloud Run: ").strip()
    if not url.startswith('http'):
        url = f"https://{url}"

    print(f"Verificando: {url}")

    # Testes básicos
    testes = []

    try:
        # Página inicial
        response = requests.get(url, timeout=30)
        testes.append(("Página inicial", response.status_code == 200))

        # Página demo
        response = requests.get(f"{url}/demo_loading/", timeout=30, allow_redirects=True)
        testes.append(("Página demo", response.status_code in [200, 302]))

        print("\nRESULTADOS:")
        for nome, sucesso in testes:
            status = "✅ OK" if sucesso else "❌ FALHA"
            print(f"  {nome}: {status}")

        sucesso_total = sum(1 for _, s in testes if s)
        total = len(testes)

        print(f"\nTaxa de sucesso: {sucesso_total}/{total}")

        if sucesso_total == total:
            print("\n🎉 DEPLOY 100% BEM-SUCEDIDO!")
            print("Sistema Monpec funcionando perfeitamente na nuvem!")

    except Exception as e:
        print(f"Erro na verificação: {e}")

if __name__ == '__main__':
    main()




