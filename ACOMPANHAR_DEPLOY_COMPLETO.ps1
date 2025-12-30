# Script COMPLETO para acompanhar todo o processo de deploy
# Mostra build, deploy e logs em uma única tela

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ACOMPANHAR DEPLOY COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# CONFIGURACOES
# ========================================
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host "[CONFIG] Projeto: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "[CONFIG] Servico: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host "[CONFIG] Regiao: $REGION" -ForegroundColor Yellow
Write-Host ""

# ========================================
# PASSO 1: VERIFICAR BUILDS
# ========================================
Write-Host "[1/4] Verificando builds recentes..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STATUS DOS BUILDS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
gcloud builds list --limit=3 --format="table(id,status,createTime,duration)" --project=$PROJECT_ID
Write-Host ""

# ========================================
# PASSO 2: VERIFICAR STATUS DO SERVICO
# ========================================
Write-Host "[2/4] Verificando status do servico..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STATUS DO SERVICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID 2>&1

if ([string]::IsNullOrWhiteSpace($SERVICE_URL)) {
    Write-Host "[AVISO] Servico nao encontrado ou ainda nao foi deployado" -ForegroundColor Yellow
} else {
    Write-Host "[OK] URL: $SERVICE_URL" -ForegroundColor Green
    Write-Host ""
    gcloud run services describe $SERVICE_NAME --region=$REGION --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].message)" --project=$PROJECT_ID
}
Write-Host ""

# ========================================
# PASSO 3: VERIFICAR REVISOES
# ========================================
Write-Host "[3/4] Verificando revisoes (versoes)..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REVISOES DO SERVICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION --limit=3 --format="table(metadata.name,status.conditions[0].status,metadata.creationTimestamp)" --project=$PROJECT_ID
Write-Host ""

# ========================================
# PASSO 4: LOGS RECENTES
# ========================================
Write-Host "[4/4] Logs recentes do servico..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LOGS RECENTES (ultimas 20 linhas)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
$logs = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=20 --format="table(timestamp,severity,textPayload)" --project=$PROJECT_ID 2>&1
if ($logs -match "Listed 0") {
    Write-Host "Nenhum log encontrado ainda." -ForegroundColor Yellow
} else {
    $logs
}
Write-Host ""

# ========================================
# MENU DE OPCOES
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OPCOES DE ACOMPANHAMENTO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acompanhar BUILD em tempo real" -ForegroundColor White
Write-Host "2. Acompanhar LOGS do servico em tempo real" -ForegroundColor White
Write-Host "3. Ver status completo do servico" -ForegroundColor White
Write-Host "4. Ver erros especificos" -ForegroundColor White
Write-Host "5. Sair" -ForegroundColor White
Write-Host ""
$OPCAO = Read-Host "Escolha uma opcao (1-5)"

if ($OPCAO -eq "1") {
    Write-Host ""
    Write-Host "Acompanhando build mais recente (Ctrl+C para parar)..." -ForegroundColor Yellow
    Write-Host ""
    gcloud builds log --stream --project=$PROJECT_ID
} elseif ($OPCAO -eq "2") {
    Write-Host ""
    Write-Host "Acompanhando logs do servico (Ctrl+C para parar)..." -ForegroundColor Yellow
    Write-Host ""
    gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --project=$PROJECT_ID
} elseif ($OPCAO -eq "3") {
    Write-Host ""
    & ".\VERIFICAR_DEPLOY.bat"
} elseif ($OPCAO -eq "4") {
    Write-Host ""
    & ".\VERIFICAR_ERROS_DEPLOY.bat"
} else {
    Write-Host "Saindo..." -ForegroundColor Yellow
    exit 0
}

Read-Host "Pressione Enter para sair"

