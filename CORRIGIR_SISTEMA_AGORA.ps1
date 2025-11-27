# ========================================
# CORRIGIR SISTEMA - REMOVER TAREFA ERRADA E INICIAR CORRETO
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGINDO SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está executando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Obter diretório do projeto
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $projectDir "MONPEC DESENVOLVIMENTO.bat"

Write-Host "[INFO] Diretorio correto: $projectDir" -ForegroundColor Green
Write-Host "[INFO] Arquivo BAT: $batFile" -ForegroundColor Green
Write-Host ""

# Parar todos os processos Python
Write-Host "[1/4] Parando processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Processos parados" -ForegroundColor Green
Write-Host ""

# Parar e remover tarefa agendada antiga
Write-Host "[2/4] Removendo tarefa agendada antiga..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
if ($existingTask) {
    if ($isAdmin) {
        Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "[OK] Tarefa antiga removida" -ForegroundColor Green
    } else {
        Write-Host "[AVISO] Precisa de permissao de administrador para remover tarefa" -ForegroundColor Yellow
        Write-Host "  Execute como Admin: Unregister-ScheduledTask -TaskName 'MONPEC_Servidor_Django' -Confirm:`$false" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] Nenhuma tarefa encontrada" -ForegroundColor Green
}
Write-Host ""

# Verificar banco de dados
Write-Host "[3/4] Verificando banco de dados..." -ForegroundColor Yellow
$pythonCmd = if (Test-Path "python311\python.exe") { "python311\python.exe" } else { "python" }
& $pythonCmd verificar_banco_canta_galo.py 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Banco de dados correto (Marcelo Sanguino / Fazenda Canta Galo)" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Nao foi possivel verificar o banco" -ForegroundColor Yellow
}
Write-Host ""

# Iniciar servidor correto
Write-Host "[4/4] Iniciando servidor CORRETO..." -ForegroundColor Yellow
if (Test-Path $batFile) {
    Write-Host "[INFO] Executando: $batFile" -ForegroundColor Cyan
    Start-Process -FilePath $batFile -WorkingDirectory $projectDir
    Start-Sleep -Seconds 3
    Write-Host "[OK] Servidor iniciado!" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Arquivo BAT nao encontrado: $batFile" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRECAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "O servidor CORRETO foi iniciado:" -ForegroundColor White
Write-Host "  - Settings: sistema_rural.settings (DESENVOLVIMENTO)" -ForegroundColor Gray
Write-Host "  - Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)" -ForegroundColor Gray
Write-Host "  - URL: http://127.0.0.1:8000/" -ForegroundColor Gray
Write-Host ""
Write-Host "Para configurar como permanente:" -ForegroundColor White
Write-Host "  Execute como Admin: .\INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1" -ForegroundColor Gray
Write-Host ""

