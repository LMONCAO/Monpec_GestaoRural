# Script PowerShell para deploy completo no Google Cloud
# MonPEC - Sistema de Gestão Rural

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETO MONPEC - GCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gcloud
try {
    $gcloudVersion = gcloud --version 2>&1
    Write-Host "✓ Google Cloud SDK instalado" -ForegroundColor Green
} catch {
    Write-Host "ERRO: gcloud não está instalado!" -ForegroundColor Red
    exit 1
}

# Obter projeto
$PROJECT_ID = gcloud config get-value project 2>&1
if ([string]::IsNullOrWhiteSpace($PROJECT_ID)) {
    Write-Host "Nenhum projeto configurado." -ForegroundColor Yellow
    gcloud projects list
    $PROJECT_ID = Read-Host "Digite o PROJECT_ID"
    gcloud config set project $PROJECT_ID
}

Write-Host "Projeto: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Etapa 1: Habilitar APIs
Write-Host "[1/6] Habilitando APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable cloudresourcemanager.googleapis.com --quiet
Write-Host "✓ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Etapa 2: Verificar Cloud SQL
Write-Host "[2/6] Verificando banco de dados..." -ForegroundColor Yellow
$DB_INSTANCE = gcloud sql instances list --filter="name:monpec*" --format="value(name)" 2>&1 | Select-Object -First 1

if ([string]::IsNullOrWhiteSpace($DB_INSTANCE)) {
    Write-Host "Nenhuma instância Cloud SQL encontrada." -ForegroundColor Yellow
    $create = Read-Host "Deseja criar agora? (s/n)"
    if ($create -eq "s" -or $create -eq "S") {
        $DB_ROOT_PASSWORD = Read-Host "Senha do root do PostgreSQL" -AsSecureString
        $DB_ROOT_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_ROOT_PASSWORD)
        )
        Write-Host "Criando instância (isso pode levar alguns minutos)..."
        gcloud sql instances create monpec-db `
            --database-version=POSTGRES_15 `
            --tier=db-f1-micro `
            --region=us-central1 `
            --root-password=$DB_ROOT_PASSWORD_PLAIN
        
        gcloud sql databases create monpec_db --instance=monpec-db
        $DB_USER_PASSWORD = Read-Host "Senha para o usuário monpec_user" -AsSecureString
        $DB_USER_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_USER_PASSWORD)
        )
        gcloud sql users create monpec_user `
            --instance=monpec-db `
            --password=$DB_USER_PASSWORD_PLAIN
        
        $DB_INSTANCE = "monpec-db"
        Write-Host "✓ Banco de dados criado" -ForegroundColor Green
    }
} else {
    Write-Host "✓ Instância encontrada: $DB_INSTANCE" -ForegroundColor Green
}

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)" 2>&1
Write-Host "Connection Name: $CONNECTION_NAME" -ForegroundColor Green
Write-Host ""

# Etapa 3: Build e Deploy
Write-Host "[3/6] Fazendo build e deploy..." -ForegroundColor Yellow
Write-Host "Isso pode levar alguns minutos..."
Write-Host ""

# Verificar se cloudbuild.yaml existe, senão usar cloudbuild-config.yaml
if (Test-Path "cloudbuild.yaml") {
    $buildConfig = "cloudbuild.yaml"
} elseif (Test-Path "cloudbuild-config.yaml") {
    $buildConfig = "cloudbuild-config.yaml"
} else {
    Write-Host "ERRO: Arquivo cloudbuild.yaml não encontrado!" -ForegroundColor Red
    exit 1
}

gcloud builds submit --config $buildConfig
Write-Host "✓ Deploy concluído" -ForegroundColor Green
Write-Host ""

# Etapa 4: Configurar variáveis de ambiente
Write-Host "[4/6] Configurando variáveis de ambiente..." -ForegroundColor Yellow
Write-Host "Você precisará fornecer algumas informações:"
Write-Host ""

# Gerar SECRET_KEY
try {
    $SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $SECRET_KEY = ""
    }
} catch {
    $SECRET_KEY = ""
}

if ([string]::IsNullOrWhiteSpace($SECRET_KEY)) {
    $SECRET_KEY = Read-Host "SECRET_KEY do Django (ou pressione Enter para gerar)"
    if ([string]::IsNullOrWhiteSpace($SECRET_KEY)) {
        # Gerar uma chave simples
        $SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object {[char]$_})
        Write-Host "SECRET_KEY gerada automaticamente" -ForegroundColor Yellow
    }
}

