# Script de Deploy Completo - MONPEC para Google Cloud Run
# Este script faz: build, deploy, migrações e criação de usuário admin
# Uso: .\DEPLOY_COMPLETO.ps1 [PROJECT_ID] [REGION]

param(
    [string]$ProjectId = "monpec-sistema-rural",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

$ServiceName = "monpec"
$ImageName = "gcr.io/$ProjectId/$ServiceName"
$AdminPassword = "L6171r12@@"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "  Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Host "❌ Google Cloud SDK não está instalado" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Google Cloud SDK encontrado" -ForegroundColor Green
Write-Host ""

# Verificar login
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $activeAccount -or $activeAccount -match "Listed 0 items") {
    Write-Host "⚠️  Nenhuma conta ativa encontrada. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}

# Definir projeto
Write-Host "Configurando projeto: $ProjectId" -ForegroundColor Yellow
gcloud config set project $ProjectId

# Habilitar APIs necessárias
Write-Host ""
Write-Host "Habilitando APIs necessárias..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Build da imagem
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 1: BUILD DA IMAGEM DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔨 Construindo imagem Docker..." -ForegroundColor Yellow
Write-Host "(Isso pode levar alguns minutos...)" -ForegroundColor Gray
Write-Host ""

gcloud builds submit --tag $ImageName --timeout=30m

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao construir imagem Docker" -ForegroundColor Red
    Write-Host "Verifique se o Dockerfile existe no diretório atual" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Imagem construída com sucesso!" -ForegroundColor Green
Write-Host ""

# Deploy no Cloud Run
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 2: DEPLOY NO CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
Write-Host ""

# Verificar se o serviço já existe para decidir entre create ou update
$existingService = gcloud run services describe $ServiceName --region $Region --format="value(metadata.name)" 2>&1

if ($existingService -and $existingService -ne "") {
    Write-Host "Serviço existente encontrado. Atualizando..." -ForegroundColor Gray
    $deployCommand = "update"
} else {
    Write-Host "Criando novo serviço..." -ForegroundColor Gray
    $deployCommand = "deploy"
}

gcloud run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao fazer deploy" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter URL do serviço
$ServiceUrl = gcloud run services describe $ServiceName --region $Region --format="value(status.url)" 2>&1
Write-Host "URL do serviço: $ServiceUrl" -ForegroundColor Cyan
Write-Host ""

# Executar migrações
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 3: EXECUTAR MIGRAÇÕES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔄 Executando migrações do banco de dados..." -ForegroundColor Yellow
Write-Host ""

# Criar job de migração se não existir
$migrateJobExists = gcloud run jobs describe monpec-migrate --region $Region --format="value(metadata.name)" 2>&1

if (-not $migrateJobExists -or $migrateJobExists -match "ERROR") {
    Write-Host "Criando job de migração..." -ForegroundColor Gray
    gcloud run jobs create monpec-migrate `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args manage.py,migrate `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
}

# Executar migração
Write-Host "Executando migrações..." -ForegroundColor Yellow
gcloud run jobs execute monpec-migrate --region $Region --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Aviso: Erro ao executar migrações" -ForegroundColor Yellow
    Write-Host "Você pode executar manualmente depois" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✅ Migrações executadas com sucesso!" -ForegroundColor Green
}
Write-Host ""

# Criar usuário admin
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 4: CRIAR USUÁRIO ADMIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Criando usuário administrador..." -ForegroundColor Yellow
Write-Host ""

# Criar job de criação de admin se não existir
$adminJobExists = gcloud run jobs describe monpec-create-admin --region $Region --format="value(metadata.name)" 2>&1

if (-not $adminJobExists -or $adminJobExists -match "ERROR") {
    Write-Host "Criando job de criação de admin..." -ForegroundColor Gray
    gcloud run jobs create monpec-create-admin `
        --image $ImageName `
        --region $Region `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
        --command python `
        --args criar_admin.py `
        --max-retries 1 `
        --task-timeout 300 `
        --quiet
}

# Executar criação de admin
Write-Host "Executando criação do usuário admin..." -ForegroundColor Yellow
gcloud run jobs execute monpec-create-admin --region $Region --wait

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Aviso: Erro ao criar usuário admin" -ForegroundColor Yellow
    Write-Host "Você pode executar manualmente depois" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✅ Usuário admin criado com sucesso!" -ForegroundColor Green
}
Write-Host ""

# Resumo final
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY COMPLETO CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 INFORMAÇÕES DE ACESSO:" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL do Sistema: $ServiceUrl" -ForegroundColor White
Write-Host ""
Write-Host "Credenciais de Acesso:" -ForegroundColor Yellow
Write-Host "  Usuário: admin" -ForegroundColor White
Write-Host "  Senha: $AdminPassword" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ⚠️  PRÓXIMOS PASSOS (OPCIONAL)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configurar variáveis de ambiente adicionais:" -ForegroundColor Gray
Write-Host "   gcloud run services update $ServiceName --region $Region --update-env-vars `"SECRET_KEY=sua-chave-secreta`"" -ForegroundColor DarkGray
Write-Host ""
Write-Host "2. Conectar ao Cloud SQL (se usar banco de dados):" -ForegroundColor Gray
Write-Host "   gcloud run services update $ServiceName --region $Region --add-cloudsql-instances $ProjectId`:$Region`:monpec-db" -ForegroundColor DarkGray
Write-Host ""
Write-Host "3. Configurar domínio personalizado:" -ForegroundColor Gray
Write-Host "   gcloud run domain-mappings create --service $ServiceName --domain monpec.com.br --region $Region" -ForegroundColor DarkGray
Write-Host ""
Write-Host "4. Ver logs do serviço:" -ForegroundColor Gray
Write-Host "   gcloud run services logs read $ServiceName --region $Region --follow" -ForegroundColor DarkGray
Write-Host ""
















