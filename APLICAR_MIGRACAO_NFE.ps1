# Script para aplicar migração de NF-e (adicionar campo cliente)
# Execute este script para aplicar a migração 0070

Write-Host "🔄 Aplicando Migração de NF-e" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script na raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    exit 1
}

# Ativar ambiente virtual se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path "env\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\env\Scripts\Activate.ps1
}

# Verificar se a migração existe
$migrationFile = "gestao_rural\migrations\0070_adicionar_cliente_nota_fiscal.py"
if (-not (Test-Path $migrationFile)) {
    Write-Host "AVISO: Arquivo de migração não encontrado: $migrationFile" -ForegroundColor Yellow
    Write-Host "Criando migração..." -ForegroundColor Cyan
    python manage.py makemigrations gestao_rural
}

# Executar migração específica
Write-Host "`n[1/2] Aplicando migração 0070..." -ForegroundColor Cyan
python manage.py migrate gestao_rural 0070_adicionar_cliente_nota_fiscal

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tentando aplicar todas as migrações pendentes..." -ForegroundColor Yellow
    python manage.py migrate gestao_rural
}

# Verificar se a migração foi aplicada
Write-Host "`n[2/2] Verificando migração..." -ForegroundColor Cyan
python manage.py showmigrations gestao_rural | Select-String "0070"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Migração aplicada com sucesso!" -ForegroundColor Green
    Write-Host "O campo 'cliente' foi adicionado à tabela NotaFiscal." -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Verifique se a migração foi aplicada corretamente." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Para verificar todas as migrações, execute:" -ForegroundColor Cyan
Write-Host "python manage.py showmigrations gestao_rural" -ForegroundColor White
Write-Host ""

