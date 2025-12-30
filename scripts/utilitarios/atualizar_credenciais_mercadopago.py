#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para atualizar as credenciais do Mercado Pago no arquivo .env
"""

import os
import re
from pathlib import Path

# Credenciais de PRODUÇÃO fornecidas
MERCADOPAGO_ACCESS_TOKEN = "APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940"
MERCADOPAGO_PUBLIC_KEY = "APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3"

# Caminho do arquivo .env
env_file = Path('.env')

def atualizar_credenciais():
    """Atualiza ou adiciona as credenciais do Mercado Pago no arquivo .env"""
    
    if not env_file.exists():
        print("Arquivo .env nao encontrado!")
        print("Criando arquivo .env com as credenciais...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# Configuracoes Mercado Pago\n")
            f.write(f"MERCADOPAGO_ACCESS_TOKEN={MERCADOPAGO_ACCESS_TOKEN}\n")
            f.write(f"MERCADOPAGO_PUBLIC_KEY={MERCADOPAGO_PUBLIC_KEY}\n")
            f.write("PAYMENT_GATEWAY_DEFAULT=mercadopago\n")
        print("Arquivo .env criado com sucesso!")
        return
    
    # Ler conteúdo atual
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Atualizar ou adicionar MERCADOPAGO_ACCESS_TOKEN
    if re.search(r'^MERCADOPAGO_ACCESS_TOKEN=', content, re.MULTILINE):
        content = re.sub(
            r'^MERCADOPAGO_ACCESS_TOKEN=.*$',
            f'MERCADOPAGO_ACCESS_TOKEN={MERCADOPAGO_ACCESS_TOKEN}',
            content,
            flags=re.MULTILINE
        )
        print("MERCADOPAGO_ACCESS_TOKEN atualizado")
    else:
        # Adicionar no final do arquivo
        if not content.endswith('\n'):
            content += '\n'
        content += f"\n# Configuracoes Mercado Pago\n"
        content += f"MERCADOPAGO_ACCESS_TOKEN={MERCADOPAGO_ACCESS_TOKEN}\n"
        print("MERCADOPAGO_ACCESS_TOKEN adicionado")
    
    # Atualizar ou adicionar MERCADOPAGO_PUBLIC_KEY
    if re.search(r'^MERCADOPAGO_PUBLIC_KEY=', content, re.MULTILINE):
        content = re.sub(
            r'^MERCADOPAGO_PUBLIC_KEY=.*$',
            f'MERCADOPAGO_PUBLIC_KEY={MERCADOPAGO_PUBLIC_KEY}',
            content,
            flags=re.MULTILINE
        )
        print("MERCADOPAGO_PUBLIC_KEY atualizado")
    else:
        # Adicionar após MERCADOPAGO_ACCESS_TOKEN
        if 'MERCADOPAGO_ACCESS_TOKEN' in content:
            content = content.replace(
                f'MERCADOPAGO_ACCESS_TOKEN={MERCADOPAGO_ACCESS_TOKEN}',
                f'MERCADOPAGO_ACCESS_TOKEN={MERCADOPAGO_ACCESS_TOKEN}\nMERCADOPAGO_PUBLIC_KEY={MERCADOPAGO_PUBLIC_KEY}'
            )
        else:
            if not content.endswith('\n'):
                content += '\n'
            content += f"MERCADOPAGO_PUBLIC_KEY={MERCADOPAGO_PUBLIC_KEY}\n"
        print("MERCADOPAGO_PUBLIC_KEY adicionado")
    
    # Garantir que PAYMENT_GATEWAY_DEFAULT está configurado
    if not re.search(r'^PAYMENT_GATEWAY_DEFAULT=', content, re.MULTILINE):
        if not content.endswith('\n'):
            content += '\n'
        content += "PAYMENT_GATEWAY_DEFAULT=mercadopago\n"
        print("PAYMENT_GATEWAY_DEFAULT adicionado")
    else:
        # Atualizar para mercadopago se não estiver
        content = re.sub(
            r'^PAYMENT_GATEWAY_DEFAULT=.*$',
            'PAYMENT_GATEWAY_DEFAULT=mercadopago',
            content,
            flags=re.MULTILINE
        )
        print("PAYMENT_GATEWAY_DEFAULT atualizado")
    
    # Salvar arquivo
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\nCredenciais do Mercado Pago configuradas com sucesso!")
    print("\nResumo das configuracoes:")
    print(f"   MERCADOPAGO_ACCESS_TOKEN: {MERCADOPAGO_ACCESS_TOKEN[:20]}...")
    print(f"   MERCADOPAGO_PUBLIC_KEY: {MERCADOPAGO_PUBLIC_KEY[:20]}...")
    print(f"   PAYMENT_GATEWAY_DEFAULT: mercadopago")
    print("\nIMPORTANTE: Reinicie o servidor Django para aplicar as mudancas!")

if __name__ == '__main__':
    try:
        atualizar_credenciais()
    except Exception as e:
        print(f"Erro ao atualizar credenciais: {e}")
        import traceback
        traceback.print_exc()

