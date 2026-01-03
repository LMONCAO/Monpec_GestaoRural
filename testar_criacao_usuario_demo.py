#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar a criação de usuário demo e identificar problemas
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from gestao_rural.models_auditoria import UsuarioAtivo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_criacao_usuario():
    """Testa a criação de um usuário demo"""
    print("=" * 60)
    print("TESTANDO CRIAÇÃO DE USUÁRIO DEMO")
    print("=" * 60)
    
    email = 'leandro@leandro.com.br'
    nome_completo = 'leandro'
    telefone = '679999'
    
    try:
        # 1. Verificar se tabela UsuarioAtivo existe
        print("\n1. Verificando tabela UsuarioAtivo...")
        with connection.cursor() as cursor:
            if 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'gestao_rural_usuarioativo'
                    );
                """)
            else:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='gestao_rural_usuarioativo';
                """)
            
            tabela_existe = cursor.fetchone()[0] if cursor.rowcount > 0 else False
        
        if tabela_existe:
            print("✅ Tabela UsuarioAtivo existe")
        else:
            print("❌ Tabela UsuarioAtivo NÃO existe")
            print("   Aplicando migrations...")
            from django.core.management import call_command
            call_command('migrate', verbosity=0, interactive=False)
        
        # 2. Verificar se usuário já existe
        print(f"\n2. Verificando usuário com email {email}...")
        user = User.objects.filter(email__iexact=email).first()
        
        if user:
            print(f"✅ Usuário já existe: {user.username} (ID: {user.id})")
            print(f"   Ativo: {user.is_active}")
        else:
            print("   Usuário não existe, será criado")
        
        # 3. Tentar criar usuário
        print("\n3. Criando/atualizando usuário...")
        from django.db import transaction
        
        with transaction.atomic():
            if user:
                # Atualizar usuário existente
                user.set_password('monpec')
                user.is_active = True
                user.email = email.lower()
                user.save()
                print(f"✅ Usuário atualizado: {user.username}")
            else:
                # Criar novo usuário
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
            
            # 4. Tentar criar UsuarioAtivo
            print("\n4. Criando registro UsuarioAtivo...")
            try:
                usuario_ativo, created = UsuarioAtivo.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'nome_completo': nome_completo,
                        'email': email.lower(),
                        'telefone': telefone,
                    }
                )
                if created:
                    print(f"✅ UsuarioAtivo criado: ID {usuario_ativo.id}")
                else:
                    print(f"✅ UsuarioAtivo já existe: ID {usuario_ativo.id}")
            except Exception as e:
                print(f"⚠️ Erro ao criar UsuarioAtivo: {e}")
                print("   Mas o usuário foi criado com sucesso!")
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"\nCredenciais:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Senha: monpec")
        print(f"  Ativo: {user.is_active}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    sucesso = testar_criacao_usuario()
    sys.exit(0 if sucesso else 1)

