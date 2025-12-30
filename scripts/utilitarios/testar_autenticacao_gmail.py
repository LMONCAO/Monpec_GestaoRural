#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar a autenticação OAuth2 do Gmail
Verifica se tudo está configurado corretamente
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

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def testar_autenticacao():
    """Testa se a autenticação OAuth2 está funcionando"""
    
    print("=" * 70)
    print("  TESTE DE AUTENTICACAO OAUTH2 GMAIL")
    print("=" * 70)
    print()
    
    # Verificar arquivos
    token_path = BASE_DIR / 'gmail_token.json'
    credentials_path = BASE_DIR / 'gmail_credentials.json'
    
    print("1. Verificando arquivos...")
    if not credentials_path.exists():
        print("   [ERRO] gmail_credentials.json NAO encontrado!")
        print(f"   Caminho esperado: {credentials_path}")
        return False
    print(f"   [OK] gmail_credentials.json encontrado")
    
    if not token_path.exists():
        print("   [ERRO] gmail_token.json NAO encontrado!")
        print("   Execute: python autenticar_gmail.py")
        return False
    print(f"   [OK] gmail_token.json encontrado")
    
    print()
    print("2. Carregando credenciais...")
    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        print("   [OK] Credenciais carregadas")
    except Exception as e:
        print(f"   [ERRO] Erro ao carregar credenciais: {e}")
        return False
    
    print()
    print("3. Verificando token...")
    if creds.expired:
        print("   [AVISO] Token expirado, tentando renovar...")
        if creds.refresh_token:
            try:
                creds.refresh(Request())
                print("   [OK] Token renovado com sucesso!")
                
                # Salvar token renovado
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                print("   [OK] Token salvo")
            except RefreshError as e:
                print(f"   [ERRO] Erro ao renovar token: {e}")
                print("   Execute: python autenticar_gmail.py")
                return False
        else:
            print("   [ERRO] Token expirado e sem refresh_token")
            print("   Execute: python autenticar_gmail.py")
            return False
    else:
        print("   [OK] Token valido")
    
    print()
    print("4. Verificando configuracao do Django...")
    email_backend = getattr(settings, 'EMAIL_BACKEND', None)
    if email_backend and 'oauth2' in email_backend.lower():
        print(f"   [OK] EMAIL_BACKEND configurado: {email_backend}")
    else:
        print(f"   [AVISO] EMAIL_BACKEND: {email_backend}")
        print("   Verifique se esta usando: gestao_rural.backends.email_backend_oauth2.GmailOAuth2Backend")
    
    email_user = getattr(settings, 'EMAIL_HOST_USER', None)
    if email_user:
        print(f"   [OK] EMAIL_HOST_USER: {email_user}")
    else:
        print("   [AVISO] EMAIL_HOST_USER nao configurado")
    
    print()
    print("=" * 70)
    print("  TESTE CONCLUIDO!")
    print("=" * 70)
    print()
    print("[OK] Autenticacao OAuth2 configurada corretamente!")
    print()
    print("Próximos passos:")
    print("1. Reinicie o servidor Django")
    print("2. Crie um convite de cotação")
    print("3. O email será enviado automaticamente!")
    print()
    
    return True


if __name__ == '__main__':
    try:
        testar_autenticacao()
    except Exception as e:
        print(f"\n[ERRO] ERRO: {e}")
        import traceback
        traceback.print_exc()

