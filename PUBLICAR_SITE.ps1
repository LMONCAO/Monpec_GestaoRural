# 🚀 Script de Publicação - MONPEC.COM.BR
# Execute este script para publicar seu site no Google Cloud

Write-Host "🚀 MONPEC - Publicação no Google Cloud" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
try {
    $gcloudVersion = gcloud --version 2>&1
    Write-Host "✅ Google Cloud SDK encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud SDK não encontrado!" -ForegroundColor Red
    Write-Host "   Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$DB_INSTANCE = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "Monpec2025!"

Write-Host "📋 Configurações:" -ForegroundColor Yellow
Write-Host "   Projeto: $PROJECT_ID"
Write-Host "   Região: $REGION"
Write-Host "   Serviço: $SERVICE_NAME"
Write-Host ""

# Verificar autenticação
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
$currentProject = gcloud config get-value project 2>&1
if ($LASTEXITCODE -ne 0 -or $currentProject -eq "") {
    Write-Host "⚠️  Não autenticado. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}

# Configurar projeto
Write-Host "⚙️  Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
Write-Host ""
Write-Host "📦 Habilitando APIs necessárias..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Verificar se o banco de dados existe
Write-Host ""
Write-Host "🗄️  Verificando banco de dados..." -ForegroundColor Yellow
$dbExists = gcloud sql instances describe $DB_INSTANCE 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Banco de dados não encontrado. Criando..." -ForegroundColor Yellow
    Write-Host "   Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
    
    gcloud sql instances create $DB_INSTANCE `
        --database-version=POSTGRES_14 `
        --tier=db-f1-micro `
        --region=$REGION `
        --root-password=$DB_PASSWORD
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Instância do banco criada!" -ForegroundColor Green
        
        # Criar banco de dados
        Write-Host "   Criando banco de dados..." -ForegroundColor Yellow
        gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
        
        # Criar usuário
        Write-Host "   Criando usuário..." -ForegroundColor Yellow
        gcloud sql users create $DB_USER `
            --instance=$DB_INSTANCE `
            --password=$DB_PASSWORD
        
        Write-Host "✅ Banco de dados configurado!" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao criar banco de dados" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Banco de dados já existe" -ForegroundColor Green
}

# Obter connection name
Write-Host ""
Write-Host "🔗 Obtendo connection name..." -ForegroundColor Yellow
$CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
Write-Host "   Connection Name: $CONNECTION_NAME" -ForegroundColor Cyan

# Build da imagem
Write-Host ""
Write-Host "🔨 Fazendo build da imagem Docker..." -ForegroundColor Yellow
Write-Host "   Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build. Verifique os logs acima." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build concluído!" -ForegroundColor Green

# Deploy no Cloud Run
Write-Host ""
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars `
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
        DEBUG=False,`
        DB_NAME=$DB_NAME,`
        DB_USER=$DB_USER,`
        DB_PASSWORD=$DB_PASSWORD,`
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME `
    --memory=512Mi `
    --cpu=1 `
    --timeout=300 `
    --max-instances=10

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy. Verifique os logs acima." -ForegroundColor Red
    exit 1
}

# Obter URL do serviço
Write-Host ""
Write-Host "🌐 Obtendo URL do serviço..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
Write-Host ""
Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URL do serviço: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "   1. Execute as migrações do banco de dados"
Write-Host "   2. Configure o domínio monpec.com.br no console do Google Cloud"
Write-Host "   3. Configure os registros DNS no seu provedor de domínio"
Write-Host ""
Write-Host "   Para executar migrações, use:" -ForegroundColor Cyan
Write-Host "   .\EXECUTAR_MIGRACOES.ps1" -ForegroundColor White
Write-Host ""


