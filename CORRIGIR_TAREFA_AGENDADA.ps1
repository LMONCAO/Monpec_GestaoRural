# ========================================
# CORRIGIR TAREFA AGENDADA - REMOVER E RECRIAR
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
    Write-Host "  Unregister-ScheduledTask -TaskName 'MONPEC_Servidor_Django' -Confirm:`$false" -ForegroundColor Gray
    pause
    exit
}

# Obter diretório do projeto
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $projectDir "MONPEC DESENVOLVIMENTO.bat"

Write-Host "[INFO] Diretorio do projeto: $projectDir" -ForegroundColor Green
Write-Host "[INFO] Arquivo BAT: $batFile" -ForegroundColor Green
Write-Host ""

# Verificar se o arquivo BAT existe
if (-not (Test-Path $batFile)) {
    Write-Host "[ERRO] Arquivo 'MONPEC DESENVOLVIMENTO.bat' nao encontrado!" -ForegroundColor Red
    pause
    exit
}

# Parar tarefa existente se estiver rodando
$existingTask = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "[INFO] Tarefa existente encontrada. Verificando configuração..." -ForegroundColor Yellow
    
    $action = $existingTask.Actions[0]
    Write-Host "  Script atual: $($action.Arguments)" -ForegroundColor Gray
    
    # Verificar se está apontando para o diretório errado
    if ($action.Arguments -like "*Monpec_projetista*" -or $action.Arguments -like "*SERVIDOR_PERMANENTE.ps1*") {
        Write-Host "[AVISO] Tarefa esta apontando para diretorio ERRADO!" -ForegroundColor Red
        Write-Host "  Removendo tarefa antiga..." -ForegroundColor Yellow
        
        Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        
        Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false
        Write-Host "[OK] Tarefa antiga removida" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Tarefa parece estar correta, mas vamos recriar para garantir" -ForegroundColor Yellow
        Stop-ScheduledTask -TaskName "MONPEC_Servidor_Django" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Unregister-ScheduledTask -TaskName "MONPEC_Servidor_Django" -Confirm:$false
    }
} else {
    Write-Host "[INFO] Nenhuma tarefa existente encontrada" -ForegroundColor Green
}

# Parar processos Python
Write-Host "[INFO] Parando processos Python..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "[OK] Processos parados" -ForegroundColor Green
Write-Host ""

# Criar nova tarefa agendada correta
Write-Host "[INFO] Criando nova tarefa agendada CORRETA..." -ForegroundColor Yellow

# Criar ação da tarefa (executar o arquivo BAT)
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
try {
    Register-ScheduledTask `
        -TaskName "MONPEC_Servidor_Django" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Servidor Django MONPEC - Desenvolvimento - Sistema CORRETO com Marcelo Sanguino / Fazenda Canta Galo" `
        -Force | Out-Null
    
    Write-Host "[OK] Tarefa agendada criada com sucesso!" -ForegroundColor Green
    Write-Host ""
    
    # Verificar configuração
    $newTask = Get-ScheduledTask -TaskName "MONPEC_Servidor_Django"
    $newAction = $newTask.Actions[0]
    Write-Host "[INFO] Configuracao da nova tarefa:" -ForegroundColor Cyan
    Write-Host "  Script: $($newAction.Execute)" -ForegroundColor Gray
    Write-Host "  Diretorio: $($newAction.WorkingDirectory)" -ForegroundColor Gray
    Write-Host ""
    
    # Perguntar se deseja iniciar agora
    $response = Read-Host "Deseja iniciar o servidor agora? (s/n)"
    if ($response -eq 's' -or $response -eq 'S') {
        Write-Host "[INFO] Iniciando servidor..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName "MONPEC_Servidor_Django"
        Start-Sleep -Seconds 5
        
        # Verificar se está rodando
        $taskInfo = Get-ScheduledTaskInfo -TaskName "MONPEC_Servidor_Django"
        if ($taskInfo.State -eq 'Running') {
            Write-Host "[OK] Servidor iniciado!" -ForegroundColor Green
        } else {
            Write-Host "[AVISO] Tarefa iniciada, aguarde alguns segundos..." -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "[ERRO] Falha ao criar tarefa agendada: $_" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRECAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "A tarefa agendada foi corrigida e agora usa:" -ForegroundColor White
Write-Host "  - Arquivo: MONPEC DESENVOLVIMENTO.bat" -ForegroundColor Gray
Write-Host "  - Settings: sistema_rural.settings (DESENVOLVIMENTO)" -ForegroundColor Gray
Write-Host "  - Banco: db.sqlite3 (com Marcelo Sanguino / Fazenda Canta Galo)" -ForegroundColor Gray
Write-Host ""
Write-Host "O servidor iniciara automaticamente no proximo login." -ForegroundColor White
Write-Host ""

pause