$DB_NAME = Read-Host "DB_NAME [monpec_db]"
if ([string]::IsNullOrWhiteSpace($DB_NAME)) { $DB_NAME = "monpec_db" }

$DB_USER = Read-Host "DB_USER [monpec_user]"
if ([string]::IsNullOrWhiteSpace($DB_USER)) { $DB_USER = "monpec_user" }

$DB_PASSWORD = Read-Host "DB_PASSWORD" -AsSecureString
$DB_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD)
)

$MERCADOPAGO_ACCESS_TOKEN = Read-Host "MERCADOPAGO_ACCESS_TOKEN" -AsSecureString
$MERCADOPAGO_ACCESS_TOKEN_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($MERCADOPAGO_ACCESS_TOKEN)
)

$MERCADOPAGO_PUBLIC_KEY = Read-Host "MERCADOPAGO_PUBLIC_KEY" -AsSecureString
$MERCADOPAGO_PUBLIC_KEY_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($MERCADOPAGO_PUBLIC_KEY)
)

$SITE_URL = Read-Host "SITE_URL [https://monpec.com.br]"
if ([string]::IsNullOrWhiteSpace($SITE_URL)) { $SITE_URL = "https://monpec.com.br" }

Write-Host ""
Write-Host "Configurando variáveis..." -ForegroundColor Yellow

gcloud run services update monpec `
  --region=us-central1 `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
  --set-env-vars="SECRET_KEY=$SECRET_KEY" `
  --set-env-vars="DEBUG=False" `
  --set-env-vars="DB_NAME=$DB_NAME" `
  --set-env-vars="DB_USER=$DB_USER" `
  --set-env-vars="DB_PASSWORD=$DB_PASSWORD_PLAIN" `
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME" `
  --set-env-vars="MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN_PLAIN" `
  --set-env-vars="MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY_PLAIN" `
  --set-env-vars="MERCADOPAGO_SUCCESS_URL=$SITE_URL/assinaturas/sucesso/" `
  --set-env-vars="MERCADOPAGO_CANCEL_URL=$SITE_URL/assinaturas/cancelado/" `
  --set-env-vars="SITE_URL=$SITE_URL" `
  --set-env-vars="PAYMENT_GATEWAY_DEFAULT=mercadopago" `
  --set-env-vars="PYTHONUNBUFFERED=1" `
  --add-cloudsql-instances=$CONNECTION_NAME

Write-Host "✓ Variáveis configuradas" -ForegroundColor Green
Write-Host ""

# Etapa 5: Aplicar migrações
Write-Host "[5/6] Aplicando migrações..." -ForegroundColor Yellow

# Verificar se job existe
$JOB_EXISTS = gcloud run jobs describe migrate-monpec --region=us-central1 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Criando job de migração..."
    gcloud run jobs create migrate-monpec `
      --image=gcr.io/$PROJECT_ID/monpec:latest `
      --region=us-central1 `
      --command=python `
      --args=manage.py,migrate `
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
      --set-env-vars="SECRET_KEY=$SECRET_KEY" `
      --set-env-vars="DB_NAME=$DB_NAME" `
      --set-env-vars="DB_USER=$DB_USER" `
      --set-env-vars="DB_PASSWORD=$DB_PASSWORD_PLAIN" `
      --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME" `
      --set-env-vars="PYTHONUNBUFFERED=1" `
      --add-cloudsql-instances=$CONNECTION_NAME `
      --max-retries=3 `
      --task-timeout=600
}

Write-Host "Executando migrações..."
gcloud run jobs execute migrate-monpec --region=us-central1 --wait
Write-Host "✓ Migrações aplicadas" -ForegroundColor Green
Write-Host ""

# Etapa 6: Obter URL
Write-Host "[6/6] Obtendo informações do serviço..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe monpec --region=us-central1 --format="value(status.url)" 2>&1
Write-Host "✓ Serviço disponível" -ForegroundColor Green
Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL do serviço: $SERVICE_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Acesse: $SERVICE_URL/admin"
Write-Host "2. Crie um superusuário"
Write-Host "3. Configure domínio personalizado (opcional)"
Write-Host ""
Write-Host "Tudo pronto! Seu sistema está no ar! 🚀" -ForegroundColor Green
Write-Host ""


