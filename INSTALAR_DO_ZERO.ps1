# 🚀 SCRIPT DE INSTALAÇÃO DO ZERO - GCP (PowerShell)
# Instala tudo do zero no Google Cloud Platform
# Projeto: monpec-sistema-rural

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"

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

# Verificar se gcloud está instalado
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Error "gcloud CLI não está instalado!"
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 INSTALAÇÃO DO ZERO - MONPEC GCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar projeto
Write-Log "Verificando projeto atual..."
$CURRENT_PROJECT = gcloud config get-value project 2>$null
if ($CURRENT_PROJECT -ne $PROJECT_ID) {
    Write-Warning "Projeto atual: $CURRENT_PROJECT"
    $response = Read-Host "Deseja configurar para $PROJECT_ID? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        gcloud config set project $PROJECT_ID
        Write-Success "Projeto configurado!"
    } else {
        Write-Error "Operação cancelada!"
        exit 1
    }
} else {
    Write-Success "Projeto correto: $PROJECT_ID"
}
Write-Host ""

# Habilitar APIs necessárias
Write-Log "Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable sql-component.googleapis.com --quiet
Write-Success "APIs habilitadas!"
Write-Host ""

# Solicitar senha do banco
Write-Warning "Você precisará fornecer uma senha para o banco de dados."
Write-Warning "A senha deve ter no mínimo 8 caracteres."
$securePassword = Read-Host "Digite a senha do banco de dados" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$DB_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
if ($DB_PASSWORD.Length -lt 8) {
    Write-Error "Senha deve ter no mínimo 8 caracteres!"
    exit 1
}
Write-Host ""

# Solicitar SECRET_KEY do Django
Write-Warning "Você pode fornecer uma SECRET_KEY do Django ou deixar gerar automaticamente."
$response = Read-Host "Deseja fornecer SECRET_KEY? (s/n)"
if ($response -eq "s" -or $response -eq "S") {
    $secureKey = Read-Host "Digite a SECRET_KEY" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $SECRET_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
} else {
    # Gerar SECRET_KEY automaticamente
    $bytes = New-Object byte[] 50
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $SECRET_KEY = [Convert]::ToBase64String($bytes)
    Write-Success "SECRET_KEY gerada automaticamente"
}
Write-Host ""

# 1. CRIAR INSTÂNCIA CLOUD SQL
Write-Log "1/6 - Criando instância Cloud SQL PostgreSQL 15..."
try {
    $null = gcloud sql instances describe $INSTANCE_NAME 2>&1
    Write-Warning "Instância Cloud SQL já existe: $INSTANCE_NAME"
    $response = Read-Host "Deseja usar a instância existente? (s/n)"
    if ($response -ne "s" -and $response -ne "S") {
        Write-Error "Operação cancelada! Delete a instância existente primeiro."
        exit 1
    }
} catch {
    Write-Log "  Criando instância PostgreSQL 15..."
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
}
Write-Host ""

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)"
Write-Log "Connection name: $CONNECTION_NAME"
Write-Host ""

# 2. CRIAR BANCO DE DADOS E USUÁRIO
Write-Log "2/6 - Criando banco de dados e usuário..."
try {
    gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet
} catch {
    Write-Warning "Banco já existe"
}
try {
    gcloud sql users create $DB_USER `
        --instance=$INSTANCE_NAME `
        --password=$DB_PASSWORD `
        --quiet
} catch {
    Write-Warning "Usuário já existe"
}
Write-Success "Banco de dados e usuário criados!"
Write-Host ""

# 3. BUILD DA IMAGEM DOCKER
Write-Log "3/6 - Fazendo build da imagem Docker..."
Write-Log "  Isso pode levar alguns minutos..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
Write-Success "Imagem Docker criada!"
Write-Host ""

# 4. DEPLOY NO CLOUD RUN
Write-Log "4/6 - Fazendo deploy no Cloud Run..."
Write-Log "  Configurando variáveis de ambiente e recursos..."

# Construir lista de variáveis de ambiente
$ENV_VARS = "DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

# Adicionar variáveis opcionais se fornecidas
$response = Read-Host "Deseja configurar Mercado Pago agora? (s/n)"
if ($response -eq "s" -or $response -eq "S") {
    $MP_TOKEN = Read-Host "Digite MERCADOPAGO_ACCESS_TOKEN"
    $MP_PUBLIC_KEY = Read-Host "Digite MERCADOPAGO_PUBLIC_KEY"
    $ENV_VARS = "$ENV_VARS,MERCADOPAGO_ACCESS_TOKEN=$MP_TOKEN,MERCADOPAGO_PUBLIC_KEY=$MP_PUBLIC_KEY"
}

# Fazer deploy
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
Write-Host ""

# Obter URL do serviço
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
Write-Log "URL do serviço: $SERVICE_URL"
Write-Host ""

# 5. APLICAR MIGRAÇÕES
Write-Log "5/6 - Aplicando migrações do Django..."
Write-Log "  Criando job de migração..."

# Criar job para migrações
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

# Executar job
Write-Log "  Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait
Write-Success "Migrações aplicadas!"
Write-Host ""

# 6. COLETAR ARQUIVOS ESTÁTICOS
Write-Log "6/6 - Coletando arquivos estáticos..."
Write-Log "  Criando job para collectstatic..."

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

# Executar job
Write-Log "  Executando collectstatic..."
gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait
Write-Success "Arquivos estáticos coletados!"
Write-Host ""

# RESUMO FINAL
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Log "Recursos criados:"
Write-Host "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
Write-Host "  ✅ Banco de dados: $DB_NAME"
Write-Host "  ✅ Usuário: $DB_USER"
Write-Host "  ✅ Imagem Docker: $IMAGE_NAME"
Write-Host "  ✅ Serviço Cloud Run: $SERVICE_NAME"
Write-Host "  ✅ Migrações aplicadas"
Write-Host "  ✅ Arquivos estáticos coletados"
Write-Host ""
Write-Log "URLs:"
Write-Host "  🌐 Serviço: $SERVICE_URL"
Write-Host ""
Write-Warning "PRÓXIMOS PASSOS:"
Write-Host ""
Write-Host "1. Criar superusuário:"
Write-Host "   gcloud run jobs create create-superuser --image $IMAGE_NAME --region $REGION \"
Write-Host "     --set-cloudsql-instances $CONNECTION_NAME --set-env-vars $ENV_VARS \"
Write-Host "     --command python --args 'manage.py,createsuperuser' --interactive"
Write-Host ""
Write-Host "2. Configurar domínio personalizado (opcional):"
Write-Host "   gcloud run domain-mappings create --service $SERVICE_NAME \"
Write-Host "     --domain monpec.com.br --region $REGION"
Write-Host ""
Write-Host "3. Acessar o sistema:"
Write-Host "   $SERVICE_URL"
Write-Host ""
Write-Success "Tudo pronto! 🎉"
Write-Host ""
















