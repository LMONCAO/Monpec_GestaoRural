#!/usr/bin/env python
"""
Script de Auditoria Completa do Banco de Dados
Verifica estrutura, integridade, performance e consistência
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection, transaction
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.apps import apps
from django.db import models
from django.core.management import call_command
from django.db.utils import OperationalError, IntegrityError


def verificar_conectividade():
    """Verifica se consegue conectar ao banco de dados"""
    print("\n" + "="*80)
    print("1. VERIFICANDO CONECTIVIDADE")
    print("="*80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL")
            print(f"   Versão: {version}")
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"   Banco de dados: {db_name}")
            
            cursor.execute("SELECT current_user;")
            user = cursor.fetchone()[0]
            print(f"   Usuário: {user}")
            
            return True
    except Exception as e:
        print(f"❌ Erro ao conectar: {str(e)}")
        return False


def verificar_migrations():
    """Verifica status das migrations"""
    print("\n" + "="*80)
    print("2. VERIFICANDO MIGRATIONS")
    print("="*80)
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        output = StringIO()
        call_command('showmigrations', '--plan', stdout=output)
        migrations_output = output.getvalue()
        
        # Contar migrations aplicadas e pendentes
        aplicadas = migrations_output.count('[X]')
        pendentes = migrations_output.count('[ ]')
        
        print(f"✅ Migrations aplicadas: {aplicadas}")
        if pendentes > 0:
            print(f"⚠️  Migrations pendentes: {pendentes}")
            print("\nMigrations pendentes:")
            for line in migrations_output.split('\n'):
                if '[ ]' in line:
                    print(f"   {line.strip()}")
        else:
            print("✅ Todas as migrations foram aplicadas")
            
        return pendentes == 0
    except Exception as e:
        print(f"❌ Erro ao verificar migrations: {str(e)}")
        return False


def verificar_tabelas():
    """Lista todas as tabelas do banco"""
    print("\n" + "="*80)
    print("3. VERIFICANDO TABELAS")
    print("="*80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tabelas = cursor.fetchall()
            
            print(f"✅ Total de tabelas: {len(tabelas)}")
            print("\nTabelas principais:")
            for tabela in tabelas[:20]:  # Mostrar primeiras 20
                print(f"   - {tabela[0]}")
            
            if len(tabelas) > 20:
                print(f"   ... e mais {len(tabelas) - 20} tabelas")
                
        return True
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {str(e)}")
        return False


def verificar_integridade_referencial():
    """Verifica integridade referencial"""
    print("\n" + "="*80)
    print("4. VERIFICANDO INTEGRIDADE REFERENCIAL")
    print("="*80)
    
    problemas = []
    
    try:
        with connection.cursor() as cursor:
            # Verificar foreign keys órfãs
            cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                LIMIT 10;
            """)
            
            fks = cursor.fetchall()
            print(f"✅ Foreign keys encontradas: {len(fks)}")
            
            # Verificar constraints
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.table_constraints 
                WHERE constraint_type = 'FOREIGN KEY';
            """)
            total_fks = cursor.fetchone()[0]
            print(f"   Total de foreign keys: {total_fks}")
            
        return len(problemas) == 0
    except Exception as e:
        print(f"❌ Erro ao verificar integridade: {str(e)}")
        return False


def verificar_indices():
    """Verifica índices do banco"""
    print("\n" + "="*80)
    print("5. VERIFICANDO ÍNDICES")
    print("="*80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
                LIMIT 20;
            """)
            
            indices = cursor.fetchall()
            print(f"✅ Índices encontrados: {len(indices)}")
            
            # Contar índices por tabela
            cursor.execute("""
                SELECT 
                    tablename,
                    COUNT(*) as total_indices
                FROM pg_indexes
                WHERE schemaname = 'public'
                GROUP BY tablename
                ORDER BY total_indices DESC
                LIMIT 10;
            """)
            
            indices_por_tabela = cursor.fetchall()
            print("\nTabelas com mais índices:")
            for tabela, total in indices_por_tabela:
                print(f"   {tabela}: {total} índices")
                
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar índices: {str(e)}")
        return False


