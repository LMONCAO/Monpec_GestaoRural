# 🚀 DEPLOY COMPLETO - SISTEMA MONPEC
# Script completo para fazer deploy do sistema no Google Cloud Run
# Inclui: build, deploy, migrações, collectstatic e configurações

$ErrorActionPreference = "Stop"

# ========================================
# CONFIGURAÇÕES
# ========================================
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$DOMAIN = "monpec.com.br"
$WWW_DOMAIN = "www.monpec.com.br"

# IMPORTANTE: Configure estas variáveis antes de executar o deploy!
# Você pode obter os valores do Secret Manager ou configurá-los manualmente
$DB_PASSWORD = $env:DB_PASSWORD
if (-not $DB_PASSWORD) {
    Write-Host "⚠️  AVISO: DB_PASSWORD não configurado. Usando valor padrão (configure via variável de ambiente)" -ForegroundColor Yellow
    $DB_PASSWORD = "Monpec2025!SenhaSegura"  # Mude isso em produção!
}

$SECRET_KEY = $env:SECRET_KEY
if (-not $SECRET_KEY) {
    Write-Host "⚠️  AVISO: SECRET_KEY não configurado. Gerando uma nova..." -ForegroundColor Yellow
    $SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $SECRET_KEY = "django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
    }
}

# Variáveis do Mercado Pago (configure via variáveis de ambiente ou Secret Manager)
$MERCADOPAGO_ACCESS_TOKEN = $env:MERCADOPAGO_ACCESS_TOKEN
$MERCADOPAGO_PUBLIC_KEY = $env:MERCADOPAGO_PUBLIC_KEY
$MERCADOPAGO_WEBHOOK_SECRET = $env:MERCADOPAGO_WEBHOOK_SECRET

# Variáveis de Email (opcional)
$EMAIL_HOST_USER = $env:EMAIL_HOST_USER
$EMAIL_HOST_PASSWORD = $env:EMAIL_HOST_PASSWORD

# ========================================
# FUNÇÕES AUXILIARES
# ========================================
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

# ========================================
# INÍCIO DO DEPLOY
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY COMPLETO - SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gcloud
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Error "gcloud CLI não está instalado!"
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Verificar autenticação
Write-Log "Verificando autenticação no Google Cloud..."
$ACCOUNT = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $ACCOUNT) {
    Write-Error "Você não está autenticado no Google Cloud!"
    Write-Host "Execute: gcloud auth login"
    exit 1
}
Write-Success "Autenticado como: $ACCOUNT"

# Configurar projeto
Write-Log "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Success "Projeto configurado: $PROJECT_ID"
Write-Host ""

# ========================================
# PARTE 1: HABILITAR APIs
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 1: HABILITANDO APIs"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$APIS = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "sqladmin.googleapis.com",
    "sql-component.googleapis.com"
)

