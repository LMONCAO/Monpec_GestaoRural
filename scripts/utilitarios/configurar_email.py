#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar envio de emails no MONPEC
Cria ou atualiza o arquivo .env com as configurações de email
"""

import os
from pathlib import Path

def criar_arquivo_env():
    """Cria o arquivo .env com configurações de email"""
    
    base_dir = Path(__file__).parent
    env_file = base_dir / '.env'
    
    print("=" * 50)
    print("  CONFIGURAR ENVIO DE E-MAILS - MONPEC")
    print("=" * 50)
    print()
    
    # Verificar se .env já existe
    if env_file.exists():
        print("[AVISO] Arquivo .env ja existe!")
        resposta = input("Deseja adicionar/atualizar configuracoes de email? (S/N): ")
        if resposta.upper() != 'S':
            print("Operacao cancelada.")
            return
        print()
    
    print("Escolha o provedor de email:")
    print("1. Gmail (Recomendado)")
    print("2. Outlook/Hotmail")
    print("3. Yahoo Mail")
    print("4. Servidor SMTP Personalizado")
    print()
    
    opcao = input("Digite o numero da opcao (1-4): ").strip()
    
    config = {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    }
    
    if opcao == '1':
        # Gmail
        config['EMAIL_HOST'] = 'smtp.gmail.com'
        config['EMAIL_PORT'] = '587'
        config['EMAIL_USE_TLS'] = 'True'
        print()
        print("[IMPORTANTE] Para Gmail, voce precisa usar uma SENHA DE APP!")
        print("   Acesse: https://myaccount.google.com/apppasswords")
        print("   Gere uma senha de app e use ela abaixo.")
        print()
        email_user = input("Digite seu email Gmail (ex: seu-email@gmail.com): ").strip()
        email_password = input("Digite a Senha de App do Gmail: ").strip()
        config['EMAIL_HOST_USER'] = email_user
        config['EMAIL_HOST_PASSWORD'] = email_password
        config['DEFAULT_FROM_EMAIL'] = email_user
        
    elif opcao == '2':
        # Outlook
        config['EMAIL_HOST'] = 'smtp-mail.outlook.com'
        config['EMAIL_PORT'] = '587'
        config['EMAIL_USE_TLS'] = 'True'
        email_user = input("Digite seu email Outlook (ex: seu-email@outlook.com): ").strip()
        email_password = input("Digite sua senha: ").strip()
        config['EMAIL_HOST_USER'] = email_user
        config['EMAIL_HOST_PASSWORD'] = email_password
        config['DEFAULT_FROM_EMAIL'] = email_user
        
    elif opcao == '3':
        # Yahoo
        config['EMAIL_HOST'] = 'smtp.mail.yahoo.com'
        config['EMAIL_PORT'] = '587'
        config['EMAIL_USE_TLS'] = 'True'
        print()
        print("[AVISO] Para Yahoo, voce pode precisar de uma Senha de App!")
        print()
        email_user = input("Digite seu email Yahoo (ex: seu-email@yahoo.com): ").strip()
        email_password = input("Digite sua senha ou Senha de App: ").strip()
        config['EMAIL_HOST_USER'] = email_user
        config['EMAIL_HOST_PASSWORD'] = email_password
        config['DEFAULT_FROM_EMAIL'] = email_user
        
    elif opcao == '4':
        # SMTP Personalizado
        config['EMAIL_HOST'] = input("Digite o servidor SMTP (ex: mail.seudominio.com.br): ").strip()
        port = input("Digite a porta (padrão: 587): ").strip()
        config['EMAIL_PORT'] = port if port else '587'
        config['EMAIL_USE_TLS'] = 'True'
        config['EMAIL_HOST_USER'] = input("Digite o usuário SMTP (ex: noreply@seudominio.com.br): ").strip()
        config['EMAIL_HOST_PASSWORD'] = input("Digite a senha: ").strip()
        config['DEFAULT_FROM_EMAIL'] = input("Digite o email remetente (ex: noreply@seudominio.com.br): ").strip()
        
    else:
        print("Opção inválida!")
        return
    
    # Solicitar URL do site
    print()
    site_url = input("Digite a URL do site (ex: http://localhost:8000 ou https://seudominio.com.br): ").strip()
    config['SITE_URL'] = site_url if site_url else 'http://localhost:8000'
    
    # Criar conteúdo do .env
    env_content = """# ============================================
# CONFIGURACAO DE E-MAIL - MONPEC
# ============================================
# Gerado automaticamente pelo script configurar_email.py
#
# IMPORTANTE: Para Gmail, use Senha de App (não a senha normal)
# Acesse: https://myaccount.google.com/apppasswords
# ============================================

"""
    
    for key, value in config.items():
        env_content += f"{key}={value}\n"
    
    # Se .env já existe, adicionar ou atualizar apenas as linhas de email
    if env_file.exists():
        linhas_atuais = env_file.read_text(encoding='utf-8').split('\n')
        linhas_novas = []
        chaves_email = list(config.keys()) + ['SITE_URL']
        
        # Remover linhas antigas de email
        for linha in linhas_atuais:
            if not any(linha.startswith(f"{chave}=") for chave in chaves_email):
                linhas_novas.append(linha)
        
        # Adicionar novas configurações
        linhas_novas.append('')
        linhas_novas.append('# Configurações de Email')
        for key, value in config.items():
            linhas_novas.append(f"{key}={value}")
        
        env_file.write_text('\n'.join(linhas_novas), encoding='utf-8')
    else:
        env_file.write_text(env_content, encoding='utf-8')
    
    print()
    print("=" * 50)
    print("  CONFIGURACAO CONCLUIDA!")
    print("=" * 50)
    print()
    print("[OK] Arquivo .env criado/atualizado com sucesso!")
    print()
    print("Proximos passos:")
    print("1. Reinicie o servidor Django")
    print("2. Teste criando um convite de cotacao")
    print()
    print("[IMPORTANTE]")
    print("   - Para Gmail, certifique-se de usar uma Senha de App")
    print("   - Verifique a pasta de spam se o email nao chegar")
    print("   - O arquivo .env contem senhas - NAO commite no Git!")
    print()

if __name__ == '__main__':
    try:
        criar_arquivo_env()
    except KeyboardInterrupt:
        print("\n\nOperacao cancelada pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()

