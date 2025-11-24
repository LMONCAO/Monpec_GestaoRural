# ========================================
# REINICIAR SISTEMA COM ULTIMAS ATUALIZACOES
# ========================================
# Este script:
# 1. Faz commit das alteracoes (templates criados)
# 2. Faz push para o GitHub
# 3. Faz build e deploy no Google Cloud Run
# ========================================

Write-Host "REINICIANDO SISTEMA COM ULTIMAS ATUALIZACOES" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host ""

# Verificar se estamos no diretorio correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: Execute este script na raiz do projeto Django!" -ForegroundColor Red
    Write-Host "   Diretorio atual: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# ========================================
# ETAPA 1: COMMIT E PUSH PARA GITHUB
# ========================================
Write-Host "ETAPA 1: Atualizando repositorio GitHub..." -ForegroundColor Cyan
Write-Host ""

# Verificar se Git esta disponivel
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Git nao encontrado!" -ForegroundColor Red
    Write-Host "   Instale o Git: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Verificar se e um repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "AVISO: Este diretorio nao e um repositorio Git" -ForegroundColor Yellow
    Write-Host "   Pulando etapa de commit/push..." -ForegroundColor Yellow
    $skipGit = $true
} else {
    $skipGit = $false
    
    # Verificar status
    Write-Host "Verificando status do repositorio..." -ForegroundColor Cyan
    git status --short
    
    # Adicionar todos os arquivos
    Write-Host "Adicionando arquivos ao staging..." -ForegroundColor Cyan
    git add .
    
    # Verificar se ha alteracoes para commitar
    $statusOutput = git status --porcelain
    if ($statusOutput) {
        Write-Host "Fazendo commit das alteracoes..." -ForegroundColor Cyan
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $commitMessage = "Atualizacao: Criados templates faltantes do sistema - $timestamp"
        git commit -m $commitMessage
        
        # Fazer push
        Write-Host "Enviando para o GitHub..." -ForegroundColor Cyan
        $currentBranch = git branch --show-current
        if (-not $currentBranch) {
            $currentBranch = "master"
        }
        
        try {
            git push origin $currentBranch
            Write-Host "Push concluido com sucesso!" -ForegroundColor Green
        } catch {
            Write-Host "AVISO: Erro ao fazer push. Execute manualmente:" -ForegroundColor Yellow
            Write-Host "   git push origin $currentBranch" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Nenhuma alteracao para commitar." -ForegroundColor Gray
    }
}

Write-Host ""

# ========================================
# ETAPA 2: DEPLOY NO GOOGLE CLOUD RUN
# ========================================
Write-Host "ETAPA 2: Fazendo deploy no Google Cloud Run..." -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud esta disponivel
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "Google Cloud SDK encontrado" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Google Cloud SDK nao encontrado!" -ForegroundColor Red
    Write-Host "   Instale o SDK: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Ou execute o deploy manualmente no Cloud Shell:" -ForegroundColor Yellow
    Write-Host "   1. Acesse: https://console.cloud.google.com/" -ForegroundColor Yellow
    Write-Host "   2. Abra o Cloud Shell" -ForegroundColor Yellow
    Write-Host "   3. Execute: cd ~/Monpec_GestaoRural && git pull" -ForegroundColor Yellow
    Write-Host "   4. Execute: gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec" -ForegroundColor Yellow
    Write-Host "   5. Execute: gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --platform managed --allow-unauthenticated --project=monpec-sistema-rural" -ForegroundColor Yellow
    exit 1
}

# Configurar projeto
Write-Host "Configurando projeto Google Cloud..." -ForegroundColor Cyan
gcloud config set project monpec-sistema-rural

# Verificar se esta autenticado
Write-Host "Verificando autenticacao..." -ForegroundColor Cyan
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authStatus) {
    Write-Host "Nao autenticado. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}

# Build da imagem
Write-Host ""
Write-Host "Fazendo build da imagem Docker..." -ForegroundColor Cyan
Write-Host "   Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec --project=monpec-sistema-rural

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Build falhou!" -ForegroundColor Red
    exit 1
}

Write-Host "Build concluido com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter connection name do banco
Write-Host "Obtendo informacoes do banco de dados..." -ForegroundColor Cyan
$connectionName = gcloud sql instances describe monpec-db --format="value(connectionName)" --project=monpec-sistema-rural 2>&1

if (-not $connectionName -or $connectionName -match "ERROR") {
    Write-Host "AVISO: Nao foi possivel obter connection name do banco" -ForegroundColor Yellow
    Write-Host "   Continuando deploy sem conexao ao banco..." -ForegroundColor Yellow
    $connectionName = $null
}

# Deploy no Cloud Run
Write-Host ""
Write-Host "Fazendo deploy no Cloud Run..." -ForegroundColor Cyan
Write-Host "   Isso pode levar 2-3 minutos..." -ForegroundColor Yellow

$deployCommand = "gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --platform managed --allow-unauthenticated --project=monpec-sistema-rural --memory=512Mi --cpu=1 --timeout=300 --max-instances=10"

if ($connectionName) {
    $deployCommand += " --add-cloudsql-instances=$connectionName"
}

# Adicionar variaveis de ambiente
$deployCommand += " --set-env-vars=`"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False`""

Invoke-Expression $deployCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Deploy falhou!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green

# Obter URL do servico
Write-Host ""
Write-Host "Obtendo URL do servico..." -ForegroundColor Cyan
$serviceUrl = gcloud run services describe monpec --region us-central1 --format="value(status.url)" --project=monpec-sistema-rural

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "SISTEMA REINICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do sistema: $serviceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar logs:" -ForegroundColor Yellow
Write-Host "   gcloud run services logs read monpec --region us-central1 --limit 50" -ForegroundColor Gray
Write-Host ""
Write-Host "Para verificar status:" -ForegroundColor Yellow
Write-Host "   gcloud run services describe monpec --region us-central1" -ForegroundColor Gray
Write-Host ""
