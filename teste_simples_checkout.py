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

print("=== TESTANDO CHECKOUT APÓS CONFIGURAÇÃO ===")

# Criar ou obter usuário de teste
User = get_user_model()
user, created = User.objects.get_or_create(
    username='teste_checkout',
    defaults={
        'email': 'teste@checkout.com',
        'first_name': 'Teste',
        'last_name': 'Checkout'
    }
)

print(f"Usuário: {user.username} (criado: {created})")
client.force_login(user)

# Testar POST no endpoint de checkout
print("\nTestando POST /assinaturas/plano/basico/checkout/")
data = {
    'nome': 'Teste Checkout',
    'email': 'teste@checkout.com'
}

try:
    response = client.post('/assinaturas/plano/basico/checkout/', data, follow=True)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Sucesso! Resposta JSON:")
        import json
        try:
            data = json.loads(response.content.decode())
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.content.decode()[:500])
    else:
        print("❌ Erro na resposta:")
        print(response.content.decode()[:500])

except Exception as e:
    print(f"❌ Exceção: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
