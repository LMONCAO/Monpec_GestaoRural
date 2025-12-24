# Script PowerShell para Deploy no Google Cloud (Windows)
# Execute no PowerShell como Administrador

Write-Host "MONPEC - Deploy no Google Cloud (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud esta instalado
Write-Host "Verificando gcloud..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "OK: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: gcloud nao encontrado!" -ForegroundColor Red
    Write-Host "   Instale: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit
}

# Verificar autenticacao
Write-Host ""
Write-Host "Verificando autenticacao..." -ForegroundColor Yellow
$auth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($auth) {
    Write-Host "OK: Autenticado como: $auth" -ForegroundColor Green
} else {
    Write-Host "AVISO: Nao autenticado. Executando login..." -ForegroundColor Yellow
    gcloud auth login
}

# Verificar projeto
Write-Host ""
Write-Host "Verificando projeto..." -ForegroundColor Yellow
$project = gcloud config get-value project 2>&1
if ($project -and -not $project.ToString().Contains("ERROR")) {
    Write-Host "OK: Projeto: $project" -ForegroundColor Green
} else {
    Write-Host "AVISO: Nenhum projeto configurado" -ForegroundColor Yellow
    Write-Host "   Configurando projeto monpec-sistema-rural..." -ForegroundColor Yellow
    gcloud config set project monpec-sistema-rural
    $project = "monpec-sistema-rural"
}

# Configuracoes
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$DB_INSTANCE = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "Monpec2025!"

Write-Host ""
Write-Host "Configuracoes:" -ForegroundColor Cyan
Write-Host "   Projeto: $project" -ForegroundColor White
Write-Host "   Regiao: $REGION" -ForegroundColor White
Write-Host "   Servico: $SERVICE_NAME" -ForegroundColor White
Write-Host ""

# Menu
Write-Host "Escolha uma opcao:" -ForegroundColor Yellow
Write-Host "1. Habilitar APIs" -ForegroundColor White
Write-Host "2. Criar banco de dados Cloud SQL" -ForegroundColor White
Write-Host "3. Build e Deploy no Cloud Run" -ForegroundColor White
Write-Host "4. Executar migracoes" -ForegroundColor White
Write-Host "5. Deploy completo (todos os passos)" -ForegroundColor Green
Write-Host "6. Verificar status" -ForegroundColor White
Write-Host "0. Sair" -ForegroundColor Red
Write-Host ""

$opcao = Read-Host "Digite o numero da opcao"

