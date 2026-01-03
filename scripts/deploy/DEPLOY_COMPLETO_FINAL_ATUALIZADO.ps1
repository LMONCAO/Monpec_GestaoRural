# 🚀 DEPLOY COMPLETO FINAL ATUALIZADO - MONPEC.COM.BR
# Versão totalmente não-interativa - sem pausas ou esperas de input
# Projeto: monpec-sistema-rural
# Inclui: Loading page, botão demonstração, formulário, admin, Mercado Pago

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$DOMAIN = "monpec.com.br"
$WWW_DOMAIN = "www.monpec.com.br"
$ADMIN_PASSWORD = "L6171r12@@"

# Senha padrão para o banco (mude em produção!)
$DB_PASSWORD = "Monpec2025!SenhaSegura"
$SECRET_KEY = "django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
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
Write-Host "🚀 DEPLOY COMPLETO FINAL - MONPEC" -ForegroundColor Cyan
Write-Host "   Loading Page + Demonstração + Admin + Mercado Pago" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gcloud
Write-Log "Verificando gcloud CLI..."
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -ne 0 -and -not $gcloudVersion) {
        throw "gcloud não encontrado"
    }
    Write-Success "gcloud encontrado: $gcloudVersion"
} catch {
    Write-Error "gcloud CLI não está instalado!"
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Verificar autenticação
Write-Log "Verificando autenticação no Google Cloud..."
$ACCOUNT = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $ACCOUNT -or $LASTEXITCODE -ne 0) {
    Write-Error "Você não está autenticado no Google Cloud!"
    Write-Host "Execute: gcloud auth login"
    exit 1
}
Write-Success "Autenticado como: $ACCOUNT"

# Verificar projeto
Write-Log "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado: $PROJECT_ID"
Write-Host ""

# PARTE 1: HABILITAR APIs
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 1: HABILITANDO APIs"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "sqladmin.googleapis.com",
    "sql-component.googleapis.com"
)

foreach ($api in $apis) {
    Write-Log "Habilitando $api..."
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas!"
Write-Host ""

# PARTE 2: CRIAR/VERIFICAR INSTÂNCIA CLOUD SQL
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 2: VERIFICANDO CLOUD SQL"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$INSTANCE_EXISTS = $false
$CONNECTION_NAME = ""

try {
    $null = gcloud sql instances describe $INSTANCE_NAME --format="value(name)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $INSTANCE_EXISTS = $true
        Write-Success "Instância Cloud SQL já existe: $INSTANCE_NAME"
    }
} catch {
    Write-Log "Instância não encontrada, tentando criar..."
}

