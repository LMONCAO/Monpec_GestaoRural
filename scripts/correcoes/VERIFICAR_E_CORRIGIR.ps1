# ==========================================
# VERIFICAR E CORRIGIR PROBLEMAS
# Sistema MONPEC - Gestão Rural
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 VERIFICANDO E CORRIGINDO PROBLEMAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

$pythonCmd = "python"
if (Test-Path "python311\python.exe") {
    $pythonCmd = "python311\python.exe"
}

# Carregar variáveis
if (Test-Path ".env_producao") {
    Get-Content ".env_producao" | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

if (-not $env:SECRET_KEY) {
    $env:SECRET_KEY = "YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
}
$env:DJANGO_SETTINGS_MODULE = "sistema_rural.settings_producao"
$env:DEBUG = "False"

$erros = @()

# 1. Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
try {
    $version = & $pythonCmd --version 2>&1
    Write-Host "✅ $version" -ForegroundColor Green
} catch {
    $erros += "Python não encontrado"
    Write-Host "❌ Python não encontrado" -ForegroundColor Red
}
Write-Host ""

# 2. Verificar dependências
Write-Host "[2/6] Verificando dependências..." -ForegroundColor Yellow
try {
    & $pythonCmd -c "import django; print(f'Django {django.__version__}')" 2>&1
    Write-Host "✅ Django instalado" -ForegroundColor Green
} catch {
    $erros += "Django não instalado"
    Write-Host "❌ Django não instalado. Execute: pip install -r requirements.txt" -ForegroundColor Red
}
Write-Host ""

# 3. Verificar banco de dados
Write-Host "[3/6] Verificando banco de dados..." -ForegroundColor Yellow
try {
    $result = & $pythonCmd manage.py check --database default --settings=sistema_rural.settings_producao 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Banco de dados OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Problemas detectados no banco:" -ForegroundColor Yellow
        Write-Host $result -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Não foi possível verificar o banco: $_" -ForegroundColor Yellow
}
Write-Host ""

# 4. Verificar migrações pendentes
Write-Host "[4/6] Verificando migrações..." -ForegroundColor Yellow
try {
    $migrations = & $pythonCmd manage.py showmigrations --settings=sistema_rural.settings_producao 2>&1 | Select-String "\[ \]"
    if ($migrations) {
        Write-Host "⚠️  Migrações pendentes encontradas:" -ForegroundColor Yellow
        $migrations | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        Write-Host ""
        Write-Host "   Aplicando migrações..." -ForegroundColor Yellow
        & $pythonCmd manage.py migrate --settings=sistema_rural.settings_producao --noinput
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Migrações aplicadas" -ForegroundColor Green
        }
    } else {
        Write-Host "✅ Todas as migrações aplicadas" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Erro ao verificar migrações: $_" -ForegroundColor Yellow
}
Write-Host ""

# 5. Verificar arquivos estáticos
Write-Host "[5/6] Verificando arquivos estáticos..." -ForegroundColor Yellow
if (Test-Path "staticfiles") {
    $staticCount = (Get-ChildItem -Path "staticfiles" -Recurse -File | Measure-Object).Count
    Write-Host "✅ $staticCount arquivos estáticos encontrados" -ForegroundColor Green
} else {
    Write-Host "⚠️  Diretório staticfiles não encontrado" -ForegroundColor Yellow
    Write-Host "   Coletando arquivos estáticos..." -ForegroundColor Yellow
    & $pythonCmd manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
}
Write-Host ""

# 6. Verificar configurações
Write-Host "[6/6] Verificando configurações..." -ForegroundColor Yellow
try {
    $check = & $pythonCmd manage.py check --settings=sistema_rural.settings_producao 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Configurações OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Avisos nas configurações:" -ForegroundColor Yellow
        Write-Host $check -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Erro ao verificar configurações: $_" -ForegroundColor Yellow
}
Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
if ($erros.Count -eq 0) {
    Write-Host "✅ SISTEMA PRONTO PARA USO!" -ForegroundColor Green
} else {
    Write-Host "⚠️  PROBLEMAS ENCONTRADOS:" -ForegroundColor Yellow
    $erros | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
