switch ($opcao) {
    "1" {
        Write-Host "Habilitando APIs..." -ForegroundColor Yellow
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable run.googleapis.com
        gcloud services enable sqladmin.googleapis.com
        gcloud services enable cloudresourcemanager.googleapis.com
        gcloud services enable containerregistry.googleapis.com
        Write-Host "OK: APIs habilitadas!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "Criando banco de dados..." -ForegroundColor Yellow
        
        # Verificar se ja existe
        $instanceExists = gcloud sql instances describe $DB_INSTANCE --format="value(name)" 2>&1
        if ($instanceExists -like "*$DB_INSTANCE*") {
            Write-Host "AVISO: Instancia ja existe" -ForegroundColor Yellow
        } else {
            Write-Host "   Criando instancia PostgreSQL..." -ForegroundColor White
            gcloud sql instances create $DB_INSTANCE --database-version=POSTGRES_14 --tier=db-f1-micro --region=$REGION --root-password=$DB_PASSWORD
            
            Write-Host "   Criando banco de dados..." -ForegroundColor White
            gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
            
            Write-Host "   Criando usuario..." -ForegroundColor White
            gcloud sql users create $DB_USER --instance=$DB_INSTANCE --password=$DB_PASSWORD
        }
        
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        Write-Host "OK: Connection Name: $connectionName" -ForegroundColor Cyan
    }
    
    "3" {
        Write-Host "Fazendo build..." -ForegroundColor Yellow
        
        if (-not (Test-Path "Dockerfile")) {
            Write-Host "ERRO: Dockerfile nao encontrado!" -ForegroundColor Red
            Write-Host "   Certifique-se de estar na pasta Monpec_projetista" -ForegroundColor Yellow
            exit
        }
        
        Write-Host "   Build da imagem..." -ForegroundColor White
        gcloud builds submit --tag gcr.io/$project/$SERVICE_NAME
        
        Write-Host "Fazendo deploy..." -ForegroundColor Yellow
        
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        
        # Gerar SECRET_KEY
        $pythonCmd = "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
        $secretKey = python -c $pythonCmd 2>&1 | Out-String
        $secretKey = $secretKey.Trim()
        
        $envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$connectionName,SECRET_KEY=$secretKey"
        
        gcloud run deploy $SERVICE_NAME --image gcr.io/$project/$SERVICE_NAME --platform managed --region $REGION --allow-unauthenticated --add-cloudsql-instances $connectionName --set-env-vars $envVars --memory=512Mi --cpu=1 --timeout=300
        
        $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
        $cloudRunHost = $serviceUrl -replace "https://", ""
        
        Write-Host "OK: Deploy concluido!" -ForegroundColor Green
        Write-Host "URL: $serviceUrl" -ForegroundColor Cyan
        
        gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars "CLOUD_RUN_HOST=$cloudRunHost"
    }
    
    "4" {
        Write-Host "Executando migracoes..." -ForegroundColor Yellow
        
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        
        # Gerar SECRET_KEY
        $pythonCmd = "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
        $secretKey = python -c $pythonCmd 2>&1 | Out-String
        $secretKey = $secretKey.Trim()
        
        $envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$connectionName,SECRET_KEY=$secretKey"
        
        Write-Host "   Criando job de migracao..." -ForegroundColor White
        gcloud run jobs create migrate-db --image gcr.io/$project/$SERVICE_NAME --region $REGION --add-cloudsql-instances $connectionName --set-env-vars $envVars --command python --args "manage.py,migrate" --max-retries=1 --memory=512Mi --cpu=1
        
        Write-Host "   Executando migracoes..." -ForegroundColor White
        gcloud run jobs execute migrate-db --region $REGION
        
        Write-Host "OK: Migracoes executadas!" -ForegroundColor Green
    }
    
    "5" {
        Write-Host "Deploy completo iniciado..." -ForegroundColor Cyan
        
        # Passo 1: APIs
        Write-Host "[1/4] Habilitando APIs..." -ForegroundColor Yellow
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable run.googleapis.com
        gcloud services enable sqladmin.googleapis.com
        gcloud services enable cloudresourcemanager.googleapis.com
        gcloud services enable containerregistry.googleapis.com
        
        # Passo 2: Banco
        Write-Host "[2/4] Criando banco de dados..." -ForegroundColor Yellow
        $instanceExists = gcloud sql instances describe $DB_INSTANCE --format="value(name)" 2>&1
        if (-not ($instanceExists -like "*$DB_INSTANCE*")) {
            gcloud sql instances create $DB_INSTANCE --database-version=POSTGRES_14 --tier=db-f1-micro --region=$REGION --root-password=$DB_PASSWORD
            gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
            gcloud sql users create $DB_USER --instance=$DB_INSTANCE --password=$DB_PASSWORD
        }
        
        # Passo 3: Build e Deploy
        Write-Host "[3/4] Build e Deploy..." -ForegroundColor Yellow
        $connectionName = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"
        
        # Gerar SECRET_KEY
        $pythonCmd = "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
        $secretKey = python -c $pythonCmd 2>&1 | Out-String
        $secretKey = $secretKey.Trim()
        
        gcloud builds submit --tag gcr.io/$project/$SERVICE_NAME
        
        $envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$connectionName,SECRET_KEY=$secretKey"
        
        gcloud run deploy $SERVICE_NAME --image gcr.io/$project/$SERVICE_NAME --platform managed --region $REGION --allow-unauthenticated --add-cloudsql-instances $connectionName --set-env-vars $envVars --memory=512Mi --cpu=1 --timeout=300
        
        $serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
        $cloudRunHost = $serviceUrl -replace "https://", ""
        gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars "CLOUD_RUN_HOST=$cloudRunHost"
        
        # Passo 4: Migracoes
        Write-Host "[4/4] Executando migracoes..." -ForegroundColor Yellow
        gcloud run jobs create migrate-db --image gcr.io/$project/$SERVICE_NAME --region $REGION --add-cloudsql-instances $connectionName --set-env-vars $envVars --command python --args "manage.py,migrate" --max-retries=1 --memory=512Mi --cpu=1
        gcloud run jobs execute migrate-db --region $REGION
        
        Write-Host ""
        Write-Host "OK: Deploy completo finalizado!" -ForegroundColor Green
        Write-Host "URL: $serviceUrl" -ForegroundColor Cyan
    }
    
    "6" {
        Write-Host "Status do servico:" -ForegroundColor Yellow
        gcloud run services describe $SERVICE_NAME --region $REGION
    }
    
    "0" {
        Write-Host "Ate logo!" -ForegroundColor Cyan
        exit
    }
    
    default {
        Write-Host "ERRO: Opcao invalida!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "OK: Operacao concluida!" -ForegroundColor Green
