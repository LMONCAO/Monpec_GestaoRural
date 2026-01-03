#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para testar criação de usuário demo e identificar problemas
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection, transaction
from gestao_rural.models_auditoria import UsuarioAtivo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_criacao_completa():
    """Testa criação completa de usuário demo"""
    print("=" * 70)
    print("TESTE COMPLETO DE CRIAÇÃO DE USUÁRIO DEMO")
    print("=" * 70)
    
    email = 'lljkkk@yhhh.com.br'
    nome_completo = 'kkkkk'
    telefone = '67993092123'
    
    print(f"\n📧 Email: {email}")
    print(f"👤 Nome: {nome_completo}")
    print(f"📱 Telefone: {telefone}")
    
    # 1. Verificar conexão com banco
    print("\n1️⃣ Verificando conexão com banco de dados...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão com banco OK")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    # 2. Verificar se usuário já existe
    print(f"\n2️⃣ Verificando se usuário já existe...")
    user_existente = User.objects.filter(email__iexact=email).first()
    if user_existente:
        print(f"✅ Usuário já existe: {user_existente.username} (ID: {user_existente.id})")
        print(f"   Ativo: {user_existente.is_active}")
        print(f"   Email: {user_existente.email}")
    else:
        print("   Usuário não existe, será criado")
    
    # 3. Tentar criar/atualizar usuário
    print(f"\n3️⃣ Criando/atualizando usuário...")
    try:
        with transaction.atomic():
            user = User.objects.filter(email__iexact=email).first()
            
            if user:
                print(f"   Atualizando usuário existente...")
                user.set_password('monpec')
                user.is_active = True
                user.email = email.lower()
                user.save()
                print(f"✅ Usuário atualizado com sucesso")
            else:
                print(f"   Criando novo usuário...")
                username_base = email.split('@')[0]
                username = username_base
                sufixo = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{sufixo}"
                    sufixo += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email.lower(),
                    password='monpec',
                    first_name=nome_completo.split()[0] if nome_completo.split() else '',
                    last_name=' '.join(nome_completo.split()[1:]) if len(nome_completo.split()) > 1 else '',
                    is_active=True,
                )
                print(f"✅ Usuário criado: {username} (ID: {user.id})")
            
            # 4. Criar UsuarioAtivo
            print(f"\n4️⃣ Criando/atualizando UsuarioAtivo...")
            try:
                usuario_ativo, created = UsuarioAtivo.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'nome_completo': nome_completo,
                        'email': email.lower(),
                        'telefone': telefone,
                    }
                )
                if not created:
                    usuario_ativo.nome_completo = nome_completo
                    usuario_ativo.telefone = telefone
                    usuario_ativo.save()
                print(f"✅ UsuarioAtivo {'criado' if created else 'atualizado'}: ID {usuario_ativo.id}")
            except Exception as e:
                print(f"⚠️ Erro ao criar UsuarioAtivo: {e}")
                print("   Mas o usuário foi criado/atualizado com sucesso")
        
        # 5. Verificar se usuário foi salvo
        print(f"\n5️⃣ Verificando se usuário foi salvo corretamente...")
        user_verificado = User.objects.filter(email__iexact=email).first()
        if user_verificado:
            print(f"✅ Usuário verificado: {user_verificado.username}")
            print(f"   ID: {user_verificado.id}")
            print(f"   Email: {user_verificado.email}")
            print(f"   Ativo: {user_verificado.is_active}")
            print(f"   Senha configurada: {bool(user_verificado.password)}")
        else:
            print(f"❌ Usuário não foi encontrado após criação!")
            return False
        
        print("\n" + "=" * 70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print(f"\n📋 Credenciais:")
        print(f"   Username: {user_verificado.username}")
        print(f"   Email: {user_verificado.email}")
        print(f"   Senha: monpec")
        print(f"   Ativo: {user_verificado.is_active}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    sucesso = testar_criacao_completa()
    sys.exit(0 if sucesso else 1)

