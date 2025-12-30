# 🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC.COM.BR
# Executa todo o processo de deploy sem necessidade de interação
# Projeto: monpec-sistema-rural

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
Write-Host "🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC" -ForegroundColor Cyan
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

# Verificar projeto
Write-Log "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Success "Projeto configurado: $PROJECT_ID"
Write-Host ""

# PARTE 1: HABILITAR APIs
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 1: HABILITANDO APIs"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable sql-component.googleapis.com --quiet
Write-Success "APIs habilitadas!"
Write-Host ""

# PARTE 2: CRIAR/VERIFICAR INSTÂNCIA CLOUD SQL
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
    Write-Log "Criando instância Cloud SQL PostgreSQL 15..."
    gcloud sql instances create $INSTANCE_NAME `
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
        --quiet
    Write-Success "Instância Cloud SQL criada!"
    $INSTANCE_EXISTS = $true
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
    
    # Criar usuário
    Write-Log "Verificando usuário do banco..."
    try {
        gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 | Out-Null
        Write-Success "Usuário criado: $DB_USER"
    } catch {
        Write-Log "Usuário já existe (atualizando senha...)"
        gcloud sql users set-password $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 | Out-Null
    }
}

Write-Host ""

# PARTE 3: BUILD E DEPLOY
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 3: BUILD E DEPLOY"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Fazendo build da imagem Docker (isso pode levar 5-10 minutos)..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s 2>&1 | Tee-Object -Variable BUILD_OUTPUT
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build da imagem Docker!"
    exit 1
}
Write-Success "Imagem Docker criada com sucesso!"
Write-Host ""

Write-Log "Fazendo deploy no Cloud Run..."
$ENV_VARS = "DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,PORT=8080"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 2 `
    --timeout 600 `
    --max-instances 10 `
    --min-instances 0 `
    --port 8080 `
    --quiet 2>&1 | Tee-Object -Variable DEPLOY_OUTPUT

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy do Cloud Run!"
    exit 1
}

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
Write-Success "Deploy no Cloud Run concluído!"
Write-Log "URL do serviço: $SERVICE_URL"
Write-Host ""

# PARTE 4: MIGRAÇÕES
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 4: APLICANDO MIGRAÇÕES"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$JOB_NAME = "migrate-monpec"
Write-Log "Criando job de migração..."
try {
    gcloud run jobs create $JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --memory 2Gi `
        --cpu 1 `
        --max-retries 3 `
        --task-timeout 600 `
        --command python `
        --args "manage.py,migrate,--noinput" `
        --quiet 2>&1 | Out-Null
    Write-Success "Job de migração criado!"
} catch {
    Write-Log "Job já existe, atualizando..."
    gcloud run jobs update $JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --memory 2Gi `
        --cpu 1 `
        --max-retries 3 `
        --task-timeout 600 `
        --command python `
        --args "manage.py,migrate,--noinput" `
        --quiet 2>&1 | Out-Null
}

Write-Log "Executando migrações (aguarde...)"
gcloud run jobs execute $JOB_NAME --region $REGION --wait 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Migrações aplicadas com sucesso!"
} else {
    Write-Warning "Aviso: Pode ter havido algum problema nas migrações. Verifique os logs."
}
Write-Host ""

# PARTE 5: COLLECTSTATIC
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 5: COLETANDO ARQUIVOS ESTÁTICOS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$STATIC_JOB_NAME = "collectstatic-monpec"
Write-Log "Criando job de collectstatic..."
try {
    gcloud run jobs create $STATIC_JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --memory 2Gi `
        --cpu 1 `
        --max-retries 3 `
        --task-timeout 600 `
        --command python `
        --args "manage.py,collectstatic,--noinput" `
        --quiet 2>&1 | Out-Null
    Write-Success "Job de collectstatic criado!"
} catch {
    Write-Log "Job já existe, atualizando..."
    gcloud run jobs update $STATIC_JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --memory 2Gi `
        --cpu 1 `
        --max-retries 3 `
        --task-timeout 600 `
        --command python `
        --args "manage.py,collectstatic,--noinput" `
        --quiet 2>&1 | Out-Null
}

Write-Log "Coletando arquivos estáticos (aguarde...)"
gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Arquivos estáticos coletados com sucesso!"
} else {
    Write-Warning "Aviso: Pode ter havido algum problema no collectstatic. Verifique os logs."
}
Write-Host ""

# PARTE 6: CONFIGURAR DOMÍNIO
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 6: CONFIGURAÇÃO DE DOMÍNIO"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

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
Write-Host ""

# PARTE 7: VERIFICAÇÃO FINAL
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 7: VERIFICAÇÃO FINAL"
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

# RESUMO FINAL
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "✅ DEPLOY COMPLETO CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 RECURSOS CRIADOS:" -ForegroundColor Cyan
Write-Host "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
Write-Host "  ✅ Banco de dados: $DB_NAME"
Write-Host "  ✅ Serviço Cloud Run: $SERVICE_NAME"
Write-Host "  ✅ Domain mappings: $DOMAIN e $WWW_DOMAIN"
Write-Host ""
Write-Host "🌐 URLs:" -ForegroundColor Cyan
Write-Host "  • Cloud Run: $SERVICE_URL"
Write-Host "  • Domínio: https://$DOMAIN (após configurar DNS)"
Write-Host "  • WWW: https://$WWW_DOMAIN (após configurar DNS)"
Write-Host ""
Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure os registros DNS no seu provedor de domínio"
Write-Host "   (execute: gcloud run domain-mappings describe $DOMAIN --region $REGION)"
Write-Host ""
Write-Host "2. Aguarde a propagação DNS (geralmente 5-30 minutos)"
Write-Host ""
Write-Host "3. Acesse o sistema:"
Write-Host "   $SERVICE_URL (funciona imediatamente)"
Write-Host ""
Write-Host "4. Para criar superusuário, execute:"
Write-Host "   gcloud run jobs create create-superuser --image $IMAGE_NAME --region $REGION --set-cloudsql-instances $CONNECTION_NAME --set-env-vars $ENV_VARS --command python --args 'manage.py,createsuperuser' --interactive"
Write-Host ""
Write-Success "🎉 Tudo pronto! Sistema disponível em: $SERVICE_URL"
Write-Host ""

















