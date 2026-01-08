#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

# Criar cliente de teste
client = Client()

print("=== TESTANDO CHECKOUT COMPLETO ===")

# Fazer login com usuário existente
User = get_user_model()
try:
    user = User.objects.first()
    if user:
        client.force_login(user)
        print("Login realizado como: {}".format(user.username))
        print("Nome completo: {}".format(user.get_full_name()))
        print("Email: {}".format(user.email))
    else:
        print("Nenhum usuario encontrado")
        sys.exit(1)
except Exception as e:
    print("Erro no login: {}".format(e))
    sys.exit(1)

# Testar a view de assinaturas_dashboard primeiro
print("\n1. Testando GET /assinaturas/")
try:
    response = client.get('/assinaturas/')
    print("Status: {}".format(response.status_code))
    if response.status_code == 200:
        print("Dashboard carregado com sucesso")
    else:
        print("Erro no dashboard: {}".format(response.content.decode()[:200]))
        sys.exit(1)
except Exception as e:
    print("Erro ao carregar dashboard: {}".format(e))
    sys.exit(1)

# Testar o endpoint de checkout
print("\n2. Testando POST /assinaturas/plano/basico/checkout/")
try:
    data = {
        'nome': user.get_full_name() or user.username,
        'email': user.email
    }
    print("Enviando dados: {}".format(data))

    response = client.post('/assinaturas/plano/basico/checkout/', data)
    print("Status: {}".format(response.status_code))

    if response.status_code == 200:
        content = response.content.decode()
        print("Resposta: {}".format(content[:300]))
        if 'url' in content:
            print("URL de checkout encontrada - SUCESSO!")
        else:
            print("URL de checkout NAO encontrada")
    else:
        print("Erro na resposta: {}".format(response.content.decode()[:500]))
        # Se for erro 500, vamos tentar debugar mais
        if response.status_code == 500:
            print("\n=== ERRO 500 DETECTADO ===")
            print("Vou tentar identificar o problema...")
            # Vamos importar e testar diretamente a view
            try:
                from gestao_rural.views_assinaturas import iniciar_checkout
                from django.http import HttpRequest
                from django.contrib.auth.models import AnonymousUser

                # Criar uma request mock
                request = HttpRequest()
                request.method = 'POST'
                request.POST = data
                request.user = user

                print("Testando view diretamente...")
                result = iniciar_checkout(request, 'basico')
                print("Resultado da view: {}".format(result.status_code))
                print("Conteudo: {}".format(result.content.decode()[:300]))

            except Exception as e:
                print("Erro ao testar view diretamente: {}".format(e))
                import traceback
                traceback.print_exc()

except Exception as e:
    print("Erro no checkout: {}".format(e))
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
