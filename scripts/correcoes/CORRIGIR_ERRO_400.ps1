# Script PowerShell para corrigir erro 400 no Cloud Run
# Execute este script no PowerShell do Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔍 DIAGNÓSTICO E CORREÇÃO - ERRO 400" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host "📋 Verificando configurações do projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

Write-Host ""
Write-Host "1️⃣ Verificando variáveis de ambiente do serviço..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
$envVars = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(spec.template.spec.containers[0].env)" 2>$null

if ($envVars) {
    Write-Host "✅ Variáveis de ambiente encontradas" -ForegroundColor Green
    Write-Host $envVars
} else {
    Write-Host "⚠️ Erro ao obter variáveis de ambiente" -ForegroundColor Red
}

Write-Host ""
Write-Host "2️⃣ Verificando logs recentes do serviço..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host "Últimas 50 linhas de log:"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" `
    --limit=50 `
    --format="table(timestamp,severity,textPayload)" `
    --project=$PROJECT_ID 2>$null

Write-Host ""
Write-Host "3️⃣ Verificando status do serviço..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
$serviceStatus = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="table(status.conditions[0].type,status.conditions[0].status,status.url)" 2>$null

if ($serviceStatus) {
    Write-Host $serviceStatus
} else {
    Write-Host "⚠️ Erro ao obter status" -ForegroundColor Red
}

Write-Host ""
Write-Host "4️⃣ Verificando variáveis de ambiente críticas..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host "Variáveis necessárias:"
Write-Host "  - SECRET_KEY"
Write-Host "  - DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
Write-Host "  - DB_NAME"
Write-Host "  - DB_USER"
Write-Host "  - DB_PASSWORD"
Write-Host "  - CLOUD_SQL_CONNECTION_NAME"
Write-Host ""

Write-Host ""
Write-Host "5️⃣ Aplicando correções..." -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Verificar se SECRET_KEY está configurada
$secretKey = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(spec.template.spec.containers[0].env[?(@.name=='SECRET_KEY')].value)" 2>$null

if ([string]::IsNullOrEmpty($secretKey)) {
    Write-Host "⚠️ SECRET_KEY não configurada. Configurando..." -ForegroundColor Yellow
    # Gerar uma nova SECRET_KEY
    $newSecretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})
    
    Write-Host "Atualizando serviço com SECRET_KEY..."
    gcloud run services update $SERVICE_NAME `
        --region=$REGION `
        --update-env-vars "SECRET_KEY=$newSecretKey" `
        --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SECRET_KEY configurada" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erro ao atualizar SECRET_KEY" -ForegroundColor Red
    }
} else {
    Write-Host "✅ SECRET_KEY já está configurada" -ForegroundColor Green
}

# Verificar se DJANGO_SETTINGS_MODULE está configurado
$settingsModule = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_SETTINGS_MODULE')].value)" 2>$null

if ([string]::IsNullOrEmpty($settingsModule)) {
    Write-Host "⚠️ DJANGO_SETTINGS_MODULE não configurado. Configurando..." -ForegroundColor Yellow
    gcloud run services update $SERVICE_NAME `
        --region=$REGION `
        --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
        --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ DJANGO_SETTINGS_MODULE configurado" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erro ao atualizar DJANGO_SETTINGS_MODULE" -ForegroundColor Red
    }
} else {
    Write-Host "✅ DJANGO_SETTINGS_MODULE já está configurado: $settingsModule" -ForegroundColor Green
}

# Verificar se DEBUG está configurado
$debugValue = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DEBUG')].value)" 2>$null

if ([string]::IsNullOrEmpty($debugValue) -or $debugValue -ne "False") {
    Write-Host "⚠️ DEBUG não está configurado como False. Configurando..." -ForegroundColor Yellow
    gcloud run services update $SERVICE_NAME `
        --region=$REGION `
        --update-env-vars "DEBUG=False" `
        --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ DEBUG configurado como False" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erro ao atualizar DEBUG" -ForegroundColor Red
    }
} else {
    Write-Host "✅ DEBUG já está configurado corretamente: $debugValue" -ForegroundColor Green
}

Write-Host ""
Write-Host "6️⃣ Verificando conexão com Cloud SQL..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
$cloudSqlConn = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>$null

if ([string]::IsNullOrEmpty($cloudSqlConn)) {
    Write-Host "⚠️ CLOUD_SQL_CONNECTION_NAME não configurado" -ForegroundColor Yellow
    Write-Host "Configurando com valor padrão..."
    gcloud run services update $SERVICE_NAME `
        --region=$REGION `
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
        --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ CLOUD_SQL_CONNECTION_NAME configurado" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erro ao atualizar CLOUD_SQL_CONNECTION_NAME" -ForegroundColor Red
    }
} else {
    Write-Host "✅ CLOUD_SQL_CONNECTION_NAME configurado: $cloudSqlConn" -ForegroundColor Green
}

Write-Host ""
Write-Host "7️⃣ Aplicando migrações do banco de dados..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host "Criando job de migração..."

# Verificar se o job já existe
$jobExists = gcloud run jobs describe migrate-monpec --region=$REGION --format="value(metadata.name)" 2>$null

if ([string]::IsNullOrEmpty($jobExists)) {
    Write-Host "Criando job de migração..."
    gcloud run jobs create migrate-monpec `
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest `
        --region=$REGION `
        --command python `
        --args "manage.py,migrate,--noinput" `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
        --cloud-sql-instances=$cloudSqlConn `
        --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Job de migração criado" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erro ao criar job de migração" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Job de migração já existe" -ForegroundColor Green
}

Write-Host "Executando migrações..."
gcloud run jobs execute migrate-monpec --region=$REGION --wait 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migrações executadas com sucesso" -ForegroundColor Green
} else {
    Write-Host "⚠️ Erro ao executar migrações" -ForegroundColor Red
}

Write-Host ""
Write-Host "8️⃣ Verificando URL do serviço..." -ForegroundColor Yellow
Write-Host "----------------------------------------"
$serviceUrl = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(status.url)" 2>$null

if ($serviceUrl) {
    Write-Host "✅ URL do serviço: $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️ IMPORTANTE: Verifique se o ALLOWED_HOSTS em settings_gcp.py inclui o host do Cloud Run"
} else {
    Write-Host "❌ Não foi possível obter URL do serviço" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ DIAGNÓSTICO CONCLUÍDO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Verifique os logs do serviço para mais detalhes"
Write-Host "  2. Certifique-se de que todas as variáveis de ambiente estão configuradas"
Write-Host "  3. Verifique se as migrações foram aplicadas com sucesso"
Write-Host "  4. Teste o acesso ao serviço novamente"
Write-Host ""
if ($serviceUrl) {
    Write-Host "🔗 URL do serviço: $serviceUrl" -ForegroundColor Cyan
}
Write-Host ""





