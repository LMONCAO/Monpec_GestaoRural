# Script PowerShell para carregar dados do banco de dados
# Uso: .\scripts\carregar_dados_banco.ps1 -Fonte sqlite -Caminho "db_backup.sqlite3"

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("sqlite", "postgresql", "json", "csv", "sincronizar")]
    [string]$Fonte,
    
    [string]$Caminho,
    [string]$Tabela,
    [int]$UsuarioId,
    [switch]$Sobrescrever,
    [switch]$DryRun,
    
    # Opções PostgreSQL
    [string]$Host = "localhost",
    [int]$Port = 5432,
    [string]$Database,
    [string]$User,
    [string]$Password
)

# Ativar ambiente virtual se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Ativando ambiente virtual..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
}

# Construir comando
$comando = "python manage.py carregar_dados_banco --fonte $Fonte"

if ($Caminho) {
    $comando += " --caminho `"$Caminho`""
}

if ($Tabela) {
    $comando += " --tabela $Tabela"
}

if ($UsuarioId) {
    $comando += " --usuario-id $UsuarioId"
}

if ($Sobrescrever) {
    $comando += " --sobrescrever"
}

if ($DryRun) {
    $comando += " --dry-run"
}

# Opções PostgreSQL
if ($Fonte -eq "postgresql") {
    $comando += " --host $Host --port $Port"
    if ($Database) { $comando += " --database $Database" }
    if ($User) { $comando += " --user $User" }
    if ($Password) { $comando += " --password $Password" }
}

Write-Host "🚀 Executando: $comando" -ForegroundColor Green
Write-Host ""

# Executar comando
Invoke-Expression $comando

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Processo concluído com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro durante a execução!" -ForegroundColor Red
    exit $LASTEXITCODE
}


