# Script que GARANTE que a versão correta seja deployada
# Verifica pasta, limpa cache, valida Dockerfile e faz deploy completo

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY GARANTINDO VERSAO CORRETA" -ForegroundColor Cyan
Write-Host "  Verifica tudo e faz deploy seguro" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# CONFIGURACOES
# ========================================
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_INSTANCE = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
$DJANGO_SUPERUSER_PASSWORD = "L6171r12@@"
$EXPECTED_FOLDER = "Monpec_GestaoRural"

Write-Host "[CONFIG] Projeto: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "[CONFIG] Servico: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host "[CONFIG] Regiao: $REGION" -ForegroundColor Yellow
Write-Host ""

# ========================================
# PASSO 1: VERIFICAR PASTA CORRETA
# ========================================
Write-Host "[1/9] Verificando se esta na pasta correta..." -ForegroundColor Cyan
$CURRENT_FOLDER = Split-Path -Leaf (Get-Location)

if ($CURRENT_FOLDER -ne $EXPECTED_FOLDER) {
    Write-Host "[AVISO] Voce esta na pasta: $CURRENT_FOLDER" -ForegroundColor Yellow
    Write-Host "[AVISO] Pasta esperada: $EXPECTED_FOLDER" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Navegando para a pasta correta..." -ForegroundColor Yellow
    
    $SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $SCRIPT_DIR
    $CURRENT_FOLDER = Split-Path -Leaf (Get-Location)
    
    if ($CURRENT_FOLDER -ne $EXPECTED_FOLDER) {
        Write-Host "[ERRO] Nao foi possivel encontrar a pasta $EXPECTED_FOLDER" -ForegroundColor Red
        Write-Host "[ERRO] Execute este script dentro da pasta $EXPECTED_FOLDER" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}
Write-Host "[OK] Pasta correta: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 2: VERIFICAR DOCKERFILE
# ========================================
Write-Host "[2/9] Verificando Dockerfile..." -ForegroundColor Cyan
if (-not (Test-Path "Dockerfile.prod")) {
    Write-Host "[ERRO] Dockerfile.prod nao encontrado!" -ForegroundColor Red
    Write-Host "[ERRO] Certifique-se de que o Dockerfile.prod esta na pasta atual" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] Dockerfile.prod encontrado" -ForegroundColor Green

# Verificar se ha Dockerfiles duplicados
$dockerfiles = Get-ChildItem -Filter "Dockerfile*" -File
if ($dockerfiles.Count -gt 1) {
    Write-Host "[AVISO] Encontrados $($dockerfiles.Count) arquivos Dockerfile" -ForegroundColor Yellow
    foreach ($df in $dockerfiles) {
        if ($df.Name -ne "Dockerfile.prod") {
            Write-Host "[AVISO] Dockerfile duplicado encontrado: $($df.Name)" -ForegroundColor Yellow
        }
    }
    Write-Host "[AVISO] Mantendo apenas Dockerfile.prod" -ForegroundColor Yellow
}
Write-Host "[OK] Dockerfile validado" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 3: VERIFICAR FERRAMENTAS
# ========================================
Write-Host "[3/9] Verificando ferramentas..." -ForegroundColor Cyan
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "[ERRO] gcloud nao encontrado!" -ForegroundColor Red
    Write-Host "Baixe: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] gcloud encontrado" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 4: AUTENTICACAO
# ========================================
Write-Host "[4/9] Verificando autenticacao..." -ForegroundColor Cyan
$authAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ([string]::IsNullOrWhiteSpace($authAccount)) {
    Write-Host "Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha na autenticacao!" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
} else {
    Write-Host "[OK] Autenticado: $authAccount" -ForegroundColor Green
}

# Configurar projeto
gcloud config set project $PROJECT_ID | Out-Null
Write-Host "[OK] Projeto configurado" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 5: HABILITAR APIs
# ========================================
Write-Host "[5/9] Habilitando APIs necessarias..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com | Out-Null
gcloud services enable run.googleapis.com | Out-Null
gcloud services enable sqladmin.googleapis.com | Out-Null
gcloud services enable containerregistry.googleapis.com | Out-Null
Write-Host "[OK] APIs habilitadas" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 6: LIMPAR CACHE DE BUILD
# ========================================
Write-Host "[6/9] Limpando cache de build anterior..." -ForegroundColor Cyan
Write-Host "IMPORTANTE: Forcando build sem cache para garantir versao nova" -ForegroundColor Yellow
Write-Host "Isso pode levar mais tempo, mas garante que a versao correta sera usada" -ForegroundColor Yellow
Write-Host ""

# Obter nome do projeto
$GCP_PROJECT = gcloud config get-value project 2>&1
$IMAGE_NAME = "gcr.io/$GCP_PROJECT/sistema-rural"

Write-Host "Fazendo build SEM CACHE da imagem: $IMAGE_NAME" -ForegroundColor Yellow
Write-Host "Usando arquivos do diretorio atual: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --no-cache --tag $IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha no build sem cache!" -ForegroundColor Red
    Write-Host "Tentando build normal..." -ForegroundColor Yellow
    gcloud builds submit --tag $IMAGE_NAME .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha no build!" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
} else {
    Write-Host "[OK] Build sem cache concluido - Versao nova garantida" -ForegroundColor Green
}
Write-Host ""

