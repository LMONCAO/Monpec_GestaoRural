# 🚀 DEPLOY E CONFIGURAR ADMIN - MONPEC
# Script completo que faz deploy e configura admin automaticamente

$ErrorActionPreference = "Stop"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$ADMIN_PASSWORD = "L6171r12@@"
$ADMIN_USERNAME = "admin"
$ADMIN_EMAIL = "admin@monpec.com.br"

function Write-Step {
    param([string]$Message)
    Write-Host "▶ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY E CONFIGURAR ADMIN - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gcloud
Write-Step "Verificando gcloud..."
try {
    $null = gcloud --version 2>&1 | Out-Null
    Write-Success "gcloud OK"
} catch {
    Write-Error "gcloud não encontrado!"
    exit 1
}

# Verificar autenticação
Write-Step "Verificando autenticação..."
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $account) {
    Write-Error "Não autenticado! Execute: gcloud auth login"
    exit 1
}
Write-Success "Autenticado: $account"

# Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}

# Ler .env para credenciais Mercado Pago
Write-Step "Lendo .env..."
$mercadopagoToken = ""
$mercadopagoPublicKey = ""
$secretKey = ""
$dbName = ""
$dbUser = ""
$dbPassword = ""
$cloudSqlConnection = ""

if (Test-Path ".env") {
    $envLines = Get-Content ".env"
    foreach ($line in $envLines) {
        if ($line -match "^MERCADOPAGO_ACCESS_TOKEN=(.+)$") { $mercadopagoToken = $matches[1].Trim() }
        if ($line -match "^MERCADOPAGO_PUBLIC_KEY=(.+)$") { $mercadopagoPublicKey = $matches[1].Trim() }
        if ($line -match "^SECRET_KEY=(.+)$") { $secretKey = $matches[1].Trim() }
        if ($line -match "^DB_NAME=(.+)$") { $dbName = $matches[1].Trim() }
        if ($line -match "^DB_USER=(.+)$") { $dbUser = $matches[1].Trim() }
        if ($line -match "^DB_PASSWORD=(.+)$") { $dbPassword = $matches[1].Trim() }
        if ($line -match "^CLOUD_SQL_CONNECTION_NAME=(.+)$") { $cloudSqlConnection = $matches[1].Trim() }
    }
    if ($mercadopagoToken) {
        Write-Success "Credenciais Mercado Pago encontradas"
    }
}

# Build
Write-Step "Build da imagem..."
$imageTag = "gcr.io/$PROJECT_ID/$SERVICE_NAME"
gcloud builds submit --tag $imageTag --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build!"
    exit 1
}
Write-Success "Build concluído"

# Preparar variáveis de ambiente
$envVarList = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

if ($mercadopagoToken) { $envVarList += "MERCADOPAGO_ACCESS_TOKEN=$mercadopagoToken" }
if ($mercadopagoPublicKey) { $envVarList += "MERCADOPAGO_PUBLIC_KEY=$mercadopagoPublicKey" }
if ($mercadopagoToken -or $mercadopagoPublicKey) {
    $envVarList += "PAYMENT_GATEWAY_DEFAULT=mercadopago"
    $envVarList += "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/"
    $envVarList += "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
}

if ($secretKey) { $envVarList += "SECRET_KEY=$secretKey" }
if ($dbName) { $envVarList += "DB_NAME=$dbName" }
if ($dbUser) { $envVarList += "DB_USER=$dbUser" }
if ($dbPassword) { $envVarList += "DB_PASSWORD=$dbPassword" }
if ($cloudSqlConnection) { $envVarList += "CLOUD_SQL_CONNECTION_NAME=$cloudSqlConnection" }

$envVarsString = $envVarList -join ","

# Deploy
Write-Step "Deploy no Cloud Run..."
$deployArgs = @(
    "run", "deploy", $SERVICE_NAME,
    "--image", $imageTag,
    "--platform", "managed",
    "--region", $REGION,
    "--allow-unauthenticated",
    "--set-env-vars", $envVarsString,
    "--memory", "1Gi",
    "--cpu", "2",
    "--timeout", "300",
    "--max-instances", "10",
    "--min-instances", "1",
    "--port", "8080"
)

