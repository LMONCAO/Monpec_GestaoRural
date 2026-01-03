# ==========================================
# Script Completo: Instalar e Configurar PostgreSQL
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Instalação e Configuração PostgreSQL" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Chocolatey está instalado
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if (-not $chocoInstalled) {
    Write-Host "⚠️  Chocolatey não encontrado." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opção 1: Instalar Chocolatey primeiro:" -ForegroundColor White
    Write-Host "  Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Opção 2: Baixar PostgreSQL manualmente:" -ForegroundColor White
    Write-Host "  https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host ""
    
    $continuar = Read-Host "Deseja instalar Chocolatey agora? (S/N)"
    if ($continuar -eq "S" -or $continuar -eq "s") {
        Write-Host ""
        Write-Host "Instalando Chocolatey..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
        if ($chocoInstalled) {
            Write-Host "✅ Chocolatey instalado!" -ForegroundColor Green
        } else {
            Write-Host "❌ Erro ao instalar Chocolatey. Tente manualmente." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "Por favor, instale PostgreSQL manualmente e execute este script novamente." -ForegroundColor Yellow
        exit 0
    }
}

# Verificar se PostgreSQL já está instalado
$pgInstalled = Get-Command psql -ErrorAction SilentlyContinue
$pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue

if (-not $pgInstalled -and -not $pgService) {
    Write-Host ""
    Write-Host "PostgreSQL não encontrado. Instalando..." -ForegroundColor Yellow
    Write-Host "  (Isso pode demorar alguns minutos)" -ForegroundColor Gray
    Write-Host ""
    
    # Instalar PostgreSQL via Chocolatey
    choco install postgresql --params '/Password:postgres' -y
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL instalado!" -ForegroundColor Green
        
        # Recarregar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Aguardar serviço iniciar
        Write-Host ""
        Write-Host "Aguardando serviço PostgreSQL iniciar..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        # Iniciar serviço
        $pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
        if ($pgService) {
            Start-Service $pgService.Name
            Write-Host "✅ Serviço PostgreSQL iniciado!" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ Erro ao instalar PostgreSQL." -ForegroundColor Red
        Write-Host "   Tente instalar manualmente: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ PostgreSQL já está instalado!" -ForegroundColor Green
    
    # Verificar se serviço está rodando
    $pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
    if ($pgService) {
        if ($pgService.Status -ne 'Running') {
            Write-Host "Iniciando serviço PostgreSQL..." -ForegroundColor Yellow
            Start-Service $pgService.Name
            Start-Sleep -Seconds 5
        }
        Write-Host "✅ Serviço PostgreSQL está rodando!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Criando banco de dados..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Criar banco de dados usando script Python separado
$createDbScript = @"
import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        host=config('DB_HOST', default='localhost'),
        port=config('DB_PORT', default='5432'),
        user=config('DB_USER', default='postgres'),
        password=config('DB_PASSWORD', default='postgres'),
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    db_name = config('DB_NAME', default='monpec_db_local')
    
    cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute('CREATE DATABASE ' + db_name)
        print('Banco ' + db_name + ' criado!')
    else:
        print('Banco ' + db_name + ' ja existe.')
    
    cursor.close()
    conn.close()
except Exception as e:
    print('Erro: ' + str(e))
"@

$createDbScript | Out-File -FilePath "temp_create_db.py" -Encoding UTF8
python temp_create_db.py 2>&1
Remove-Item temp_create_db.py -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Aplicando migrações..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migrações aplicadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro ao aplicar migrações. Verifique os erros acima." -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verificando tabelas..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

python manage.py showmigrations | Select-String "\[ \]"

$pending = (python manage.py showmigrations | Select-String "\[ \]").Count
if ($pending -eq 0) {
    Write-Host ""
    Write-Host "✅ Todas as migrações foram aplicadas!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Ainda há $pending migração(ões) pendente(s)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