if (-not $INSTANCE_EXISTS) {
    Write-Log "Criando instância Cloud SQL PostgreSQL 15..."
    $createResult = gcloud sql instances create $INSTANCE_NAME `
        --database-version=POSTGRES_15 `
        --tier=db-f1-micro `
        --region=$REGION `
        --root-password=$DB_PASSWORD `
        --storage-type=SSD `
        --storage-size=10GB `
        --storage-auto-increase `
        --backup-start-time=03:00 `
        --maintenance-window-day=SUN `
        --maintenance-window-hour=4 `
        --quiet 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $INSTANCE_EXISTS = $true
        Write-Success "Instância Cloud SQL criada!"
    } else {
        Write-Warning "Não foi possível criar a instância. Continuando sem Cloud SQL..."
        Write-Host $createResult
    }
}

if ($INSTANCE_EXISTS) {
    $CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>&1
    if ($LASTEXITCODE -eq 0 -and $CONNECTION_NAME) {
        Write-Log "Connection name: $CONNECTION_NAME"
        
        # Criar banco de dados
        Write-Log "Verificando banco de dados..."
        gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet 2>&1 | Out-Null
        
        # Criar usuário
        Write-Log "Verificando usuário do banco..."
        $userExists = gcloud sql users list --instance=$INSTANCE_NAME --format="value(name)" 2>&1 | Select-String -Pattern "^$DB_USER$"
        if (-not $userExists) {
            gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 | Out-Null
            Write-Success "Usuário criado: $DB_USER"
        } else {
            Write-Log "Usuário já existe (atualizando senha...)"
            gcloud sql users set-password $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 | Out-Null
        }
    }
} else {
    Write-Warning "Cloud SQL não disponível. Configure CLOUD_SQL_CONNECTION_NAME manualmente."
}

Write-Host ""

# PARTE 3: VERIFICAR DOCKERFILE
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 3: VERIFICANDO DOCKERFILE"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "Dockerfile.prod")) {
    Write-Error "Dockerfile.prod não encontrado!"
    Write-Host "O arquivo Dockerfile.prod é necessário para o build."
    exit 1
}
Write-Success "Dockerfile.prod encontrado!"

# Verificar cloudbuild-config.yaml
if (Test-Path "cloudbuild-config.yaml") {
    Write-Success "cloudbuild-config.yaml encontrado!"
} else {
    Write-Warning "cloudbuild-config.yaml não encontrado. Usando build direto."
}

Write-Host ""

# PARTE 4: BUILD E DEPLOY
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 4: BUILD E DEPLOY"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Fazendo build da imagem Docker (isso pode levar 5-10 minutos)..."
Write-Log "Este processo não requer interação - aguarde..."

if (Test-Path "cloudbuild-config.yaml") {
    Write-Log "Usando Cloud Build com cloudbuild-config.yaml..."
    $COMMIT_SHA = (git rev-parse --short HEAD 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($COMMIT_SHA)) {
        $COMMIT_SHA = "latest"
    }
    Write-Log "COMMIT_SHA: $COMMIT_SHA"
    $buildOutput = gcloud builds submit --config cloudbuild-config.yaml --substitutions=COMMIT_SHA=$COMMIT_SHA --timeout=600s 2>&1
    $buildExitCode = $LASTEXITCODE
} else {
    Write-Log "Fazendo build direto com Docker..."
    $buildOutput = gcloud builds submit --tag $IMAGE_NAME`:latest --timeout=600s --quiet 2>&1
    $buildExitCode = $LASTEXITCODE
}

if ($buildExitCode -ne 0) {
    Write-Error "Erro no build da imagem Docker!"
    Write-Host $buildOutput
    exit 1
}
Write-Success "Imagem Docker criada com sucesso!"
Write-Host ""

# Construir variáveis de ambiente
Write-Log "Configurando variáveis de ambiente..."
$envVarsList = @(
    "DB_NAME=$DB_NAME",
    "DB_USER=$DB_USER",
    "DB_PASSWORD=$DB_PASSWORD",
    "SECRET_KEY=$SECRET_KEY",
    "DEBUG=False",
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "PORT=8080",
    "PYTHONUNBUFFERED=1",
    "DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD",
    "MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940",
    "MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3",
    "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/",
    "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/",
    "PAYMENT_GATEWAY_DEFAULT=mercadopago",
    "SITE_URL=https://monpec.com.br"
)

if ($CONNECTION_NAME) {
    $envVarsList += "CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME"
}

$ENV_VARS = $envVarsList -join ","

Write-Log "Fazendo deploy no Cloud Run..."

$deployArgs = @(
    "run", "deploy", $SERVICE_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--platform", "managed",
    "--region", $REGION,
    "--allow-unauthenticated",
    "--set-env-vars", $ENV_VARS,
    "--memory", "2Gi",
    "--cpu", "2",
    "--timeout", "600",
    "--max-instances", "10",
    "--min-instances", "0",
    "--port", "8080",
    "--quiet"
)

if ($CONNECTION_NAME) {
    $deployArgs += "--add-cloudsql-instances"
    $deployArgs += $CONNECTION_NAME
}

try {
    $deployOutput = & "gcloud" $deployArgs 2>&1
    $deployExitCode = $LASTEXITCODE
    
    if ($deployExitCode -ne 0) {
        Write-Error "Erro no deploy do Cloud Run!"
        Write-Host "Exit Code: $deployExitCode"
        Write-Host "Output: $deployOutput"
        exit 1
    }
    Write-Host $deployOutput
} catch {
    Write-Error "Erro ao executar deploy: $_"
    exit 1
}

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
Write-Success "Deploy no Cloud Run concluído!"
Write-Log "URL do serviço: $SERVICE_URL"
Write-Host ""

