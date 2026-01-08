#!/usr/bin/env python
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

# Criar cliente de teste
client = Client()

print("=== TESTANDO ENDPOINT DE CHECKOUT ===")

# Tentar fazer login com um usuário de teste
print("1. Fazendo login...")
User = get_user_model()
try:
    # Tentar encontrar um usuário existente
    user = User.objects.first()
    if user:
        client.force_login(user)
        print(f"Login realizado como: {user.username}")
    else:
        print("Nenhum usuário encontrado no banco de dados")
        # Criar um usuário de teste
        user = User.objects.create_user(
            username='teste_user',
            email='teste@teste.com',
            password='teste123',
            first_name='Teste',
            last_name='Usuario'
        )
        client.force_login(user)
        print(f"Usuário de teste criado e login realizado: {user.username}")
except Exception as e:
    print(f"Erro no login: {e}")

# Testar GET na página de assinaturas
print("\n2. Testando GET /assinaturas/")
response = client.get('/assinaturas/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode()
    print(f"Conteúdo contém 'assinaturas': {'assinaturas' in content}")
    print(f"Tamanho do conteúdo: {len(content)} caracteres")
else:
    print(f"Redirecionado para: {response['Location'] if 'Location' in response else 'N/A'}")

# Testar POST no endpoint de checkout
print("\n3. Testando POST /assinaturas/plano/basico/checkout/")
data = {
    'nome': 'Teste Usuario',
    'email': 'teste@teste.com'
}
response = client.post('/assinaturas/plano/basico/checkout/', data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode()
    print(f"Resposta: {content[:500]}...")
else:
    print(f"Erro na resposta: {response.content.decode()[:500]}...")
    if 'Location' in response:
        print(f"Redirecionado para: {response['Location']}")

print("\n=== FIM DO TESTE ===")
