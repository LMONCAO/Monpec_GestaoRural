#!/usr/bin/env python3
import os
import sys
import django

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings_gcp'
os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DB_PORT'] = '5433'
os.environ['DB_NAME'] = 'monpec-db'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'L6171r12@@jjms'
os.environ['SECRET_KEY'] = 'django-insecure-monpec-gcp-2025-secret-key-production'
os.environ['DEBUG'] = 'False'

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

print('🔍 MAPEANDO TODAS AS URLs COM ERRO 500...')
print('=' * 60)

# Criar cliente de teste
client = Client()

# URLs públicas
urls_publicas = [
    ('/', 'home'),
    ('/assinaturas/', 'assinaturas_dashboard'),
    ('/login/', 'login'),
]

print('📋 URLs PÚBLICAS:')
erros_500 = []

for url, name in urls_publicas:
    try:
        response = client.get(url, follow=True)
        if response.status_code == 500:
            print(f'❌ 500: {url} ({name})')
            erros_500.append((url, name, 'PÚBLICA'))
        elif response.status_code == 200:
            print(f'✅ 200: {url} ({name})')
        else:
            print(f'⚠️ {response.status_code}: {url} ({name})')
    except Exception as e:
        print(f'💥 ERRO: {url} ({name}) - {str(e)[:100]}...')

print()
print('🔐 URLs QUE PRECISAM AUTENTICAÇÃO:')

# Criar usuário de teste
User = get_user_model()
usuario, created = User.objects.get_or_create(
    username='teste_erros_500',
    defaults={
        'email': 'teste@monpec.com.br',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    usuario.set_password('teste123')
    usuario.save()

# Fazer login
client.login(username='teste_erros_500', password='teste123')

# URLs que precisam autenticação
urls_autenticadas = [
    ('/propriedade/', 'propriedade_list'),
    ('/pecuaria/', 'pecuaria_dashboard'),
    ('/financeiro/', 'financeiro_dashboard'),
    ('/compras/', 'compras_dashboard'),
    ('/vendas/', 'vendas_dashboard'),
    ('/nutricao/', 'nutricao_dashboard'),
    ('/projetos-bancarios/', 'projetos_bancarios_dashboard'),
]

for url, name in urls_autenticadas:
    try:
        response = client.get(url, follow=True)
        if response.status_code == 500:
            print(f'❌ 500: {url} ({name})')
            erros_500.append((url, name, 'AUTENTICADA'))
        elif response.status_code == 200:
            print(f'✅ 200: {url} ({name})')
        else:
            print(f'⚠️ {response.status_code}: {url} ({name})')
    except Exception as e:
        print(f'💥 ERRO: {url} ({name}) - {str(e)[:100]}...')

print()
print('🎯 FOCO: ASSINATURAS')
print('Verificando especificamente as URLs de assinatura...')

# URLs específicas de assinatura
urls_assinaturas = [
    ('/assinaturas/', 'assinaturas_dashboard'),
    ('/assinaturas/plano/teste/checkout/', 'assinaturas_checkout'),
    ('/assinaturas/sucesso/', 'assinaturas_sucesso'),
    ('/assinaturas/cancelado/', 'assinaturas_cancelado'),
]

for url, name in urls_assinaturas:
    try:
        response = client.get(url, follow=True)
        if response.status_code == 500:
            print(f'❌ 500: {url} ({name})')
            erros_500.append((url, name, 'ASSINATURAS'))
        elif response.status_code == 200:
            print(f'✅ 200: {url} ({name})')
        else:
            print(f'⚠️ {response.status_code}: {url} ({name})')
    except Exception as e:
        print(f'💥 ERRO: {url} ({name}) - {str(e)[:100]}...')

print()
print('🚨 RESUMO DOS ERROS 500:')
print('=' * 40)

if erros_500:
    print(f'❌ ENCONTRADOS {len(erros_500)} ERROS 500:')
    for url, name, tipo in erros_500:
        print(f'  • {url} ({name}) - {tipo}')
    print()
    print('🔧 PRÓXIMOS PASSOS:')
    print('1. Corrigir URLs de assinaturas (prioridade alta)')
    print('2. Verificar logs detalhados de cada erro')
    print('3. Corrigir campos faltantes nos modelos')
    print('4. Executar migrações específicas se necessário')
else:
    print('✅ NENHUM ERRO 500 ENCONTRADO!')
    print('🎉 SISTEMA TOTALMENTE FUNCIONAL!')

print()
print('📊 LEGENDA:')
print('✅ 200 = Funcionando perfeitamente')
print('⚠️ XXX = Códigos diferentes (pode precisar atenção)')
print('❌ 500 = ERRO INTERNO DO SERVIDOR (precisa correção urgente)')
print('💥 ERRO = Erro de conexão ou configuração')


