# ========================================
# REMOVER SERVIDOR PERMANENTE MONPEC
# ========================================
# Este script remove a configuração de servidor permanente.
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REMOVER SERVIDOR PERMANENTE MONPEC" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está rodando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERRO] Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botão direito e selecione 'Executar como administrador'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

$taskName = "MONPEC_Servidor_Django"

Write-Host "[1/3] Parando tarefa agendada..." -ForegroundColor Yellow
try {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Write-Host "[OK] Tarefa parada" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Tarefa não estava rodando" -ForegroundColor Gray
}

Write-Host "[2/3] Parando processos do servidor na porta 8000..." -ForegroundColor Yellow
$processes = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
if ($processes) {
    foreach ($proc in $processes) {
        $pid = ($proc -split '\s+')[-1]
        if ($pid -and $pid -ne "0") {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "[OK] Processo $pid parado" -ForegroundColor Green
            } catch {
                Write-Host "[AVISO] Não foi possível parar processo $pid" -ForegroundColor Yellow
            }
        }
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "[INFO] Nenhum processo encontrado na porta 8000" -ForegroundColor Gray
}

Write-Host "[3/3] Removendo tarefa agendada..." -ForegroundColor Yellow
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop
    Write-Host "[OK] Tarefa agendada removida com sucesso!" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*não encontrada*" -or $_.Exception.Message -like "*not found*") {
        Write-Host "[INFO] Tarefa não encontrada (já foi removida)" -ForegroundColor Gray
    } else {
        Write-Host "[ERRO] Erro ao remover tarefa: $_" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SERVIDOR PERMANENTE REMOVIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "O servidor não iniciará mais automaticamente." -ForegroundColor Cyan
Write-Host "Para iniciar manualmente, use: INICIAR_SERVIDOR_WINDOWS.bat" -ForegroundColor Yellow
Write-Host ""
pause





