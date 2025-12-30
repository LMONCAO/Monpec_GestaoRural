# 🗑️ SCRIPT DE LIMPEZA DE RECURSOS GCP (PowerShell)
# Remove todos os recursos antigos do Google Cloud Platform
# Projeto: monpec-sistema-rural

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"

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
Write-Host "🗑️  LIMPEZA DE RECURSOS GCP - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Warning "ATENÇÃO: Este script vai DELETAR recursos do Google Cloud!"
Write-Warning "Certifique-se de ter feito backup dos dados importantes!"
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

# Confirmação final
Write-Warning "Você está prestes a DELETAR:"
Write-Host "  - Serviço Cloud Run: $SERVICE_NAME"
Write-Host "  - Jobs do Cloud Run relacionados"
Write-Host "  - Instância Cloud SQL: $INSTANCE_NAME (com confirmação)"
Write-Host "  - Imagens Docker antigas"
Write-Host "  - Domain mappings"
Write-Host ""
$CONFIRM = Read-Host "Tem CERTEZA que deseja continuar? Digite 'CONFIRMAR' para prosseguir"
if ($CONFIRM -ne "CONFIRMAR") {
    Write-Error "Operação cancelada!"
    exit 1
}
Write-Host ""

# 1. DELETAR SERVIÇO CLOUD RUN
Write-Log "1/5 - Deletando serviço Cloud Run..."
try {
    $null = gcloud run services describe $SERVICE_NAME --region $REGION 2>&1
    gcloud run services delete $SERVICE_NAME --region $REGION --quiet
    Write-Success "Serviço Cloud Run deletado!"
} catch {
    Write-Warning "Serviço Cloud Run não encontrado (já foi deletado ou não existe)"
}
Write-Host ""

# 2. DELETAR JOBS DO CLOUD RUN
Write-Log "2/5 - Deletando jobs do Cloud Run..."
try {
    $JOBS = gcloud run jobs list --region $REGION --format="value(name)" 2>$null | Where-Object { $_ -like "*monpec*" }
    if ($JOBS) {
        foreach ($JOB in $JOBS) {
            Write-Log "  Deletando job: $JOB"
            gcloud run jobs delete $JOB --region $REGION --quiet 2>$null
        }
        Write-Success "Jobs deletados!"
    } else {
        Write-Warning "Nenhum job encontrado"
    }
} catch {
    Write-Warning "Nenhum job encontrado"
}
Write-Host ""

# 3. DELETAR INSTÂNCIA CLOUD SQL (COM CONFIRMAÇÃO)
Write-Log "3/5 - Verificando instância Cloud SQL..."
try {
    $null = gcloud sql instances describe $INSTANCE_NAME 2>&1
    Write-Warning "⚠️  ATENÇÃO: Você está prestes a DELETAR o banco de dados!"
    Write-Warning "⚠️  TODOS OS DADOS SERÃO PERDIDOS PERMANENTEMENTE!"
    Write-Host ""
    $CONFIRM_DB = Read-Host "Digite 'DELETAR BANCO' para confirmar a exclusão do banco"
    if ($CONFIRM_DB -eq "DELETAR BANCO") {
        Write-Log "  Deletando instância Cloud SQL: $INSTANCE_NAME"
        gcloud sql instances delete $INSTANCE_NAME --quiet
        Write-Success "Instância Cloud SQL deletada!"
    } else {
        Write-Warning "Exclusão do banco cancelada (banco mantido)"
    }
} catch {
    Write-Warning "Instância Cloud SQL não encontrada (já foi deletada ou não existe)"
}
Write-Host ""

# 4. DELETAR IMAGENS DOCKER ANTIGAS
Write-Log "4/5 - Deletando imagens Docker antigas..."
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
try {
    $IMAGES = gcloud container images list-tags $IMAGE_NAME --format="value(digest)" 2>$null
    if ($IMAGES) {
        $IMAGE_COUNT = ($IMAGES | Measure-Object).Count
        Write-Log "  Encontradas $IMAGE_COUNT imagens antigas"
        $response = Read-Host "Deseja deletar todas as imagens antigas? (s/n)"
        if ($response -eq "s" -or $response -eq "S") {
            foreach ($DIGEST in $IMAGES) {
                gcloud container images delete "$IMAGE_NAME@$DIGEST" --quiet 2>$null
            }
            Write-Success "Imagens Docker deletadas!"
        } else {
            Write-Warning "Imagens mantidas"
        }
    } else {
        Write-Warning "Nenhuma imagem encontrada"
    }
} catch {
    Write-Warning "Nenhuma imagem encontrada"
}
Write-Host ""

# 5. DELETAR DOMAIN MAPPINGS
Write-Log "5/5 - Deletando domain mappings..."
try {
    $DOMAINS = gcloud run domain-mappings list --region $REGION --format="value(name)" 2>$null
    if ($DOMAINS) {
        foreach ($DOMAIN in $DOMAINS) {
            Write-Log "  Deletando domain mapping: $DOMAIN"
            gcloud run domain-mappings delete $DOMAIN --region $REGION --quiet 2>$null
        }
        Write-Success "Domain mappings deletados!"
    } else {
        Write-Warning "Nenhum domain mapping encontrado"
    }
} catch {
    Write-Warning "Nenhum domain mapping encontrado"
}
Write-Host ""

# RESUMO
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Success "LIMPEZA CONCLUÍDA!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Log "Recursos deletados:"
Write-Host "  ✅ Serviço Cloud Run"
Write-Host "  ✅ Jobs do Cloud Run"
Write-Host "  ✅ Instância Cloud SQL (se confirmado)"
Write-Host "  ✅ Imagens Docker antigas (se confirmado)"
Write-Host "  ✅ Domain mappings"
Write-Host ""
Write-Warning "Próximo passo: Execute INSTALAR_DO_ZERO.ps1 para criar tudo do zero"
Write-Host ""























