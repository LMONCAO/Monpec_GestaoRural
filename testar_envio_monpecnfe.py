#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de envio de email para monpecnfe@gmail.com
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

import django
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_envio():
    """Testa envio para monpecnfe@gmail.com"""
    
    print("=" * 70)
    print("  TESTE DE ENVIO PARA monpecnfe@gmail.com")
    print("=" * 70)
    print()
    
    destinatario = "monpecnfe@gmail.com"
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
    
    print(f"Enviando para: {destinatario}")
    print(f"De: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        msg = EmailMultiAlternatives(
            subject=assunto,
            body=mensagem_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario]
        )
        msg.attach_alternative(mensagem_html, "text/html")
        
        msg.send(fail_silently=False)
        
        print("=" * 70)
        print("  EMAIL ENVIADO COM SUCESSO!")
        print("=" * 70)
        print()
        print(f"Email enviado para: {destinatario}")
        print()
        print("Verifique:")
        print("1. Caixa de entrada de monpecnfe@gmail.com")
        print("2. Pasta de spam/lixo eletronico")
        print("3. Aguarde alguns minutos")
        print()
        
        return True
        
    except Exception as e:
        print("=" * 70)
        print("  ERRO AO ENVIAR EMAIL")
        print("=" * 70)
        print()
        print(f"Erro: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    testar_envio()



































