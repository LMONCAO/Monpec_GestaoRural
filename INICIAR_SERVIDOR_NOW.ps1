# Script para iniciar o servidor Django
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO SERVIDOR MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ir para o diretório do projeto
$projectPath = "C:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural"
Set-Location $projectPath
Write-Host "[INFO] Diretório: $projectPath" -ForegroundColor Yellow

# Parar processos Python existentes
Write-Host "[INFO] Parando processos Python existentes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verificar Python
Write-Host "[INFO] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Python não encontrado!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green

# Verificar configuração Django
Write-Host "[INFO] Verificando configuração Django..." -ForegroundColor Yellow
python manage.py check 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Erro na configuração Django!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] Configuração Django OK" -ForegroundColor Green

# Verificar porta 8000
Write-Host "[INFO] Verificando porta 8000..." -ForegroundColor Yellow
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[AVISO] Porta 8000 já está em uso!" -ForegroundColor Yellow
    Write-Host "[INFO] Tentando liberar porta..." -ForegroundColor Yellow
    $processId = $portInUse.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Iniciar servidor
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SERVIDOR INICIANDO..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[INFO] URL: http://localhost:8000/" -ForegroundColor Green
Write-Host "[INFO] Para parar: Ctrl+C ou feche esta janela" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor em nova janela
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; python manage.py runserver 0.0.0.0:8000"

# Aguardar e verificar
Start-Sleep -Seconds 5
$serverRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($serverRunning) {
    Write-Host "[OK] Servidor iniciado com sucesso!" -ForegroundColor Green
    Write-Host "[INFO] Acesse: http://localhost:8000/" -ForegroundColor Cyan
} else {
    Write-Host "[AVISO] Servidor pode não ter iniciado. Verifique a janela que abriu." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
























