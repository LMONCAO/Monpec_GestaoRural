# Script completo: Deploy + Configuração + Migrações
# Execute este script para fazer tudo de uma vez

Write-Host "🚀 ==========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY COMPLETO AUTOMÁTICO" -ForegroundColor Cyan
Write-Host "   MonPEC - Google Cloud Run" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "❌ Erro: gcloud CLI não está instalado!" -ForegroundColor Red
    Write-Host "   Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authStatus) {
    Write-Host "❌ Você não está autenticado!" -ForegroundColor Red
    Write-Host "   Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Autenticado como: $authStatus" -ForegroundColor Green
Write-Host ""

# Obter projeto
$projectId = gcloud config get-value project 2>$null
if (-not $projectId) {
    Write-Host "❌ Nenhum projeto configurado!" -ForegroundColor Red
    $projectId = Read-Host "Digite o ID do projeto Google Cloud"
    gcloud config set project $projectId
}
Write-Host "✅ Projeto: $projectId" -ForegroundColor Green
Write-Host ""

# Perguntar sobre variáveis de ambiente
Write-Host "⚙️  CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE" -ForegroundColor Cyan
Write-Host "   Você precisa fornecer algumas informações:" -ForegroundColor Yellow
Write-Host ""

$secretKey = Read-Host "Digite a SECRET_KEY do Django (ou pressione Enter para pular)"
$dbPassword = Read-Host "Digite a senha do banco de dados (ou pressione Enter para pular)"
$cloudSqlConnection = Read-Host "Digite o CLOUD_SQL_CONNECTION_NAME (ou pressione Enter para pular)"

Write-Host ""
Write-Host "📦 PASSO 1: Fazendo build e deploy..." -ForegroundColor Cyan
Write-Host ""

# Executar deploy
& .\DEPLOY_AGORA.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

# Configurar variáveis se fornecidas
if ($secretKey -or $dbPassword -or $cloudSqlConnection) {
    Write-Host ""
    Write-Host "⚙️  PASSO 2: Configurando variáveis de ambiente..." -ForegroundColor Cyan
    Write-Host ""
    
    $updateCmd = "gcloud run services update monpec --region us-central1"
    
    if ($secretKey) {
        $updateCmd += " --update-env-vars=`"SECRET_KEY=$secretKey`""
    }
    if ($dbPassword) {
        $updateCmd += " --update-env-vars=`"DB_PASSWORD=$dbPassword`""
    }
    if ($cloudSqlConnection) {
        $updateCmd += " --update-env-vars=`"CLOUD_SQL_CONNECTION_NAME=$cloudSqlConnection`""
    }
    
    $updateCmd += " --update-env-vars=`"DEBUG=False`""
    $updateCmd += " --update-env-vars=`"DB_NAME=monpec_db`""
    $updateCmd += " --update-env-vars=`"DB_USER=monpec_user`""
    
    Invoke-Expression $updateCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Variáveis configuradas" -ForegroundColor Green
    }
}

# Aplicar migrações
Write-Host ""
Write-Host "📝 PASSO 3: Aplicando migrações..." -ForegroundColor Cyan
Write-Host ""

$applyMigrations = Read-Host "Deseja aplicar migrações agora? (S/N)"
if ($applyMigrations -eq "S" -or $applyMigrations -eq "s") {
    & .\APLICAR_MIGRACOES.ps1
}

# Criar superusuário
Write-Host ""
Write-Host "👤 PASSO 4: Criar superusuário..." -ForegroundColor Cyan
Write-Host ""

$createSuperuser = Read-Host "Deseja criar um superusuário agora? (S/N)"
if ($createSuperuser -eq "S" -or $createSuperuser -eq "s") {
    & .\CRIAR_SUPERUSUARIO.ps1
}

# Obter URL final
$serviceUrl = gcloud run services describe monpec --region us-central1 --format="value(status.url)" 2>$null

Write-Host ""
Write-Host "✅ ==========================================" -ForegroundColor Green
Write-Host "   DEPLOY COMPLETO!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Configure todas as variáveis de ambiente necessárias" -ForegroundColor Gray
Write-Host "   2. Verifique os logs: gcloud run services logs read monpec --region us-central1" -ForegroundColor Gray
Write-Host "   3. Acesse: $serviceUrl" -ForegroundColor Gray
Write-Host ""
















