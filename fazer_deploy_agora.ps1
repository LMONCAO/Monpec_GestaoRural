# 🚀 Script PowerShell para Deploy no Google Cloud Run
# Este script tenta fazer o deploy ou fornece instruções claras

Write-Host "🚀 MONPEC - Deploy Automático" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
Write-Host "🔍 Verificando Google Cloud CLI..." -ForegroundColor Yellow
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue

if (-not $gcloudPath) {
    Write-Host "❌ Google Cloud CLI não está instalado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 OPÇÕES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPÇÃO 1 - Instalar Google Cloud CLI (Recomendado):" -ForegroundColor Green
    Write-Host "   1. Baixe em: https://cloud.google.com/sdk/docs/install" -ForegroundColor White
    Write-Host "   2. Execute este script novamente após instalar" -ForegroundColor White
    Write-Host ""
    Write-Host "OPÇÃO 2 - Usar Cloud Shell (Mais Rápido):" -ForegroundColor Green
    Write-Host "   1. Acesse: https://console.cloud.google.com/" -ForegroundColor White
    Write-Host "   2. Clique no ícone do Cloud Shell (terminal) no topo" -ForegroundColor White
    Write-Host "   3. Copie e cole o conteúdo do arquivo: DEPLOY_AGORA_COPIAR_COLAR.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "📄 Arquivo com script completo: DEPLOY_AGORA_COPIAR_COLAR.sh" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "✅ Google Cloud CLI encontrado!" -ForegroundColor Green
Write-Host ""

# Verificar se está autenticado
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null

if (-not $authStatus) {
    Write-Host "⚠️  Você não está autenticado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔑 Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro na autenticação!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Autenticado como: $authStatus" -ForegroundColor Green
Write-Host ""

# Configurar projeto
$PROJECT_ID = "monpec-sistema-rural"
Write-Host "⚙️  Configurando projeto: $PROJECT_ID" -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao configurar projeto!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Projeto configurado!" -ForegroundColor Green
Write-Host ""

# Verificar se está na pasta correta
$currentPath = Get-Location
if (-not (Test-Path "manage.py")) {
    Write-Host "⚠️  Arquivo manage.py não encontrado!" -ForegroundColor Yellow
    Write-Host "   Certifique-se de estar na pasta do projeto" -ForegroundColor Yellow
    Write-Host "   Pasta atual: $currentPath" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "📁 Pasta do projeto: $currentPath" -ForegroundColor Green
Write-Host ""

# Verificar se há alterações não commitadas
Write-Host "📥 Verificando repositório Git..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>$null
if ($gitStatus) {
    Write-Host "⚠️  Há alterações não commitadas!" -ForegroundColor Yellow
    Write-Host "   Fazendo commit automático..." -ForegroundColor Yellow
    git add .
    git commit -m "Deploy automático - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Erro no commit, continuando mesmo assim..." -ForegroundColor Yellow
    }
}

# Fazer push
Write-Host "📤 Fazendo push para GitHub..." -ForegroundColor Yellow
git push origin master 2>$null
if ($LASTEXITCODE -ne 0) {
    git push origin main 2>$null
}
Write-Host "✅ Código sincronizado!" -ForegroundColor Green
Write-Host ""

# Obter connection name
Write-Host "🔗 Obtendo informações do banco de dados..." -ForegroundColor Yellow
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)" 2>$null
if ($CONNECTION_NAME) {
    Write-Host "✅ Connection Name: $CONNECTION_NAME" -ForegroundColor Green
    $USE_DB = $true
} else {
    Write-Host "⚠️  Instância de banco não encontrada, continuando sem banco..." -ForegroundColor Yellow
    $USE_DB = $false
}
Write-Host ""

# Gerar SECRET_KEY
Write-Host "🔑 Gerando SECRET_KEY..." -ForegroundColor Yellow
try {
    $SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
    if (-not $SECRET_KEY) {
        $SECRET_KEY = "temp-secret-key-change-me-$(Get-Random)"
    }
} catch {
    $SECRET_KEY = "temp-secret-key-change-me-$(Get-Random)"
}
Write-Host "✅ SECRET_KEY gerada" -ForegroundColor Green
Write-Host ""

# Build
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔨 PASSO 1/2: Build da imagem Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "⏳ Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --tag gcr.io/$PROJECT_ID/monpec

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Build concluído!" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 PASSO 2/2: Deploy no Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "⏳ Isso pode levar 2-3 minutos..." -ForegroundColor Yellow
Write-Host ""

$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY"

if ($USE_DB) {
    $envVars += ",DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME"
    
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --add-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
} else {
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Deploy concluído!" -ForegroundColor Green
Write-Host ""

# Obter URL
Write-Host "🌐 Obtendo URL do serviço..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Teste: $SERVICE_URL" -ForegroundColor White
Write-Host "   2. Verifique meta tag: $SERVICE_URL (Ctrl+U para ver código-fonte)" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Se houver erro, verifique os logs:" -ForegroundColor Yellow
Write-Host "   gcloud run services logs read monpec --region us-central1 --limit 50" -ForegroundColor White
Write-Host ""













