#!/usr/bin/env python
"""
Script de diagnóstico para identificar problemas no servidor de produção.
Execute este script no servidor para identificar a causa do "Internal Server Error".
"""
import os
import sys
import platform
from pathlib import Path

# Adicionar o diretório do projeto ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("=" * 80)
print("DIAGNÓSTICO DO SISTEMA MONPEC - PRODUÇÃO")
print("=" * 80)
print()

# 1. Verificar sistema operacional
print("1. SISTEMA OPERACIONAL:")
print(f"   - Sistema: {platform.system()}")
print(f"   - Versão: {platform.release()}")
print(f"   - Arquitetura: {platform.machine()}")
print()

# 2. Verificar Python
print("2. PYTHON:")
print(f"   - Versão: {sys.version}")
print(f"   - Executável: {sys.executable}")
print()

# 3. Verificar variáveis de ambiente
print("3. VARIÁVEIS DE AMBIENTE:")
print(f"   - DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE', 'NÃO DEFINIDO')}")
print(f"   - SECRET_KEY: {'DEFINIDO' if os.getenv('SECRET_KEY') else 'NÃO DEFINIDO'}")
print(f"   - DEBUG: {os.getenv('DEBUG', 'NÃO DEFINIDO')}")
print(f"   - DB_NAME: {os.getenv('DB_NAME', 'NÃO DEFINIDO')}")
print(f"   - DB_USER: {os.getenv('DB_USER', 'NÃO DEFINIDO')}")
print(f"   - DB_HOST: {os.getenv('DB_HOST', 'NÃO DEFINIDO')}")
print()

# 4. Verificar arquivo .env_producao
print("4. ARQUIVO .env_producao:")
env_file = BASE_DIR / '.env_producao'
if env_file.exists():
    print(f"   - Arquivo existe: SIM ({env_file})")
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"   - Linhas: {len(lines)}")
            # Verificar se tem SECRET_KEY
            has_secret = any('SECRET_KEY' in line for line in lines)
            print(f"   - Contém SECRET_KEY: {'SIM' if has_secret else 'NÃO'}")
    except Exception as e:
        print(f"   - Erro ao ler arquivo: {e}")
else:
    print(f"   - Arquivo existe: NÃO ({env_file})")
print()

# 5. Tentar importar Django
print("5. DJANGO:")
try:
    import django
    print(f"   - Versão Django: {django.get_version()}")
    print(f"   - Django instalado: SIM")
except ImportError as e:
    print(f"   - Django instalado: NÃO")
    print(f"   - Erro: {e}")
    sys.exit(1)
print()

# 6. Tentar carregar settings
print("6. CONFIGURAÇÕES:")
try:
    # Tentar usar settings_producao
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_producao')
    django.setup()
    
    from django.conf import settings
    print(f"   - Settings Module: {settings.SETTINGS_MODULE}")
    print(f"   - DEBUG: {settings.DEBUG}")
    print(f"   - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   - SECRET_KEY definida: {'SIM' if settings.SECRET_KEY else 'NÃO'}")
    print(f"   - SECRET_KEY válida: {'SIM' if settings.SECRET_KEY and len(settings.SECRET_KEY) > 20 else 'NÃO'}")
    print(f"   - CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    print(f"   - Database Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"   - Database Name: {settings.DATABASES['default'].get('NAME', 'N/A')}")
except Exception as e:
    print(f"   - ERRO ao carregar settings: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# 7. Verificar banco de dados
print("7. BANCO DE DADOS:")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"   - Conexão: OK")
        print(f"   - Teste de query: OK")
except Exception as e:
    print(f"   - ERRO na conexão: {e}")
    import traceback
    traceback.print_exc()
print()

# 8. Verificar migrações
print("8. MIGRAÇÕES:")
try:
    from django.core.management import call_command
    from io import StringIO
    output = StringIO()
    call_command('showmigrations', '--list', stdout=output, no_color=True)
    migrations = output.getvalue()
    print(f"   - Migrações pendentes: {'SIM' if '[ ]' in migrations else 'NÃO'}")
    if '[ ]' in migrations:
        print("   - ATENÇÃO: Existem migrações pendentes!")
        # Mostrar apenas as pendentes
        pending = [line for line in migrations.split('\n') if '[ ]' in line]
        for line in pending[:5]:  # Mostrar apenas as 5 primeiras
            print(f"     {line.strip()}")
        if len(pending) > 5:
            print(f"     ... e mais {len(pending) - 5} migrações pendentes")
except Exception as e:
    print(f"   - ERRO ao verificar migrações: {e}")
print()

# 9. Verificar arquivos estáticos
print("9. ARQUIVOS ESTÁTICOS:")
try:
    static_root = Path(settings.STATIC_ROOT)
    print(f"   - STATIC_ROOT: {static_root}")
    print(f"   - Diretório existe: {'SIM' if static_root.exists() else 'NÃO'}")
    if static_root.exists():
        files = list(static_root.rglob('*'))
        print(f"   - Arquivos estáticos: {len([f for f in files if f.is_file()])}")
except Exception as e:
    print(f"   - ERRO: {e}")
print()

# 10. Verificar logs
print("10. LOGS:")
try:
    if hasattr(settings, 'LOGGING') and 'handlers' in settings.LOGGING:
        for handler_name, handler_config in settings.LOGGING.get('handlers', {}).items():
            if 'filename' in handler_config:
                log_file = Path(handler_config['filename'])
                print(f"   - {handler_name}: {log_file}")
                if log_file.exists():
                    print(f"     - Existe: SIM")
                    print(f"     - Tamanho: {log_file.stat().st_size} bytes")
                    # Mostrar últimas 5 linhas
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            if lines:
                                print(f"     - Últimas linhas:")
                                for line in lines[-5:]:
                                    print(f"       {line.strip()}")
                    except Exception as e:
                        print(f"     - Erro ao ler: {e}")
                else:
                    print(f"     - Existe: NÃO")
except Exception as e:
    print(f"   - ERRO: {e}")
print()

# 11. Verificar WSGI
print("11. WSGI:")
try:
    from sistema_rural import wsgi
    print(f"   - WSGI module: OK")
    print(f"   - Application: {type(wsgi.application).__name__}")
except Exception as e:
    print(f"   - ERRO: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 80)
print("DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)
print()
print("PRÓXIMOS PASSOS:")
print("1. Se houver erros acima, corrija-os primeiro")
print("2. Se houver migrações pendentes, execute: python manage.py migrate --settings=sistema_rural.settings_producao")
print("3. Se arquivos estáticos estiverem faltando, execute: python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput")
print("4. Verifique os logs para mais detalhes sobre o erro específico")
print()









