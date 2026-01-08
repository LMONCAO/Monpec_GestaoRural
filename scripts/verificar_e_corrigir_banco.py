#!/usr/bin/env python
"""
Script para verificar e corrigir tabelas faltantes no banco de dados
Execute via: python verificar_e_corrigir_banco.py
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def verificar_tabela_existe(nome_tabela):
    """Verifica se uma tabela existe"""
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [nome_tabela])
            elif connection.vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?;
                """, [nome_tabela])
            else:
                cursor.execute("SHOW TABLES LIKE %s", [nome_tabela])
            
            return cursor.fetchone() is not None
    except Exception as e:
        print(f'⚠️ Erro ao verificar tabela {nome_tabela}: {e}')
        return False

def main():
    print('=' * 60)
    print('🔍 VERIFICAÇÃO E CORREÇÃO DO BANCO DE DADOS')
    print('=' * 60)
    print()
    
    # 1. Executar makemigrations para garantir que não há novas migrations pendentes
    print('📝 1. Verificando migrations pendentes...')
    try:
        call_command('makemigrations', interactive=False)
        print('✅ Makemigrations executado')
    except Exception as e:
        print(f'⚠️ Erro ao executar makemigrations: {e}')
    
    # 2. Executar migrate para aplicar todas as migrations
    print()
    print('🔄 2. Aplicando todas as migrations...')
    try:
        call_command('migrate', interactive=False, verbosity=1)
        print('✅ Migrations aplicadas com sucesso')
    except Exception as e:
        print(f'❌ Erro ao aplicar migrations: {e}')
        return False
    
    # 3. Verificar tabelas críticas
    print()
    print('🔍 3. Verificando tabelas críticas...')
    tabelas_criticas = [
        'gestao_rural_produtorrural',
        'gestao_rural_propriedade',
        'gestao_rural_categoriaanimal',
        'gestao_rural_inventariorebanho',
        'gestao_rural_assinaturacliente',
        'gestao_rural_tenantusuario',
        'gestao_rural_usuarioativo',
        'django_migrations',
    ]
    
    tabelas_faltantes = []
    for tabela in tabelas_criticas:
        existe = verificar_tabela_existe(tabela)
        if existe:
            print(f'✅ {tabela} - OK')
        else:
            print(f'❌ {tabela} - FALTANDO')
            tabelas_faltantes.append(tabela)
    
    if tabelas_faltantes:
        print()
        print(f'⚠️ ATENÇÃO: {len(tabelas_faltantes)} tabela(s) faltando!')
        print('Tabelas faltantes:')
        for tabela in tabelas_faltantes:
            print(f'  - {tabela}')
        print()
        print('💡 Execute as migrations novamente ou verifique os erros acima.')
        return False
    else:
        print()
        print('✅ Todas as tabelas críticas existem!')
    
    # 4. Verificar estrutura do banco
    print()
    print('🔍 4. Verificando estrutura do banco...')
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'gestao_rural_%';
                """)
                count = cursor.fetchone()[0]
                print(f'✅ Encontradas {count} tabelas do app gestao_rural')
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'gestao_rural_%';
                """)
                count = cursor.fetchone()[0]
                print(f'✅ Encontradas {count} tabelas do app gestao_rural')
    except Exception as e:
        print(f'⚠️ Erro ao verificar estrutura: {e}')
    
    print()
    print('=' * 60)
    print('✅ VERIFICAÇÃO CONCLUÍDA!')
    print('=' * 60)
    return True

if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)


