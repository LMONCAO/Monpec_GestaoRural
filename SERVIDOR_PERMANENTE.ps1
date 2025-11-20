# ========================================
# SERVIDOR PERMANENTE MONPEC
# ========================================
# Este script mantém o servidor Django rodando continuamente.
# Se o servidor cair, ele reinicia automaticamente.
# ========================================

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Verificar Python
$pythonPath = $null
if (Test-Path "python311\python.exe") {
    $pythonPath = Join-Path $scriptDir "python311\python.exe"
} else {
    $pythonCheck = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCheck) {
        $pythonPath = "python"
    } else {
        Write-Host "[ERRO] Python não encontrado!" | Out-File -FilePath "$scriptDir\django_error.log" -Append
        exit 1
    }
}

$logFile = Join-Path $scriptDir "django_server.log"
$errorLog = Join-Path $scriptDir "django_error.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Add-Content -Path $logFile -Value $logMessage
    Write-Host $logMessage
}

function Write-ErrorLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $errorMessage = "[$timestamp] ERRO: $Message"
    Add-Content -Path $errorLog -Value $errorMessage
}

# Função para verificar se o servidor está rodando
function Test-ServerRunning {
    $portCheck = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
    return ($null -ne $portCheck)
}

# Função para parar processos existentes na porta 8000
function Stop-ExistingServer {
    $processes = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
    if ($processes) {
        foreach ($proc in $processes) {
            $pid = ($proc -split '\s+')[-1]
            if ($pid -and $pid -ne "0") {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Log "Processo $pid parado"
                } catch {
                    Write-ErrorLog "Erro ao parar processo $pid : $_"
                }
            }
        }
        Start-Sleep -Seconds 2
    }
}

# Loop principal - mantém o servidor rodando
Write-Log "=== SERVIDOR PERMANENTE INICIADO ==="
Write-Log "Diretório: $scriptDir"
Write-Log "Python: $pythonPath"

while ($true) {
    try {
        # Verificar se já está rodando
        if (Test-ServerRunning) {
            Write-Log "Servidor já está rodando na porta 8000"
            Start-Sleep -Seconds 60
            continue
        }

        Write-Log "Iniciando servidor Django..."
        
        # Parar processos existentes
        Stop-ExistingServer

        # Iniciar servidor Django em background
        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = $pythonPath
        $processInfo.Arguments = "manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows"
        $processInfo.WorkingDirectory = $scriptDir
        $processInfo.UseShellExecute = $false
        $processInfo.RedirectStandardOutput = $true
        $processInfo.RedirectStandardError = $true
        $processInfo.CreateNoWindow = $true

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo

        # Capturar output
        $outputBuilder = New-Object System.Text.StringBuilder
        $errorBuilder = New-Object System.Text.StringBuilder

        $outputEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -Action {
            if ($EventArgs.Data) {
                [void]$Event.MessageData.AppendLine($EventArgs.Data)
                Write-Log $EventArgs.Data
            }
        } -MessageData $outputBuilder

        $errorEvent = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -Action {
            if ($EventArgs.Data) {
                [void]$Event.MessageData.AppendLine($EventArgs.Data)
                Write-ErrorLog $EventArgs.Data
            }
        } -MessageData $errorBuilder

        $process.Start() | Out-Null
        $process.BeginOutputReadLine()
        $process.BeginErrorReadLine()

        Write-Log "Servidor iniciado (PID: $($process.Id))"

        # Aguardar alguns segundos para verificar se iniciou corretamente
        Start-Sleep -Seconds 5

        if (-not $process.HasExited) {
            if (Test-ServerRunning) {
                Write-Log "Servidor rodando com sucesso na porta 8000"
                
                # Monitorar o processo
                while (-not $process.HasExited) {
                    Start-Sleep -Seconds 30
                    
                    # Verificar se ainda está na porta
                    if (-not (Test-ServerRunning)) {
                        Write-ErrorLog "Servidor não está mais na porta 8000, mas processo ainda existe"
                        $process.Kill()
                        break
                    }
                }

                if ($process.HasExited) {
                    $exitCode = $process.ExitCode
                    Write-ErrorLog "Servidor parou inesperadamente (Exit Code: $exitCode)"
                    
                    if ($errorBuilder.ToString()) {
                        Write-ErrorLog "Erros capturados: $($errorBuilder.ToString())"
                    }
                }
            } else {
                Write-ErrorLog "Servidor não iniciou corretamente na porta 8000"
                if (-not $process.HasExited) {
                    $process.Kill()
                }
            }
        } else {
            Write-ErrorLog "Servidor terminou imediatamente após iniciar"
            if ($errorBuilder.ToString()) {
                Write-ErrorLog "Erros: $($errorBuilder.ToString())"
            }
        }

        # Limpar eventos
        Unregister-Event -SourceIdentifier $outputEvent.Name -ErrorAction SilentlyContinue
        Unregister-Event -SourceIdentifier $errorEvent.Name -ErrorAction SilentlyContinue
        Remove-Event -SourceIdentifier $outputEvent.Name -ErrorAction SilentlyContinue
        Remove-Event -SourceIdentifier $errorEvent.Name -ErrorAction SilentlyContinue

        Write-Log "Aguardando 10 segundos antes de reiniciar..."
        Start-Sleep -Seconds 10

    } catch {
        Write-ErrorLog "Erro no loop principal: $_"
        Write-Log "Aguardando 30 segundos antes de tentar novamente..."
        Start-Sleep -Seconds 30
    }
}






