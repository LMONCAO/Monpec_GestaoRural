# 🔥 RESETAR GOOGLE CLOUD - EXCLUIR TUDO E PREPARAR PARA NOVO DEPLOY
# ⚠️ ATENÇÃO: Este script EXCLUI TODOS os recursos do projeto!
# Use apenas se deseja resetar completamente o ambiente

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
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

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "🔥 RESETAR GOOGLE CLOUD - EXCLUIR TUDO" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Warning "⚠️  ATENÇÃO: Este script vai EXCLUIR todos os recursos!"
Write-Host "   • Serviços Cloud Run"
Write-Host "   • Jobs Cloud Run"
Write-Host "   • Instância Cloud SQL (E TODOS OS DADOS!)"
Write-Host "   • Domain Mappings"
Write-Host "   • Imagens Docker no Container Registry"
Write-Host ""

# Confirmação
$confirm = Read-Host "Digite 'CONFIRMAR' para continuar (qualquer outra coisa cancela)"
if ($confirm -ne "CONFIRMAR") {
    Write-Host "Operação cancelada pelo usuário." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Log "Verificando autenticação no Google Cloud..."
$ACCOUNT = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $ACCOUNT) {
    Write-Error "Você não está autenticado no Google Cloud!"
    Write-Host "Execute: gcloud auth login"
    exit 1
}
Write-Success "Autenticado como: $ACCOUNT"

Write-Log "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Success "Projeto configurado: $PROJECT_ID"
Write-Host ""

# PARTE 1: EXCLUIR DOMAIN MAPPINGS
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 1: EXCLUINDO DOMAIN MAPPINGS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Excluindo domain mapping para $DOMAIN..."
try {
    gcloud run domain-mappings delete $DOMAIN --region $REGION --quiet 2>&1 | Out-Null
    Write-Success "Domain mapping excluído: $DOMAIN"
} catch {
    Write-Log "Domain mapping não encontrado: $DOMAIN"
}

Write-Log "Excluindo domain mapping para $WWW_DOMAIN..."
try {
    gcloud run domain-mappings delete $WWW_DOMAIN --region $REGION --quiet 2>&1 | Out-Null
    Write-Success "Domain mapping excluído: $WWW_DOMAIN"
} catch {
    Write-Log "Domain mapping não encontrado: $WWW_DOMAIN"
}

Write-Host ""

# PARTE 2: EXCLUIR JOBS DO CLOUD RUN
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 2: EXCLUINDO JOBS DO CLOUD RUN"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$JOB_NAMES = @("migrate-monpec", "collectstatic-monpec", "create-superuser")
foreach ($JOB_NAME in $JOB_NAMES) {
    Write-Log "Excluindo job: $JOB_NAME..."
    try {
        gcloud run jobs delete $JOB_NAME --region $REGION --quiet 2>&1 | Out-Null
        Write-Success "Job excluído: $JOB_NAME"
    } catch {
        Write-Log "Job não encontrado: $JOB_NAME"
    }
}

# Excluir todos os jobs (caso haja outros)
Write-Log "Listando todos os jobs restantes..."
$ALL_JOBS = gcloud run jobs list --region $REGION --format="value(name)" 2>&1
if ($ALL_JOBS) {
    foreach ($JOB in $ALL_JOBS) {
        $JOB_SHORT = $JOB.Split('/')[-1]
        Write-Log "Excluindo job: $JOB_SHORT..."
        try {
            gcloud run jobs delete $JOB_SHORT --region $REGION --quiet 2>&1 | Out-Null
            Write-Success "Job excluído: $JOB_SHORT"
        } catch {
            Write-Log "Erro ao excluir job: $JOB_SHORT"
        }
    }
}

Write-Host ""

# PARTE 3: EXCLUIR SERVIÇO CLOUD RUN
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 3: EXCLUINDO SERVIÇO CLOUD RUN"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Excluindo serviço: $SERVICE_NAME..."
try {
    gcloud run services delete $SERVICE_NAME --region $REGION --quiet 2>&1 | Out-Null
    Write-Success "Serviço Cloud Run excluído: $SERVICE_NAME"
} catch {
    Write-Log "Serviço não encontrado: $SERVICE_NAME"
}

# Excluir todos os serviços (caso haja outros)
Write-Log "Listando todos os serviços restantes..."
$ALL_SERVICES = gcloud run services list --region $REGION --format="value(name)" 2>&1
if ($ALL_SERVICES) {
    foreach ($SERVICE in $ALL_SERVICES) {
        $SERVICE_SHORT = $SERVICE.Split('/')[-1]
        Write-Log "Excluindo serviço: $SERVICE_SHORT..."
        try {
            gcloud run services delete $SERVICE_SHORT --region $REGION --quiet 2>&1 | Out-Null
            Write-Success "Serviço excluído: $SERVICE_SHORT"
        } catch {
            Write-Log "Erro ao excluir serviço: $SERVICE_SHORT"
        }
    }
}

