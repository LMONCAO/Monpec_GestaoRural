#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para configurar OAuth2 do Google para envio de emails
Guia passo a passo interativo
"""

import os
import sys
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).parent

def main():
    print("=" * 70)
    print("  CONFIGURACAO OAUTH2 GOOGLE PARA ENVIO DE EMAILS - MONPEC")
    print("=" * 70)
    print()
    print("Email configurado: l.moncaosilva@gmail.com")
    print()
    
    # Verificar se já existe credenciais
    credentials_path = BASE_DIR / 'gmail_credentials.json'
    token_path = BASE_DIR / 'gmail_token.json'
    
    # PASSO 1: Verificar credenciais do Google Cloud
    print("=" * 70)
    print("  PASSO 1: Verificar Credenciais do Google Cloud")
    print("=" * 70)
    print()
    
    if not credentials_path.exists():
        print("[AVISO] Arquivo gmail_credentials.json NAO encontrado!")
        print()
        print("Voce precisa obter este arquivo do Google Cloud Console.")
        print()
        print("INSTRUCOES DETALHADAS:")
        print()
        print("1. Abra seu navegador e acesse:")
        print("   https://console.cloud.google.com/")
        print()
        input("   Pressione ENTER quando estiver no Google Cloud Console...")
        
        print()
        print("2. Crie ou selecione um projeto:")
        print("   - Clique no menu de projetos (topo da tela)")
        print("   - Clique em 'New Project' se for criar novo")
        print("   - Nome: 'MONPEC Gmail' (ou qualquer nome)")
        print("   - Clique em 'Create'")
        print()
        input("   Pressione ENTER quando tiver criado/selecionado o projeto...")
        
        print()
        print("3. Ative a Gmail API:")
        print("   - No menu lateral, clique em 'APIs & Services' > 'Library'")
        print("   - Procure por 'Gmail API'")
        print("   - Clique em 'Gmail API'")
        print("   - Clique no botao 'ENABLE' (azul, no topo)")
        print()
        input("   Pressione ENTER quando tiver ativado a Gmail API...")
        
        print()
        print("4. Configure OAuth Consent Screen (primeira vez):")
        print("   - No menu lateral, clique em 'APIs & Services' > 'OAuth consent screen'")
        print("   - Escolha 'External' e clique em 'CREATE'")
        print("   - Preencha:")
        print("     * App name: MONPEC")
        print("     * User support email: l.moncaosilva@gmail.com")
        print("     * Developer contact: l.moncaosilva@gmail.com")
        print("   - Clique em 'SAVE AND CONTINUE'")
        print("   - Em 'Scopes', clique em 'ADD OR REMOVE SCOPES'")
        print("     * Procure e selecione: https://www.googleapis.com/auth/gmail.send")
        print("   - Clique em 'UPDATE' e depois 'SAVE AND CONTINUE'")
        print("   - Em 'Test users', clique em 'ADD USERS'")
        print("     * Adicione: l.moncaosilva@gmail.com")
        print("   - Clique em 'SAVE AND CONTINUE' varias vezes ate finalizar")
        print()
        input("   Pressione ENTER quando tiver configurado o OAuth consent screen...")
        
        print()
        print("5. Crie as credenciais OAuth2:")
        print("   - No menu lateral, clique em 'APIs & Services' > 'Credentials'")
        print("   - Clique em 'CREATE CREDENTIALS' > 'OAuth client ID'")
        print("   - Application type: 'Desktop app'")
        print("   - Name: 'MONPEC Gmail'")
        print("   - Clique em 'CREATE'")
        print()
        input("   Pressione ENTER quando tiver criado as credenciais...")
        
        print()
        print("6. Baixe o arquivo JSON:")
        print("   - Clique no icone de download ao lado das credenciais criadas")
        print("   - Salve o arquivo como 'gmail_credentials.json'")
        print("   - Mova o arquivo para esta pasta:")
        print(f"     {BASE_DIR}")
        print()
        input("   Pressione ENTER quando tiver colocado o arquivo gmail_credentials.json nesta pasta...")
        
        # Verificar novamente
        if not credentials_path.exists():
            print()
            print("[ERRO] Arquivo gmail_credentials.json ainda nao encontrado!")
            print(f"       Por favor, coloque o arquivo em: {BASE_DIR}")
            print()
            input("Pressione ENTER para tentar novamente ou CTRL+C para sair...")
            return main()
    else:
        print("[OK] Arquivo gmail_credentials.json encontrado!")
    
    print()
    print("=" * 70)
    print("  PASSO 2: Autenticar com Google")
    print("=" * 70)
    print()
    
    # Importar e executar autenticação
    try:
        from autenticar_gmail import autenticar_gmail
        
        print("Iniciando autenticacao...")
        print("O navegador vai abrir para voce autorizar o acesso.")
        print()
        input("Pressione ENTER para abrir o navegador e autenticar...")
        
        if autenticar_gmail():
            print()
            print("[OK] Autenticacao concluida com sucesso!")
        else:
            print()
            print("[ERRO] Falha na autenticacao. Tente novamente.")
            return
            
    except Exception as e:
        print()
        print(f"[ERRO] Erro durante autenticacao: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=" * 70)
    print("  PASSO 3: Configurar arquivo .env")
    print("=" * 70)
    print()
    
    # Configurar .env
    env_file = BASE_DIR / '.env'
    env_content = """# ============================================
# CONFIGURACAO DE E-MAIL - MONPEC (OAuth2)
# ============================================
# Configurado automaticamente para usar OAuth2 do Google
# Email: l.moncaosilva@gmail.com

EMAIL_BACKEND=gestao_rural.backends.email_backend_oauth2.GmailOAuth2Backend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=l.moncaosilva@gmail.com
DEFAULT_FROM_EMAIL=l.moncaosilva@gmail.com
SITE_URL=http://localhost:8000
"""
    
    # Ler .env existente se houver
    if env_file.exists():
        linhas_atuais = env_file.read_text(encoding='utf-8').split('\n')
        linhas_novas = []
        chaves_email = ['EMAIL_BACKEND', 'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USE_TLS', 
                       'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'DEFAULT_FROM_EMAIL', 'SITE_URL']
        
        # Remover linhas antigas de email
        for linha in linhas_atuais:
            if not any(linha.strip().startswith(f"{chave}=") for chave in chaves_email):
                linhas_novas.append(linha)
        
        # Adicionar novas configurações
        if linhas_novas and linhas_novas[-1].strip():
            linhas_novas.append('')
        linhas_novas.append('# Configuracoes de Email (OAuth2)')
        linhas_novas.extend(env_content.split('\n'))
        
        env_file.write_text('\n'.join(linhas_novas), encoding='utf-8')
    else:
        env_file.write_text(env_content, encoding='utf-8')
    
    print("[OK] Arquivo .env configurado!")
    print()
    
    print("=" * 70)
    print("  CONFIGURACAO CONCLUIDA!")
    print("=" * 70)
    print()
    print("Resumo:")
    print("  - Credenciais: gmail_credentials.json [OK]" if credentials_path.exists() else "  - Credenciais: [FALTANDO]")
    print("  - Token: gmail_token.json [OK]" if token_path.exists() else "  - Token: [FALTANDO]")
    print("  - .env: configurado [OK]")
    print()
    print("Proximos passos:")
    print("1. Reinicie o servidor Django")
    print("2. Crie um convite de cotacao para testar")
    print("3. O email sera enviado automaticamente!")
    print()
    print("NOTA: Se o token expirar no futuro, execute novamente:")
    print("      python autenticar_gmail.py")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperacao cancelada pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()



































