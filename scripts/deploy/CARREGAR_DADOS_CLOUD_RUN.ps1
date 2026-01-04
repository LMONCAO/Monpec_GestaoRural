# Script PowerShell para carregar dados do banco no Google Cloud Run
# Execute no PowerShell com Google Cloud SDK instalado

param(
    [string]$Fonte = "sqlite",
    [string]$Caminho = "backup/db_backup.sqlite3",
    [int]$UsuarioId = 1,
    [switch]$Sobrescrever,
    [switch]$DryRun
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📊 CARREGAR DADOS DO BANCO - SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Configurações do projeto
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$DB_INSTANCE = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "L6171r12@@jjms"
$CLOUD_SQL_CONNECTION_NAME = "$PROJECT_ID`:$REGION`:$DB_INSTANCE"

# Detectar imagem
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

# Configurar projeto
Write-Host "📋 Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

Write-Host ""
Write-Host "📊 Parâmetros:" -ForegroundColor Yellow
Write-Host "   Fonte: $Fonte"
Write-Host "   Caminho: $Caminho"
Write-Host "   Usuário ID: $UsuarioId"
Write-Host "   Sobrescrever: $(if ($Sobrescrever) { 'Sim' } else { 'Não' })"
Write-Host "   Dry Run: $(if ($DryRun) { 'Sim' } else { 'Não' })"
Write-Host ""

# Construir comando
$COMANDO_ARGS = "carregar_dados_banco --fonte $Fonte"
if ($Caminho -and $Fonte -ne "sincronizar") {
    $COMANDO_ARGS += " --caminho `"$Caminho`""
}
if ($UsuarioId) {
    $COMANDO_ARGS += " --usuario-id $UsuarioId"
}
if ($Sobrescrever) {
    $COMANDO_ARGS += " --sobrescrever"
}
if ($DryRun) {
    $COMANDO_ARGS += " --dry-run"
}

Write-Host "🚀 Executando: python manage.py $COMANDO_ARGS" -ForegroundColor Green
Write-Host "⏱️  Este processo pode levar 2-5 minutos..." -ForegroundColor Yellow
Write-Host ""

# Deletar job anterior se existir
Write-Host "🧹 Limpando jobs anteriores..." -ForegroundColor Yellow
gcloud run jobs delete carregar-dados-banco --region=$REGION --quiet 2>$null

# Criar job
Write-Host "📦 Criando Cloud Run Job..." -ForegroundColor Yellow
$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Converter argumentos para formato do gcloud (separados por vírgula)
$argsArray = $COMANDO_ARGS -split ' ' | Where-Object { $_ -ne '' }
$cmdArgs = "manage.py," + ($argsArray -join ',')

Write-Host "📝 Comando: python $cmdArgs" -ForegroundColor Cyan

gcloud run jobs create carregar-dados-banco `
  --region=$REGION `
  --image="$IMAGE_NAME" `
  --set-env-vars=$envVars `
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME `
  --command="python" `
  --args=$cmdArgs `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --timeout=1800

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ ERRO: Não foi possível criar o job." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "   1. Verifique se a imagem existe:"
    Write-Host "      gcloud container images list --repository=gcr.io/$PROJECT_ID"
    Write-Host ""
    Write-Host "   2. Se a imagem tiver outro nome, altere a variável `$IMAGE_NAME no script"
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ Job criado! Executando..." -ForegroundColor Green
Write-Host "⏱️  Aguarde 2-5 minutos (o processo está rodando)..." -ForegroundColor Yellow
Write-Host ""

# Executar o job
gcloud run jobs execute carregar-dados-banco --region=$REGION --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "✅ SUCESSO! Dados carregados!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🧹 Deseja remover o job temporário? (opcional)" -ForegroundColor Yellow
    Write-Host "   Execute: gcloud run jobs delete carregar-dados-banco --region=$REGION"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ ERRO ao executar o job." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Verifique os logs:" -ForegroundColor Yellow
    Write-Host "   gcloud logging read `"resource.type=cloud_run_job AND resource.labels.job_name=carregar-dados-banco`" --limit=50"
    Write-Host ""
    exit 1
}


