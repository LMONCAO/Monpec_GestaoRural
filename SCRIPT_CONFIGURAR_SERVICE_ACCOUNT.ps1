# Script para ajudar a criar a Service Account no Google Cloud
# Execute este script após criar a service account manualmente no console

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuração da Service Account" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "❌ gcloud CLI não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, instale o Google Cloud SDK:" -ForegroundColor Yellow
    Write-Host "https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ gcloud CLI encontrado" -ForegroundColor Green
Write-Host ""

# Configurar projeto
$PROJECT_ID = "monpec-sistema-rural"
Write-Host "📦 Configurando projeto: $PROJECT_ID" -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao configurar projeto!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Projeto configurado" -ForegroundColor Green
Write-Host ""

# Verificar se a service account já existe
$SA_EMAIL = "github-actions-deploy@$PROJECT_ID.iam.gserviceaccount.com"
Write-Host "🔍 Verificando se service account já existe..." -ForegroundColor Cyan

$saExists = gcloud iam service-accounts describe $SA_EMAIL 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Service account já existe: $SA_EMAIL" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Verificando permissões..." -ForegroundColor Cyan
    
    # Listar permissões atuais
    gcloud projects get-iam-policy $PROJECT_ID `
        --flatten="bindings[].members" `
        --format="table(bindings.role)" `
        --filter="bindings.members:$SA_EMAIL"
    
    Write-Host ""
    Write-Host "💡 Para adicionar permissões manualmente, execute:" -ForegroundColor Yellow
    Write-Host "gcloud projects add-iam-policy-binding $PROJECT_ID `" -ForegroundColor Gray
    Write-Host "  --member=`"serviceAccount:$SA_EMAIL`" `" -ForegroundColor Gray
    Write-Host "  --role=`"roles/run.admin`"" -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "⚠️  Service account não encontrada" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Para criar a service account, execute no console GCP:" -ForegroundColor Cyan
    Write-Host "   1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts?project=$PROJECT_ID" -ForegroundColor White
    Write-Host "   2. Clique em 'CREATE SERVICE ACCOUNT'" -ForegroundColor White
    Write-Host "   3. Nome: github-actions-deploy" -ForegroundColor White
    Write-Host "   4. Adicione as permissões:" -ForegroundColor White
    Write-Host "      - Cloud Run Admin" -ForegroundColor Gray
    Write-Host "      - Service Account User" -ForegroundColor Gray
    Write-Host "      - Cloud Build Editor" -ForegroundColor Gray
    Write-Host "      - Storage Admin" -ForegroundColor Gray
    Write-Host "      - Cloud SQL Client" -ForegroundColor Gray
    Write-Host "   5. Crie uma chave JSON" -ForegroundColor White
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Próximos Passos:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. ✅ Se a service account existe, crie uma chave JSON no console" -ForegroundColor Green
Write-Host "2. ✅ Configure o secret GCP_SA_KEY no GitHub" -ForegroundColor Green
Write-Host "3. ✅ Faça push do código para o GitHub" -ForegroundColor Green
Write-Host "4. ✅ O deploy será executado automaticamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Consulte: DEPLOY_AGORA_PASSO_A_PASSO.md para instruções detalhadas" -ForegroundColor Cyan
Write-Host ""

