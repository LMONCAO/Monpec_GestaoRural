# ==========================================
# SCRIPT DE DEPLOY E CORREÇÃO COMPLETA
# Sistema MONPEC - Gestão Rural
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY E CORREÇÃO DO SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mudar para o diretório do projeto
Set-Location $PSScriptRoot

# 1. Verificar Python
Write-Host "[1/7] Verificando Python..." -ForegroundColor Yellow
$pythonCmd = "python"
if (Test-Path "python311\python.exe") {
    $pythonCmd = "python311\python.exe"
    Write-Host "✅ Python encontrado: $pythonCmd" -ForegroundColor Green
} else {
    try {
        $pythonVersion = & python --version 2>&1
        Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python não encontrado! Instale Python 3.11 ou superior." -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# 2. Instalar/Atualizar dependências
Write-Host "[2/7] Instalando/Atualizando dependências..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade pip --quiet
& $pythonCmd -m pip install -r requirements.txt --quiet
Write-Host "✅ Dependências instaladas" -ForegroundColor Green
Write-Host ""

# 3. Configurar variáveis de ambiente
Write-Host "[3/7] Configurando variáveis de ambiente..." -ForegroundColor Yellow

# Carregar variáveis do .env_producao se existir
if (Test-Path ".env_producao") {
    Get-Content ".env_producao" | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "✅ Variáveis carregadas do .env_producao" -ForegroundColor Green
} else {
    Write-Host "⚠️  Arquivo .env_producao não encontrado" -ForegroundColor Yellow
    Write-Host "   Configurando variáveis padrão..." -ForegroundColor Yellow
    
    # Configurar variáveis mínimas necessárias
    if (-not $env:SECRET_KEY) {
        $env:SECRET_KEY = "YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
        Write-Host "   ⚠️  SECRET_KEY usando valor padrão (configure em produção!)" -ForegroundColor Yellow
    }
    
    $env:DEBUG = "False"
    $env:DJANGO_SETTINGS_MODULE = "sistema_rural.settings_producao"
}

Write-Host ""

# 4. Verificar conexão com banco de dados
Write-Host "[4/7] Verificando conexão com banco de dados..." -ForegroundColor Yellow
try {
    & $pythonCmd manage.py check --database default 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Conexão com banco de dados OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Verificação do banco retornou código $LASTEXITCODE" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Não foi possível verificar o banco (pode ser normal se ainda não existir)" -ForegroundColor Yellow
}
Write-Host ""

# 5. Aplicar migrações
Write-Host "[5/7] Aplicando migrações do banco de dados..." -ForegroundColor Yellow
try {
    & $pythonCmd manage.py migrate --settings=sistema_rural.settings_producao --noinput
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrações aplicadas com sucesso" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao aplicar migrações" -ForegroundColor Red
        Write-Host "   Tente executar manualmente: python manage.py migrate --settings=sistema_rural.settings_producao" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro ao aplicar migrações: $_" -ForegroundColor Red
}
Write-Host ""

# 6. Coletar arquivos estáticos
Write-Host "[6/7] Coletando arquivos estáticos..." -ForegroundColor Yellow
try {
    # Criar diretório de staticfiles se não existir
    $staticDir = "staticfiles"
    if (-not (Test-Path $staticDir)) {
        New-Item -ItemType Directory -Path $staticDir | Out-Null
    }
    
    & $pythonCmd manage.py collectstatic --settings=sistema_rural.settings_producao --noinput --clear
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Arquivos estáticos coletados" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Aviso ao coletar arquivos estáticos (pode ser normal)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao coletar arquivos estáticos: $_" -ForegroundColor Yellow
}
Write-Host ""

# 7. Verificar configurações
Write-Host "[7/7] Verificando configurações do sistema..." -ForegroundColor Yellow
try {
    & $pythonCmd manage.py check --settings=sistema_rural.settings_producao --deploy
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Configurações verificadas" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Alguns avisos nas configurações (verifique acima)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao verificar configurações: $_" -ForegroundColor Yellow
}
Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOY E CORREÇÃO CONCLUÍDOS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Iniciar o servidor:" -ForegroundColor White
Write-Host "   python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ou usar o script de inicialização:" -ForegroundColor White
Write-Host "   .\INICIAR_SERVIDOR.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Acessar o sistema:" -ForegroundColor White
Write-Host "   http://localhost:8000" -ForegroundColor Gray
Write-Host "   ou" -ForegroundColor Gray
Write-Host "   https://monpec.com.br" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   - Configure SECRET_KEY em produção!" -ForegroundColor Yellow
Write-Host "   - Configure variáveis de banco de dados se necessário" -ForegroundColor Yellow
Write-Host "   - Verifique os logs em caso de erro" -ForegroundColor Yellow
Write-Host ""









