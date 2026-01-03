# ==========================================
# Script para Aplicar Migrações no PostgreSQL
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Aplicando Migrações no PostgreSQL" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env.local existe
if (-not (Test-Path ".env.local")) {
    Write-Host "❌ Arquivo .env.local não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute primeiro: .\configurar_postgresql_local.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "1. Verificando conexão com o banco de dados..." -ForegroundColor Yellow

# Tentar importar configurações do .env.local
try {
    # Carregar variáveis do .env.local
    Get-Content ".env.local" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and $value) {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    
    # Verificar se as variáveis foram carregadas
    $dbName = [Environment]::GetEnvironmentVariable("DB_NAME", "Process")
    if (-not $dbName) {
        Write-Host "❌ Variáveis de ambiente não carregadas corretamente!" -ForegroundColor Red
        Write-Host "   Verifique o arquivo .env.local" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Configurações carregadas do .env.local" -ForegroundColor Green
    Write-Host "   Banco: $dbName" -ForegroundColor White
} catch {
    Write-Host "❌ Erro ao carregar .env.local: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Verificando estado das migrações..." -ForegroundColor Yellow
python manage.py showmigrations --plan | Select-Object -First 20

Write-Host ""
Write-Host "3. Aplicando migrações..." -ForegroundColor Yellow
Write-Host ""

# Aplicar migrações
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migrações aplicadas com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "4. Verificando estado final..." -ForegroundColor Yellow
    python manage.py showmigrations | Select-String "\[ \]" | Select-Object -First 10
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Cyan
        Write-Host "✅ Processo concluído!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "❌ Erro ao aplicar migrações!" -ForegroundColor Red
    Write-Host "   Verifique os erros acima e corrija antes de continuar." -ForegroundColor Yellow
    exit 1
}

