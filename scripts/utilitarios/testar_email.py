#!/usr/bin/env python
"""
Script para testar o envio de e-mails no sistema MONPEC
Execute: python testar_email.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.mail import send_mail, get_connection
from django.conf import settings

def testar_configuracao_email():
    """Testa a configuração de e-mail"""
    
    print("=" * 50)
    print("TESTE DE CONFIGURAÇÃO DE E-MAIL - MONPEC")
    print("=" * 50)
    print()
    
    # Verificar configurações
    print("📋 Verificando configurações...")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Verificar se está usando console backend
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("⚠️  ATENÇÃO: Você está usando o backend de CONSOLE!")
        print("   Os e-mails serão apenas impressos no terminal, não enviados.")
        print("   Configure o .env ou settings.py para usar SMTP real.")
        print()
        resposta = input("Deseja continuar mesmo assim? (S/N): ")
        if resposta.upper() != 'S':
            print("Teste cancelado.")
            return False
        print()
    
    # Solicitar e-mail de destino
    print("=" * 50)
    email_destino = input("Digite o e-mail de destino para teste: ").strip()
    
    if not email_destino:
        print("❌ E-mail não informado. Teste cancelado.")
        return False
    
    # Validar formato do e-mail
    if '@' not in email_destino:
        print("❌ E-mail inválido. Teste cancelado.")
        return False
    
    print()
    print("📧 Enviando e-mail de teste...")
    print()
    
    try:
        # Tentar enviar e-mail
        send_mail(
            subject='Teste de E-mail - Sistema MONPEC',
            message=f'''
Olá!

Este é um e-mail de teste do sistema MONPEC.

Se você recebeu este e-mail, significa que a configuração de e-mail está funcionando corretamente!

Configurações:
- Backend: {settings.EMAIL_BACKEND}
- Host: {settings.EMAIL_HOST}
- Porta: {settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}

Atenciosamente,
Sistema MONPEC
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_destino],
            fail_silently=False,
        )
        
        print("✅ E-mail enviado com sucesso!")
        print()
        print("📬 Verifique a caixa de entrada do e-mail:", email_destino)
        print("   (Não esqueça de verificar a pasta de SPAM)")
        print()
        return True
        
    except Exception as e:
        print()
        print("❌ ERRO ao enviar e-mail:")
        print(f"   {type(e).__name__}: {str(e)}")
        print()
        
        # Sugestões de solução
        print("💡 Possíveis soluções:")
        if 'authentication' in str(e).lower() or 'login' in str(e).lower():
            print("   1. Verifique se o e-mail e senha estão corretos")
            print("   2. Para Gmail, use uma SENHA DE APP (não a senha normal)")
            print("   3. Acesse: https://myaccount.google.com/apppasswords")
        elif 'connection' in str(e).lower() or 'refused' in str(e).lower():
            print("   1. Verifique se a porta está correta (587 para TLS, 465 para SSL)")
            print("   2. Verifique se o firewall não está bloqueando")
            print("   3. Teste com EMAIL_USE_SSL=True e porta 465")
        elif 'timeout' in str(e).lower():
            print("   1. Verifique sua conexão com a internet")
            print("   2. Verifique se o servidor SMTP está acessível")
        else:
            print("   1. Verifique todas as configurações no .env ou settings.py")
            print("   2. Consulte o arquivo: COMO_CONFIGURAR_EMAIL_REAL.md")
        
        print()
        return False

def testar_conexao_smtp():
    """Testa apenas a conexão SMTP sem enviar e-mail"""
    
    print("=" * 50)
    print("TESTE DE CONEXÃO SMTP")
    print("=" * 50)
    print()
    
    try:
        connection = get_connection()
        connection.open()
        print("✅ Conexão SMTP estabelecida com sucesso!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar: {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    print()
    
    # Menu
    print("Escolha o tipo de teste:")
    print("1. Teste completo (enviar e-mail)")
    print("2. Teste de conexão SMTP apenas")
    print()
    
    opcao = input("Digite a opção (1 ou 2): ").strip()
    print()
    
    if opcao == '1':
        testar_configuracao_email()
    elif opcao == '2':
        testar_conexao_smtp()
    else:
        print("Opção inválida. Executando teste completo...")
        print()
        testar_configuracao_email()


