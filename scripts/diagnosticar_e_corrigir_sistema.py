#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico e correção completa do sistema
Verifica e corrige:
1. Migrations pendentes
2. Tabelas faltantes
3. Usuário demo
4. Templates
5. Permissões de arquivos
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from django.conf import settings
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verificar_tabelas():
    """Verifica quais tabelas existem no banco de dados"""
    logger.info("=" * 60)
    logger.info("VERIFICANDO TABELAS DO BANCO DE DADOS")
    logger.info("=" * 60)
    
    with connection.cursor() as cursor:
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
        else:  # SQLite
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name;
            """)
        
        tabelas = [row[0] for row in cursor.fetchall()]
        logger.info(f"Total de tabelas encontradas: {len(tabelas)}")
        
        # Verificar tabelas críticas
        tabelas_criticas = [
            'auth_user',
            'gestao_rural_produtorrural',
            'gestao_rural_propriedade',
            'gestao_rural_usuarioativo',
            'django_migrations',
        ]
        
        logger.info("\nTabelas críticas:")
        for tabela in tabelas_criticas:
            if tabela in tabelas:
                logger.info(f"  ✅ {tabela}")
            else:
                logger.warning(f"  ❌ {tabela} - FALTANDO!")
        
        return tabelas


def aplicar_migrations():
    """Aplica todas as migrations pendentes"""
    logger.info("\n" + "=" * 60)
    logger.info("APLICANDO MIGRATIONS PENDENTES")
    logger.info("=" * 60)
    
    try:
        # Verificar migrations pendentes
        logger.info("Verificando migrations pendentes...")
        call_command('showmigrations', verbosity=0)
        
        # Aplicar migrations
        logger.info("Aplicando migrations...")
        call_command('migrate', verbosity=2, interactive=False)
        
        logger.info("✅ Migrations aplicadas com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar migrations: {e}")
        return False


def verificar_usuario_demo():
    """Verifica e cria usuário demo se necessário"""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICANDO USUÁRIO DEMO")
    logger.info("=" * 60)
    
    try:
        # Verificar se tabela UsuarioAtivo existe
        from django.db import connection
        with connection.cursor() as cursor:
            if 'postgresql' in settings.DATABASES['default']['ENGINE']:
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
        
        if not tabela_existe:
            logger.warning("⚠️ Tabela UsuarioAtivo não existe. Aplicando migrations...")
            aplicar_migrations()
        
        # Verificar usuário demo padrão
        demo_user, created = User.objects.get_or_create(
            username='demo_monpec',
            defaults={
                'email': 'demo@monpec.com.br',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            logger.info("✅ Usuário demo_monpec criado com sucesso!")
        else:
            # Verificar senha
            if not demo_user.check_password('demo123'):
                demo_user.set_password('demo123')
                demo_user.save()
                logger.info("✅ Senha do usuário demo_monpec atualizada!")
            else:
                logger.info("✅ Usuário demo_monpec já existe e está configurado corretamente!")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao verificar/criar usuário demo: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def verificar_templates():
    """Verifica se os templates necessários existem"""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICANDO TEMPLATES")
    logger.info("=" * 60)
    
    base_dir = Path(settings.BASE_DIR)
    templates_dir = base_dir / 'templates'
    
    templates_necessarios = [
        'gestao_rural/demo/demo_loading.html',
        'gestao_rural/demo_setup.html',
        'gestao_rural/login_clean.html',
        'base.html',
    ]
    
    todos_ok = True
    for template_path in templates_necessarios:
        template_file = templates_dir / template_path
        if template_file.exists():
            logger.info(f"  ✅ {template_path}")
        else:
            logger.warning(f"  ❌ {template_path} - NÃO ENCONTRADO!")
            todos_ok = False
    
    return todos_ok


def verificar_permissoes_arquivos():
    """Verifica e cria diretórios necessários para arquivos"""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICANDO PERMISSÕES E DIRETÓRIOS DE ARQUIVOS")
    logger.info("=" * 60)
    
    base_dir = Path(settings.BASE_DIR)
    
    diretorios_necessarios = [
        settings.MEDIA_ROOT,
        settings.STATIC_ROOT,
        base_dir / 'staticfiles',
        base_dir / 'media',
    ]
    
    todos_ok = True
    for diretorio in diretorios_necessarios:
        dir_path = Path(diretorio)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            # Verificar permissões de escrita
            test_file = dir_path / '.test_write'
            test_file.write_text('test')
            test_file.unlink()
            logger.info(f"  ✅ {dir_path} - OK (criado/permissões OK)")
        except Exception as e:
            logger.error(f"  ❌ {dir_path} - ERRO: {e}")
            todos_ok = False
    
    return todos_ok


def verificar_migrations_aplicadas():
    """Verifica quais migrations foram aplicadas"""
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICANDO STATUS DAS MIGRATIONS")
    logger.info("=" * 60)
    
    try:
        from django.db.migrations.recorder import MigrationRecorder
        recorder = MigrationRecorder(connection)
        migrations_aplicadas = recorder.applied_migrations()
        
        logger.info(f"Total de migrations aplicadas: {len(migrations_aplicadas)}")
        
        # Verificar migrations do app gestao_rural
        migrations_gestao = [m for m in migrations_aplicadas if m[0] == 'gestao_rural']
        logger.info(f"Migrations do gestao_rural: {len(migrations_gestao)}")
        
        # Verificar última migration
        if migrations_gestao:
            ultima = max(migrations_gestao, key=lambda x: x[1])
            logger.info(f"Última migration aplicada: {ultima[1]}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao verificar migrations: {e}")
        return False


def main():
    """Função principal"""
    logger.info("\n" + "=" * 60)
    logger.info("DIAGNÓSTICO E CORREÇÃO DO SISTEMA MONPEC")
    logger.info("=" * 60)
    logger.info(f"Diretório base: {settings.BASE_DIR}")
    logger.info(f"Banco de dados: {settings.DATABASES['default']['ENGINE']}")
    logger.info(f"DEBUG: {settings.DEBUG}")
    
    resultados = {
        'tabelas': False,
        'migrations': False,
        'usuario_demo': False,
        'templates': False,
        'permissoes': False,
    }
    
    # 1. Verificar tabelas
    try:
        tabelas = verificar_tabelas()
        resultados['tabelas'] = len(tabelas) > 0
    except Exception as e:
        logger.error(f"Erro ao verificar tabelas: {e}")
    
    # 2. Aplicar migrations
    resultados['migrations'] = aplicar_migrations()
    
    # 3. Verificar migrations aplicadas
    verificar_migrations_aplicadas()
    
    # 4. Verificar usuário demo
    resultados['usuario_demo'] = verificar_usuario_demo()
    
    # 5. Verificar templates
    resultados['templates'] = verificar_templates()
    
    # 6. Verificar permissões
    resultados['permissoes'] = verificar_permissoes_arquivos()
    
    # Resumo final
    logger.info("\n" + "=" * 60)
    logger.info("RESUMO DO DIAGNÓSTICO")
    logger.info("=" * 60)
    
    for item, status in resultados.items():
        status_text = "✅ OK" if status else "❌ ERRO"
        logger.info(f"{item.upper()}: {status_text}")
    
    todos_ok = all(resultados.values())
    
    if todos_ok:
        logger.info("\n✅ SISTEMA ESTÁ CONFIGURADO CORRETAMENTE!")
    else:
        logger.warning("\n⚠️ ALGUNS PROBLEMAS FORAM ENCONTRADOS. Verifique os logs acima.")
    
    return todos_ok


if __name__ == '__main__':
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


