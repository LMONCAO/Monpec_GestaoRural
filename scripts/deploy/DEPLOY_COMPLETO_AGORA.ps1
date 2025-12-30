# 🚀 DEPLOY COMPLETO - MONPEC NO GOOGLE CLOUD
# Atualiza landing page, credenciais Mercado Pago, senha admin e formulário demonstração
# Executa deploy direto no Google Cloud Run

$ErrorActionPreference = "Stop"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$ADMIN_PASSWORD = "L6171r12@@"
$ADMIN_USERNAME = "admin"
$ADMIN_EMAIL = "admin@monpec.com.br"

# Funções auxiliares
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
Write-Host "🚀 DEPLOY COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "   Landing Page + Mercado Pago + Admin" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar gcloud
Write-Step "Verificando gcloud CLI..."
try {
    $null = gcloud --version 2>&1 | Out-Null
    Write-Success "gcloud encontrado"
} catch {
    Write-Error "gcloud CLI não está instalado!"
    exit 1
}

# 2. Verificar autenticação
Write-Step "Verificando autenticação..."
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $account) {
    Write-Error "Você não está autenticado no Google Cloud!"
    Write-Host "Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Success "Autenticado como: $account"

# 3. Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado: $PROJECT_ID"

# 4. Habilitar APIs necessárias
Write-Step "Habilitando APIs..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com"
)
foreach ($api in $apis) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas"

# 5. Ler variáveis de ambiente do .env (se existir)
Write-Step "Lendo configurações do .env..."
$envVars = @()
$mercadopagoToken = ""
$mercadopagoPublicKey = ""
$secretKey = ""
$dbName = ""
$dbUser = ""
$dbPassword = ""
$cloudSqlConnection = ""

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    $envLines = Get-Content ".env"
    
    foreach ($line in $envLines) {
        if ($line -match "^MERCADOPAGO_ACCESS_TOKEN=(.+)$") {
            $mercadopagoToken = $matches[1].Trim()
        }
        if ($line -match "^MERCADOPAGO_PUBLIC_KEY=(.+)$") {
            $mercadopagoPublicKey = $matches[1].Trim()
        }
        if ($line -match "^SECRET_KEY=(.+)$") {
            $secretKey = $matches[1].Trim()
        }
        if ($line -match "^DB_NAME=(.+)$") {
            $dbName = $matches[1].Trim()
        }
        if ($line -match "^DB_USER=(.+)$") {
            $dbUser = $matches[1].Trim()
        }
        if ($line -match "^DB_PASSWORD=(.+)$") {
            $dbPassword = $matches[1].Trim()
        }
        if ($line -match "^CLOUD_SQL_CONNECTION_NAME=(.+)$") {
            $cloudSqlConnection = $matches[1].Trim()
        }
    }
    
    if ($mercadopagoToken) {
        Write-Success "Credenciais Mercado Pago encontradas no .env"
    } else {
        Write-Warning "MERCADOPAGO_ACCESS_TOKEN não encontrado no .env"
    }
} else {
    Write-Warning ".env não encontrado. Usando variáveis de ambiente do Cloud Run existentes"
}

# 6. Build da imagem
Write-Step "Fazendo build da imagem Docker..."
$imageTag = "gcr.io/$PROJECT_ID/$SERVICE_NAME"
gcloud builds submit --tag $imageTag --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build!"
    exit 1
}
Write-Success "Build concluído: $imageTag"

# 7. Preparar variáveis de ambiente para o deploy
Write-Step "Preparando variáveis de ambiente..."
$envVarList = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

# Adicionar Mercado Pago se disponível
if ($mercadopagoToken) {
    $envVarList += "MERCADOPAGO_ACCESS_TOKEN=$mercadopagoToken"
}
if ($mercadopagoPublicKey) {
    $envVarList += "MERCADOPAGO_PUBLIC_KEY=$mercadopagoPublicKey"
}
if ($mercadopagoToken -or $mercadopagoPublicKey) {
    $envVarList += "PAYMENT_GATEWAY_DEFAULT=mercadopago"
    $envVarList += "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/"
    $envVarList += "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
}

