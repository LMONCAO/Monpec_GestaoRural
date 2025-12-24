# Script para Configurar Cloud Run com Banco de Dados
# Execute este script após criar o banco de dados

param(
    [string]$ProjectId = "monpec-sistema-rural",
    [string]$Region = "us-central1",
    [string]$ServiceName = "monpec"
)

$ErrorActionPreference = "Stop"

Write-Host "⚙️ Configurando Cloud Run com Banco de Dados..." -ForegroundColor Green
Write-Host ""

# Connection name do Cloud SQL
$ConnectionName = "$ProjectId`:us-central1:monpec-db"

Write-Host "Connection Name: $ConnectionName" -ForegroundColor Yellow

# Solicitar informações do banco
Write-Host ""
Write-Host "📋 Informações do Banco de Dados:" -ForegroundColor Cyan
$DbName = Read-Host "Nome do banco de dados (padrão: monpec_db)"
if ([string]::IsNullOrWhiteSpace($DbName)) { $DbName = "monpec_db" }

$DbUser = Read-Host "Usuário do banco (padrão: monpec_user)"
if ([string]::IsNullOrWhiteSpace($DbUser)) { $DbUser = "monpec_user" }

$DbPassword = Read-Host "Senha do banco" -AsSecureString
$DbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($DbPassword))

# Gerar SECRET_KEY
Write-Host ""
Write-Host "🔐 Gerando SECRET_KEY..." -ForegroundColor Yellow
$SecretKey = python -c "import secrets; print(secrets.token_urlsafe(50))"
if (-not $SecretKey) {
    $SecretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})
}

Write-Host "SECRET_KEY gerada!" -ForegroundColor Green
Write-Host ""

# Atualizar serviço com todas as variáveis
Write-Host "🚀 Atualizando serviço Cloud Run..." -ForegroundColor Yellow

$EnvVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "SECRET_KEY=$SecretKey",
    "CLOUD_SQL_CONNECTION_NAME=$ConnectionName",
    "DB_NAME=$DbName",
    "DB_USER=$DbUser",
    "DB_PASSWORD=$DbPasswordPlain"
)

$EnvVarsString = $EnvVars -join ","

gcloud run services update $ServiceName `
    --region $Region `
    --add-cloudsql-instances $ConnectionName `
    --update-env-vars $EnvVarsString `
    --quiet

Write-Host ""
Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Variáveis configuradas:" -ForegroundColor Cyan
Write-Host "  - CLOUD_SQL_CONNECTION_NAME: $ConnectionName"
Write-Host "  - DB_NAME: $DbName"
Write-Host "  - DB_USER: $DbUser"
Write-Host "  - SECRET_KEY: [configurada]"
Write-Host ""
Write-Host "⚠️  Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Execute as migrações:"
Write-Host "   gcloud run jobs execute monpec-migrate --region $Region"
Write-Host ""
Write-Host "2. Crie o usuário admin:"
Write-Host "   .\criar_admin_cloud_run.ps1 $ProjectId $Region"
Write-Host ""




















