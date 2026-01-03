# Script para garantir que a versão Curral V3 seja enviada no deploy
# Este script verifica se os arquivos da tela curral v3 estão presentes,
# faz commit e push, e depois faz o deploy

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COM CURRAL V3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git está instalado
$gitPath = $null
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitPath = "git"
} elseif (Test-Path "C:\Program Files\Git\bin\git.exe") {
    $gitPath = "C:\Program Files\Git\bin\git.exe"
} elseif (Test-Path "C:\Program Files (x86)\Git\bin\git.exe") {
    $gitPath = "C:\Program Files (x86)\Git\bin\git.exe"
} else {
    Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
    Write-Host "Instale o Git em: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Verificar se estamos na pasta correta
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Esta não é uma pasta Git!" -ForegroundColor Red
    Write-Host "Navegue até a pasta do projeto Monpec_GestaoRural" -ForegroundColor Yellow
    exit 1
}

# Verificar se os arquivos da tela curral v3 existem
Write-Host "Verificando arquivos da tela Curral V3..." -ForegroundColor Yellow
$arquivosV3 = @(
    "templates\gestao_rural\curral_dashboard_v3.html",
    "gestao_rural\views_curral.py",
    "gestao_rural\urls.py",
    "sistema_rural\urls.py"
)

$arquivosFaltando = @()
foreach ($arquivo in $arquivosV3) {
    if (Test-Path $arquivo) {
        Write-Host "  [OK] $arquivo" -ForegroundColor Green
    } else {
        Write-Host "  [ERRO] $arquivo NÃO ENCONTRADO!" -ForegroundColor Red
        $arquivosFaltando += $arquivo
    }
}

if ($arquivosFaltando.Count -gt 0) {
    Write-Host ""
    Write-Host "ERRO: Alguns arquivos da tela Curral V3 estão faltando!" -ForegroundColor Red
    Write-Host "Não é possível fazer deploy sem esses arquivos." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Todos os arquivos da tela Curral V3 estão presentes!" -ForegroundColor Green
Write-Host ""

# Verificar status do Git
Write-Host "Verificando status do repositório..." -ForegroundColor Yellow
$status = & $gitPath status --porcelain

if ($status) {
    Write-Host ""
    Write-Host "Há alterações não commitadas:" -ForegroundColor Yellow
    & $gitPath status --short
    Write-Host ""
    
    $resposta = Read-Host "Deseja fazer commit e push dessas alterações? (S/N)"
    if ($resposta -eq "S" -or $resposta -eq "s" -or $resposta -eq "Y" -or $resposta -eq "y") {
        Write-Host ""
        Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
        & $gitPath add .
        
        Write-Host "Fazendo commit..." -ForegroundColor Yellow
        $mensagem = "Atualização: Garantir que tela Curral V3 está incluída no deploy - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        & $gitPath commit -m $mensagem
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "AVISO: Erro ao fazer commit, mas continuando..." -ForegroundColor Yellow
        } else {
            Write-Host "Commit realizado com sucesso!" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "Fazendo push para GitHub..." -ForegroundColor Yellow
        & $gitPath push origin master 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            & $gitPath push origin main 2>&1 | Out-Null
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Push realizado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "AVISO: Erro ao fazer push, mas continuando com deploy..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Commit cancelado. Continuando com deploy..." -ForegroundColor Yellow
    }
} else {
    Write-Host "Nenhuma alteração pendente." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "ERRO: Google Cloud CLI não está instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Configurar projeto
$PROJECT_ID = "monpec-sistema-rural"
Write-Host "Configurando projeto: $PROJECT_ID" -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host ""

# Build
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 1/2: BUILD DA IMAGEM DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --tag gcr.io/$PROJECT_ID/monpec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Build falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Build concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 2/2: DEPLOY NO CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Isso pode levar 2-3 minutos..." -ForegroundColor Yellow
Write-Host ""

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)" 2>$null

# Gerar SECRET_KEY
$SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
if (-not $SECRET_KEY) {
    $SECRET_KEY = "temp-key-$(Get-Random)"
}

$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY"

if ($CONNECTION_NAME) {
    $envVars += ",DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME"
    
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --add-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
} else {
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Deploy falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter URL
$SERVICE_URL = gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

Write-Host "========================================" -ForegroundColor Green
Write-Host "  DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do serviço:" -ForegroundColor Cyan
Write-Host "  $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "Teste a tela Curral V3:" -ForegroundColor Yellow
Write-Host "  $SERVICE_URL/propriedade/1/curral/v3/" -ForegroundColor White
Write-Host ""

