# Script para Configurar Variaveis de Ambiente e Verificar Logs
# Execute este script apos o deploy para configurar o servico

Write-Host "Configurando Variaveis de Ambiente do Cloud Run" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$CLOUD_SQL_CONNECTION = "$PROJECT_ID:$REGION:monpec-db"

# Configurar projeto
gcloud config set project $PROJECT_ID

Write-Host "1. Configurando variaveis de ambiente..." -ForegroundColor Yellow

# Gerar SECRET_KEY se nao tiver
$secretKey = Read-Host "Digite a SECRET_KEY (ou pressione Enter para gerar uma nova)"
if ([string]::IsNullOrWhiteSpace($secretKey)) {
    Write-Host "Gerando nova SECRET_KEY..." -ForegroundColor Gray
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
    if (-not $secretKey) {
        # Fallback se Python nao funcionar
        $secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object {[char]$_})
    }
    Write-Host "SECRET_KEY gerada: $secretKey" -ForegroundColor Green
}

# Solicitar credenciais do banco
Write-Host ""
Write-Host "Configuracoes do Banco de Dados:" -ForegroundColor Yellow
$dbName = Read-Host "Nome do banco (padrao: monpec_db)"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "monpec_db" }

$dbUser = Read-Host "Usuario do banco (padrao: monpec_user)"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "monpec_user" }

$dbPassword = Read-Host "Senha do banco" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))

Write-Host ""
Write-Host "Configurando variaveis de ambiente no Cloud Run..." -ForegroundColor Yellow

# Configurar variaveis de ambiente
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "SECRET_KEY=$secretKey",
    "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION",
    "DB_NAME=$dbName",
    "DB_USER=$dbUser",
    "DB_PASSWORD=$dbPasswordPlain"
)

$envVarsString = $envVars -join ","

gcloud run services update $SERVICE_NAME `
    --region=$REGION `
    --set-env-vars=$envVarsString `
    --add-cloudsql-instances=$CLOUD_SQL_CONNECTION

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Variaveis de ambiente configuradas com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Erro ao configurar variaveis de ambiente!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Verificando logs do servico..." -ForegroundColor Yellow
Write-Host "   (Mostrando ultimos 20 logs de erro)" -ForegroundColor Gray
Write-Host ""

gcloud logging read `
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" `
    --limit=20 `
    --format="table(timestamp,severity,textPayload)" `
    --project=$PROJECT_ID

Write-Host ""
Write-Host "3. Verificando status do servico..." -ForegroundColor Yellow

$serviceUrl = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1
Write-Host "URL do servico: $serviceUrl" -ForegroundColor Cyan

Write-Host ""
Write-Host "4. Próximos passos:" -ForegroundColor Yellow
Write-Host "   a) Execute as migracoes do Django:" -ForegroundColor Gray
Write-Host "      gcloud run jobs create migrate-monpec --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --region $REGION --command python --args manage.py,migrate --set-env-vars=`"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`" --add-cloudsql-instances=$CLOUD_SQL_CONNECTION" -ForegroundColor White
Write-Host ""
Write-Host "      gcloud run jobs execute migrate-monpec --region $REGION" -ForegroundColor White
Write-Host ""
Write-Host "   b) Crie um superusuario:" -ForegroundColor Gray
Write-Host "      Acesse: $serviceUrl/admin" -ForegroundColor White
Write-Host "      Ou use o comando createsuperuser via job" -ForegroundColor White
Write-Host ""
Write-Host "   c) Teste o servico:" -ForegroundColor Gray
Write-Host "      Acesse: $serviceUrl" -ForegroundColor White
Write-Host ""

Write-Host "Processo concluido!" -ForegroundColor Green



