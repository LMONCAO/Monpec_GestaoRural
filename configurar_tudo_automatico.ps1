# ==========================================
# Script Automático: Configurar Tudo
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Configuração Automática PostgreSQL" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar/criar arquivo .env
Write-Host "1. Verificando arquivo .env..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    if (Test-Path .env.local) {
        Copy-Item .env.local .env -Force
        Write-Host "   ✅ Arquivo .env criado a partir de .env.local" -ForegroundColor Green
    } else {
        @"
DEBUG=True
SECRET_KEY=django-insecure-dev-local-2025-temp-key
DB_NAME=monpec_db_local
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
"@ | Out-File -FilePath .env -Encoding UTF8
        Write-Host "   ✅ Arquivo .env criado com configurações padrão" -ForegroundColor Green
    }
} else {
    Write-Host "   ✅ Arquivo .env já existe" -ForegroundColor Green
}

Write-Host ""

# 2. Verificar PostgreSQL
Write-Host "2. Verificando PostgreSQL..." -ForegroundColor Yellow

# Tentar várias formas de encontrar PostgreSQL
$pgFound = $false
$pgPath = $null

# Verificar no PATH
$pgCmd = Get-Command psql -ErrorAction SilentlyContinue
if ($pgCmd) {
    $pgFound = $true
    $pgPath = $pgCmd.Source
    Write-Host "   ✅ PostgreSQL encontrado no PATH: $pgPath" -ForegroundColor Green
}

# Verificar em locais comuns
if (-not $pgFound) {
    $commonPaths = @(
        "C:\Program Files\PostgreSQL\*\bin\psql.exe",
        "C:\Program Files (x86)\PostgreSQL\*\bin\psql.exe"
    )
    
    foreach ($pathPattern in $commonPaths) {
        $found = Get-ChildItem -Path $pathPattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $pgFound = $true
            $pgPath = $found.FullName
            Write-Host "   ✅ PostgreSQL encontrado: $pgPath" -ForegroundColor Green
            # Adicionar ao PATH da sessão atual
            $binPath = Split-Path $pgPath
            $env:Path += ";$binPath"
            break
        }
    }
}

if (-not $pgFound) {
    Write-Host "   ⚠️  PostgreSQL não encontrado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Por favor, instale PostgreSQL:" -ForegroundColor White
    Write-Host "   1. Baixe de: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host "   2. Durante instalação, use senha: postgres" -ForegroundColor Gray
    Write-Host "   3. Execute este script novamente" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Ou instale via Chocolatey (como Administrador):" -ForegroundColor White
    Write-Host "   choco install postgresql --params '/Password:postgres' -y" -ForegroundColor Gray
    Write-Host ""
    
    # Tentar conectar mesmo assim (pode estar instalado mas não no PATH)
    Write-Host "   Tentando conectar mesmo assim..." -ForegroundColor Yellow
}

Write-Host ""

# 3. Tentar criar banco de dados
Write-Host "3. Criando banco de dados..." -ForegroundColor Yellow

$createDbScript = @"
import os
import sys
from decouple import config

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    db_name = config('DB_NAME', default='monpec_db_local')
    db_user = config('DB_USER', default='postgres')
    db_password = config('DB_PASSWORD', default='postgres')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE ' + db_name)
            print('SUCCESS: Banco ' + db_name + ' criado!')
        else:
            print('INFO: Banco ' + db_name + ' ja existe.')
        
        cursor.close()
        conn.close()
        print('SUCCESS: Conexao com PostgreSQL OK!')
        sys.exit(0)
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if 'Connection refused' in error_msg or 'could not connect' in error_msg.lower():
            print('ERROR: PostgreSQL nao esta rodando ou nao esta acessivel.')
            print('       Verifique se o servico PostgreSQL esta iniciado.')
        elif 'password authentication failed' in error_msg.lower():
            print('ERROR: Senha incorreta. Verifique DB_PASSWORD no arquivo .env')
        else:
            print('ERROR: ' + error_msg)
        sys.exit(1)
    except Exception as e:
        print('ERROR: ' + str(e))
        sys.exit(1)
except ImportError:
    print('ERROR: psycopg2 nao esta instalado. Execute: pip install psycopg2-binary')
    sys.exit(1)
"@

$createDbScript | Out-File -FilePath "temp_create_db.py" -Encoding UTF8
$dbResult = python temp_create_db.py 2>&1
Remove-Item temp_create_db.py -ErrorAction SilentlyContinue

if ($dbResult -match "SUCCESS") {
    Write-Host "   ✅ $dbResult" -ForegroundColor Green
    $dbOk = $true
} elseif ($dbResult -match "INFO") {
    Write-Host "   ℹ️  $dbResult" -ForegroundColor Cyan
    $dbOk = $true
} else {
    Write-Host "   ❌ $dbResult" -ForegroundColor Red
    $dbOk = $false
}

Write-Host ""

# 4. Aplicar migrações
if ($dbOk) {
    Write-Host "4. Aplicando migrações..." -ForegroundColor Yellow
    Write-Host ""
    
    python manage.py migrate
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "   ✅ Migrações aplicadas!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "   ❌ Erro ao aplicar migrações" -ForegroundColor Red
    }
} else {
    Write-Host "4. ⏭️  Pulando migrações (banco não configurado)" -ForegroundColor Yellow
}

Write-Host ""

# 5. Verificar estado final
Write-Host "5. Verificando estado final..." -ForegroundColor Yellow

$pending = (python manage.py showmigrations 2>&1 | Select-String "\[ \]").Count
if ($pending -eq 0) {
    Write-Host "   ✅ Todas as migrações foram aplicadas!" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Ainda há $pending migração(ões) pendente(s)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($dbOk) {
    Write-Host "✅ Configuração concluída!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Configuração parcial" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor White
    Write-Host "  1. Instale PostgreSQL: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host "  2. Inicie o serviço PostgreSQL" -ForegroundColor Gray
    Write-Host "  3. Execute este script novamente" -ForegroundColor Gray
}
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""


