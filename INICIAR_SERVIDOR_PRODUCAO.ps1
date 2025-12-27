# ==========================================
# INICIAR SERVIDOR EM PRODUÇÃO
# Sistema MONPEC - Gestão Rural
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO SERVIDOR MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mudar para o diretório do projeto
Set-Location $PSScriptRoot

# Parar processos Python existentes
Write-Host "[INFO] Parando processos Python existentes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*$PSScriptRoot*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verificar Python
$pythonCmd = "python"
if (Test-Path "python311\python.exe") {
    $pythonCmd = "python311\python.exe"
}

# Carregar variáveis de ambiente
if (Test-Path ".env_producao") {
    Get-Content ".env_producao" | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Configurar variáveis mínimas
if (-not $env:SECRET_KEY) {
    $env:SECRET_KEY = "YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
}

$env:DEBUG = "False"
$env:DJANGO_SETTINGS_MODULE = "sistema_rural.settings_producao"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SERVIDOR INICIANDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[IMPORTANTE] Para acessar o sistema:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   URL DO LOGIN:" -ForegroundColor White
Write-Host "   http://localhost:8000/login/" -ForegroundColor Green
Write-Host ""
Write-Host "   OU se estiver em produção:" -ForegroundColor White
Write-Host "   https://monpec.com.br/login/" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
& $pythonCmd manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao









