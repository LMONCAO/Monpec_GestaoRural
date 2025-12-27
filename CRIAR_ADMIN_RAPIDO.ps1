# 🚀 CRIAR ADMIN RÁPIDO - Via Cloud Run Job
# Método mais direto usando comando inline

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "👤 CRIANDO ADMIN EM PRODUÇÃO (RÁPIDO)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$JOB_NAME = "criar-admin-rapido"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Configurar projeto
gcloud config set project $PROJECT_ID --quiet 2>&1 | Out-Null

# Obter variáveis de ambiente do serviço
Write-Host "▶ Obtendo variáveis de ambiente do serviço..." -ForegroundColor Blue
$serviceEnv = gcloud run services describe $SERVICE_NAME --region $REGION --format="get(spec.template.spec.containers[0].env)" 2>&1

# Construir string de variáveis
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

# Extrair variáveis importantes do serviço
$dbVars = @("DB_NAME", "DB_USER", "DB_PASSWORD", "SECRET_KEY", "MERCADOPAGO_ACCESS_TOKEN")
foreach ($var in $dbVars) {
    $value = ($serviceEnv | Select-String -Pattern "$var=([^,]+)" | ForEach-Object { $_.Matches.Groups[1].Value })
    if ($value) {
        $envVars += "$var=$value"
    }
}

$envVarsString = $envVars -join ","

Write-Host "▶ Criando job..." -ForegroundColor Blue

# Criar job com comando Python inline
$pythonCmd = "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u='admin';e='admin@monpec.com.br';p='L6171r12@@';user=User.objects.filter(username=u).first();[setattr(user,attr,val) for attr,val in [('password',User.objects.make_password(p)),('is_superuser',True),('is_staff',True),('is_active',True),('email',e)] if user] and user.save() or User.objects.create_superuser(u,e,p);print('✅ Admin criado/atualizado!')"

# Criar/atualizar job
$jobCreate = gcloud run jobs create $JOB_NAME `
    --image "$IMAGE_NAME`:latest" `
    --region $REGION `
    --set-env-vars $envVarsString `
    --memory=1Gi `
    --cpu=1 `
    --max-retries=1 `
    --task-timeout=300 `
    --command=python `
    --args="-c","$pythonCmd" `
    --quiet 2>&1

if ($LASTEXITCODE -ne 0) {
    # Tentar atualizar
    gcloud run jobs update $JOB_NAME `
        --image "$IMAGE_NAME`:latest" `
        --region $REGION `
        --set-env-vars $envVarsString `
        --memory=1Gi `
        --cpu=1 `
        --max-retries=1 `
        --task-timeout=300 `
        --command=python `
        --args="-c","$pythonCmd" `
        --quiet 2>&1 | Out-Null
}

Write-Host "▶ Executando job..." -ForegroundColor Blue
$result = gcloud run jobs execute $JOB_NAME --region $REGION --wait 2>&1

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Admin criado/atualizado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 CREDENCIAIS:" -ForegroundColor Cyan
    Write-Host "   Usuário: admin" -ForegroundColor White
    Write-Host "   Senha: L6171r12@@" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Acesse: https://monpec.com.br/login/" -ForegroundColor Cyan
} else {
    Write-Host "❌ Erro ao executar. Verificando logs..." -ForegroundColor Red
    gcloud run jobs executions list --job=$JOB_NAME --region=$REGION --limit=1 --format="value(name)" | ForEach-Object {
        gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME" --limit=20 --format="table(timestamp,textPayload)"
    }
}

Write-Host ""

