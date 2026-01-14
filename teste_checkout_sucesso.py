import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print('=== TESTE COM USUÁRIO L.MONCAOSILVA ===')
print('')

client = Client()

# Testar com usuário l.moncaosilva (assinatura ativa)
usuario = User.objects.filter(username='l.moncaosilva').first()
if usuario:
    client.force_login(usuario)
    print(f'✅ Usuário {usuario.username} logado (assinatura ATIVA)')

    # Verificar assinatura
    from gestao_rural.models import AssinaturaCliente
    assinatura = AssinaturaCliente.objects.filter(usuario=usuario).first()
    if assinatura:
        print(f'📋 Status da assinatura: {assinatura.status}')
    else:
        print('❌ Assinatura não encontrada')

    # Testar página de sucesso
    response = client.get('/assinaturas/sucesso/', follow=True)
    print(f'✅ Status final: {response.status_code}')

    # Mostrar redirecionamentos
    if hasattr(response, 'redirect_chain') and response.redirect_chain:
        print('🔄 Redirecionamentos:')
        for url, status in response.redirect_chain:
            print(f'   {status}: {url}')

    # Verificar URL final
    final_path = response.request.get('PATH_INFO', 'desconhecido')
    print(f'🎯 URL final: {final_path}')

    if response.status_code == 200:
        print('✅ Página final carregada com sucesso!')
        # Verificar conteúdo
        content = response.content.decode('utf-8')
        if 'assinaturas_confirmacao' in content or 'dados de acesso' in content:
            print('✅ Conteúdo de confirmação exibido')
        elif 'dashboard' in content.lower():
            print('✅ Redirecionado para dashboard')
        else:
            print('⚠️ Conteúdo pode não estar correto')
    else:
        print(f'❌ Problema na página final: {response.status_code}')

else:
    print('❌ Usuário l.moncaosilva não encontrado')