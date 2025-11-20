# Script de verificação pré-deploy (PowerShell)
Write-Host "🔍 VERIFICAÇÃO PRÉ-DEPLOY - MONPEC" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está na pasta correta
Write-Host "📁 Verificando estrutura de arquivos..." -ForegroundColor Yellow

$errors = @()

if (Test-Path "manage.py") {
    Write-Host "✅ manage.py encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ manage.py NÃO encontrado - você está na pasta errada!" -ForegroundColor Red
    $errors += "manage.py"
}

if (Test-Path "Dockerfile") {
    Write-Host "✅ Dockerfile encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Dockerfile NÃO encontrado" -ForegroundColor Red
    $errors += "Dockerfile"
}

if (Test-Path "requirements_producao.txt") {
    Write-Host "✅ requirements_producao.txt encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ requirements_producao.txt NÃO encontrado" -ForegroundColor Red
    $errors += "requirements_producao.txt"
}

if (Test-Path "sistema_rural/settings_gcp.py") {
    Write-Host "✅ settings_gcp.py encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ settings_gcp.py NÃO encontrado" -ForegroundColor Red
    $errors += "settings_gcp.py"
}

# Verificar gcloud
Write-Host ""
Write-Host "🔧 Verificando gcloud CLI..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "✅ gcloud CLI instalado" -ForegroundColor Green
    Write-Host "   $gcloudVersion" -ForegroundColor Gray
} catch {
    Write-Host "❌ gcloud CLI NÃO encontrado" -ForegroundColor Red
    Write-Host "   Instale: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    $errors += "gcloud"
}

# Verificar autenticação
Write-Host ""
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
try {
    $auth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    if ($auth) {
        Write-Host "✅ Autenticado no Google Cloud" -ForegroundColor Green
        Write-Host "   $auth" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Não autenticado - execute: gcloud auth login" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao verificar autenticação" -ForegroundColor Yellow
}

# Verificar projeto
Write-Host ""
Write-Host "📦 Verificando projeto..." -ForegroundColor Yellow
try {
    $project = gcloud config get-value project 2>&1
    if ($project -and -not $project.ToString().Contains("ERROR")) {
        Write-Host "✅ Projeto configurado: $project" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Nenhum projeto configurado" -ForegroundColor Yellow
        Write-Host "   Configure: gcloud config set project SEU_PROJETO" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao verificar projeto" -ForegroundColor Yellow
}

# Verificar Python
Write-Host ""
Write-Host "🐍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Python não encontrado" -ForegroundColor Yellow
    }
}

# Verificar estrutura Django
Write-Host ""
Write-Host "📋 Verificando estrutura Django..." -ForegroundColor Yellow
if (Test-Path "sistema_rural") {
    Write-Host "✅ Pasta sistema_rural encontrada" -ForegroundColor Green
    
    if (Test-Path "sistema_rural/settings.py") {
        Write-Host "✅ settings.py encontrado" -ForegroundColor Green
    }
    
    if (Test-Path "sistema_rural/wsgi.py") {
        Write-Host "✅ wsgi.py encontrado" -ForegroundColor Green
    }
    
    if (Test-Path "sistema_rural/middleware.py") {
        Write-Host "✅ middleware.py encontrado" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Pasta sistema_rural NÃO encontrada" -ForegroundColor Red
    $errors += "sistema_rural"
}

# Resumo
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "📊 RESUMO DA VERIFICAÇÃO" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "✅ Todos os arquivos essenciais verificados" -ForegroundColor Green
    Write-Host "✅ Estrutura Django verificada" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Pronto para deploy!" -ForegroundColor Green
} else {
    Write-Host "❌ Erros encontrados:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "   - $error" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "⚠️  Corrija os erros antes de fazer o deploy" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📖 Próximo passo: Siga o arquivo COMECE_AGORA.md" -ForegroundColor Cyan
Write-Host ""






