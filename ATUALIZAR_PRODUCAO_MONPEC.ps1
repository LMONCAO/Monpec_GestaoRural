# SCRIPT DE ATUALIZACAO PARA PRODUCAO - MONPEC.COM.BR
# Atualiza o sistema Monpec para producao no dominio monpec.com.br
# Servidor: Google Cloud Run

param(
    [string]$Projeto = "monpec-sistema-rural",
    [string]$Regiao = "us-central1",
    [string]$Servico = "monpec",
    [string]$Dominio = "monpec.com.br",
    [switch]$ConfigurarDominio = $false,
    [switch]$ApenasBuild = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ATUALIZACAO PARA PRODUCAO" -ForegroundColor Cyan
Write-Host "   MONPEC.COM.BR - GOOGLE CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Funções auxiliares
function Write-Success { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Error { Write-Host "[ERRO] $args" -ForegroundColor Red }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Yellow }
function Write-Step { Write-Host "[*] $args" -ForegroundColor Blue }

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Error "Arquivo manage.py não encontrado!"
    Write-Info "Execute este script na raiz do projeto Django."
    exit 1
}

# Verificar se gcloud está instalado
$gcloudAvailable = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudAvailable) {
    Write-Error "gcloud CLI não encontrado!"
    Write-Info "Instale o Google Cloud SDK:"
    Write-Host "  https://cloud.google.com/sdk/docs/install" -ForegroundColor Gray
    Write-Host "  Ou: choco install gcloudsdk" -ForegroundColor Gray
    exit 1
}

Write-Step "Configurações:"
Write-Host "  Projeto: $Projeto" -ForegroundColor Gray
Write-Host "  Região: $Regiao" -ForegroundColor Gray
Write-Host "  Serviço: $Servico" -ForegroundColor Gray
Write-Host "  Domínio: $Dominio" -ForegroundColor Gray
Write-Host ""

# Verificar autenticação
Write-Step "Verificando autenticação no Google Cloud..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Info "Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
}
Write-Success "Autenticado como: $authCheck"

# Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $Projeto
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado!"

# Habilitar APIs necessárias
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "  Habilitando $api..."
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas!"

# Verificar arquivos necessários
Write-Step "Verificando arquivos necessários..."
$arquivosNecessarios = @("Dockerfile", "requirements_producao.txt", "sistema_rural/settings_gcp.py")
$arquivosFaltando = @()

foreach ($arquivo in $arquivosNecessarios) {
    if (-not (Test-Path $arquivo)) {
        $arquivosFaltando += $arquivo
    }
}

if ($arquivosFaltando.Count -gt 0) {
    Write-Error "Arquivos faltando:"
    foreach ($arquivo in $arquivosFaltando) {
        Write-Host "  - $arquivo" -ForegroundColor Red
    }
    exit 1
}
Write-Success "Todos os arquivos necessários encontrados!"

# Verificar se o domínio está configurado no settings_gcp.py
Write-Step "Verificando configuração do domínio no código..."
$settingsContent = Get-Content "sistema_rural/settings_gcp.py" -Raw
if ($settingsContent -notmatch "monpec\.com\.br") {
    Write-Error "Domínio monpec.com.br não encontrado em settings_gcp.py!"
    Write-Info "Verifique se o domínio está configurado em ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS"
    exit 1
}
Write-Success "Domínio configurado no código!"

# Build da imagem Docker
Write-Step "Fazendo build da imagem Docker..."
Write-Info "Isso pode levar 10-15 minutos..."
$imageTag = "gcr.io/$Projeto/$Servico"
gcloud builds submit --tag $imageTag
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build!"
    Write-Info "Verifique os logs acima para mais detalhes."
    exit 1
}
Write-Success "Build concluído!"

if ($ApenasBuild) {
    Write-Host ""
    Write-Success "Build concluido! Imagem: $imageTag"
    Write-Host ""
    Write-Info "Para fazer deploy, execute:"
    Write-Host "  .\ATUALIZAR_PRODUCAO_MONPEC.ps1 -ConfigurarDominio" -ForegroundColor Gray
    exit 0
}

# Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
Write-Info "Isso pode levar 2-3 minutos..."
gcloud run deploy $Servico `
    --image $imageTag `
    --platform managed `
    --region $Regiao `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --memory=512Mi `
    --cpu=1 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy!"
    Write-Info "Verifique os logs acima para mais detalhes."
    exit 1
}
Write-Success "Deploy concluído!"

# Obter URL do serviço
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $Servico --region $Regiao --format 'value(status.url)'
if (-not $serviceUrl) {
    Write-Error "Não foi possível obter URL do serviço!"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[OK] DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do servico Cloud Run:" -ForegroundColor Cyan
Write-Host "   $serviceUrl" -ForegroundColor White
Write-Host ""

# Verificar e configurar domínio
Write-Step "Verificando configuração do domínio $Dominio..."
$domainMapping = gcloud run domain-mappings describe $Dominio --region $Regiao 2>&1
if ($LASTEXITCODE -ne 0 -or $ConfigurarDominio) {
    if ($ConfigurarDominio -or ($LASTEXITCODE -ne 0)) {
        Write-Info "Configurando mapeamento do domínio $Dominio..."
        gcloud run domain-mappings create `
            --service $Servico `
            --domain $Dominio `
            --region $Regiao
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Mapeamento do domínio criado!"
            Write-Host ""
            Write-Info "PROXIMOS PASSOS IMPORTANTES:" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "1. Anote os registros DNS que apareceram acima" -ForegroundColor White
            Write-Host "2. Acesse o painel do seu provedor de dominio (Registro.br, etc.)" -ForegroundColor White
            Write-Host "3. Adicione os registros DNS fornecidos pelo Google Cloud" -ForegroundColor White
            Write-Host "4. Aguarde a propagacao DNS (15 minutos - 2 horas)" -ForegroundColor White
            Write-Host ""
            Write-Info "Para ver os registros DNS novamente:"
            Write-Host "  gcloud run domain-mappings describe $Dominio --region $Regiao" -ForegroundColor Gray
        } else {
            Write-Error "Erro ao criar mapeamento do domínio!"
            Write-Info "Verifique se o domínio já não está mapeado ou há problemas de permissão."
        }
    } else {
        Write-Info "Domínio não está mapeado."
        Write-Info "Para mapear o domínio, execute:"
        Write-Host "  .\ATUALIZAR_PRODUCAO_MONPEC.ps1 -ConfigurarDominio" -ForegroundColor Gray
    }
} else {
    Write-Success "Domínio $Dominio já está mapeado!"
    Write-Host ""
    Write-Host "Acesse: https://$Dominio" -ForegroundColor Green
}

# Verificar também www
Write-Step "Verificando configuração do domínio www.$Dominio..."
$wwwDomain = "www.$Dominio"
$wwwMapping = gcloud run domain-mappings describe $wwwDomain --region $Regiao 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Info "Domínio www.$Dominio não está mapeado (opcional)."
} else {
    Write-Success "Domínio www.$Dominio também está mapeado!"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMANDOS UTEIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ver logs:" -ForegroundColor Yellow
Write-Host "  gcloud run services logs read $Servico --region $Regiao --limit 50" -ForegroundColor Gray
Write-Host ""
Write-Host "Ver status:" -ForegroundColor Yellow
Write-Host "  gcloud run services describe $Servico --region $Regiao" -ForegroundColor Gray
Write-Host ""
Write-Host "Ver domínios mapeados:" -ForegroundColor Yellow
Write-Host "  gcloud run domain-mappings list --region $Regiao" -ForegroundColor Gray
Write-Host ""
Write-Host "Abrir no navegador:" -ForegroundColor Yellow
Write-Host "  start $serviceUrl" -ForegroundColor Gray
if ($domainMapping -and $LASTEXITCODE -eq 0) {
    Write-Host "  start https://$Dominio" -ForegroundColor Gray
}
Write-Host ""

Write-Success "ATUALIZACAO PARA PRODUCAO CONCLUIDA!"
Write-Host ""
