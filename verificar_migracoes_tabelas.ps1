# ==========================================
# Script para Verificar Migrações e Tabelas
# Compara modelos com tabelas no banco
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verificação de Migrações e Tabelas" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está usando PostgreSQL
Write-Host "1. Verificando tipo de banco de dados..." -ForegroundColor Yellow

try {
    $dbCheck = python -c "import os; from decouple import config; db_name = config('DB_NAME', default=None); print('POSTGRESQL' if db_name else 'SQLITE')" 2>&1
    if ($dbCheck -match "SQLITE") {
        Write-Host "⚠️  Usando SQLite. Para compatibilidade com Google Cloud, configure PostgreSQL." -ForegroundColor Yellow
        Write-Host "   Execute: .\configurar_postgresql_local.ps1" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "✅ Usando PostgreSQL" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Não foi possível verificar o tipo de banco" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "2. Verificando estado das migrações..." -ForegroundColor Yellow
python manage.py showmigrations | Select-String "\[ \]" | ForEach-Object {
    Write-Host "   ⚠️  Migração pendente: $_" -ForegroundColor Yellow
}

$pendingCount = (python manage.py showmigrations | Select-String "\[ \]").Count
if ($pendingCount -eq 0) {
    Write-Host "✅ Todas as migrações foram aplicadas" -ForegroundColor Green
} else {
    Write-Host "   Total de migrações pendentes: $pendingCount" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "3. Verificando tabelas no banco de dados..." -ForegroundColor Yellow

# Listar modelos do Django
Write-Host ""
Write-Host "Modelos definidos no código:" -ForegroundColor Cyan
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.apps import apps
from django.db import connection

# Listar todos os modelos
models = []
for app_config in apps.get_app_configs():
    for model in app_config.get_models():
        if hasattr(model, '_meta') and hasattr(model._meta, 'db_table'):
            models.append(model._meta.db_table)

models.sort()
for model in models:
    print(f'  - {model}')
" 2>&1

Write-Host ""
Write-Host "Tabelas no banco de dados:" -ForegroundColor Cyan

# Verificar tabelas no banco
try {
    $dbName = python -c "import os; from decouple import config; print(config('DB_NAME', default='db.sqlite3'))" 2>&1
    
    if ($dbName -match "\.sqlite3$") {
        # SQLite
        python -c "
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
db_path = BASE_DIR / 'db.sqlite3'

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name\")
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        print(f'  - {table}')
    conn.close()
else:
    print('  ⚠️  Banco SQLite não encontrado')
" 2>&1
    } else {
        # PostgreSQL
        $dbUser = python -c "import os; from decouple import config; print(config('DB_USER', default='postgres'))" 2>&1
        $dbPassword = python -c "import os; from decouple import config; print(config('DB_PASSWORD', default=''))" 2>&1
        $dbHost = python -c "import os; from decouple import config; print(config('DB_HOST', default='localhost'))" 2>&1
        $dbPort = python -c "import os; from decouple import config; print(config('DB_PORT', default='5432'))" 2>&1
        
        $env:PGPASSWORD = $dbPassword
        
        $tables = psql -U $dbUser -h $dbHost -p $dbPort -d $dbName -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $tables | ForEach-Object {
                $table = $_.Trim()
                if ($table) {
                    Write-Host "  - $table" -ForegroundColor White
                }
            }
        } else {
            Write-Host "  ❌ Erro ao conectar ao PostgreSQL" -ForegroundColor Red
            Write-Host "     Verifique as credenciais no .env.local" -ForegroundColor Yellow
        }
        
        Remove-Item Env:\PGPASSWORD
    }
} catch {
    Write-Host "  ❌ Erro ao verificar tabelas: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Verificando integridade do Django..." -ForegroundColor Yellow
python manage.py check --deploy 2>&1 | Select-Object -First 20

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verificação concluída!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se houver migrações pendentes, execute:" -ForegroundColor Yellow
Write-Host "  .\aplicar_migracoes_postgresql.ps1" -ForegroundColor White
Write-Host ""

