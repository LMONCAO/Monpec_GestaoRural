# ========================================
# VERIFICAR STATUS DO SERVIDOR MONPEC
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STATUS DO SERVIDOR MONPEC" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar porta 8000
Write-Host "[1/4] Verificando porta 8000..." -ForegroundColor Yellow
$porta = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
if ($porta) {
    Write-Host "[OK] Servidor está rodando na porta 8000" -ForegroundColor Green
    $porta
} else {
    Write-Host "[ERRO] Servidor NÃO está rodando na porta 8000" -ForegroundColor Red
}

# Verificar tarefa agendada
Write-Host ""
Write-Host "[2/4] Verificando tarefa agendada..." -ForegroundColor Yellow
$taskName = "MONPEC_Servidor_Django"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($task) {
    $taskState = (Get-ScheduledTaskInfo -TaskName $taskName).State
    Write-Host "[OK] Tarefa agendada encontrada" -ForegroundColor Green
    Write-Host "     Status: $taskState" -ForegroundColor Cyan
    
    if ($taskState -eq "Running") {
        Write-Host "     ✓ Servidor está rodando automaticamente" -ForegroundColor Green
    } elseif ($taskState -eq "Ready") {
        Write-Host "     ! Servidor configurado mas não está rodando" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Tarefa agendada não encontrada (servidor não está permanente)" -ForegroundColor Gray
}

# Verificar processos Python
Write-Host ""
Write-Host "[3/4] Verificando processos Python..." -ForegroundColor Yellow
$pythonProcs = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "[OK] Processos Python encontrados:" -ForegroundColor Green
    $pythonProcs | Format-Table Id, ProcessName, StartTime, @{Label="CPU"; Expression={$_.CPU}} -AutoSize
} else {
    Write-Host "[INFO] Nenhum processo Python encontrado" -ForegroundColor Gray
}

# Verificar logs
Write-Host ""
Write-Host "[4/4] Verificando logs..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logFile = Join-Path $scriptDir "django_server.log"
$errorLog = Join-Path $scriptDir "django_error.log"

if (Test-Path $logFile) {
    Write-Host "[OK] Log do servidor encontrado" -ForegroundColor Green
    Write-Host "     Últimas 5 linhas:" -ForegroundColor Cyan
    Get-Content $logFile -Tail 5 | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
} else {
    Write-Host "[INFO] Log do servidor não encontrado" -ForegroundColor Gray
}

if (Test-Path $errorLog) {
    $errorCount = (Get-Content $errorLog | Measure-Object -Line).Lines
    if ($errorCount -gt 0) {
        Write-Host ""
        Write-Host "[AVISO] Log de erros encontrado ($errorCount linhas)" -ForegroundColor Yellow
        Write-Host "     Últimas 5 linhas:" -ForegroundColor Cyan
        Get-Content $errorLog -Tail 5 | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Para mais detalhes:" -ForegroundColor Yellow
Write-Host "  - Logs: django_server.log" -ForegroundColor Cyan
Write-Host "  - Erros: django_error.log" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testar acesso: http://localhost:8000" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause






