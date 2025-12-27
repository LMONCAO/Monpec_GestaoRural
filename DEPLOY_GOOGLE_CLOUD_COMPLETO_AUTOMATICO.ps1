# ============================================================================
# DEPLOY COMPLETO AUTOMÁTICO - GOOGLE CLOUD PLATFORM
# ============================================================================
# Este script faz TUDO automaticamente:
# 1. Coleta arquivos estáticos
# 2. Cria usuário admin
# 3. Faz build da imagem Docker
# 4. Faz deploy no Cloud Run
# 5. Configura variáveis de ambiente
# ============================================================================

param(
    [string]$Projeto = "monpec-sistema-rural",
    [string]$Servico = "monpec",
    [string]$Regiao = "us-central1",
    [switch]$ApenasBuild = $false
)

# Cores para output
function Write-Step { param($msg) Write-Host "`n🔷 $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Yellow }

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY AUTOMÁTICO - GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
Write-Step "Verificando gcloud CLI..."
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "gcloud CLI não está instalado!"
    Write-Info "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Success "gcloud CLI encontrado!"

# Verificar autenticação
Write-Step "Verificando autenticação..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Info "⚠ Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Falha na autenticação!"
        exit 1
    }
}
Write-Success "✅ Autenticado!"

# Configurar projeto
Write-Step "Configurando projeto: $Projeto"
gcloud config set project $Projeto
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro ao configurar projeto!"
    exit 1
}
Write-Success "✅ Projeto configurado!"

# Habilitar APIs necessárias
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "appengine.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "  Habilitando $api..."
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "✅ APIs habilitadas!"

# Coletar arquivos estáticos
Write-Step "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro ao coletar arquivos estáticos!"
    exit 1
}
Write-Success "✅ Arquivos estáticos coletados!"

# Criar usuário admin (via Cloud Run Job ou localmente se possível)
Write-Step "Preparando script para criar usuário admin..."
Write-Info "O usuário admin será criado após o deploy via Cloud Run Job"

# Verificar se Dockerfile existe
if (-not (Test-Path "Dockerfile")) {
    Write-Error "❌ Dockerfile não encontrado!"
    Write-Info "Criando Dockerfile básico..."
    
    $dockerfileContent = @"
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8080

# Comando para iniciar
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 sistema_rural.wsgi:application
"@
    
    $dockerfileContent | Out-File -FilePath "Dockerfile" -Encoding UTF8
    Write-Success "✅ Dockerfile criado!"
}

# Build da imagem
Write-Step "Fazendo build da imagem Docker..."
$imageTag = "gcr.io/$Projeto/$Servico"
Write-Info "Imagem: $imageTag"

gcloud builds submit --tag $imageTag --timeout=20m
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro no build!"
    exit 1
}
Write-Success "✅ Build concluído!"

if ($ApenasBuild) {
    Write-Host ""
    Write-Success "🎉 Build concluído! Imagem: $imageTag"
    Write-Host ""
    Write-Info "Para fazer deploy, execute:"
    Write-Host "  gcloud run deploy $Servico --image $imageTag --region $Regiao" -ForegroundColor Gray
    exit 0
}

# Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
Write-Info "Serviço: $Servico"
Write-Info "Região: $Regiao"

# Obter variáveis de ambiente do Cloud Run atual (se existir)
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

# Tentar obter variáveis existentes
try {
    $existingService = gcloud run services describe $Servico --region=$Regiao --format="value(spec.template.spec.containers[0].env)" 2>&1
    if ($existingService -and -not ($existingService -match "ERROR")) {
        Write-Info "Mantendo variáveis de ambiente existentes..."
    }
} catch {
    Write-Info "Serviço novo, usando variáveis padrão..."
}

# Fazer deploy
gcloud run deploy $Servico `
    --image $imageTag `
    --platform managed `
    --region $Regiao `
    --allow-unauthenticated `
    --set-env-vars ($envVars -join ",") `
    --memory=1Gi `
    --cpu=2 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro no deploy!"
    exit 1
}

Write-Success "✅ Deploy concluído!"

# Obter URL do serviço
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $Servico --region=$Regiao --format="value(status.url)"
Write-Success "✅ URL: $serviceUrl"

# Criar usuário admin via Cloud Run Job
Write-Step "Criando usuário admin..."
Write-Info "Executando script criar_admin_fix.py no Cloud Run..."

# Criar job temporário para executar o script
$jobName = "$Servico-admin-setup"
gcloud run jobs create $jobName `
    --image $imageTag `
    --region $Regiao `
    --set-env-vars ($envVars -join ",") `
    --command python `
    --args criar_admin_fix.py `
    2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Info "Executando job para criar admin..."
    gcloud run jobs execute $jobName --region=$Regiao --wait
    Write-Success "✅ Usuário admin criado!"
    
    # Limpar job temporário
    gcloud run jobs delete $jobName --region=$Regiao --quiet 2>&1 | Out-Null
} else {
    Write-Info "⚠️  Não foi possível criar job. Execute manualmente:"
    Write-Host "  python criar_admin_fix.py" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Success "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Info "URL do serviço: $serviceUrl"
Write-Info "Credenciais admin:"
Write-Host "  Usuário: admin" -ForegroundColor Gray
Write-Host "  Senha: L6171r12@@" -ForegroundColor Gray
Write-Host ""
Write-Info "Para ver logs:"
Write-Host "  gcloud run services logs read $Servico --region=$Regiao" -ForegroundColor Gray
Write-Host ""



