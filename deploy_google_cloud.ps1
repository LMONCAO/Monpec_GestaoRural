# 🚀 Script PowerShell para Deploy no Google Cloud
# Execute como Administrador

Write-Host "🚀 MONPEC - Deploy no Google Cloud" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
Write-Host "📋 Verificando instalação do gcloud..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1
    Write-Host "✅ gcloud encontrado!" -ForegroundColor Green
} catch {
    Write-Host "❌ gcloud não encontrado!" -ForegroundColor Red
    Write-Host "📥 Instalando gcloud..." -ForegroundColor Yellow
    
    # Download do instalador
    $installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"
    Invoke-WebRequest -Uri "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe" -OutFile $installerPath
    Start-Process $installerPath -Wait
    
    Write-Host "✅ Instalação concluída! Por favor, reinicie o PowerShell e execute novamente." -ForegroundColor Green
    exit
}

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$DB_INSTANCE = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "Monpec2025!"

Write-Host ""
Write-Host "⚙️  Configurações:" -ForegroundColor Cyan
Write-Host "   Projeto: $PROJECT_ID" -ForegroundColor White
Write-Host "   Região: $REGION" -ForegroundColor White
Write-Host "   Serviço: $SERVICE_NAME" -ForegroundColor White
Write-Host ""

# Menu
Write-Host "Escolha uma opção:" -ForegroundColor Yellow
Write-Host "1. Configurar projeto e autenticar" -ForegroundColor White
Write-Host "2. Habilitar APIs necessárias" -ForegroundColor White
Write-Host "3. Criar banco de dados Cloud SQL" -ForegroundColor White
Write-Host "4. Build e Deploy no Cloud Run" -ForegroundColor White
Write-Host "5. Executar migrações" -ForegroundColor White
Write-Host "6. Deploy completo (todos os passos)" -ForegroundColor Green
Write-Host "7. Verificar status" -ForegroundColor White
Write-Host "0. Sair" -ForegroundColor Red
Write-Host ""

$opcao = Read-Host "Digite o número da opção"

