import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print('=== VERIFICAÇÃO DO SISTEMA DE EMAIL ===')
print(f'Backend atual: {settings.EMAIL_BACKEND}')
print(f'Servidor SMTP: {getattr(settings, "EMAIL_HOST", "Não configurado")}')
print(f'Porta: {getattr(settings, "EMAIL_PORT", "Não configurado")}')
print(f'Usuário: {getattr(settings, "EMAIL_HOST_USER", "Não configurado")}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')

print('\n=== TESTE DE ENVIO DE EMAIL ===')
try:
    send_mail(
        'Teste MONPEC - Sistema de Reset de Senha',
        'Este é um teste do sistema de recuperação de senha.\n\nSe você recebeu este email, o sistema está funcionando corretamente.',
        settings.DEFAULT_FROM_EMAIL,
        ['teste@exemplo.com'],
        fail_silently=False,
    )
    print('✅ Email de teste enviado com sucesso!')
    print('📧 Verifique o console/terminal onde o servidor Django está rodando')
except Exception as e:
    print(f'❌ Erro ao enviar email: {e}')
    print('💡 POSSÍVEIS CAUSAS:')
    print('   - Backend em modo DEBUG (console) - emails aparecem no terminal')
    print('   - Problemas de configuração SMTP')
    print('   - Firewall bloqueando conexões')