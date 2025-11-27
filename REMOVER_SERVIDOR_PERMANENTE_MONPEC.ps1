# ========================================
# REMOVER SERVIDOR PERMANENTE MONPEC
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REMOVER SERVIDOR PERMANENTE MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está executando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERRO] Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito e selecione 'Executar como administrador'" -ForegroundColor Yellow
    pause
    exit
}

# Parar tarefa se estiver rodando
$task = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "[INFO] Parando tarefa agendada..." -ForegroundColor Yellow
    Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
    Write-Host "[OK] Tarefa parada" -ForegroundColor Green
    
    Write-Host "[INFO] Removendo tarefa agendada..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false
    Write-Host "[OK] Tarefa removida" -ForegroundColor Green
} else {
    Write-Host "[INFO] Tarefa agendada nao encontrada" -ForegroundColor Yellow
}

# Parar processos Python
Write-Host "[INFO] Parando processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Processos parados" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REMOCAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "O servidor permanente foi removido com sucesso." -ForegroundColor White
Write-Host ""

pause



