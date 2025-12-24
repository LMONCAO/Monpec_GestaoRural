#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o envio de email usando OAuth2
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

import django
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_envio_email():
    """Testa o envio de email usando OAuth2"""
    
    print("=" * 70)
    print("  TESTE DE ENVIO DE EMAIL - OAUTH2 GMAIL")
    print("=" * 70)
    print()
    
    # Verificar configuração
    print("1. Verificando configuracao...")
    email_backend = getattr(settings, 'EMAIL_BACKEND', None)
    print(f"   EMAIL_BACKEND: {email_backend}")
    
    email_user = getattr(settings, 'EMAIL_HOST_USER', None)
    print(f"   EMAIL_HOST_USER: {email_user}")
    
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    print(f"   DEFAULT_FROM_EMAIL: {from_email}")
    print()
    
    # Email de teste
    destinatario = "monpec@gmail.com"
    assunto = "Teste de Email - MONPEC OAuth2"
    
    mensagem_texto = """
Este é um email de teste do sistema MONPEC.

Se você recebeu este email, significa que a configuração OAuth2 está funcionando corretamente!

Atenciosamente,
Sistema MONPEC
"""
    
    mensagem_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #0d6efd;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            background-color: #f8f9fa;
            padding: 30px;
            border: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>MONPEC - Teste de Email</h1>
    </div>
    
    <div class="content">
        <p>Este é um email de teste do sistema MONPEC.</p>
        <p>Se você recebeu este email, significa que a configuração OAuth2 está funcionando corretamente!</p>
        <p>Atenciosamente,<br>Sistema MONPEC</p>
    </div>
</body>
</html>
"""
    
    print("2. Enviando email de teste...")
    print(f"   Para: {destinatario}")
    print(f"   De: {from_email}")
    print()
    
    try:
        # Criar mensagem
        msg = EmailMultiAlternatives(
            subject=assunto,
            body=mensagem_texto,
            from_email=from_email,
            to=[destinatario]
        )
        msg.attach_alternative(mensagem_html, "text/html")
        
        # Enviar
        msg.send(fail_silently=False)
        
        print("=" * 70)
        print("  EMAIL ENVIADO COM SUCESSO!")
        print("=" * 70)
        print()
        print(f"Email enviado para: {destinatario}")
        print()
        print("Verifique:")
        print("1. Caixa de entrada de monpec@gmail.com")
        print("2. Pasta de spam/lixo eletronico")
        print("3. Aguarde alguns minutos (pode haver atraso)")
        print()
        
        return True
        
    except Exception as e:
        print("=" * 70)
        print("  ERRO AO ENVIAR EMAIL")
        print("=" * 70)
        print()
        print(f"Erro: {e}")
        print()
        print("Detalhes do erro:")
        import traceback
        traceback.print_exc()
        print()
        return False


if __name__ == '__main__':
    try:
        testar_envio_email()
    except KeyboardInterrupt:
        print("\n\nTeste cancelado pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()

















