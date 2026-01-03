# Script para configurar variáveis de ambiente no Cloud Run
# Edite as variáveis abaixo antes de executar

param(
    [string]$ServiceName = "monpec",
    [string]$Region = "us-central1",
    [string]$SecretKey = "",
    [string]$DbName = "monpec_db",
    [string]$DbUser = "monpec_user",
    [string]$DbPassword = "",
    [string]$CloudSqlConnection = ""
)

Write-Host "⚙️  Configurando variáveis de ambiente..." -ForegroundColor Cyan
Write-Host ""

if (-not $SecretKey) {
    Write-Host "❌ Erro: SECRET_KEY não fornecida!" -ForegroundColor Red
    Write-Host "   Edite este script e defina a variável `$SecretKey" -ForegroundColor Yellow
    exit 1
}

if (-not $DbPassword) {
    Write-Host "❌ Erro: DB_PASSWORD não fornecida!" -ForegroundColor Red
    Write-Host "   Edite este script e defina a variável `$DbPassword" -ForegroundColor Yellow
    exit 1
}

if (-not $CloudSqlConnection) {
    Write-Host "⚠️  Aviso: CLOUD_SQL_CONNECTION_NAME não definida" -ForegroundColor Yellow
    Write-Host "   Execute: gcloud sql instances describe INSTANCE_NAME --format=`"value(connectionName)`"" -ForegroundColor Gray
}

$envVars = @(
    "SECRET_KEY=$SecretKey",
    "DEBUG=False",
    "DB_NAME=$DbName",
    "DB_USER=$DbUser",
    "DB_PASSWORD=$DbPassword"
)

if ($CloudSqlConnection) {
    $envVars += "CLOUD_SQL_CONNECTION_NAME=$CloudSqlConnection"
}

$envVarsString = $envVars -join ","

Write-Host "📝 Variáveis a configurar:" -ForegroundColor Yellow
foreach ($var in $envVars) {
    $key = $var.Split('=')[0]
    $value = if ($key -eq "DB_PASSWORD" -or $key -eq "SECRET_KEY") { "***" } else { $var.Split('=')[1] }
    Write-Host "   $key = $value" -ForegroundColor Gray
}
Write-Host ""

$confirm = Read-Host "Deseja continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "❌ Operação cancelada" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔄 Atualizando serviço..." -ForegroundColor Yellow

$updateCmd = "gcloud run services update $ServiceName --region=$Region"
foreach ($var in $envVars) {
    $updateCmd += " --update-env-vars=`"$var`""
}

Invoke-Expression $updateCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Variáveis de ambiente configuradas com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro ao configurar variáveis!" -ForegroundColor Red
    exit 1
}
















