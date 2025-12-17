# ========================================
# VERIFICAR E CORRIGIR SISTEMA MONPEC
# Garante que o sistema use o banco correto (Marcelo Sanguino / Fazenda Canta Galo)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO E CORRIGINDO SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Obter diretório do projeto
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "[INFO] Diretorio do projeto: $projectDir" -ForegroundColor Green
Write-Host ""

# 1. Verificar banco de dados
Write-Host "[1/5] Verificando banco de dados..." -ForegroundColor Yellow
$pythonCmd = if (Test-Path "$projectDir\python311\python.exe") { "$projectDir\python311\python.exe" } else { "python" }

Push-Location $projectDir
try {
    & $pythonCmd verificar_banco_canta_galo.py 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Banco de dados correto (Marcelo Sanguino / Fazenda Canta Galo)" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Banco de dados incorreto ou nao encontrado!" -ForegroundColor Red
        Write-Host "[INFO] O banco deve conter Marcelo Sanguino e Fazenda Canta Galo" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[AVISO] Nao foi possivel verificar o banco: $_" -ForegroundColor Yellow
}
Pop-Location
Write-Host ""

# 2. Verificar tarefa agendada
Write-Host "[2/5] Verificando tarefa agendada..." -ForegroundColor Yellow
$task = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "[INFO] Tarefa encontrada: $($task.TaskName)" -ForegroundColor Cyan
    Write-Host "  Estado: $($task.State)" -ForegroundColor Gray
    
    $action = $task.Actions[0]
    $taskFile = $action.Execute
    $taskDir = $action.WorkingDirectory
    
    Write-Host "  Arquivo executado: $taskFile" -ForegroundColor Gray
    Write-Host "  Diretorio: $taskDir" -ForegroundColor Gray
    
    # Verificar se está apontando para o diretório correto
    if ($taskDir -ne $projectDir) {
        Write-Host "[AVISO] Tarefa aponta para diretorio diferente!" -ForegroundColor Yellow
        Write-Host "  Esperado: $projectDir" -ForegroundColor Yellow
        Write-Host "  Atual: $taskDir" -ForegroundColor Yellow
        Write-Host "[INFO] Execute INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1 como Admin para corrigir" -ForegroundColor Cyan
    } else {
        Write-Host "[OK] Tarefa aponta para o diretorio correto" -ForegroundColor Green
    }
    
    # Verificar se o arquivo executado é o correto
    $correctBat = Join-Path $projectDir "INICIAR_SISTEMA_CORRETO.bat"
    if ($taskFile -notlike "*INICIAR_SISTEMA_CORRETO.bat*" -and $taskFile -notlike "*MONPEC DESENVOLVIMENTO.bat*") {
        Write-Host "[AVISO] Tarefa pode estar usando arquivo incorreto!" -ForegroundColor Yellow
        Write-Host "  Recomendado: INICIAR_SISTEMA_CORRETO.bat ou MONPEC DESENVOLVIMENTO.bat" -ForegroundColor Yellow
        Write-Host "[INFO] Execute INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1 como Admin para corrigir" -ForegroundColor Cyan
    } else {
        Write-Host "[OK] Tarefa usa arquivo correto" -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] Nenhuma tarefa agendada encontrada" -ForegroundColor Gray
}
Write-Host ""

# 3. Verificar processos Python rodando
Write-Host "[3/5] Verificando processos Python..." -ForegroundColor Yellow
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
if ($pythonProcesses) {
    Write-Host "[INFO] Processos Python encontrados: $($pythonProcesses.Count)" -ForegroundColor Cyan
    foreach ($proc in $pythonProcesses) {
        Write-Host "  PID $($proc.Id): $($proc.ProcessName) - $($proc.Path)" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] Nenhum processo Python rodando" -ForegroundColor Gray
}
Write-Host ""

# 4. Verificar porta 8000
Write-Host "[4/5] Verificando porta 8000..." -ForegroundColor Yellow
$porta = netstat -ano | Select-String ":8000"
if ($porta) {
    Write-Host "[INFO] Porta 8000 em uso:" -ForegroundColor Cyan
    $porta | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "[INFO] Porta 8000 nao esta em uso" -ForegroundColor Gray
}
Write-Host ""

# 5. Resumo e recomendações
Write-Host "[5/5] Resumo e recomendacoes..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para garantir que o sistema use o banco correto:" -ForegroundColor White
Write-Host "  1. Use sempre: INICIAR_SISTEMA_CORRETO.bat" -ForegroundColor Gray
Write-Host "  2. Ou use: MONPEC DESENVOLVIMENTO.bat (agora verifica o banco)" -ForegroundColor Gray
Write-Host "  3. Para servidor permanente, execute como Admin:" -ForegroundColor Gray
Write-Host "     INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Banco de dados correto:" -ForegroundColor White
Write-Host "  - Produtor: Marcelo Sanguino" -ForegroundColor Gray
Write-Host "  - Fazenda: Fazenda Canta Galo" -ForegroundColor Gray
Write-Host "  - Arquivo: db.sqlite3 (neste diretorio)" -ForegroundColor Gray
Write-Host ""

pause













