# 🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC.COM.BR (PowerShell)
# Executa limpeza, instalação, configuração de domínio e verificação
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

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Info "Este script vai:"
Write-Host "  1. Limpar recursos antigos do GCP"
Write-Host "  2. Criar instância Cloud SQL"
Write-Host "  3. Fazer build e deploy no Cloud Run"
Write-Host "  4. Configurar domínio monpec.com.br"
Write-Host "  5. Verificar se tudo está funcionando"
Write-Host ""

# Verificar gcloud
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Error "gcloud CLI não está instalado!"
    exit 1
}

# Verificar projeto
Write-Log "Verificando projeto..."
$CURRENT_PROJECT = gcloud config get-value project 2>$null
if ($CURRENT_PROJECT -ne $PROJECT_ID) {
    Write-Warning "Projeto atual: $CURRENT_PROJECT"
    gcloud config set project $PROJECT_ID
    Write-Success "Projeto configurado para: $PROJECT_ID"
} else {
    Write-Success "Projeto correto: $PROJECT_ID"
}
Write-Host ""

# Solicitar credenciais
Write-Warning "Você precisará fornecer:"
Write-Host "  1. Senha do banco de dados (mínimo 8 caracteres)"
Write-Host "  2. SECRET_KEY do Django (ou deixar gerar automaticamente)"
Write-Host ""

$securePassword = Read-Host "Digite a senha do banco de dados" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$DB_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
if ($DB_PASSWORD.Length -lt 8) {
    Write-Error "Senha deve ter no mínimo 8 caracteres!"
    exit 1
}

$response = Read-Host "Deseja fornecer SECRET_KEY? (s/n)"
if ($response -eq "s" -or $response -eq "S") {
    $secureKey = Read-Host "Digite a SECRET_KEY" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $SECRET_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
} else {
    $bytes = New-Object byte[] 50
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $SECRET_KEY = [Convert]::ToBase64String($bytes)
    Write-Success "SECRET_KEY gerada automaticamente"
}
Write-Host ""

# PARTE 1: LIMPEZA
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 1: LIMPEZA DE RECURSOS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Deletando serviço Cloud Run..."
try {
    gcloud run services delete $SERVICE_NAME --region $REGION --quiet 2>$null
} catch {
    Write-Warning "Serviço não encontrado"
}

Write-Log "Deletando jobs..."
try {
    $JOBS = gcloud run jobs list --region $REGION --format="value(name)" 2>$null | Where-Object { $_ -like "*monpec*" }
    foreach ($JOB in $JOBS) {
        gcloud run jobs delete $JOB --region $REGION --quiet 2>$null
    }
} catch {
    Write-Warning "Nenhum job encontrado"
}

Write-Log "Verificando instância Cloud SQL..."
try {
    $null = gcloud sql instances describe $INSTANCE_NAME 2>&1
    Write-Warning "Instância Cloud SQL existe. Deseja deletar? (s/n)"
    $response = Read-Host
    if ($response -eq "s" -or $response -eq "S") {
        gcloud sql instances delete $INSTANCE_NAME --quiet
        Write-Success "Instância deletada!"
        Write-Log "Aguardando 30 segundos para garantir exclusão..."
        Start-Sleep -Seconds 30
    }
} catch {
    Write-Warning "Instância não encontrada"
}

Write-Success "Limpeza concluída!"
Write-Host ""

