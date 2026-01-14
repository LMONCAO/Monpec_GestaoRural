#!/usr/bin/env python
"""
SCRIPT PARA GERAR E CONFIGURAR SECRETS DO GITHUB
Gera valores seguros e mostra como configurar no GitHub
"""

import os
import json
import secrets
import string
from pathlib import Path

def gerar_secret_key():
    """Gera uma SECRET_KEY segura para Django"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(50))

def main():
    print("🔐 CONFIGURAÇÃO DE SECRETS PARA GITHUB")
    print("=" * 60)

    # Gerar secrets
    secrets_config = {
        'DJANGO_SECRET_KEY': gerar_secret_key(),
        'MERCADOPAGO_ACCESS_TOKEN': 'YOUR_MERCADOPAGO_ACCESS_TOKEN_HERE',
        'EMAIL_HOST_PASSWORD': 'YOUR_GMAIL_APP_PASSWORD_HERE',
        'CONSULTOR_TELEFONE': '67999688561',
        'GCP_SA_KEY': 'YOUR_GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON_HERE'
    }

    # Salvar em arquivo local (não commitar!)
    secrets_file = Path('github_secrets_local.json')
    with open(secrets_file, 'w', encoding='utf-8') as f:
        json.dump(secrets_config, f, indent=2, ensure_ascii=False)

    print("📝 SECRETS GERADOS (arquivo local: github_secrets_local.json)")
    print("\n" + "=" * 60)
    print("🔑 CONFIGURE ESTES SECRETS NO GITHUB:")
    print("📍 GitHub → Seu Repositório → Settings → Secrets and variables → Actions")
    print()

    for key, value in secrets_config.items():
        print(f"🔹 {key}")
        if key == 'DJANGO_SECRET_KEY':
            print(f"   Valor: {value}")
        elif key == 'CONSULTOR_TELEFONE':
            print(f"   Valor: {value}")
        else:
            print(f"   Valor: [COLE AQUI O SEU {key}]")
        print()

    print("📋 GUIA DE CONFIGURAÇÃO DETALHADA:")
    print("=" * 60)

    print("\n1️⃣ GCP_SA_KEY (Google Cloud Service Account):")
    print("   • Vá para Google Cloud Console")
    print("   • IAM & Admin → Service Accounts")
    print("   • Crie uma conta de serviço ou use existente")
    print("   • Keys → Add Key → JSON")
    print("   • Copie TODO o conteúdo do arquivo JSON")
    print("   • Cole como valor do secret GCP_SA_KEY")

    print("\n2️⃣ MERCADOPAGO_ACCESS_TOKEN:")
    print("   • Vá para Mercado Pago Dashboard")
    print("   • Aplicações → Sua aplicação")
    print("   • Produção → Access Token")
    print("   • Copie o access token de produção")

    print("\n3️⃣ EMAIL_HOST_PASSWORD:")
    print("   • Vá para Gmail → Configurações")
    print("   • Segurança → Senhas de app")
    print("   • Gere uma senha para 'MONPEC'")
    print("   • Use essa senha (sem espaços)")

    print("\n4️⃣ CONSULTOR_TELEFONE:")
    print("   • Já configurado: 67999688561")
    print("   • Número do WhatsApp do consultor")

    print("\n5️⃣ DJANGO_SECRET_KEY:")
    print("   • Já gerada automaticamente")
    print("   • Copie do arquivo github_secrets_local.json")

    print("\n" + "=" * 60)
    print("✅ APÓS CONFIGURAR TODOS OS SECRETS:")
    print("   • Faça um push para a branch master/main")
    print("   • O GitHub Actions fará o deploy automático")
    print("   • Monitore o progresso na aba 'Actions'")

    print("\n🔍 PARA VERIFICAR O DEPLOY:")
    print("   • GitHub → Actions → Último workflow")
    print("   • Ver logs detalhados de cada step")
    print("   • URL do serviço aparecerá nos logs")

    print("\n📞 SUPORTE:")
    print("   📱 WhatsApp: (67) 99968-8561")
    print("   📧 Email: l.moncaosilva@gmail.com")

    print("\n" + "⚠️  IMPORTANTE:")
    print("   • NUNCA commite o arquivo github_secrets_local.json")
    print("   • Os secrets são criptografados no GitHub")
    print("   • Apenas pessoas com acesso admin podem ver os valores")

    # Avisar sobre arquivo local
    print(f"\n📁 ARQUIVO CRIADO: {secrets_file}")
    print("   🔒 Este arquivo contém dados sensíveis!")
    print("   🔒 NÃO faça commit dele!")
    print("   🗑️ Apague após configurar os secrets no GitHub!")

if __name__ == '__main__':
    main()