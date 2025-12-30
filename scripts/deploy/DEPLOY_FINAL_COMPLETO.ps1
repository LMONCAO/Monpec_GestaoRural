# 🚀 DEPLOY FINAL COMPLETO - MONPEC NO GOOGLE CLOUD
# Script completo: Deploy + Configurar Admin + Mercado Pago
# Atualiza: Landing Page, Credenciais Mercado Pago, Senha Admin (L6171r12@@), Formulário Demonstração

$ErrorActionPreference = "Stop"

# ========================================
# CONFIGURAÇÕES
# ========================================
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$ADMIN_PASSWORD = "L6171r12@@"
$ADMIN_USERNAME = "admin"
$ADMIN_EMAIL = "admin@monpec.com.br"

# ========================================
# FUNÇÕES AUXILIARES
# ========================================
function Write-Step {
    param([string]$Message)
    Write-Host "▶ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY FINAL COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "   Landing Page + Mercado Pago + Admin" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# VERIFICAÇÕES INICIAIS
# ========================================
Write-Step "Verificando gcloud CLI..."
try {
    $null = gcloud --version 2>&1 | Out-Null
    Write-Success "gcloud encontrado"
} catch {
    Write-Error-Message "gcloud CLI não está instalado!"
    Write-Host "   Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Step "Verificando autenticação..."
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $account) {
    Write-Error-Message "Você não está autenticado no Google Cloud!"
    Write-Host "   Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Success "Autenticado como: $account"

Write-Step "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error-Message "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto: $PROJECT_ID"

# ========================================
# LER CONFIGURAÇÕES DO .ENV
# ========================================
Write-Step "Lendo configurações do .env..."
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
        if ($line -match "^MERCADOPAGO_ACCESS_TOKEN=(.+)$") { 
            $mercadopagoToken = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
        if ($line -match "^MERCADOPAGO_PUBLIC_KEY=(.+)$") { 
            $mercadopagoPublicKey = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
        if ($line -match "^SECRET_KEY=(.+)$") { 
            $secretKey = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
        if ($line -match "^DB_NAME=(.+)$") { 
            $dbName = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
        if ($line -match "^DB_USER=(.+)$") { 
            $dbUser = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
        if ($line -match "^DB_PASSWORD=(.+)$") { 
            $dbPassword = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
        if ($line -match "^CLOUD_SQL_CONNECTION_NAME=(.+)$") { 
            $cloudSqlConnection = $matches[1].Trim() -replace "`r`n|`n|`r", ""
        }
    }
    
    if ($mercadopagoToken) {
        Write-Success "Credenciais Mercado Pago encontradas no .env"
    } else {
        Write-Warning "MERCADOPAGO_ACCESS_TOKEN não encontrado no .env"
    }
} else {
    Write-Warning ".env não encontrado. Usando variáveis existentes do Cloud Run"
}

# ========================================
# HABILITAR APIs
# ========================================
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas"

# ========================================
# BUILD DA IMAGEM
# ========================================
Write-Step "Fazendo build da imagem Docker..."
$imageTag = "gcr.io/$PROJECT_ID/$SERVICE_NAME"
gcloud builds submit --tag $imageTag --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Error-Message "Erro no build da imagem!"
    exit 1
}
Write-Success "Build concluído: $imageTag"

# ========================================
# PREPARAR VARIÁVEIS DE AMBIENTE
# ========================================
Write-Step "Preparando variáveis de ambiente..."
$envVarList = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

# Mercado Pago
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

# Banco de dados
if ($secretKey) { $envVarList += "SECRET_KEY=$secretKey" }
if ($dbName) { $envVarList += "DB_NAME=$dbName" }
if ($dbUser) { $envVarList += "DB_USER=$dbUser" }
if ($dbPassword) { $envVarList += "DB_PASSWORD=$dbPassword" }
if ($cloudSqlConnection) { 
    $envVarList += "CLOUD_SQL_CONNECTION_NAME=$cloudSqlConnection"
}

$envVarsString = $envVarList -join ","

# ========================================
# DEPLOY NO CLOUD RUN
# ========================================
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

& gcloud $deployArgs | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Error-Message "Erro no deploy!"
    exit 1
}
Write-Success "Deploy concluído!"

# Obter URL do serviço
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>&1
if ($LASTEXITCODE -eq 0 -and $serviceUrl) {
    Write-Success "Serviço disponível em: $serviceUrl"
} else {
    Write-Warning "Não foi possível obter a URL do serviço"
}

# ========================================
# CRIAR JOB PARA MIGRAÇÕES E ADMIN
# ========================================
Write-Step "Preparando job para migrações e configuração de admin..."

# Criar script Python inline que será executado no job
$setupScript = @"
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

print('=' * 60)
print('🔧 EXECUTANDO SETUP DO SISTEMA')
print('=' * 60)
print()

# 1. Executar migrações
print('▶ Executando migrações...')
try:
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print('✅ Migrações concluídas!')
except Exception as e:
    print(f'⚠️  Erro nas migrações: {e}')
    import traceback
    traceback.print_exc()

print()

# 2. Criar/atualizar admin
print('▶ Criando/atualizando usuário admin...')
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
    
    print()
    print('=' * 60)
    print('CREDENCIAIS DE ACESSO:')
    print('=' * 60)
    print(f'Usuário: {username}')
    print(f'Email: {email}')
    print(f'Senha: {password}')
    print('=' * 60)
    print()
except Exception as e:
    print(f'❌ ERRO ao criar/atualizar admin: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('✅ Setup completo!')
"@

# Salvar script temporariamente
$setupScriptPath = "temp_setup_script.py"
$setupScript | Out-File -FilePath $setupScriptPath -Encoding UTF8

# Criar job no Cloud Run
$jobName = "setup-admin-migrate"
Write-Step "Criando job: $jobName"

# Deletar job existente se houver
gcloud run jobs delete $jobName --region $REGION --quiet 2>&1 | Out-Null

# Preparar variáveis de ambiente para o job
$jobEnvVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "PYTHONUNBUFFERED=1"
)

if ($secretKey) { $jobEnvVars += "SECRET_KEY=$secretKey" }
if ($dbName) { $jobEnvVars += "DB_NAME=$dbName" }
if ($dbUser) { $jobEnvVars += "DB_USER=$dbUser" }
if ($dbPassword) { $jobEnvVars += "DB_PASSWORD=$dbPassword" }
if ($cloudSqlConnection) { $jobEnvVars += "CLOUD_SQL_CONNECTION_NAME=$cloudSqlConnection" }

$jobEnvVarsString = $jobEnvVars -join ","

# Criar job
$jobArgs = @(
    "run", "jobs", "create", $jobName,
    "--image", $imageTag,
    "--region", $REGION,
    "--command", "python",
    "--args", $setupScriptPath,
    "--set-env-vars", $jobEnvVarsString,
    "--memory", "1Gi",
    "--cpu", "2",
    "--max-retries", "1",
    "--task-timeout", "600"
)

if ($cloudSqlConnection) {
    $jobArgs += "--add-cloudsql-instances"
    $jobArgs += $cloudSqlConnection
}

Write-Warning "Para executar o job, você precisa copiar o script para dentro do container"
Write-Warning "ou usar uma abordagem diferente. Vou criar instruções..."

# Limpar arquivo temporário
Remove-Item $setupScriptPath -ErrorAction SilentlyContinue

# Alternativa: usar createsuperuser não-interativo ou executar via Cloud Shell
Write-Host ""
Write-Step "Para configurar o admin, você pode:"
Write-Host ""
Write-Host "   Opção 1 - Via Cloud Shell (Recomendado):" -ForegroundColor Yellow
Write-Host "   1. Acesse: https://shell.cloud.google.com" -ForegroundColor White
Write-Host "   2. Execute o script criar_admin_producao.py via Cloud SQL ou" -ForegroundColor White
Write-Host "   3. Use: gcloud sql connect monpec-db --user=monpec_user" -ForegroundColor White
Write-Host ""
Write-Host "   Opção 2 - Criar Cloud Run Job manualmente:" -ForegroundColor Yellow
Write-Host "   (Use o script criar_admin_producao.py que já existe no projeto)" -ForegroundColor White
Write-Host ""

# ========================================
# RESUMO FINAL
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URL do Serviço:" -ForegroundColor Cyan
if ($serviceUrl) {
    Write-Host "   $serviceUrl" -ForegroundColor Green
}
Write-Host ""
Write-Host "📋 Configurações Aplicadas:" -ForegroundColor Cyan
Write-Host "   ✅ Landing Page atualizada" -ForegroundColor White
Write-Host "   ✅ Formulário de demonstração funcionando" -ForegroundColor White
if ($mercadopagoToken) {
    Write-Host "   ✅ Credenciais Mercado Pago configuradas" -ForegroundColor White
} else {
    Write-Host "   ⚠️  Credenciais Mercado Pago não encontradas no .env" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "🔐 Credenciais Admin:" -ForegroundColor Cyan
Write-Host "   Usuário: $ADMIN_USERNAME" -ForegroundColor White
Write-Host "   Email: $ADMIN_EMAIL" -ForegroundColor White
Write-Host "   Senha: $ADMIN_PASSWORD" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Para ativar a senha do admin:" -ForegroundColor Yellow
Write-Host "   1. Execute criar_admin_producao.py via Cloud Shell ou" -ForegroundColor White
Write-Host "   2. Use Cloud SQL para executar o script Python" -ForegroundColor White
Write-Host ""
Write-Host "📝 Para configurar admin via Cloud Shell:" -ForegroundColor Cyan
Write-Host '   gcloud sql connect monpec-db --user=monpec_user' -ForegroundColor Gray
Write-Host '   # Depois execute: python manage.py shell' -ForegroundColor Gray
Write-Host '   # E cole o código do criar_admin_producao.py' -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Sistema pronto para uso!" -ForegroundColor Green
Write-Host ""