# PARTE 2: INSTALAÇÃO
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 2: INSTALAÇÃO DO ZERO"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable sql-component.googleapis.com --quiet
Write-Success "APIs habilitadas!"

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
    --enable-bin-log `
    --maintenance-window-day=SUN `
    --maintenance-window-hour=4 `
    --quiet
Write-Success "Instância Cloud SQL criada!"

$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)"
Write-Log "Connection name: $CONNECTION_NAME"

Write-Log "Criando banco de dados e usuário..."
try {
    gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet
} catch {
    Write-Warning "Banco já existe"
}
try {
    gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet
} catch {
    Write-Warning "Usuário já existe"
}
Write-Success "Banco e usuário criados!"

Write-Log "Fazendo build da imagem Docker (isso pode levar alguns minutos)..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
Write-Success "Imagem Docker criada!"

Write-Log "Fazendo deploy no Cloud Run..."
$ENV_VARS = "DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 4Gi `
    --cpu 2 `
    --timeout 600 `
    --max-instances 10 `
    --min-instances 0 `
    --port 8080 `
    --quiet

Write-Success "Deploy no Cloud Run concluído!"

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Log "URL do serviço: $SERVICE_URL"

Write-Log "Aplicando migrações..."
$JOB_NAME = "migrate-monpec"
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
        --quiet
} catch {
    Write-Warning "Job já existe"
}

gcloud run jobs execute $JOB_NAME --region $REGION --wait
Write-Success "Migrações aplicadas!"

Write-Log "Coletando arquivos estáticos..."
$STATIC_JOB_NAME = "collectstatic-monpec"
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
        --quiet
} catch {
    Write-Warning "Job já existe"
}

gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait
Write-Success "Arquivos estáticos coletados!"

# PARTE 3: CONFIGURAR DOMÍNIO
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 3: CONFIGURAÇÃO DE DOMÍNIO"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Criando domain mapping para $DOMAIN..."
try {
    gcloud run domain-mappings create --service $SERVICE_NAME --domain $DOMAIN --region $REGION --quiet
} catch {
    Write-Warning "Domain mapping já existe"
}

Write-Log "Criando domain mapping para $WWW_DOMAIN..."
try {
    gcloud run domain-mappings create --service $SERVICE_NAME --domain $WWW_DOMAIN --region $REGION --quiet
} catch {
    Write-Warning "Domain mapping já existe"
}

Write-Log "Obtendo informações de DNS..."
try {
    $DOMAIN_MAPPING = gcloud run domain-mappings describe $DOMAIN --region $REGION --format="value(status.resourceRecords)" 2>$null
    if ($DOMAIN_MAPPING) {
        Write-Success "Domain mappings criados!"
        Write-Warning "IMPORTANTE: Configure os registros DNS no seu provedor de domínio:"
        Write-Host ""
        gcloud run domain-mappings describe $DOMAIN --region $REGION --format="table(status.resourceRecords)"
        Write-Host ""
    }
} catch {
    Write-Warning "Domain mappings criados, mas pode levar alguns minutos para propagar"
}

# PARTE 4: VERIFICAÇÃO
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 4: VERIFICAÇÃO"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Verificando status do serviço..."
$SERVICE_STATUS = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>$null
if ($SERVICE_STATUS -eq "True") {
    Write-Success "Serviço está ativo!"
} else {
    Write-Error "Serviço não está ativo!"
}

Write-Log "Testando conectividade..."
try {
    $response = Invoke-WebRequest -Uri $SERVICE_URL -Method Get -TimeoutSec 10 -UseBasicParsing
    $HTTP_STATUS = $response.StatusCode
    if ($HTTP_STATUS -eq 200 -or $HTTP_STATUS -eq 302 -or $HTTP_STATUS -eq 301) {
        Write-Success "Serviço respondendo (HTTP $HTTP_STATUS)"
    } else {
        Write-Warning "Serviço retornou HTTP $HTTP_STATUS (pode estar inicializando)"
    }
} catch {
    Write-Warning "Não foi possível testar conectividade (pode estar inicializando)"
}

# RESUMO FINAL
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "DEPLOY COMPLETO CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Log "Recursos criados:"
Write-Host "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
Write-Host "  ✅ Banco de dados: $DB_NAME"
Write-Host "  ✅ Serviço Cloud Run: $SERVICE_NAME"
Write-Host "  ✅ Domain mappings: $DOMAIN e $WWW_DOMAIN"
Write-Host ""
Write-Log "URLs:"
Write-Host "  🌐 Cloud Run: $SERVICE_URL"
Write-Host "  🌐 Domínio: https://$DOMAIN (pode levar alguns minutos para propagar)"
Write-Host "  🌐 WWW: https://$WWW_DOMAIN (pode levar alguns minutos para propagar)"
Write-Host ""
Write-Warning "PRÓXIMOS PASSOS:"
Write-Host ""
Write-Host "1. Configure os registros DNS no seu provedor de domínio"
Write-Host "   (os registros foram exibidos acima)"
Write-Host ""
Write-Host "2. Aguarde a propagação DNS (pode levar até 48 horas, geralmente 5-30 minutos)"
Write-Host ""
Write-Host "3. Criar superusuário:"
Write-Host "   gcloud run jobs create create-superuser \"
Write-Host "     --image $IMAGE_NAME --region $REGION \"
Write-Host "     --set-cloudsql-instances $CONNECTION_NAME \"
Write-Host "     --set-env-vars $ENV_VARS \"
Write-Host "     --command python --args 'manage.py,createsuperuser' --interactive"
Write-Host ""
Write-Host "4. Acessar o sistema:"
Write-Host "   $SERVICE_URL (funciona imediatamente)"
Write-Host "   https://$DOMAIN (após configurar DNS)"
Write-Host ""
Write-Success "Tudo pronto! 🎉"
Write-Host ""
















