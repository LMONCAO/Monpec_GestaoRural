#!/usr/bin/env python3
"""
Teste da API do Curral V4
"""

import requests
import json

# URL da API
url = "http://127.0.0.1:8000/propriedade/1/curral/api/identificar/v4/"

# Dados para teste
data = {
    "codigo": "105500550031001",
    "tipo_identificacao": "SISBOV"
}

# Headers
headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": "dummy"  # CSRF token dummy para teste
}

print("🧪 TESTANDO API DO CURRAL V4")
print("=" * 40)
print(f"URL: {url}")
print(f"Dados: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, json=data, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()

    if response.status_code == 200:
        result = response.json()
        print("✅ Resposta da API:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro na API: {response.status_code}")
        print(f"Conteúdo: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"❌ Erro de conexão: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")