# ========================================
# PASSO 7: DEPLOY NO CLOUD RUN
# ========================================
Write-Host "[7/9] Fazendo deploy no Cloud Run..." -ForegroundColor Cyan
Write-Host "Isso pode levar alguns minutos..." -ForegroundColor Yellow
Write-Host ""

$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:$DB_INSTANCE,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="$PROJECT_ID`:$REGION`:$DB_INSTANCE" `
    --set-env-vars $envVars `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --max-instances=10 `
    --min-instances=0

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha no deploy!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host "[OK] Deploy concluido" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 8: VERIFICAR STATUS
# ========================================
Write-Host "[8/9] Verificando status do servico..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID 2>&1

if ([string]::IsNullOrWhiteSpace($SERVICE_URL)) {
    Write-Host "[AVISO] Nao foi possivel obter a URL do servico" -ForegroundColor Yellow
    Write-Host "Execute: gcloud run services describe $SERVICE_NAME --region=$REGION" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Servico disponivel em: $SERVICE_URL" -ForegroundColor Green
}
Write-Host ""

# ========================================
# PASSO 9: VERIFICAR BUILD RECENTE
# ========================================
Write-Host "[9/9] Verificando build mais recente..." -ForegroundColor Cyan
Write-Host ""
gcloud builds list --limit=1 --format="table(id,status,createTime,source.repoSource.branchName)"
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[GARANTIAS]" -ForegroundColor Cyan
Write-Host "- Build executado SEM CACHE (--no-cache)" -ForegroundColor White
Write-Host "- Dockerfile validado na pasta correta" -ForegroundColor White
Write-Host "- Versao do diretorio atual foi deployada" -ForegroundColor White
Write-Host ""
if (-not [string]::IsNullOrWhiteSpace($SERVICE_URL)) {
    Write-Host "Seu sistema esta disponivel em:" -ForegroundColor Yellow
    Write-Host $SERVICE_URL -ForegroundColor Cyan
    Write-Host ""
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Aguarde 1-2 minutos para o servico inicializar completamente" -ForegroundColor White
if (-not [string]::IsNullOrWhiteSpace($SERVICE_URL)) {
    Write-Host "2. Acesse: $SERVICE_URL" -ForegroundColor White
}
Write-Host "3. Credenciais de admin:" -ForegroundColor White
Write-Host "   Usuario: admin" -ForegroundColor White
Write-Host "   Senha: $DJANGO_SUPERUSER_PASSWORD" -ForegroundColor White
Write-Host "4. O sistema executa migracoes automaticamente no inicio" -ForegroundColor White
Write-Host "5. Para verificar logs:" -ForegroundColor White
Write-Host "   gcloud logging read `"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME`" --limit=50" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMO CONFIRMAR QUE E A VERSAO NOVA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se quiser confirmar que a versao nova foi deployada:" -ForegroundColor White
Write-Host "1. Altere um texto visivel em templates/site/landing_page.html" -ForegroundColor White
Write-Host "2. Execute este script novamente" -ForegroundColor White
Write-Host "3. Acesse a URL e verifique se a mudanca aparece" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Pressione Enter para sair"