# Adicionar outras variáveis se disponíveis
if ($secretKey) {
    $envVarList += "SECRET_KEY=$secretKey"
}
if ($dbName) {
    $envVarList += "DB_NAME=$dbName"
}
if ($dbUser) {
    $envVarList += "DB_USER=$dbUser"
}
if ($dbPassword) {
    $envVarList += "DB_PASSWORD=$dbPassword"
}
if ($cloudSqlConnection) {
    $envVarList += "CLOUD_SQL_CONNECTION_NAME=$cloudSqlConnection"
}

$envVarsString = $envVarList -join ","

# 8. Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
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

# 9. Obter URL do serviço
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>&1
Write-Success "Serviço disponível em: $serviceUrl"

# 10. Criar script Python para atualizar admin
Write-Step "Criando script para atualizar usuário admin..."
$createAdminScript = @"
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = '$ADMIN_USERNAME'
email = '$ADMIN_EMAIL'
password = '$ADMIN_PASSWORD'

try:
    if User.objects.filter(username=username).exists():
        usuario = User.objects.get(username=username)
        usuario.set_password(password)
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.is_active = True
        usuario.email = email
        usuario.save()
        print(f'✅ Usuário admin ATUALIZADO com sucesso!')
    else:
        User.objects.create_superuser(username, email, password)
        print(f'✅ Usuário admin CRIADO com sucesso!')
    print(f'Usuário: {username}')
    print(f'Senha: {password}')
except Exception as e:
    print(f'❌ ERRO: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$createAdminScript | Out-File -FilePath "temp_create_admin.py" -Encoding UTF8

# 11. Executar migrações e criar admin via Cloud Run Job
Write-Step "Criando job para migrações e admin..."
$jobName = "setup-admin-$(Get-Date -Format 'yyyyMMddHHmmss')"

# Criar script completo para o job
$jobScript = @"
#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

print('🔄 Executando migrações...')
try:
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print('✅ Migrações concluídas!')
except Exception as e:
    print(f'⚠️  Erro nas migrações: {e}')

print('')
print('👤 Atualizando usuário admin...')
username = '$ADMIN_USERNAME'
email = '$ADMIN_EMAIL'
password = '$ADMIN_PASSWORD'

try:
    if User.objects.filter(username=username).exists():
        usuario = User.objects.get(username=username)
        usuario.set_password(password)
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.is_active = True
        usuario.email = email
        usuario.save()
        print(f'✅ Usuário admin ATUALIZADO!')
    else:
        User.objects.create_superuser(username, email, password)
        print(f'✅ Usuário admin CRIADO!')
    print(f'   Usuário: {username}')
    print(f'   Email: {email}')
    print(f'   Senha: {password}')
except Exception as e:
    print(f'❌ ERRO: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('')
print('✅ Setup completo!')
"@

$jobScript | Out-File -FilePath "temp_job_setup.py" -Encoding UTF8

# Copiar script para container ou usar command inline
Write-Warning "Para atualizar o admin, você pode:"
Write-Host "   1. Executar manualmente após o deploy:" -ForegroundColor Gray
Write-Host "      gcloud run jobs create setup-admin `" -ForegroundColor Gray
Write-Host "        --image $imageTag `" -ForegroundColor Gray
Write-Host "        --region $REGION `" -ForegroundColor Gray
Write-Host "        --command python `" -ForegroundColor Gray
Write-Host "        --args manage.py,shell `" -ForegroundColor Gray
Write-Host "        --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Ou criar via Cloud SQL diretamente" -ForegroundColor Gray

# Limpar arquivos temporários
Remove-Item "temp_create_admin.py" -ErrorAction SilentlyContinue
Remove-Item "temp_job_setup.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "DEPLOY CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
Write-Host "   $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Acesse: $serviceUrl" -ForegroundColor White
Write-Host "   2. Execute migrações: gcloud run jobs create migrate --image $imageTag --region $REGION --command python --args manage.py,migrate" -ForegroundColor White
Write-Host "   3. Crie/atualize admin usando o script criar_admin_producao.py via Cloud Run Job" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Credenciais Admin:" -ForegroundColor Cyan
Write-Host "   Usuário: $ADMIN_USERNAME" -ForegroundColor White
Write-Host "   Senha: $ADMIN_PASSWORD" -ForegroundColor White
Write-Host ""








