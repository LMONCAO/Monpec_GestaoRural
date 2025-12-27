# Script para Verificar Configuração do Deploy Automático

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 Verificação da Configuração" -ForegroundColor Cyan
Write-Host "Deploy Automático - GitHub Actions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$SA_NAME = "github-actions-deploy"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
$errors = 0

function Write-Check {
    param(
        [string]$Name,
        [bool]$Status,
        [string]$Message = ""
    )
    if ($Status) {
        Write-Host "✅ $Name" -ForegroundColor Green
        if ($Message) {
            Write-Host "   $Message" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ $Name" -ForegroundColor Red
        if ($Message) {
            Write-Host "   $Message" -ForegroundColor Yellow
        }
        $script:errors++
    }
}

# Verificar gcloud CLI
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
Write-Check "gcloud CLI instalado" ($null -ne $gcloudPath) "Execute: https://cloud.google.com/sdk/docs/install"

# Verificar autenticação
if ($gcloudPath) {
    $currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    Write-Check "Autenticado no Google Cloud" ($currentAccount -and $currentAccount -notmatch "ERROR") "Execute: gcloud auth login"
    
    # Verificar projeto
    $currentProject = gcloud config get-value project 2>&1
    $projectOk = ($currentProject -eq $PROJECT_ID)
    Write-Check "Projeto GCP configurado" $projectOk "Projeto atual: $currentProject (esperado: $PROJECT_ID)"
    
    if ($projectOk) {
        # Verificar Service Account
        $saExists = gcloud iam service-accounts describe $SA_EMAIL 2>&1
        Write-Check "Service Account existe" ($LASTEXITCODE -eq 0) "Service Account: $SA_EMAIL"
        
        if ($LASTEXITCODE -eq 0) {
            # Verificar permissões
            Write-Host ""
            Write-Host "📋 Verificando permissões..." -ForegroundColor Cyan
            $roles = @(
                "roles/run.admin",
                "roles/iam.serviceAccountUser",
                "roles/cloudbuild.builds.editor",
                "roles/storage.admin",
                "roles/cloudsql.client"
            )
            
            $policy = gcloud projects get-iam-policy $PROJECT_ID --format=json 2>&1 | ConvertFrom-Json
            foreach ($role in $roles) {
                $hasRole = $policy.bindings | Where-Object { 
                    $_.role -eq $role -and $_.members -contains "serviceAccount:$SA_EMAIL"
                }
                Write-Check "  Permissão: $role" ($null -ne $hasRole) ""
            }
            
            # Verificar chave JSON
            $keyFile = "github-actions-deploy-key.json"
            $keyExists = Test-Path $keyFile
            Write-Check "Chave JSON local existe" $keyExists "Arquivo: $keyFile"
        }
        
        # Verificar APIs
        Write-Host ""
        Write-Host "📋 Verificando APIs habilitadas..." -ForegroundColor Cyan
        $requiredApis = @(
            "cloudbuild.googleapis.com",
            "run.googleapis.com",
            "containerregistry.googleapis.com"
        )
        
        foreach ($api in $requiredApis) {
            $apiStatus = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>&1
            $isEnabled = $apiStatus -eq $api
            Write-Check "  API: $api" $isEnabled ""
        }
    }
}

# Verificar arquivos do workflow
Write-Host ""
Write-Host "📋 Verificando arquivos do projeto..." -ForegroundColor Cyan
$workflowFile = ".github/workflows/deploy-gcp.yml"
Write-Check "Workflow GitHub Actions existe" (Test-Path $workflowFile) "Arquivo: $workflowFile"

$dockerfile = "Dockerfile.prod"
Write-Check "Dockerfile.prod existe" (Test-Path $dockerfile) "Arquivo: $dockerfile"

# Verificar .gitignore
$gitignoreFile = ".gitignore"
if (Test-Path $gitignoreFile) {
    $gitignoreContent = Get-Content $gitignoreFile -Raw
    $keyFileInGitignore = $gitignoreContent -match "github-actions-deploy-key.json"
    Write-Check "Chave JSON no .gitignore" $keyFileInGitignore "Adicione 'github-actions-deploy-key.json' ao .gitignore"
} else {
    Write-Check ".gitignore existe" $false "Crie um arquivo .gitignore"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($errors -eq 0) {
    Write-Host "✅ TODAS AS VERIFICAÇÕES PASSARAM!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Configure o secret GCP_SA_KEY no GitHub" -ForegroundColor White
    Write-Host "   2. Faça push do código: git push origin main" -ForegroundColor White
    Write-Host "   3. Acompanhe o deploy em: https://github.com/LMONCAO/monpec/actions" -ForegroundColor White
} else {
    Write-Host "⚠️  $errors VERIFICAÇÃO(ÕES) FALHARAM" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Execute o script de configuração:" -ForegroundColor Yellow
    Write-Host "   .\CONFIGURAR_DEPLOY_AUTOMATICO.ps1" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

