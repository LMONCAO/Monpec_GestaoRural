# -*- coding: utf-8 -*-
"""
Comando para garantir que o sistema está configurado corretamente:
- Aplica migrations pendentes
- Cria usuário demo
- Verifica tabelas críticas
- Verifica templates
- Verifica permissões de arquivos
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from django.conf import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Garante que o sistema está configurado corretamente (migrations, usuário demo, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Pular aplicação de migrations',
        )
        parser.add_argument(
            '--skip-demo-user',
            action='store_true',
            help='Pular criação do usuário demo',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('CONFIGURANDO SISTEMA MONPEC'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        sucesso = True
        
        # 1. Aplicar migrations
        if not options['skip_migrations']:
            self.stdout.write('\n1. Aplicando migrations...')
            try:
                call_command('migrate', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS('✅ Migrations aplicadas'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao aplicar migrations: {e}'))
                sucesso = False
        
        # 2. Verificar tabelas críticas
        self.stdout.write('\n2. Verificando tabelas críticas...')
        try:
            with connection.cursor() as cursor:
                if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        AND table_name IN (
                            'auth_user',
                            'gestao_rural_produtorrural',
                            'gestao_rural_propriedade',
                            'gestao_rural_usuarioativo',
                            'django_migrations'
                        );
                    """)
                else:  # SQLite
                    cursor.execute("""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table' 
                        AND name IN (
                            'auth_user',
                            'gestao_rural_produtorrural',
                            'gestao_rural_propriedade',
                            'gestao_rural_usuarioativo',
                            'django_migrations'
                        );
                    """)
                
                tabelas = [row[0] for row in cursor.fetchall()]
                tabelas_esperadas = [
                    'auth_user',
                    'gestao_rural_produtorrural',
                    'gestao_rural_propriedade',
                    'gestao_rural_usuarioativo',
                    'django_migrations'
                ]
                
                faltando = [t for t in tabelas_esperadas if t not in tabelas]
                if faltando:
                    self.stdout.write(self.style.WARNING(f'⚠️ Tabelas faltando: {", ".join(faltando)}'))
                    self.stdout.write(self.style.WARNING('   Aplicando migrations novamente...'))
                    call_command('migrate', verbosity=0, interactive=False)
                else:
                    self.stdout.write(self.style.SUCCESS('✅ Todas as tabelas críticas existem'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar tabelas: {e}'))
            sucesso = False
        
        # 3. Criar usuário demo
        if not options['skip_demo_user']:
            self.stdout.write('\n3. Verificando usuário demo...')
            try:
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
                    self.stdout.write(self.style.SUCCESS('✅ Usuário demo_monpec criado!'))
                else:
                    if not demo_user.check_password('demo123'):
                        demo_user.set_password('demo123')
                        demo_user.save()
                        self.stdout.write(self.style.SUCCESS('✅ Senha do usuário demo atualizada!'))
                    else:
                        self.stdout.write(self.style.SUCCESS('✅ Usuário demo já existe e está configurado!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao criar usuário demo: {e}'))
                sucesso = False
        
        # 4. Verificar templates
        self.stdout.write('\n4. Verificando templates...')
        try:
            base_dir = Path(settings.BASE_DIR)
            templates_dir = base_dir / 'templates'
            
            templates_necessarios = [
                'gestao_rural/demo/demo_loading.html',
                'gestao_rural/demo_setup.html',
                'gestao_rural/login_clean.html',
            ]
            
            todos_ok = True
            for template_path in templates_necessarios:
                template_file = templates_dir / template_path
                if not template_file.exists():
                    self.stdout.write(self.style.WARNING(f'⚠️ Template não encontrado: {template_path}'))
                    todos_ok = False
            
            if todos_ok:
                self.stdout.write(self.style.SUCCESS('✅ Todos os templates necessários existem'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar templates: {e}'))
            sucesso = False
        
        # 5. Verificar permissões de arquivos
        self.stdout.write('\n5. Verificando diretórios e permissões...')
        try:
            base_dir = Path(settings.BASE_DIR)
            diretorios = [
                settings.MEDIA_ROOT,
                settings.STATIC_ROOT,
            ]
            
            todos_ok = True
            for diretorio in diretorios:
                dir_path = Path(diretorio)
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    # Testar escrita
                    test_file = dir_path / '.test_write'
                    test_file.write_text('test')
                    test_file.unlink()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Erro em {dir_path}: {e}'))
                    todos_ok = False
            
            if todos_ok:
                self.stdout.write(self.style.SUCCESS('✅ Diretórios e permissões OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao verificar permissões: {e}'))
            sucesso = False
        
        # Resumo
        self.stdout.write('\n' + '=' * 60)
        if sucesso:
            self.stdout.write(self.style.SUCCESS('✅ SISTEMA CONFIGURADO COM SUCESSO!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ ALGUNS PROBLEMAS FORAM ENCONTRADOS'))
        self.stdout.write('=' * 60)
        
        return 0 if sucesso else 1