switch ($opcao) {
    "1" {
        Write-Host "🔐 Autenticando no Google Cloud..." -ForegroundColor Yellow
        gcloud auth login
        gcloud config set project $PROJECT_ID
        Write-Host "✅ Autenticação concluída!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "🔧 Habilitando APIs..." -ForegroundColor Yellow
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable run.googleapis.com
        gcloud services enable sqladmin.googleapis.com
        gcloud services enable cloudresourcemanager.googleapis.com
        gcloud services enable containerregistry.googleapis.com
        Write-Host "✅ APIs habilitadas!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host "🗄️  Criando banco de dados Cloud SQL..." -ForegroundColor Yellow
        
        # Verificar se já existe
        $instanceExists = gcloud sql instances describe $DB_INSTANCE --format="value(name)" 2>&1
        if ($instanceExists -like "*$DB_INSTANCE*") {
            Write-Host "⚠️  Instância já existe. Pulando criação..." -ForegroundColor Yellow
        } else {
            Write-Host "   Criando instância PostgreSQL..." -ForegroundColor White
            gcloud sql instances create $DB_INSTANCE `
                --database-version=POSTGRES_14 `
                --tier=db-f1-micro `
                --region=$REGION `
                --root-password=$DB_PASSWORD
            
            Write-Host "   Criando banco de dados..." -ForegroundColor White
            gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
            
            Write-Host "   Criando usuário..." -ForegroundColor White
            gcloud sql users create $DB_USER `
                --instance=$DB_INSTANCE `
                --password=$DB_PASSWORD
        }
        
        # Obter connection name
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        Write-Host "✅ Banco criado!" -ForegroundColor Green
        Write-Host "   Connection Name: $connectionName" -ForegroundColor Cyan
    }
    
    "4" {
        Write-Host "🏗️  Fazendo build da imagem Docker..." -ForegroundColor Yellow
        
        # Verificar se Dockerfile existe
        if (-not (Test-Path "Dockerfile")) {
            Write-Host "❌ Dockerfile não encontrado!" -ForegroundColor Red
            exit
        }
        
        # Build
        Write-Host "   Enviando para Cloud Build..." -ForegroundColor White
        gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
        
        Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
        
        # Obter connection name
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        
        # Gerar SECRET_KEY
        $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
        
        # Deploy
        gcloud run deploy $SERVICE_NAME `
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
            --platform managed `
            --region $REGION `
            --allow-unauthenticated `
            --add-cloudsql-instances $connectionName `
            --set-env-vars `
                DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
                DEBUG=False,`
                DB_NAME=$DB_NAME,`
                DB_USER=$DB_USER,`
                DB_PASSWORD=$DB_PASSWORD,`
                CLOUD_SQL_CONNECTION_NAME=$connectionName,`
                SECRET_KEY=$secretKey
        
        Write-Host "✅ Deploy concluído!" -ForegroundColor Green
        
        # Obter URL
        $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
        Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
    }
    
    "5" {
        Write-Host "🔄 Executando migrações..." -ForegroundColor Yellow
        
        # Obter connection name
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        
        # Criar job para migrações
        Write-Host "   Criando job de migração..." -ForegroundColor White
        gcloud run jobs create migrate-db `
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
            --region $REGION `
            --add-cloudsql-instances $connectionName `
            --set-env-vars `
                DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
                DB_NAME=$DB_NAME,`
                DB_USER=$DB_USER,`
                DB_PASSWORD=$DB_PASSWORD,`
                CLOUD_SQL_CONNECTION_NAME=$connectionName `
            --command python `
            --args manage.py,migrate `
            --max-retries 1
        
        Write-Host "   Executando job..." -ForegroundColor White
        gcloud run jobs execute migrate-db --region $REGION
        
        Write-Host "✅ Migrações executadas!" -ForegroundColor Green
    }
    
    "6" {
        Write-Host "🚀 Deploy completo iniciado..." -ForegroundColor Cyan
        Write-Host ""
        
        # Passo 1: Autenticar
        Write-Host "[1/5] Autenticando..." -ForegroundColor Yellow
        gcloud auth login
        gcloud config set project $PROJECT_ID
        
        # Passo 2: Habilitar APIs
        Write-Host "[2/5] Habilitando APIs..." -ForegroundColor Yellow
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable run.googleapis.com
        gcloud services enable sqladmin.googleapis.com
        gcloud services enable cloudresourcemanager.googleapis.com
        gcloud services enable containerregistry.googleapis.com
        
        # Passo 3: Criar banco
        Write-Host "[3/5] Criando banco de dados..." -ForegroundColor Yellow
        $instanceExists = gcloud sql instances describe $DB_INSTANCE --format="value(name)" 2>&1
        if (-not ($instanceExists -like "*$DB_INSTANCE*")) {
            gcloud sql instances create $DB_INSTANCE `
                --database-version=POSTGRES_14 `
                --tier=db-f1-micro `
                --region=$REGION `
                --root-password=$DB_PASSWORD
            gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
            gcloud sql users create $DB_USER `
                --instance=$DB_INSTANCE `
                --password=$DB_PASSWORD
        }
        
        # Passo 4: Build e Deploy
        Write-Host "[4/5] Build e Deploy..." -ForegroundColor Yellow
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
        
        gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
        gcloud run deploy $SERVICE_NAME `
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
            --platform managed `
            --region $REGION `
            --allow-unauthenticated `
            --add-cloudsql-instances $connectionName `
            --set-env-vars `
                DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
                DEBUG=False,`
                DB_NAME=$DB_NAME,`
                DB_USER=$DB_USER,`
                DB_PASSWORD=$DB_PASSWORD,`
                CLOUD_SQL_CONNECTION_NAME=$connectionName,`
                SECRET_KEY=$secretKey
        
        # Passo 5: Migrações
        Write-Host "[5/5] Executando migrações..." -ForegroundColor Yellow
        gcloud run jobs create migrate-db `
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
            --region $REGION `
            --add-cloudsql-instances $connectionName `
            --set-env-vars `
                DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
                DB_NAME=$DB_NAME,`
                DB_USER=$DB_USER,`
                DB_PASSWORD=$DB_PASSWORD,`
                CLOUD_SQL_CONNECTION_NAME=$connectionName `
            --command python `
            --args manage.py,migrate `
            --max-retries 1
        gcloud run jobs execute migrate-db --region $REGION
        
        Write-Host ""
        Write-Host "✅ Deploy completo finalizado!" -ForegroundColor Green
        $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
        Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
    }
    
    "7" {
        Write-Host "📊 Status do serviço:" -ForegroundColor Yellow
        gcloud run services describe $SERVICE_NAME --region $REGION
        
        Write-Host ""
        Write-Host "📊 Status do banco de dados:" -ForegroundColor Yellow
        gcloud sql instances describe $DB_INSTANCE
    }
    
    "0" {
        Write-Host "👋 Até logo!" -ForegroundColor Cyan
        exit
    }
    
    default {
        Write-Host "❌ Opção inválida!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Operação concluída!" -ForegroundColor Green







