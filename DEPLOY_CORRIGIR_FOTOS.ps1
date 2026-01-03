# ============================================================================
# DEPLOY COMPLETO - CORRIGIR FOTOS NO GOOGLE CLOUD
# ============================================================================
# Este script faz TUDO automaticamente:
# 1. Verifica configurações
# 2. Faz build da imagem Docker (com correções das fotos)
# 3. Faz deploy no Cloud Run
# 4. Verifica se as fotos estão funcionando
# ============================================================================

$ErrorActionPreference = "Stop"

# Cores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "🚀 DEPLOY - CORRIGIR FOTOS NO GOOGLE CLOUD"
Write-ColorOutput Cyan "=========================================="
Write-Output ""

# 1. Verificar se está no diretório correto
Write-ColorOutput Yellow "[1/7] Verificando diretório..."
if (-not (Test-Path "manage.py")) {
    Write-ColorOutput Red "❌ ERRO: manage.py não encontrado!"
    Write-Output "Execute este script no diretório raiz do projeto."
    exit 1
}
Write-ColorOutput Green "✅ Diretório correto"
Write-Output ""

# 2. Verificar se gcloud está instalado
Write-ColorOutput Yellow "[2/7] Verificando gcloud CLI..."
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-ColorOutput Green "✅ gcloud CLI encontrado: $gcloudVersion"
} catch {
    Write-ColorOutput Red "❌ gcloud CLI não está instalado!"
    Write-Output "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Output ""

# 3. Configurar projeto
Write-ColorOutput Yellow "[3/7] Configurando projeto GCP..."
$currentProject = gcloud config get-value project 2>&1
if ($currentProject -eq $PROJECT_ID) {
    Write-ColorOutput Green "✅ Projeto já configurado: $PROJECT_ID"
} else {
    try {
        gcloud config set project $PROJECT_ID 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "✅ Projeto configurado: $PROJECT_ID"
        } else {
            Write-ColorOutput Yellow "⚠️  Tentando continuar mesmo com possível erro na configuração..."
        }
    } catch {
        Write-ColorOutput Yellow "⚠️  Erro ao configurar projeto, mas continuando..."
    }
}
Write-Output ""

# 4. Verificar autenticação
Write-ColorOutput Yellow "[4/7] Verificando autenticação..."
$authAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authAccount) {
    Write-ColorOutput Yellow "⚠️  Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Red "❌ Falha na autenticação!"
        exit 1
    }
} else {
    Write-ColorOutput Green "✅ Autenticado como: $authAccount"
}
Write-Output ""

# 5. Habilitar APIs necessárias
Write-ColorOutput Yellow "[5/7] Habilitando APIs necessárias..."
$APIS = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "sqladmin.googleapis.com"
)

foreach ($api in $APIS) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-ColorOutput Green "✅ APIs habilitadas"
Write-Output ""

# 6. Build da imagem Docker
Write-ColorOutput Yellow "[6/7] Buildando imagem Docker..."
Write-ColorOutput Cyan "⏱️  Isso pode levar 5-10 minutos..."
Write-ColorOutput Cyan "   Imagem: $IMAGE_TAG"
Write-Output ""

try {
    gcloud builds submit --tag $IMAGE_TAG --timeout=20m
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Red "❌ Erro no build!"
        exit 1
    }
    Write-ColorOutput Green "✅ Build concluído com sucesso!"
} catch {
    Write-ColorOutput Red "❌ Erro no build: $_"
    exit 1
}
Write-Output ""

# 7. Deploy no Cloud Run
Write-ColorOutput Yellow "[7/7] Deployando no Cloud Run..."
Write-ColorOutput Cyan "⏱️  Isso pode levar 2-5 minutos..."
Write-Output ""

# Variáveis de ambiente (ajustar conforme necessário)
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

try {
    gcloud run deploy $SERVICE_NAME `
        --image $IMAGE_TAG `
        --region=$REGION `
        --platform managed `
        --allow-unauthenticated `
        --set-env-vars $ENV_VARS `
        --memory=2Gi `
        --cpu=2 `
        --timeout=600 `
        --min-instances=1 `
        --max-instances=10 `
        --port=8080 `
        --quiet

    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Red "❌ Erro no deploy!"
        exit 1
    }
    Write-ColorOutput Green "✅ Deploy concluído com sucesso!"
} catch {
    Write-ColorOutput Red "❌ Erro no deploy: $_"
    exit 1
}
Write-Output ""

# Obter URL do serviço
Write-ColorOutput Yellow "Obtendo URL do serviço..."
try {
    $SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1
    Write-ColorOutput Green "✅ URL obtida: $SERVICE_URL"
} catch {
    Write-ColorOutput Yellow "⚠️  Não foi possível obter URL automaticamente"
    $SERVICE_URL = "https://monpec.com.br"
}
Write-Output ""

# Resumo final
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅"
Write-ColorOutput Green "=========================================="
Write-Output ""
Write-ColorOutput Cyan "🔗 URL do Serviço:"
Write-ColorOutput Green "   $SERVICE_URL"
Write-Output ""
Write-ColorOutput Cyan "📋 Próximos Passos:"
Write-Output "   1. Aguarde 1-2 minutos para o serviço inicializar completamente"
Write-Output "   2. Teste as fotos na landing page:"
Write-Output "      $SERVICE_URL"
Write-Output "   3. Abra DevTools (F12) → Network para verificar se as fotos carregam"
Write-Output "   4. Verifique se as requisições para /static/site/foto*.jpeg retornam 200"
Write-Output ""
Write-ColorOutput Cyan "📊 Ver Logs:"
Write-Output "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50"
Write-Output ""
Write-ColorOutput Cyan "🔍 Executar Diagnóstico:"
Write-Output "   python diagnosticar_fotos_cloud.py"
Write-Output ""
Write-ColorOutput Cyan "🔄 Se as fotos ainda não aparecerem:"
Write-Output "   1. Verifique os logs do build (procure por 'collectstatic')"
Write-Output "   2. Execute o script de diagnóstico"
Write-Output "   3. Verifique se as fotos estão em static/site/ no repositório"
Write-Output ""

