# ========================================
# CORRIGIR TAREFA AGENDADA - SISTEMA CORRETO
# Remove a tarefa que aponta para o diretório errado e cria uma nova
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGINDO TAREFA AGENDADA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está executando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERRO] Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "Clique com botao direito e selecione 'Executar como administrador'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ou execute manualmente no PowerShell como Admin:" -ForegroundColor Yellow
    Write-Host "  schtasks /Delete /TN `"MONPEC_Servidor_Django`" /F" -ForegroundColor Gray
    pause
    exit
}

# Obter diretório do projeto (diretório correto)
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $projectDir "INICIAR_SISTEMA_CORRETO.bat"

Write-Host "[INFO] Diretorio CORRETO: $projectDir" -ForegroundColor Green
Write-Host "[INFO] Arquivo BAT correto: $batFile" -ForegroundColor Green
Write-Host ""

# Verificar se o arquivo existe
if (-not (Test-Path $batFile)) {
    # Tentar arquivo alternativo
    $batFileAlt = Join-Path $projectDir "MONPEC DESENVOLVIMENTO.bat"
    if (Test-Path $batFileAlt) {
        $batFile = $batFileAlt
        Write-Host "[INFO] Usando arquivo alternativo: MONPEC DESENVOLVIMENTO.bat" -ForegroundColor Yellow
    } else {
        Write-Host "[ERRO] Arquivo 'INICIAR_SISTEMA_CORRETO.bat' ou 'MONPEC DESENVOLVIMENTO.bat' nao encontrado!" -ForegroundColor Red
        pause
        exit
    }
}

# 1. Parar processos Python
Write-Host "[1/5] Parando processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Processos parados" -ForegroundColor Green
Write-Host ""

# 2. Parar e remover tarefa antiga
Write-Host "[2/5] Removendo tarefa agendada antiga (diretorio errado)..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
if ($existingTask) {
    try {
        Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Disable-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false -ErrorAction Stop
        Write-Host "[OK] Tarefa antiga removida" -ForegroundColor Green
    } catch {
        Write-Host "[AVISO] Erro ao remover tarefa: $_" -ForegroundColor Yellow
        Write-Host "[INFO] Tentando via schtasks..." -ForegroundColor Yellow
        schtasks /Delete /TN "MONPEC_Servidor_Django" /F 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Tarefa removida via schtasks" -ForegroundColor Green
        } else {
            Write-Host "[ERRO] Nao foi possivel remover a tarefa automaticamente" -ForegroundColor Red
            Write-Host "[INFO] Execute manualmente: schtasks /Delete /TN `"MONPEC_Servidor_Django`" /F" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "[INFO] Nenhuma tarefa encontrada" -ForegroundColor Gray
}
Write-Host ""

# 3. Verificar banco de dados
Write-Host "[3/5] Verificando banco de dados..." -ForegroundColor Yellow
$pythonCmd = if (Test-Path "$projectDir\python311\python.exe") { "$projectDir\python311\python.exe" } else { "python" }

Push-Location $projectDir
try {
    & $pythonCmd verificar_banco_canta_galo.py 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Banco de dados correto (Marcelo Sanguino / Fazenda Canta Galo)" -ForegroundColor Green
    } else {
        Write-Host "[AVISO] Nao foi possivel verificar o banco" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[AVISO] Nao foi possivel verificar o banco: $_" -ForegroundColor Yellow
}
Pop-Location
Write-Host ""

# 4. Criar nova tarefa agendada (diretório correto)
Write-Host "[4/5] Criando nova tarefa agendada (diretorio correto)..." -ForegroundColor Yellow
try {
    # Criar ação da tarefa
    $action = New-ScheduledTaskAction -Execute $batFile -WorkingDirectory $projectDir
    
    # Criar trigger (iniciar quando o usuário fizer login)
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    
    # Criar configurações da tarefa
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable:$false `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1)
    
    # Criar principal (executar como usuário atual)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    
    # Registrar a tarefa
    Register-ScheduledTask `
        -TaskName "MONPEC_Servidor_Django" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Servidor Django MONPEC - Desenvolvimento - Sistema CORRETO com Marcelo Sanguino / Fazenda Canta Galo" `
        -Force | Out-Null
    
    Write-Host "[OK] Nova tarefa criada com sucesso!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "[ERRO] Falha ao criar tarefa: $_" -ForegroundColor Red
    pause
    exit
}

# 5. Iniciar servidor agora
Write-Host "[5/5] Iniciando servidor agora..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName "MONPEC_Servidor_Django"
    Start-Sleep -Seconds 3
    
    $taskInfo = Get-ScheduledTaskInfo -TaskName "MONPEC_Servidor_Django"
    if ($taskInfo.State -eq 'Running') {
        Write-Host "[OK] Servidor iniciado!" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Tarefa criada, iniciando..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "[AVISO] Nao foi possivel iniciar automaticamente: $_" -ForegroundColor Yellow
    Write-Host "[INFO] Execute manualmente: INICIAR_SISTEMA_CORRETO.bat" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRECAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "A tarefa agendada foi corrigida:" -ForegroundColor White
Write-Host "  - Diretorio CORRETO: $projectDir" -ForegroundColor Gray
Write-Host "  - Arquivo: $batFile" -ForegroundColor Gray
Write-Host "  - Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)" -ForegroundColor Gray
Write-Host ""
Write-Host "O servidor sera iniciado automaticamente:" -ForegroundColor White
Write-Host "  - Quando voce fizer login no Windows" -ForegroundColor Gray
Write-Host "  - Se o servidor parar, ele tentara reiniciar automaticamente" -ForegroundColor Gray
Write-Host ""
Write-Host "URL: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host ""

pause













