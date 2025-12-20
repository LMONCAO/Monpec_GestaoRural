#!/usr/bin/env python
"""
Script de diagnóstico para verificar configuração de e-mail
Execute: python diagnosticar_email.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings

def diagnosticar_email():
    """Diagnostica a configuração de e-mail"""
    
    print("=" * 60)
    print("  DIAGNÓSTICO DE CONFIGURAÇÃO DE E-MAIL - MONPEC")
    print("=" * 60)
    print()
    
    # Verificar se arquivo .env existe
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_exists = os.path.exists(env_file)
    
    print("📁 Verificando arquivo .env...")
    if env_exists:
        print(f"   ✅ Arquivo .env encontrado: {env_file}")
        print()
        print("   📄 Conteúdo do arquivo .env:")
        print("   " + "-" * 56)
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                for i, linha in enumerate(linhas, 1):
                    # Ocultar senhas
                    if 'PASSWORD' in linha.upper() and '=' in linha:
                        partes = linha.split('=', 1)
                        if len(partes) == 2:
                            print(f"   {i:2d}. {partes[0]}={'*' * min(20, len(partes[1].strip()))}")
                        else:
                            print(f"   {i:2d}. {linha.rstrip()}")
                    else:
                        print(f"   {i:2d}. {linha.rstrip()}")
        except Exception as e:
            print(f"   ❌ Erro ao ler arquivo: {e}")
    else:
        print(f"   ❌ Arquivo .env NÃO encontrado em: {env_file}")
        print("   ⚠️  O sistema está usando valores padrão do settings.py")
    print()
    
    # Verificar configurações atuais
    print("⚙️  Configurações atuais do Django:")
    print("   " + "-" * 56)
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or '(não configurado)'}")
    print(f"   EMAIL_HOST_PASSWORD: {'*' * 20 if settings.EMAIL_HOST_PASSWORD else '(não configurado)'}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   SITE_URL: {getattr(settings, 'SITE_URL', '(não configurado)')}")
    print()
    
    # Diagnóstico
    print("🔍 DIAGNÓSTICO:")
    print("   " + "-" * 56)
    
    problemas = []
    avisos = []
    
    # Verificar backend
    if 'console' in settings.EMAIL_BACKEND.lower():
        problemas.append("❌ PROBLEMA CRÍTICO: Usando backend de CONSOLE!")
        problemas.append("   Os e-mails estão sendo apenas impressos no terminal,")
        problemas.append("   não estão sendo enviados de verdade!")
        problemas.append("")
        problemas.append("   SOLUÇÃO: Configure EMAIL_BACKEND no .env:")
        problemas.append("   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
    elif 'smtp' in settings.EMAIL_BACKEND.lower():
        print("   ✅ Backend SMTP configurado corretamente")
    else:
        avisos.append(f"   ⚠️  Backend desconhecido: {settings.EMAIL_BACKEND}")
    
    print()
    
    # Verificar credenciais
    if 'smtp' in settings.EMAIL_BACKEND.lower():
        if not settings.EMAIL_HOST_USER:
            problemas.append("❌ EMAIL_HOST_USER não configurado")
        else:
            print(f"   ✅ EMAIL_HOST_USER configurado: {settings.EMAIL_HOST_USER}")
        
        if not settings.EMAIL_HOST_PASSWORD:
            problemas.append("❌ EMAIL_HOST_PASSWORD não configurado")
        else:
            print(f"   ✅ EMAIL_HOST_PASSWORD configurado")
        
        if not settings.EMAIL_HOST or settings.EMAIL_HOST == 'localhost':
            avisos.append("   ⚠️  EMAIL_HOST pode estar incorreto")
        else:
            print(f"   ✅ EMAIL_HOST: {settings.EMAIL_HOST}")
    
    print()
    
    # Mostrar problemas
    if problemas:
        print("🚨 PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(problema)
        print()
    
    # Mostrar avisos
    if avisos:
        print("⚠️  AVISOS:")
        for aviso in avisos:
            print(aviso)
        print()
    
    # Verificar variáveis de ambiente
    print("🌍 Variáveis de ambiente do sistema:")
    print("   " + "-" * 56)
    env_vars = [
        'EMAIL_BACKEND',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'DEFAULT_FROM_EMAIL',
        'SITE_URL'
    ]
    
    env_encontradas = False
    for var in env_vars:
        valor = os.getenv(var)
        if valor:
            env_encontradas = True
            if 'PASSWORD' in var:
                print(f"   {var}: {'*' * 20}")
            else:
                print(f"   {var}: {valor}")
    
    if not env_encontradas:
        print("   (Nenhuma variável de ambiente encontrada)")
    print()
    
    # Recomendações
    print("💡 RECOMENDAÇÕES:")
    print("   " + "-" * 56)
    
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("   1. Crie um arquivo .env na raiz do projeto")
        print("   2. Adicione as configurações de e-mail (veja COMO_CONFIGURAR_EMAIL_REAL.md)")
        print("   3. Reinicie o servidor Django")
        print("   4. Execute: python testar_email.py")
    elif not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("   1. Configure EMAIL_HOST_USER e EMAIL_HOST_PASSWORD no .env")
        print("   2. Para Gmail, use uma Senha de App (não a senha normal)")
        print("   3. Reinicie o servidor Django")
    else:
        print("   1. Execute: python testar_email.py para testar o envio")
        print("   2. Verifique os logs do terminal onde o servidor está rodando")
        print("   3. Verifique a pasta de spam do e-mail de destino")
    
    print()
    print("=" * 60)
    
    return len(problemas) == 0

if __name__ == '__main__':
    diagnosticar_email()