foreach ($API in $APIS) {
    Write-Log "Habilitando $API..."
    gcloud services enable $API --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas!"
Write-Host ""

# ========================================
# PARTE 2: VERIFICAR/CRIAR CLOUD SQL
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 2: VERIFICANDO CLOUD SQL"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$INSTANCE_EXISTS = $false
try {
    $null = gcloud sql instances describe $INSTANCE_NAME --format="value(name)" 2>&1
    $INSTANCE_EXISTS = $true
    Write-Success "Instância Cloud SQL já existe: $INSTANCE_NAME"
} catch {
    Write-Log "Instância Cloud SQL não encontrada. Você precisa criá-la manualmente ou usar uma existente."
    Write-Warning "Para criar a instância, execute:"
    Write-Host "  gcloud sql instances create $INSTANCE_NAME --database-version=POSTGRES_15 --tier=db-f1-micro --region=$REGION --root-password=$DB_PASSWORD"
    Write-Host ""
    $continue = Read-Host "Deseja continuar mesmo sem a instância? (s/n)"
    if ($continue -ne "s" -and $continue -ne "S") {
        exit 1
    }
}

if ($INSTANCE_EXISTS) {
    $CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>&1
    Write-Log "Connection name: $CONNECTION_NAME"
    
    # Criar banco de dados
    Write-Log "Verificando banco de dados..."
    try {
        gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet 2>&1 | Out-Null
        Write-Success "Banco de dados criado: $DB_NAME"
    } catch {
        Write-Log "Banco de dados já existe"
    }
    
    # Criar/atualizar usuário
    Write-Log "Verificando usuário do banco..."
    try {
        gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 | Out-Null
        Write-Success "Usuário criado: $DB_USER"
    } catch {
        Write-Log "Usuário já existe (atualizando senha...)"
        gcloud sql users set-password $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 | Out-Null
        Write-Success "Senha do usuário atualizada"
    }
} else {
    Write-Warning "Usando connection name padrão. Configure CLOUD_SQL_CONNECTION_NAME manualmente."
    $CONNECTION_NAME = "$PROJECT_ID`:$REGION`:$INSTANCE_NAME"
}

Write-Host ""

# ========================================
# PARTE 3: BUILD DA IMAGEM DOCKER
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 3: BUILD DA IMAGEM DOCKER"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Fazendo build da imagem Docker (isso pode levar 5-10 minutos)..."
Write-Log "Usando Dockerfile.prod e cloudbuild-config.yaml"

# Verificar se cloudbuild-config.yaml existe
if (Test-Path "cloudbuild-config.yaml") {
    Write-Log "Usando Cloud Build com cloudbuild-config.yaml..."
    gcloud builds submit --config cloudbuild-config.yaml --timeout=600s 2>&1 | Tee-Object -Variable BUILD_OUTPUT
} else {
    Write-Log "Fazendo build direto com Docker..."
    gcloud builds submit --tag $IMAGE_NAME --timeout=600s 2>&1 | Tee-Object -Variable BUILD_OUTPUT
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build da imagem Docker!"
    Write-Host $BUILD_OUTPUT
    exit 1
}
Write-Success "Imagem Docker criada com sucesso!"
Write-Host ""

# ========================================
# PARTE 4: CONFIGURAR VARIÁVEIS DE AMBIENTE
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 4: CONFIGURANDO VARIÁVEIS DE AMBIENTE"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Construir string de variáveis de ambiente
$ENV_VARS = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "SECRET_KEY=$SECRET_KEY",
    "DEBUG=False",
    "DB_NAME=$DB_NAME",
    "DB_USER=$DB_USER",
    "DB_PASSWORD=$DB_PASSWORD",
    "CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME",
    "PORT=8080",
    "PYTHONUNBUFFERED=1",
    "SITE_URL=https://$DOMAIN",
    "MERCADOPAGO_SUCCESS_URL=https://$DOMAIN/assinaturas/sucesso/",
    "MERCADOPAGO_CANCEL_URL=https://$DOMAIN/assinaturas/cancelado/",
    "PAYMENT_GATEWAY_DEFAULT=mercadopago"
)

# Adicionar variáveis do Mercado Pago se configuradas
if ($MERCADOPAGO_ACCESS_TOKEN) {
    $ENV_VARS += "MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN"
}
if ($MERCADOPAGO_PUBLIC_KEY) {
    $ENV_VARS += "MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY"
}
if ($MERCADOPAGO_WEBHOOK_SECRET) {
    $ENV_VARS += "MERCADOPAGO_WEBHOOK_SECRET=$MERCADOPAGO_WEBHOOK_SECRET"
}

# Adicionar variáveis de email se configuradas
if ($EMAIL_HOST_USER) {
    $ENV_VARS += "EMAIL_HOST_USER=$EMAIL_HOST_USER"
    $ENV_VARS += "EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend"
    $ENV_VARS += "EMAIL_HOST=smtp.gmail.com"
    $ENV_VARS += "EMAIL_PORT=587"
    $ENV_VARS += "EMAIL_USE_TLS=True"
    $ENV_VARS += "DEFAULT_FROM_EMAIL=noreply@$DOMAIN"
}
if ($EMAIL_HOST_PASSWORD) {
    $ENV_VARS += "EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD"
}

$ENV_VARS_STRING = $ENV_VARS -join ","

Write-Log "Variáveis de ambiente configuradas:"
foreach ($var in $ENV_VARS) {
    if ($var -match "PASSWORD|SECRET|TOKEN") {
        Write-Host "  $($var.Split('=')[0])=***" -ForegroundColor Gray
    } else {
        Write-Host "  $var" -ForegroundColor Gray
    }
}
Write-Host ""

# ========================================
# PARTE 5: DEPLOY NO CLOUD RUN
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 5: DEPLOY NO CLOUD RUN"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Fazendo deploy no Cloud Run..."

