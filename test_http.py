#!/usr/bin/env python
"""
Script simples para testar conectividade HTTP
"""
import urllib.request
import sys

def test_url(url):
    """Testa uma URL e retorna o código de status"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Python/3.11'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode()
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

if __name__ == '__main__':
    urls_to_test = [
        'https://monpec-29862706245.us-central1.run.app/',
        'https://monpec-29862706245.us-central1.run.app/assinaturas/',
        'https://monpec-29862706245.us-central1.run.app/login/'
    ]

    for url in urls_to_test:
        print(f"Testando {url}...")
        status = test_url(url)
        if status:
            print(f"Status: {status}")
        else:
            print("Falhou")
        print()