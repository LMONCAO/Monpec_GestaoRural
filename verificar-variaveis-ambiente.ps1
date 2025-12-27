# Script para verificar variáveis de ambiente necessárias no Cloud Run
# Este script lista todas as variáveis de ambiente configuradas e identifica as que estão faltando

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

# Variáveis de ambiente críticas necessárias
$VARIAVEIS_CRITICAS = @(
    "SECRET_KEY",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "CLOUD_SQL_CONNECTION_NAME"
)

# Variáveis de ambiente opcionais mas recomendadas
$VARIAVEIS_OPCIONAIS = @(
    "DEBUG",
    "DJANGO_SUPERUSER_PASSWORD",
    "GOOGLE_CLOUD_PROJECT",
    "GS_BUCKET_NAME",
    "USE_CLOUD_STORAGE",
    "REDIS_HOST"
)

Write-Host "Obtendo variáveis de ambiente do serviço Cloud Run..." -ForegroundColor Yellow
$envVars = gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(spec.template.spec.containers[0].env)" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Não foi possível obter informações do serviço" -ForegroundColor Red
    Write-Host "Verifique se o serviço existe e se você tem permissões" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== VARIÁVEIS CRÍTICAS ===" -ForegroundColor Yellow
$envVarNames = @()
if ($envVars) {
    # Parse das variáveis de ambiente
    $lines = $envVars -split "`n"
    foreach ($line in $lines) {
        if ($line -match "name=([^,]+)") {
            $envVarNames += $matches[1]
        }
    }
}

$faltando = @()
foreach ($var in $VARIAVEIS_CRITICAS) {
    if ($envVarNames -contains $var) {
        Write-Host "✓ $var - CONFIGURADA" -ForegroundColor Green
    } else {
        Write-Host "✗ $var - FALTANDO" -ForegroundColor Red
        $faltando += $var
    }
}

Write-Host "`n=== VARIÁVEIS OPCIONAIS ===" -ForegroundColor Yellow
foreach ($var in $VARIAVEIS_OPCIONAIS) {
    if ($envVarNames -contains $var) {
        Write-Host "✓ $var - CONFIGURADA" -ForegroundColor Green
    } else {
        Write-Host "○ $var - Não configurada (opcional)" -ForegroundColor Gray
    }
}

Write-Host "`n=== TODAS AS VARIÁVEIS CONFIGURADAS ===" -ForegroundColor Yellow
if ($envVarNames.Count -gt 0) {
    foreach ($var in $envVarNames) {
        Write-Host "  - $var" -ForegroundColor White
    }
} else {
    Write-Host "  Nenhuma variável de ambiente encontrada" -ForegroundColor Red
}

if ($faltando.Count -gt 0) {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "ATENÇÃO: Variáveis críticas faltando!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "`nPara configurar as variáveis faltantes, execute:" -ForegroundColor Yellow
    Write-Host "`ngcloud run services update $SERVICE_NAME \`" -ForegroundColor White
    Write-Host "  --region=$REGION \`" -ForegroundColor White
    Write-Host "  --project=$PROJECT_ID \`" -ForegroundColor White
    foreach ($var in $faltando) {
        Write-Host "  --set-env-vars $var=VALUE \`" -ForegroundColor White
    }
    Write-Host ""
} else {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Todas as variáveis críticas estão configuradas!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

Write-Host "`nPara ver os valores das variáveis (sem mostrar senhas):" -ForegroundColor Yellow
Write-Host "gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='yaml(spec.template.spec.containers[0].env)'" -ForegroundColor White