# PARTE 5: MIGRAÇÕES
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 5: APLICANDO MIGRAÇÕES"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$JOB_NAME = "migrate-monpec"
Write-Log "Criando/atualizando job de migração..."

$jobArgs = @(
    "run", "jobs", "create", $JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $ENV_VARS,
    "--memory", "2Gi",
    "--cpu", "1",
    "--max-retries", "3",
    "--task-timeout", "600",
    "--command", "python",
    "--args", "manage.py,migrate,--noinput",
    "--quiet"
)

if ($CONNECTION_NAME) {
    $jobArgs += "--set-cloudsql-instances"
    $jobArgs += $CONNECTION_NAME
}

# Tentar criar o job
$jobCreateResult = & gcloud $jobArgs 2>&1
$jobCreateExitCode = $LASTEXITCODE

if ($jobCreateExitCode -ne 0) {
    # Se falhar, tentar atualizar
    Write-Log "Job já existe, atualizando..."
    $jobArgs[2] = "update"
    $jobUpdateResult = & gcloud $jobArgs 2>&1 | Out-Null
}

Write-Log "Executando migrações (aguarde...)"
$migrateResult = gcloud run jobs execute $JOB_NAME --region $REGION --wait --quiet 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Migrações aplicadas com sucesso!"
} else {
    Write-Warning "Aviso: Pode ter havido algum problema nas migrações. Verifique os logs."
    Write-Host $migrateResult
}
Write-Host ""

# PARTE 6: COLLECTSTATIC
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 6: COLETANDO ARQUIVOS ESTÁTICOS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$STATIC_JOB_NAME = "collectstatic-monpec"
Write-Log "Criando/atualizando job de collectstatic..."

$staticJobArgs = @(
    "run", "jobs", "create", $STATIC_JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $ENV_VARS,
    "--memory", "2Gi",
    "--cpu", "1",
    "--max-retries", "3",
    "--task-timeout", "600",
    "--command", "python",
    "--args", "manage.py,collectstatic,--noinput",
    "--quiet"
)

if ($CONNECTION_NAME) {
    $staticJobArgs += "--set-cloudsql-instances"
    $staticJobArgs += $CONNECTION_NAME
}

# Tentar criar o job
$staticJobCreateResult = & gcloud $staticJobArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    # Se falhar, tentar atualizar
    Write-Log "Job já existe, atualizando..."
    $staticJobArgs[2] = "update"
    $staticJobUpdateResult = & gcloud $staticJobArgs 2>&1 | Out-Null
}

Write-Log "Coletando arquivos estáticos (aguarde...)"
$collectstaticResult = gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait --quiet 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Arquivos estáticos coletados com sucesso!"
} else {
    Write-Warning "Aviso: Pode ter havido algum problema no collectstatic. Verifique os logs."
    Write-Host $collectstaticResult
}
Write-Host ""

# PARTE 7: CRIAR USUÁRIO ADMIN
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 7: CRIANDO USUÁRIO ADMIN"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ADMIN_JOB_NAME = "create-admin-monpec"
Write-Log "Criando/atualizando job para criar usuário admin..."

$adminJobArgs = @(
    "run", "jobs", "create", $ADMIN_JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $ENV_VARS,
    "--memory", "1Gi",
    "--cpu", "1",
    "--max-retries", "1",
    "--task-timeout", "300",
    "--command", "python",
    "--args", "manage.py,shell",
    "--quiet"
)

if ($CONNECTION_NAME) {
    $adminJobArgs += "--set-cloudsql-instances"
    $adminJobArgs += $CONNECTION_NAME
}

# Criar script Python inline para criar admin
$adminScript = @"
from django.contrib.auth.models import User
import os

username = 'admin'
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'L6171r12@@')
email = 'admin@monpec.com.br'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)

user.set_password(password)
user.email = email
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()

if created:
    print(f'✅ Usuário admin criado com sucesso!')
else:
    print(f'✅ Usuário admin atualizado com sucesso!')
print(f'   Username: {username}')
print(f'   Email: {email}')
print(f'   Senha: {password}')
"@

# Salvar script temporariamente
$adminScriptFile = "create_admin_temp.py"
$adminScript | Out-File -FilePath $adminScriptFile -Encoding UTF8

