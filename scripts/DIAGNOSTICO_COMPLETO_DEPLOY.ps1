# Script de Diagnóstico Completo para Deploy
# Verifica permissões, secrets e configurações

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIAGNÓSTICO COMPLETO DE DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se está autenticado no GCP
Write-Host "1. Verificando autenticação no Google Cloud..." -ForegroundColor Yellow
$gcloudAuth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -eq 0 -and $gcloudAuth) {
    Write-Host "   ✅ Autenticado como: $gcloudAuth" -ForegroundColor Green
} else {
    Write-Host "   ❌ Não autenticado no Google Cloud!" -ForegroundColor Red
    Write-Host "   Execute: gcloud auth login" -ForegroundColor Yellow
}
Write-Host ""

# 2. Verificar projeto atual
Write-Host "2. Verificando projeto atual..." -ForegroundColor Yellow
$currentProject = gcloud config get-value project 2>&1
if ($LASTEXITCODE -eq 0 -and $currentProject) {
    Write-Host "   ✅ Projeto atual: $currentProject" -ForegroundColor Green
    if ($currentProject -ne "monpec-sistema-rural") {
        Write-Host "   ⚠️  Projeto diferente do esperado (monpec-sistema-rural)" -ForegroundColor Yellow
        Write-Host "   Execute: gcloud config set project monpec-sistema-rural" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Projeto não configurado!" -ForegroundColor Red
}
Write-Host ""

# 3. Verificar permissões do usuário atual
Write-Host "3. Verificando permissões do usuário atual..." -ForegroundColor Yellow
$permissions = @(
    "run.services.create",
    "run.services.update",
    "run.services.get",
    "run.services.list",
    "cloudbuild.builds.create",
    "cloudbuild.builds.get",
    "container.images.create",
    "container.images.get",
    "serviceusage.services.use",
    "iam.serviceAccounts.actAs"
)

$userEmail = gcloud config get-value account 2>&1
if ($userEmail) {
    Write-Host "   Usuário: $userEmail" -ForegroundColor Cyan
    foreach ($perm in $permissions) {
        $test = gcloud projects get-iam-policy monpec-sistema-rural --flatten="bindings[].members" --filter="bindings.members:user:$userEmail AND bindings.role:*$perm*" --format="value(bindings.role)" 2>&1
        if ($test) {
            Write-Host "   ✅ $perm" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $perm - FALTANDO" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   ❌ Não foi possível obter email do usuário" -ForegroundColor Red
}
Write-Host ""

# 4. Verificar Service Account do GitHub Actions
Write-Host "4. Verificando Service Account para GitHub Actions..." -ForegroundColor Yellow
$saName = "github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com"
$saExists = gcloud iam service-accounts describe $saName --project=monpec-sistema-rural 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Service Account existe: $saName" -ForegroundColor Green
    
    # Verificar roles do service account
    Write-Host "   Verificando roles do Service Account..." -ForegroundColor Cyan
    $saRoles = gcloud projects get-iam-policy monpec-sistema-rural --flatten="bindings[].members" --filter="bindings.members:serviceAccount:$saName" --format="value(bindings.role)" 2>&1
    if ($saRoles) {
        Write-Host "   Roles atribuídas:" -ForegroundColor Cyan
        $saRoles | ForEach-Object { Write-Host "     - $_" -ForegroundColor Green }
    } else {
        Write-Host "   ❌ Service Account não tem roles atribuídas!" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Service Account NÃO existe: $saName" -ForegroundColor Red
    Write-Host "   Precisa criar o Service Account e configurar as permissões" -ForegroundColor Yellow
}
Write-Host ""

# 5. Verificar secrets do GitHub (via API se possível, senão apenas listar)
Write-Host "5. Verificando Secrets do GitHub..." -ForegroundColor Yellow
$requiredSecrets = @(
    "GCP_SA_KEY",
    "SECRET_KEY",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DJANGO_SUPERUSER_PASSWORD"
)

Write-Host "   Secrets necessários no GitHub:" -ForegroundColor Cyan
foreach ($secret in $requiredSecrets) {
    Write-Host "     - $secret" -ForegroundColor Yellow
}
Write-Host "   ⚠️  Verifique manualmente em: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions" -ForegroundColor Yellow
Write-Host ""

# 6. Verificar serviços do Cloud Run
Write-Host "6. Verificando serviços do Cloud Run..." -ForegroundColor Yellow
$services = gcloud run services list --project=monpec-sistema-rural --format="table(name,region,status.url)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Serviços encontrados:" -ForegroundColor Cyan
    $services
} else {
    Write-Host "   ❌ Erro ao listar serviços: $services" -ForegroundColor Red
}
Write-Host ""

# 7. Verificar builds recentes do Cloud Build
Write-Host "7. Verificando builds recentes do Cloud Build..." -ForegroundColor Yellow
$builds = gcloud builds list --project=monpec-sistema-rural --limit=5 --format="table(id,status,createTime)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Últimos 5 builds:" -ForegroundColor Cyan
    $builds
} else {
    Write-Host "   ❌ Erro ao listar builds: $builds" -ForegroundColor Red
}
Write-Host ""

# 8. Verificar se o Dockerfile existe
Write-Host "8. Verificando arquivos necessários..." -ForegroundColor Yellow
$files = @("Dockerfile", "requirements_producao.txt", ".github/workflows/deploy-principal.yml")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file existe" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file NÃO existe" -ForegroundColor Red
    }
}
Write-Host ""

# 9. Resumo e recomendações
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO E RECOMENDAÇÕES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para o deploy funcionar, você precisa:" -ForegroundColor Yellow
Write-Host "1. Service Account com as seguintes roles:" -ForegroundColor Cyan
Write-Host "   - roles/run.admin" -ForegroundColor White
Write-Host "   - roles/cloudbuild.builds.editor" -ForegroundColor White
Write-Host "   - roles/storage.admin" -ForegroundColor White
Write-Host "   - roles/iam.serviceAccountUser" -ForegroundColor White
Write-Host ""
Write-Host "2. Todos os secrets configurados no GitHub:" -ForegroundColor Cyan
Write-Host "   - GCP_SA_KEY (JSON da service account)" -ForegroundColor White
Write-Host "   - SECRET_KEY (Django secret key)" -ForegroundColor White
Write-Host "   - DB_NAME, DB_USER, DB_PASSWORD" -ForegroundColor White
Write-Host "   - DJANGO_SUPERUSER_PASSWORD" -ForegroundColor White
Write-Host ""
Write-Host "3. Verificar histórico do GitHub Actions:" -ForegroundColor Cyan
Write-Host "   https://github.com/LMONCAO/Monpec_GestaoRural/actions" -ForegroundColor White
Write-Host ""
Write-Host "4. Verificar logs de erro específicos:" -ForegroundColor Cyan
Write-Host "   gcloud builds list --project=monpec-sistema-rural --limit=10" -ForegroundColor White
Write-Host ""