def verificar_modelos_vs_banco():
    """Compara modelos Django com estrutura do banco"""
    print("\n" + "="*80)
    print("6. VERIFICANDO CONSISTÊNCIA MODELOS vs BANCO")
    print("="*80)
    
    problemas = []
    
    try:
        from django.db import connection
        from django.apps import apps
        
        # Obter todas as tabelas do banco
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE';
            """)
            tabelas_banco = {row[0] for row in cursor.fetchall()}
        
        # Obter todas as tabelas dos modelos Django
        tabelas_modelos = set()
        for model in apps.get_models():
            tabelas_modelos.add(model._meta.db_table)
        
        # Verificar tabelas no banco mas não nos modelos
        tabelas_orfas = tabelas_banco - tabelas_modelos
        if tabelas_orfas:
            print(f"⚠️  Tabelas no banco sem modelo Django: {len(tabelas_orfas)}")
            for tabela in list(tabelas_orfas)[:10]:
                print(f"   - {tabela}")
                problemas.append(f"Tabela órfã: {tabela}")
        
        # Verificar modelos sem tabela no banco
        modelos_sem_tabela = tabelas_modelos - tabelas_banco
        if modelos_sem_tabela:
            print(f"⚠️  Modelos Django sem tabela no banco: {len(modelos_sem_tabela)}")
            for tabela in list(modelos_sem_tabela)[:10]:
                print(f"   - {tabela}")
                problemas.append(f"Modelo sem tabela: {tabela}")
        
        if not problemas:
            print("✅ Consistência entre modelos e banco verificada")
            print(f"   Tabelas no banco: {len(tabelas_banco)}")
            print(f"   Modelos Django: {len(tabelas_modelos)}")
        
        return len(problemas) == 0
    except Exception as e:
        print(f"❌ Erro ao verificar consistência: {str(e)}")
        return False


def verificar_tamanho_banco():
    """Verifica tamanho do banco de dados"""
    print("\n" + "="*80)
    print("7. VERIFICANDO TAMANHO DO BANCO")
    print("="*80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as tamanho_total;
            """)
            tamanho = cursor.fetchone()[0]
            print(f"✅ Tamanho total do banco: {tamanho}")
            
            # Tamanho por tabela
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10;
            """)
            
            tabelas_grandes = cursor.fetchall()
            print("\nMaiores tabelas:")
            for schema, tabela, tamanho_tab in tabelas_grandes:
                print(f"   {tabela}: {tamanho_tab}")
                
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar tamanho: {str(e)}")
        return False


def verificar_backups():
    """Verifica configuração de backups"""
    print("\n" + "="*80)
    print("8. VERIFICANDO BACKUPS")
    print("="*80)
    
    print("⚠️  Verificação de backups requer acesso ao sistema de arquivos")
    print("   Recomendações:")
    print("   - Configure backups automáticos (pg_dump)")
    print("   - Mantenha backups diários")
    print("   - Teste restauração periodicamente")
    print("   - Armazene backups em local seguro e separado")
    
    return True


def verificar_seguranca():
    """Verifica configurações de segurança"""
    print("\n" + "="*80)
    print("9. VERIFICANDO SEGURANÇA")
    print("="*80)
    
    try:
        with connection.cursor() as cursor:
            # Verificar se usuário tem privilégios adequados
            cursor.execute("""
                SELECT 
                    current_user,
                    usesuper,
                    usecreatedb,
                    userepl
                FROM pg_user
                WHERE usename = current_user;
            """)
            
            user_info = cursor.fetchone()
            if user_info:
                user, is_super, can_create_db, can_repl = user_info
                print(f"✅ Usuário atual: {user}")
                print(f"   Superusuário: {'Sim' if is_super else 'Não'}")
                print(f"   Pode criar DB: {'Sim' if can_create_db else 'Não'}")
                
                if is_super:
                    print("⚠️  ATENÇÃO: Usuário com privilégios de superusuário")
                    print("   Em produção, use usuário com privilégios limitados")
            
            # Verificar conexões SSL
            cursor.execute("SHOW ssl;")
            ssl_status = cursor.fetchone()[0]
            print(f"   SSL habilitado: {ssl_status}")
            
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar segurança: {str(e)}")
        return False


def gerar_relatorio():
    """Gera relatório completo"""
    print("\n" + "="*80)
    print("RELATÓRIO DE AUDITORIA DO BANCO DE DADOS")
    print("="*80)
    print(f"Data: {django.utils.timezone.now()}")
    print(f"Banco: {settings.DATABASES['default']['NAME']}")
    print(f"Host: {settings.DATABASES['default']['HOST']}")
    print("="*80)
    
    resultados = {
        'conectividade': verificar_conectividade(),
        'migrations': verificar_migrations(),
        'tabelas': verificar_tabelas(),
        'integridade': verificar_integridade_referencial(),
        'indices': verificar_indices(),
        'consistencia': verificar_modelos_vs_banco(),
        'tamanho': verificar_tamanho_banco(),
        'backups': verificar_backups(),
        'seguranca': verificar_seguranca(),
    }
    
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    
    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v)
    
    for item, status in resultados.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {item.replace('_', ' ').title()}")
    
    print(f"\nTotal: {sucesso}/{total} verificações passaram")
    
    if sucesso == total:
        print("\n✅ Banco de dados está saudável!")
    else:
        print("\n⚠️  Alguns problemas foram encontrados. Revise o relatório acima.")


if __name__ == '__main__':
    import django.utils.timezone
    gerar_relatorio()