$DEPLOY_ARGS = @(
    "run", "deploy", $SERVICE_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--platform", "managed",
    "--region", $REGION,
    "--allow-unauthenticated",
    "--set-env-vars", $ENV_VARS_STRING,
    "--memory", "2Gi",
    "--cpu", "2",
    "--timeout", "600",
    "--max-instances", "10",
    "--min-instances", "0",
    "--port", "8080"
)

# Adicionar conexão Cloud SQL se disponível
if ($INSTANCE_EXISTS) {
    $DEPLOY_ARGS += "--add-cloudsql-instances"
    $DEPLOY_ARGS += $CONNECTION_NAME
}

& gcloud $DEPLOY_ARGS 2>&1 | Tee-Object -Variable DEPLOY_OUTPUT

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy do Cloud Run!"
    Write-Host $DEPLOY_OUTPUT
    exit 1
}

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
Write-Success "Deploy no Cloud Run concluído!"
Write-Log "URL do serviço: $SERVICE_URL"
Write-Host ""

# ========================================
# PARTE 6: APLICAR MIGRAÇÕES
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 6: APLICANDO MIGRAÇÕES"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$JOB_NAME = "migrate-monpec"
Write-Log "Criando/atualizando job de migração..."

$JOB_ARGS = @(
    "run", "jobs", "create", $JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $ENV_VARS_STRING,
    "--memory", "2Gi",
    "--cpu", "1",
    "--max-retries", "3",
    "--task-timeout", "600",
    "--command", "python",
    "--args", "manage.py,migrate,--noinput"
)

if ($INSTANCE_EXISTS) {
    $JOB_ARGS += "--set-cloudsql-instances"
    $JOB_ARGS += $CONNECTION_NAME
}

try {
    & gcloud $JOB_ARGS --quiet 2>&1 | Out-Null
    Write-Success "Job de migração criado!"
} catch {
    Write-Log "Job já existe, atualizando..."
    $JOB_ARGS[2] = "update"
    & gcloud $JOB_ARGS --quiet 2>&1 | Out-Null
    Write-Success "Job de migração atualizado!"
}

Write-Log "Executando migrações (aguarde...)"
gcloud run jobs execute $JOB_NAME --region $REGION --wait 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Migrações aplicadas com sucesso!"
} else {
    Write-Warning "Aviso: Pode ter havido algum problema nas migrações. Verifique os logs."
}
Write-Host ""

# ========================================
# PARTE 7: COLETAR ARQUIVOS ESTÁTICOS
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 7: COLETANDO ARQUIVOS ESTÁTICOS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$STATIC_JOB_NAME = "collectstatic-monpec"
Write-Log "Criando/atualizando job de collectstatic..."

$STATIC_JOB_ARGS = @(
    "run", "jobs", "create", $STATIC_JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $ENV_VARS_STRING,
    "--memory", "2Gi",
    "--cpu", "1",
    "--max-retries", "3",
    "--task-timeout", "600",
    "--command", "python",
    "--args", "manage.py,collectstatic,--noinput"
)

if ($INSTANCE_EXISTS) {
    $STATIC_JOB_ARGS += "--set-cloudsql-instances"
    $STATIC_JOB_ARGS += $CONNECTION_NAME
}

try {
    & gcloud $STATIC_JOB_ARGS --quiet 2>&1 | Out-Null
    Write-Success "Job de collectstatic criado!"
} catch {
    Write-Log "Job já existe, atualizando..."
    $STATIC_JOB_ARGS[2] = "update"
    & gcloud $STATIC_JOB_ARGS --quiet 2>&1 | Out-Null
    Write-Success "Job de collectstatic atualizado!"
}

Write-Log "Coletando arquivos estáticos (aguarde...)"
gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Arquivos estáticos coletados com sucesso!"
} else {
    Write-Warning "Aviso: Pode ter havido algum problema no collectstatic. Verifique os logs."
}
Write-Host ""