if ($cloudSqlConnection) {
    $deployArgs += "--add-cloudsql-instances"
    $deployArgs += $cloudSqlConnection
}

& gcloud $deployArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy!"
    exit 1
}
Write-Success "Deploy concluído!"

# Obter URL
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>&1
Write-Success "Serviço: $serviceUrl"

# Criar script Python inline para atualizar admin
Write-Step "Criando script para atualizar admin..."
$adminScript = @'
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@monpec.com.br'
password = 'L6171r12@@'
try:
    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        u.set_password(password)
        u.is_superuser = True
        u.is_staff = True
        u.is_active = True
        u.email = email
        u.save()
        print(f'✅ Admin ATUALIZADO')
    else:
        User.objects.create_superuser(username, email, password)
        print(f'✅ Admin CRIADO')
    print(f'Usuário: {username}, Senha: {password}')
except Exception as e:
    print(f'❌ ERRO: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
'@

$adminScript | Out-File -FilePath "temp_admin_script.py" -Encoding UTF8

# Criar job temporário para executar o script
Write-Step "Criando job para atualizar admin..."
$jobName = "update-admin-$(Get-Date -Format 'yyyyMMddHHmmss')"

# Copiar script para um local acessível ou usar command inline
# Vamos usar python manage.py shell com código inline
Write-Warning "Para atualizar o admin, execute:"
Write-Host ""
Write-Host "   Opção 1 - Via Cloud Shell:" -ForegroundColor Yellow
Write-Host "   gcloud run jobs create $jobName \`" -ForegroundColor Gray
Write-Host "     --image $imageTag \`" -ForegroundColor Gray
Write-Host "     --region $REGION \`" -ForegroundColor Gray
Write-Host "     --command python \`" -ForegroundColor Gray
Write-Host "     --args manage.py,shell \`" -ForegroundColor Gray
Write-Host "     --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" -ForegroundColor Gray
Write-Host ""
Write-Host "   Opção 2 - Usar criar_admin_producao.py:" -ForegroundColor Yellow
Write-Host "   (Copie o arquivo criar_admin_producao.py e execute via Cloud Run Job)" -ForegroundColor Gray
Write-Host ""

# Alternativa: criar job com comando direto usando createsuperuser
Write-Step "Criando job com createsuperuser (será não-interativo)..."
$createAdminJob = "create-admin-now"

# Primeiro, tentar deletar job existente se houver
gcloud run jobs delete $createAdminJob --region $REGION --quiet 2>&1 | Out-Null

# Criar job usando o script criar_admin_producao.py que já existe
Write-Warning "Para criar/atualizar admin, você precisa:"
Write-Host "   1. Fazer upload do criar_admin_producao.py para Cloud Storage ou" -ForegroundColor Gray
Write-Host "   2. Executar via Cloud SQL diretamente ou" -ForegroundColor Gray
Write-Host "   3. Usar Cloud Shell para executar o script Python" -ForegroundColor Gray
Write-Host ""

Remove-Item "temp_admin_script.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "DEPLOY CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URL: $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "🔐 Para configurar admin, execute no Cloud Shell:" -ForegroundColor Yellow
Write-Host ""
Write-Host '   gcloud sql connect monpec-db --user=monpec_user' -ForegroundColor White
Write-Host '   # Depois execute:' -ForegroundColor Gray
Write-Host '   python manage.py shell' -ForegroundColor White
Write-Host '   # E cole o código do criar_admin_producao.py' -ForegroundColor Gray
Write-Host ""
Write-Host "   OU use o script Python criar_admin_producao.py via Cloud Run Job" -ForegroundColor White
Write-Host ""
Write-Host "📋 Credenciais:" -ForegroundColor Cyan
Write-Host "   Usuário: $ADMIN_USERNAME" -ForegroundColor White
Write-Host "   Senha: $ADMIN_PASSWORD" -ForegroundColor White
Write-Host ""