Write-Host ""

# PARTE 4: EXCLUIR INSTÂNCIA CLOUD SQL (CUIDADO - EXCLUI TODOS OS DADOS!)
Write-Host "========================================" -ForegroundColor Red
Write-Log "PARTE 4: EXCLUINDO INSTÂNCIA CLOUD SQL"
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Warning "⚠️  ATENÇÃO: Isso vai EXCLUIR TODOS OS DADOS do banco de dados!"
Write-Host ""

$confirm_db = Read-Host "Digite 'EXCLUIR' para excluir o banco de dados (qualquer outra coisa mantém o banco)"
if ($confirm_db -eq "EXCLUIR") {
    Write-Log "Excluindo instância Cloud SQL: $INSTANCE_NAME..."
    try {
        gcloud sql instances delete $INSTANCE_NAME --quiet 2>&1 | Out-Null
        Write-Success "Instância Cloud SQL excluída: $INSTANCE_NAME"
        Write-Warning "⚠️  Todos os dados foram excluídos permanentemente!"
    } catch {
        Write-Log "Instância não encontrada: $INSTANCE_NAME (pode já ter sido excluída)"
    }
} else {
    Write-Log "Instância Cloud SQL mantida (não foi excluída)"
    Write-Warning "Se você desejar excluir depois, execute:"
    Write-Host "   gcloud sql instances delete $INSTANCE_NAME"
}

Write-Host ""

# PARTE 5: EXCLUIR IMAGENS DO CONTAINER REGISTRY
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 5: EXCLUINDO IMAGENS DO CONTAINER REGISTRY"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Listando imagens no Container Registry..."
try {
    $IMAGES = gcloud container images list --repository=gcr.io/$PROJECT_ID --format="value(name)" 2>&1
    if ($IMAGES) {
        foreach ($IMAGE in $IMAGES) {
            Write-Log "Listando tags da imagem: $IMAGE..."
            $TAGS = gcloud container images list-tags $IMAGE --format="value(digest)" 2>&1
            if ($TAGS) {
                Write-Log "Excluindo imagem: $IMAGE..."
                gcloud container images delete $IMAGE --force-delete-tags --quiet 2>&1 | Out-Null
                Write-Success "Imagem excluída: $IMAGE"
            }
        }
    } else {
        Write-Log "Nenhuma imagem encontrada no Container Registry"
    }
} catch {
    Write-Log "Erro ao listar/excluir imagens (pode não haver imagens)"
}

# Excluir imagem específica também
Write-Log "Tentando excluir imagem específica: $IMAGE_NAME..."
try {
    gcloud container images delete $IMAGE_NAME --force-delete-tags --quiet 2>&1 | Out-Null
    Write-Success "Imagem excluída: $IMAGE_NAME"
} catch {
    Write-Log "Imagem não encontrada ou já excluída: $IMAGE_NAME"
}

Write-Host ""

# PARTE 6: EXCLUIR BUILD HISTORY (OPCIONAL)
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "PARTE 6: LIMPANDO HISTÓRICO DE BUILDS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Listando builds recentes..."
try {
    $BUILDS = gcloud builds list --limit=50 --format="value(id)" 2>&1
    if ($BUILDS) {
        Write-Warning "Existem builds no histórico (não serão excluídos automaticamente)"
        Write-Log "Se desejar excluir builds antigos, use:"
        Write-Host "   gcloud builds list --limit=50"
        Write-Host "   gcloud builds delete [BUILD_ID]"
    } else {
        Write-Log "Nenhum build encontrado"
    }
} catch {
    Write-Log "Erro ao listar builds"
}

Write-Host ""

# RESUMO FINAL
Write-Host "========================================" -ForegroundColor Green
Write-Success "✅ RESET CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 RECURSOS EXCLUÍDOS:" -ForegroundColor Cyan
Write-Host "  ✅ Domain Mappings (se existiam)"
Write-Host "  ✅ Jobs Cloud Run (se existiam)"
Write-Host "  ✅ Serviços Cloud Run (se existiam)"
if ($confirm_db -eq "EXCLUIR") {
    Write-Host "  ✅ Instância Cloud SQL (E TODOS OS DADOS!)"
} else {
    Write-Host "  ⏸️  Instância Cloud SQL (mantida)"
}
Write-Host "  ✅ Imagens Docker no Container Registry"
Write-Host ""

Write-Host "🚀 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para fazer um novo deploy limpo, execute:"
Write-Host "   .\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1"
Write-Host ""
Write-Host "Ou se preferir usar o Google Cloud Shell:"
Write-Host "   .\DEPLOY_GOOGLE_CLOUD_SHELL.sh"
Write-Host ""
Write-Success "🎉 Ambiente resetado com sucesso!"
Write-Host ""






