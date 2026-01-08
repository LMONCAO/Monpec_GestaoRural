#!/usr/bin/env python
import os
import sys
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

# Criar cliente de teste
client = Client()

print("=== TESTANDO CHECKOUT AUTENTICADO ===")

# Fazer login
login_response = client.post('/login/', {
    'username': 'admin',
    'password': 'admin123'
}, follow=True)

print(f"Login status: {login_response.status_code}")
if login_response.status_code == 200 and 'assinaturas' in login_response.content.decode():
    print("Login realizado com sucesso")
else:
    print("Falha no login")
    print(login_response.content.decode()[:500])
    exit(1)

# Testar POST no endpoint de checkout
print("\nTestando POST /assinaturas/plano/basico/checkout/")
data = {
    'nome': 'Leandro da Silva Moncao',
    'email': 'l.moncaosilva@gmail.com'
}

try:
    response = client.post('/assinaturas/plano/basico/checkout/', data, follow=True)
    print(f"Checkout status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode()
        print("Resposta recebida!")
        print(f"Conteúdo: {content[:500]}...")

        # Verificar se contém URL de checkout
        if 'checkout_url' in content or 'mercadopago' in content.lower():
            print("URL de checkout encontrada!")
        else:
            print("URL de checkout nao encontrada na resposta")
    else:
        print("Erro na resposta:")
        print(response.content.decode()[:500])

except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