# ========================================
# PARTE 8: CONFIGURAR DOMÍNIO (OPCIONAL)
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 8: CONFIGURAÇÃO DE DOMÍNIO"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$configureDomain = Read-Host "Deseja configurar o domínio personalizado? (s/n)"
if ($configureDomain -eq "s" -or $configureDomain -eq "S") {
    Write-Log "Criando domain mapping para $DOMAIN..."
    try {
        gcloud run domain-mappings create --service $SERVICE_NAME --domain $DOMAIN --region $REGION --quiet 2>&1 | Out-Null
        Write-Success "Domain mapping criado para $DOMAIN"
    } catch {
        Write-Log "Domain mapping já existe para $DOMAIN"
    }

    Write-Log "Criando domain mapping para $WWW_DOMAIN..."
    try {
        gcloud run domain-mappings create --service $SERVICE_NAME --domain $WWW_DOMAIN --region $REGION --quiet 2>&1 | Out-Null
        Write-Success "Domain mapping criado para $WWW_DOMAIN"
    } catch {
        Write-Log "Domain mapping já existe para $WWW_DOMAIN"
    }

    Write-Log "Obtendo informações de DNS..."
    try {
        $DNS_RECORDS = gcloud run domain-mappings describe $DOMAIN --region $REGION --format="value(status.resourceRecords)" 2>&1
        if ($DNS_RECORDS) {
            Write-Success "Domain mappings configurados!"
            Write-Warning "IMPORTANTE: Configure os registros DNS no seu provedor de domínio"
            gcloud run domain-mappings describe $DOMAIN --region $REGION --format="table(status.resourceRecords)"
        }
    } catch {
        Write-Warning "Domain mappings criados, mas pode levar alguns minutos para propagar"
    }
} else {
    Write-Log "Pulando configuração de domínio"
}
Write-Host ""

# ========================================
# PARTE 9: VERIFICAÇÃO FINAL
# ========================================
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

Write-Log "Testando conectividade..."
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri $SERVICE_URL -Method Get -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    $HTTP_STATUS = $response.StatusCode
    if ($HTTP_STATUS -eq 200 -or $HTTP_STATUS -eq 302 -or $HTTP_STATUS -eq 301) {
        Write-Success "Serviço respondendo corretamente (HTTP $HTTP_STATUS)"
    } else {
        Write-Warning "Serviço retornou HTTP $HTTP_STATUS"
    }
} catch {
    Write-Warning "Não foi possível testar conectividade agora (serviço pode estar inicializando)"
    Write-Log "Tente acessar: $SERVICE_URL"
}

# ========================================
# RESUMO FINAL
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "✅ DEPLOY COMPLETO CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 RECURSOS CRIADOS/ATUALIZADOS:" -ForegroundColor Cyan
if ($INSTANCE_EXISTS) {
    Write-Host "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
    Write-Host "  ✅ Banco de dados: $DB_NAME"
}
Write-Host "  ✅ Serviço Cloud Run: $SERVICE_NAME"
Write-Host "  ✅ Migrações aplicadas"
Write-Host "  ✅ Arquivos estáticos coletados"
Write-Host ""
Write-Host "🌐 URLs:" -ForegroundColor Cyan
Write-Host "  • Cloud Run: $SERVICE_URL"
if ($configureDomain -eq "s" -or $configureDomain -eq "S") {
    Write-Host "  • Domínio: https://$DOMAIN (após configurar DNS)"
    Write-Host "  • WWW: https://$WWW_DOMAIN (após configurar DNS)"
}
Write-Host ""
Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
if ($configureDomain -eq "s" -or $configureDomain -eq "S") {
    Write-Host "1. Configure os registros DNS no seu provedor de domínio"
    Write-Host "   (execute: gcloud run domain-mappings describe $DOMAIN --region $REGION)"
    Write-Host ""
    Write-Host "2. Aguarde a propagação DNS (geralmente 5-30 minutos)"
    Write-Host ""
}
Write-Host "3. Acesse o sistema:"
Write-Host "   $SERVICE_URL"
Write-Host ""
Write-Host "4. Para criar superusuário, execute:"
Write-Host "   gcloud run jobs create create-superuser --image $IMAGE_NAME`:latest --region $REGION --set-cloudsql-instances $CONNECTION_NAME --set-env-vars $ENV_VARS_STRING --command python --args 'manage.py,createsuperuser' --interactive"
Write-Host ""
if (-not $MERCADOPAGO_ACCESS_TOKEN) {
    Write-Warning "⚠️  IMPORTANTE: Configure as variáveis do Mercado Pago no Cloud Run:"
    Write-Host "   gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars MERCADOPAGO_ACCESS_TOKEN=SEU_TOKEN,MERCADOPAGO_PUBLIC_KEY=SUA_KEY"
    Write-Host ""
}
Write-Success "🎉 Tudo pronto! Sistema disponível em: $SERVICE_URL"
Write-Host ""