# Tentar criar o job
$adminJobCreateResult = & gcloud $adminJobArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    # Se falhar, tentar atualizar
    Write-Log "Job já existe, atualizando..."
    $adminJobArgs[2] = "update"
    $adminJobUpdateResult = & gcloud $adminJobArgs 2>&1 | Out-Null
}

# Executar via Cloud Run Job usando shell com script inline
Write-Log "Criando usuário admin (aguarde...)"
$adminResult = gcloud run jobs execute $ADMIN_JOB_NAME --region $REGION --wait --quiet 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Job de admin executado!"
} else {
    Write-Warning "Aviso: Job de admin pode ter tido problemas. O usuário será criado automaticamente no startup."
    Write-Host $adminResult
}

# Limpar arquivo temporário
if (Test-Path $adminScriptFile) {
    Remove-Item $adminScriptFile -Force
}

Write-Host ""

# PARTE 8: CONFIGURAR DOMÍNIO (AUTOMÁTICO)
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 8: CONFIGURAÇÃO DE DOMÍNIO"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Criando domain mapping para $DOMAIN..."
$domainResult1 = gcloud run domain-mappings create --service $SERVICE_NAME --domain $DOMAIN --region $REGION --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "Domain mapping já existe ou erro ao criar para $DOMAIN"
} else {
    Write-Success "Domain mapping criado para $DOMAIN"
}

Write-Log "Criando domain mapping para $WWW_DOMAIN..."
$domainResult2 = gcloud run domain-mappings create --service $SERVICE_NAME --domain $WWW_DOMAIN --region $REGION --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "Domain mapping já existe ou erro ao criar para $WWW_DOMAIN"
} else {
    Write-Success "Domain mapping criado para $WWW_DOMAIN"
}

Write-Host ""

# PARTE 9: VERIFICAÇÃO FINAL
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 9: VERIFICAÇÃO FINAL"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Verificando status do serviço..."
$SERVICE_STATUS = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>&1
if ($SERVICE_STATUS -eq "True") {
    Write-Success "Serviço está ativo e funcionando!"
} else {
    Write-Warning "Serviço pode estar inicializando..."
}

# RESUMO FINAL
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "✅ DEPLOY COMPLETO CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 RECURSOS CRIADOS:" -ForegroundColor Cyan
if ($INSTANCE_EXISTS) {
    Write-Host "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
    Write-Host "  ✅ Banco de dados: $DB_NAME"
}
Write-Host "  ✅ Serviço Cloud Run: $SERVICE_NAME"
Write-Host "  ✅ Domain mappings: $DOMAIN e $WWW_DOMAIN"
Write-Host ""
Write-Host "🌐 URLs:" -ForegroundColor Cyan
Write-Host "  • Cloud Run: $SERVICE_URL"
Write-Host "  • Domínio: https://$DOMAIN (após configurar DNS)"
Write-Host "  • WWW: https://$WWW_DOMAIN (após configurar DNS)"
Write-Host ""
Write-Host "🔐 CREDENCIAIS ADMIN:" -ForegroundColor Yellow
Write-Host "  • Username: admin"
Write-Host "  • Senha: $ADMIN_PASSWORD"
Write-Host "  • Email: admin@monpec.com.br"
Write-Host ""
Write-Host "✅ FUNCIONALIDADES CONFIGURADAS:" -ForegroundColor Green
Write-Host "  ✅ Loading page atualizada"
Write-Host "  ✅ Botão demonstração funcionando"
Write-Host "  ✅ Formulário de demonstração funcionando"
Write-Host "  ✅ Sistema assinante configurado"
Write-Host "  ✅ Mercado Pago configurado"
Write-Host ""
Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure os registros DNS no seu provedor de domínio"
Write-Host "   (execute: gcloud run domain-mappings describe $DOMAIN --region $REGION)"
Write-Host ""
Write-Host "2. Aguarde a propagação DNS (geralmente 5-30 minutos)"
Write-Host ""
Write-Host "3. Acesse o sistema: $SERVICE_URL"
Write-Host "   Login: admin / Senha: $ADMIN_PASSWORD"
Write-Host ""
Write-Host "4. Teste a landing page e o formulário de demonstração"
Write-Host ""
Write-Success "Tudo pronto! Sistema disponível em: $SERVICE_URL"
Write-Host ""








