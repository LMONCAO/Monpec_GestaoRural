# Script PowerShell para Atualizar Sistema Completo no Google Cloud
# Este script faz build e deploy completo do sistema

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZAR SISTEMA - GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"
$CONNECTION_NAME = "monpec-sistema-rural:us-central1:monpec-db"
$DB_PASSWORD = "R72dONWK0vl4yZfpEXwHVr8it"

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Erro: Execute este script na raiz do projeto!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Diretório do projeto encontrado" -ForegroundColor Green
Write-Host ""

# 1. Verificar se há Dockerfile
Write-Host "1️⃣ Verificando Dockerfile..." -ForegroundColor Blue
$dockerfile = Get-ChildItem -Path . -Filter "Dockerfile*" -File | Select-Object -First 1
if (-not $dockerfile) {
    Write-Host "⚠️ Dockerfile não encontrado. Criando Dockerfile.prod..." -ForegroundColor Yellow
    
    $dockerfileContent = @"
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Coletar arquivos estáticos (IMPORTANTE: garante que as fotos sejam copiadas)
RUN python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp || \
    (echo "⚠️ AVISO: collectstatic falhou, tentando novamente com --clear..." && \
     python manage.py collectstatic --noinput --clear --settings=sistema_rural.settings_gcp || true)

# Verificar se as fotos foram coletadas (para debug)
RUN echo "🔍 Verificando se as fotos do slideshow foram coletadas..." && \
    if [ -d "/app/staticfiles/site" ]; then \
        echo "✅ Diretório staticfiles/site existe" && \
        ls -la /app/staticfiles/site/ | grep -E "foto[1-6]\.jpeg" && echo "✅ Fotos encontradas!" || echo "⚠️ Fotos não encontradas em staticfiles/site/"; \
    else \
        echo "⚠️ Diretório staticfiles/site não existe - as fotos podem não estar sendo servidas!"; \
    fi

# Expor porta
EXPOSE 8080

# Comando para iniciar
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 sistema_rural.wsgi:application
"@
    
    $dockerfileContent | Out-File -FilePath "Dockerfile.prod" -Encoding UTF8
    Write-Host "✅ Dockerfile.prod criado" -ForegroundColor Green
} else {
    Write-Host "✅ Dockerfile encontrado: $($dockerfile.Name)" -ForegroundColor Green
}
Write-Host ""

# 2. Fazer build da imagem
Write-Host "2️⃣ Fazendo build da imagem Docker..." -ForegroundColor Blue
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Yellow
Write-Host ""

$buildResult = gcloud builds submit --tag "$IMAGE_NAME:latest" --timeout=20m 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no build da imagem!" -ForegroundColor Red
    Write-Host $buildResult
    exit 1
}
Write-Host ""

# 3. Fazer deploy no Cloud Run
Write-Host "3️⃣ Fazendo deploy no Cloud Run..." -ForegroundColor Blue
$deployResult = gcloud run deploy $SERVICE_NAME `
    --image "$IMAGE_NAME:latest" `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD,DEBUG=False" `
    --add-cloudsql-instances=$CONNECTION_NAME `
    --memory=2Gi `
    --cpu=2 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1 `
    --port=8080 `
    --quiet 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    Write-Host $deployResult
    exit 1
}
Write-Host ""

# 4. Executar migrações
Write-Host "4️⃣ Executando migrações..." -ForegroundColor Blue

# Criar job de migração se não existir
$jobExists = gcloud run jobs describe migrate-monpec-complete --region=$REGION 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Criando job de migração..." -ForegroundColor Yellow
    gcloud run jobs create migrate-monpec-complete `
        --image "$IMAGE_NAME:latest" `
        --region=$REGION `
        --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" `
        --set-cloudsql-instances=$CONNECTION_NAME `
        --command="python" `
        --args="manage.py,migrate,--noinput" `
        --memory=2Gi `
        --cpu=1 `
        --max-retries=3 `
        --task-timeout=600 `
        --quiet 2>&1 | Out-Null
}

Write-Host "   Executando migrações..." -ForegroundColor Yellow
$migrateResult = gcloud run jobs execute migrate-monpec-complete --region=$REGION --wait 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migrações aplicadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Migrações podem ter falhado. Verifique os logs:" -ForegroundColor Yellow
    Write-Host "   gcloud run jobs executions list --job=migrate-monpec-complete --region=$REGION" -ForegroundColor Cyan
}
Write-Host ""

# 5. Obter URL do serviço
Write-Host "5️⃣ Verificando URL do serviço..." -ForegroundColor Blue
$serviceUrl = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1
if ($serviceUrl) {
    Write-Host "✅ Serviço disponível em: $serviceUrl" -ForegroundColor Green
} else {
    Write-Host "⚠️ Não foi possível obter a URL do serviço" -ForegroundColor Yellow
}
Write-Host ""

# 6. Testar serviço
Write-Host "6️⃣ Testando serviço..." -ForegroundColor Blue
if ($serviceUrl) {
    try {
        $response = Invoke-WebRequest -Uri $serviceUrl -Method Get -TimeoutSec 15 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Serviço está funcionando! Status: $($response.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Serviço retorna: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Não foi possível testar o serviço" -ForegroundColor Yellow
    }
}
Write-Host ""

# Resumo final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ ATUALIZAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Resumo:" -ForegroundColor Cyan
Write-Host "  • Imagem: $IMAGE_NAME:latest" -ForegroundColor White
Write-Host "  • Serviço: $SERVICE_NAME" -ForegroundColor White
Write-Host "  • Região: $REGION" -ForegroundColor White
if ($serviceUrl) {
    Write-Host "  • URL: $serviceUrl" -ForegroundColor White
}
Write-Host ""
Write-Host "🔗 Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Verifique os logs: gcloud run services logs read $SERVICE_NAME --region=$REGION" -ForegroundColor White
Write-Host "  2. Teste o sistema em: $serviceUrl" -ForegroundColor White
Write-Host "  3. Se necessário, execute migrações manualmente:" -ForegroundColor White
Write-Host "     gcloud run jobs execute migrate-monpec-complete --region=$REGION" -ForegroundColor White
Write-Host ""
