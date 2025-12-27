#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script automatizado para configurar OAuth2 do Google
Tenta automatizar o máximo possível
"""

import webbrowser
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent

def main():
    print("=" * 70)
    print("  CONFIGURACAO AUTOMATIZADA OAUTH2 GMAIL")
    print("=" * 70)
    print()
    print("Email: l.moncaosilva@gmail.com")
    print()
    
    credentials_path = BASE_DIR / 'gmail_credentials.json'
    
    # Abrir Google Cloud Console
    print("Abrindo Google Cloud Console...")
    print()
    webbrowser.open('https://console.cloud.google.com/')
    time.sleep(2)
    
    print("INSTRUCOES RAPIDAS:")
    print()
    print("1. No Google Cloud Console que acabou de abrir:")
    print("   - Clique em 'Select a project' (topo) > 'New Project'")
    print("   - Nome: MONPEC")
    print("   - Clique em 'Create'")
    print()
    input("   Pressione ENTER quando tiver criado o projeto...")
    
    print()
    print("2. Vou abrir a pagina para ativar Gmail API...")
    time.sleep(1)
    webbrowser.open('https://console.cloud.google.com/apis/library/gmail.googleapis.com')
    print()
    print("   - Clique no botao 'ENABLE' (azul)")
    print()
    input("   Pressione ENTER quando tiver ativado a Gmail API...")
    
    print()
    print("3. Vou abrir a pagina de OAuth Consent Screen...")
    time.sleep(1)
    webbrowser.open('https://console.cloud.google.com/apis/credentials/consent')
    print()
    print("   - Se for primeira vez:")
    print("     * Escolha 'External' > 'CREATE'")
    print("     * App name: MONPEC")
    print("     * User support email: l.moncaosilva@gmail.com")
    print("     * Developer contact: l.moncaosilva@gmail.com")
    print("     * Clique 'SAVE AND CONTINUE'")
    print("   - Em 'Scopes':")
    print("     * Clique 'ADD OR REMOVE SCOPES'")
    print("     * Procure: gmail.send")
    print("     * Selecione: .../auth/gmail.send")
    print("     * Clique 'UPDATE' > 'SAVE AND CONTINUE'")
    print("   - Em 'Test users':")
    print("     * Clique 'ADD USERS'")
    print("     * Adicione: l.moncaosilva@gmail.com")
    print("     * Clique 'ADD' > Continue ate finalizar")
    print()
    input("   Pressione ENTER quando tiver configurado o OAuth consent screen...")
    
    print()
    print("4. Vou abrir a pagina para criar credenciais...")
    time.sleep(1)
    webbrowser.open('https://console.cloud.google.com/apis/credentials')
    print()
    print("   - Clique 'CREATE CREDENTIALS' > 'OAuth client ID'")
    print("   - Application type: Desktop app")
    print("   - Name: MONPEC Gmail")
    print("   - Clique 'CREATE'")
    print("   - Clique no icone de download (seta para baixo) para baixar o JSON")
    print("   - Salve como: gmail_credentials.json")
    print("   - Mova para a raiz do projeto (mesma pasta deste script)")
    print()
    print(f"   Caminho correto: {BASE_DIR / 'gmail_credentials.json'}")
    print()
    input("   Pressione ENTER quando tiver colocado gmail_credentials.json na raiz do projeto...")
    
    # Verificar se arquivo existe
    if not credentials_path.exists():
        print()
        print("[ERRO] Arquivo gmail_credentials.json ainda nao encontrado!")
        print(f"       Por favor, coloque o arquivo em: {BASE_DIR}")
        print()
        resposta = input("Tentar novamente? (S/N): ")
        if resposta.upper() == 'S':
            return main()
        else:
            print("Cancelado. Execute novamente quando tiver o arquivo.")
            return
    else:
        print()
        print("[OK] Arquivo gmail_credentials.json encontrado!")
    
    print()
    print("=" * 70)
    print("  PASSO FINAL: Autenticar com Google")
    print("=" * 70)
    print()
    print("Agora vou executar o script de autenticacao...")
    print("O navegador vai abrir para voce autorizar o acesso.")
    print()
    input("Pressione ENTER para continuar...")
    
    # Executar autenticação
    try:
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, 'autenticar_gmail.py'],
            cwd=str(BASE_DIR),
            capture_output=False
        )
        
        if result.returncode == 0:
            print()
            print("[OK] Autenticacao concluida!")
        else:
            print()
            print("[AVISO] Houve algum problema. Tente executar manualmente:")
            print("        python autenticar_gmail.py")
            
    except Exception as e:
        print()
        print(f"[ERRO] Erro ao executar autenticacao: {e}")
        print()
        print("Execute manualmente:")
        print("  python autenticar_gmail.py")
    
    print()
    print("=" * 70)
    print("  CONCLUIDO!")
    print("=" * 70)
    print()
    print("Verificando arquivos...")
    print()
    
    token_path = BASE_DIR / 'gmail_token.json'
    env_file = BASE_DIR / '.env'
    
    print(f"  Credenciais: {'[OK]' if credentials_path.exists() else '[FALTANDO]'}")
    print(f"  Token: {'[OK]' if token_path.exists() else '[FALTANDO]'}")
    print(f"  .env: {'[OK]' if env_file.exists() else '[FALTANDO]'}")
    print()
    
    if credentials_path.exists() and token_path.exists():
        print("Tudo configurado! Reinicie o servidor Django e teste criando")
        print("um convite de cotacao. Os emails serao enviados automaticamente!")
    else:
        print("Faltam alguns arquivos. Verifique os passos acima.")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()



































