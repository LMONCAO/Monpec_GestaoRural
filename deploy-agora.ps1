# Script de Deploy Simplificado - Sistema MONPEC
# Execute este script para fazer deploy completo

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY GOOGLE CLOUD - SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Variáveis de ambiente
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

# Configurar projeto
Write-Host "▶ Configurando projeto..." -ForegroundColor Blue
gcloud config set project $PROJECT_ID --quiet
Write-Host "✓ Projeto configurado`n" -ForegroundColor Green

# Habilitar APIs
Write-Host "▶ Habilitando APIs..." -ForegroundColor Blue
gcloud services enable cloudbuild.googleapis.com --quiet 2>$null
gcloud services enable run.googleapis.com --quiet 2>$null
gcloud services enable sqladmin.googleapis.com --quiet 2>$null
gcloud services enable containerregistry.googleapis.com --quiet 2>$null
Write-Host "✓ APIs habilitadas`n" -ForegroundColor Green

# Build da imagem
Write-Host "▶ Fazendo build da imagem Docker..." -ForegroundColor Blue
Write-Host "   Isso pode levar alguns minutos...`n" -ForegroundColor Gray

# Usar cloudbuild-config.yaml se existir, senão build direto
if (Test-Path "cloudbuild-config.yaml") {
    Write-Host "   Usando cloudbuild-config.yaml..." -ForegroundColor Gray
    gcloud builds submit --config cloudbuild-config.yaml --timeout=20m
} else {
    Write-Host "   Build direto..." -ForegroundColor Gray
    gcloud builds submit --tag "${IMAGE_NAME}:latest" --timeout=20m
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Build concluído`n" -ForegroundColor Green
} else {
    Write-Host "✗ Erro no build!" -ForegroundColor Red
    Write-Host "`nTentando alternativa: usando apenas arquivos essenciais..." -ForegroundColor Yellow
    
    # Criar diretório temporário limpo
    $TEMP_DIR = ".\temp_build"
    if (Test-Path $TEMP_DIR) { Remove-Item -Recurse -Force $TEMP_DIR }
    New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
    
    # Copiar apenas arquivos necessários
    Copy-Item "Dockerfile.prod" $TEMP_DIR
    Copy-Item "requirements.txt" $TEMP_DIR
    Copy-Item "manage.py" $TEMP_DIR
    Copy-Item -Recurse "sistema_rural" $TEMP_DIR
    Copy-Item -Recurse "gestao_rural" $TEMP_DIR
    Copy-Item -Recurse "templates" $TEMP_DIR -ErrorAction SilentlyContinue
    Copy-Item -Recurse "static" $TEMP_DIR -ErrorAction SilentlyContinue
    Copy-Item -Recurse "nfe" $TEMP_DIR -ErrorAction SilentlyContinue
    Copy-Item -Recurse "tenants" $TEMP_DIR -ErrorAction SilentlyContinue
    
    # Criar .gcloudignore no temp
    Set-Content -Path "$TEMP_DIR\.gcloudignore" -Value "# Ignorar tudo exceto o que foi copiado"
    
    Push-Location $TEMP_DIR
    gcloud builds submit --tag "${IMAGE_NAME}:latest" --timeout=20m
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Build concluído (método alternativo)`n" -ForegroundColor Green
        Remove-Item -Recurse -Force $TEMP_DIR
    } else {
        Write-Host "✗ Erro no build alternativo!" -ForegroundColor Red
        Remove-Item -Recurse -Force $TEMP_DIR -ErrorAction SilentlyContinue
        exit 1
    }
}

# Deploy no Cloud Run
Write-Host "▶ Fazendo deploy no Cloud Run..." -ForegroundColor Blue
gcloud run deploy $SERVICE_NAME `
    --image "${IMAGE_NAME}:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars $ENV_VARS `
    --add-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080 `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Deploy concluído`n" -ForegroundColor Green
} else {
    Write-Host "✗ Erro no deploy!" -ForegroundColor Red
    exit 1
}

# Obter URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>$null
if ($SERVICE_URL) {
    Write-Host "✓ Serviço disponível em: $SERVICE_URL`n" -ForegroundColor Green
}

# Executar migrações
Write-Host "▶ Aplicando migrações..." -ForegroundColor Blue
$JOB_NAME = "migrate-monpec"

# Verificar se job existe
$jobExists = $false
gcloud run jobs describe $JOB_NAME --region=$REGION 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { $jobExists = $true }

if ($jobExists) {
    Write-Host "   Job já existe. Executando..." -ForegroundColor Gray
    gcloud run jobs execute $JOB_NAME --region=$REGION --wait
} else {
    Write-Host "   Criando job de migração..." -ForegroundColor Gray
    gcloud run jobs create $JOB_NAME `
        --image "${IMAGE_NAME}:latest" `
        --region $REGION `
        --set-env-vars $ENV_VARS `
        --set-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" `
        --memory 2Gi `
        --cpu 1 `
        --max-retries 3 `
        --task-timeout 600 `
        --command python `
        --args "manage.py,migrate,--noinput" `
        --quiet
    
    if ($LASTEXITCODE -eq 0) {
        gcloud run jobs execute $JOB_NAME --region=$REGION --wait
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrações aplicadas`n" -ForegroundColor Green
} else {
    Write-Host "⚠ Erro nas migrações. Execute manualmente:" -ForegroundColor Yellow
    Write-Host "   gcloud run jobs execute $JOB_NAME --region=$REGION`n" -ForegroundColor Gray
}

# Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Informações:" -ForegroundColor White
Write-Host "  • Serviço: $SERVICE_NAME"
if ($SERVICE_URL) { Write-Host "  • URL: $SERVICE_URL" }
Write-Host "  • Região: $REGION"
Write-Host "  • Projeto: $PROJECT_ID"
Write-Host ""




