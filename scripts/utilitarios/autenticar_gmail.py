#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para autenticar com Google usando OAuth2
Gera o token necessário para envio de emails via Gmail
"""

import os
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Escopos necessários
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def autenticar_gmail():
    """Fluxo de autenticação OAuth2 com Google"""
    
    creds = None
    token_path = BASE_DIR / 'gmail_token.json'
    credentials_path = BASE_DIR / 'gmail_credentials.json'
    
    # Verificar se já temos token salvo
    if token_path.exists():
        print("Token encontrado, carregando...")
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # Se não temos credenciais válidas, fazer o fluxo OAuth2
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expirado, atualizando...")
            creds.refresh(Request())
        else:
            print("=" * 60)
            print("  AUTENTICACAO GOOGLE OAUTH2 PARA GMAIL")
            print("=" * 60)
            print()
            print("Este script vai abrir seu navegador para autenticar")
            print("com sua conta Google e permitir o envio de emails.")
            print()
            
            if not credentials_path.exists():
                print("ERRO: Arquivo gmail_credentials.json nao encontrado!")
                print()
                print("Para obter o arquivo de credenciais:")
                print("1. Acesse: https://console.cloud.google.com/")
                print("2. Crie um novo projeto (ou selecione um existente)")
                print("3. Ative a API Gmail:")
                print("   - Vá em 'APIs & Services' > 'Library'")
                print("   - Procure por 'Gmail API' e clique em 'Enable'")
                print("4. Vá em 'APIs & Services' > 'Credentials'")
                print("5. Clique em 'Create Credentials' > 'OAuth client ID'")
                print("6. Escolha 'Desktop app' como tipo")
                print("7. Dê um nome (ex: MONPEC Gmail)")
                print("8. Clique em 'Create'")
                print("9. Baixe o JSON e salve como 'gmail_credentials.json' na raiz do projeto")
                print()
                return False
            
            print("Iniciando fluxo de autenticacao...")
            print()
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Salvar o token para uso futuro
        print()
        print("Salvando token...")
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("Token salvo com sucesso!")
    
    print()
    print("=" * 60)
    print("  AUTENTICACAO CONCLUIDA!")
    print("=" * 60)
    print()
    print("Seu email esta configurado para usar OAuth2 do Google.")
    print("O token foi salvo em: gmail_token.json")
    print()
    print("Agora voce pode usar o sistema para enviar emails!")
    print("Configure no .env:")
    print("  EMAIL_BACKEND=gestao_rural.backends.email_backend_oauth2.GmailOAuth2Backend")
    print("  EMAIL_HOST_USER=l.moncaosilva@gmail.com")
    print("  DEFAULT_FROM_EMAIL=l.moncaosilva@gmail.com")
    print()
    
    return True


if __name__ == '__main__':
    try:
        autenticar_gmail()
    except KeyboardInterrupt:
        print("\n\nOperacao cancelada pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()










































