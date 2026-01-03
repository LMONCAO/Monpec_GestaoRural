# ========================================
# SCRIPT DE OTIMIZAÇÃO DE DESEMPENHO
# Para melhorar performance do Cursor e desenvolvimento
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OTIMIZAÇÃO DE DESEMPENHO DO NOTEBOOK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está executando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[AVISO] Execute como Administrador para otimizações completas!" -ForegroundColor Yellow
    Write-Host ""
}

# ========================================
# 1. PARAR PROCESSOS DESNECESSÁRIOS
# ========================================
Write-Host "[1/8] Parando processos desnecessários..." -ForegroundColor Green

$processosParaParar = @(
    "Teams", "Skype", "Discord", "Spotify", "Steam", 
    "OneDrive", "Dropbox", "GoogleDriveFS", "Adobe*",
    "CCXProcess", "CCLibrary", "Creative Cloud",
    "Xbox", "GameBar", "GameBarFTServer",
    "OfficeClickToRun", "MicrosoftEdgeUpdate",
    "TeamsMachineInstaller", "TeamsUpdater"
)

foreach ($proc in $processosParaParar) {
    Get-Process -Name $proc -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host "  [OK] Processos desnecessarios parados" -ForegroundColor Gray

# ========================================
# 2. CONFIGURAR PLANO DE ENERGIA - ALTA PERFORMANCE
# ========================================
Write-Host "[2/8] Configurando plano de energia..." -ForegroundColor Green

try {
    # Ativar plano de alta performance
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>$null
    if ($LASTEXITCODE -ne 0) {
        # Se não existir, criar um plano balanceado otimizado
        powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
    }
    
    # Desabilitar suspensão de USB
    powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    powercfg /setdcvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    
    # Desabilitar suspensão de disco
    powercfg /change disk-timeout-ac 0
    powercfg /change disk-timeout-dc 0
    
    # Desabilitar suspensão de monitor (apenas quando conectado)
    powercfg /change monitor-timeout-ac 0
    powercfg /change monitor-timeout-dc 5
    
    powercfg /setactive SCHEME_CURRENT
    
    Write-Host "  [OK] Plano de energia otimizado" -ForegroundColor Gray
} catch {
    Write-Host "  [AVISO] Erro ao configurar energia (pode precisar de admin)" -ForegroundColor Yellow
}

# ========================================
# 3. DESABILITAR SERVIÇOS DESNECESSÁRIOS
# ========================================
Write-Host "[3/8] Otimizando serviços do Windows..." -ForegroundColor Green

if ($isAdmin) {
    $servicosParaDesabilitar = @(
        "SysMain",              # Superfetch (pode causar lentidão)
        "WSearch",              # Windows Search (se não usar)
        "DiagTrack",            # Telemetria
        "dmwappushservice",     # WAP Push
        "WbioSrvc",             # Windows Biometric Service
        "RetailDemo",           # Retail Demo
        "RemoteRegistry",       # Registro Remoto
        "RemoteAccess",         # Roteamento e Acesso Remoto
        "SSDPSRV",              # Descoberta SSDP
        "upnphost"              # Host de Dispositivo UPnP
    )
    
    foreach ($servico in $servicosParaDesabilitar) {
        try {
            $svc = Get-Service -Name $servico -ErrorAction SilentlyContinue
            if ($svc -and $svc.Status -eq "Running") {
                Stop-Service -Name $servico -Force -ErrorAction SilentlyContinue
                Set-Service -Name $servico -StartupType Disabled -ErrorAction SilentlyContinue
            }
        } catch {
            # Ignorar erros
        }
    }
    
    Write-Host "  [OK] Servicos desnecessarios desabilitados" -ForegroundColor Gray
} else {
    Write-Host "  [AVISO] Pule esta etapa (requer admin)" -ForegroundColor Yellow
}

# ========================================
# 4. LIMPAR CACHE E ARQUIVOS TEMPORÁRIOS
# ========================================
Write-Host "[4/8] Limpando cache e arquivos temporários..." -ForegroundColor Green

try {
    # Limpar temp do usuário
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    
    # Limpar temp do Windows
    Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    
    # Limpar cache do navegador (Edge/Chrome)
    Remove-Item "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    
    # Limpar cache do Cursor
    Remove-Item "$env:APPDATA\Cursor\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:APPDATA\Cursor\CachedData\*" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "  [OK] Cache limpo" -ForegroundColor Gray
} catch {
    Write-Host "  [AVISO] Alguns arquivos podem estar em uso" -ForegroundColor Yellow
}

# ========================================
# 5. OTIMIZAR PRIORIDADES DE PROCESSO
# ========================================
Write-Host "[5/8] Otimizando prioridades de processo..." -ForegroundColor Green

try {
    # Aumentar prioridade do Cursor
    $cursorProcesses = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
    foreach ($proc in $cursorProcesses) {
        $proc.PriorityClass = "High"
    }
    
    # Aumentar prioridade do Python (para desenvolvimento)
    $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
    foreach ($proc in $pythonProcesses) {
        $proc.PriorityClass = "AboveNormal"
    }
    
    Write-Host "  [OK] Prioridades otimizadas" -ForegroundColor Gray
} catch {
    Write-Host "  [AVISO] Erro ao ajustar prioridades" -ForegroundColor Yellow
}

# ========================================
# 6. DESABILITAR ANIMAÇÕES E EFEITOS VISUAIS
# ========================================
Write-Host "[6/8] Desabilitando efeitos visuais desnecessários..." -ForegroundColor Green

if ($isAdmin) {
    try {
        # Desabilitar animações
        Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0" -ErrorAction SilentlyContinue
        
        # Desabilitar transparência
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0 -ErrorAction SilentlyContinue
        
        # Desabilitar efeitos de som
        Set-ItemProperty -Path "HKCU:\AppEvents\Schemes\Apps\.Default" -Name "(Default)" -Value "" -ErrorAction SilentlyContinue
        
        Write-Host "  [OK] Efeitos visuais otimizados" -ForegroundColor Gray
    } catch {
        Write-Host "  [AVISO] Algumas configuracoes podem precisar de reinicializacao" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [AVISO] Pule esta etapa (requer admin)" -ForegroundColor Yellow
}

# ========================================
# 7. CONFIGURAR VIRTUAL MEMORY (PAGEFILE)
# ========================================
Write-Host "[7/8] Verificando memória virtual..." -ForegroundColor Green

try {
    $ram = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
    Write-Host "  [INFO] RAM instalada: $([math]::Round($ram, 2)) GB" -ForegroundColor Gray
    
    # Recomendar tamanho do pagefile (1.5x RAM para desenvolvimento)
    $recommendedPageFile = [math]::Round($ram * 1.5, 0)
    Write-Host "  [INFO] Pagefile recomendado: $recommendedPageFile GB" -ForegroundColor Gray
    Write-Host "  [AVISO] Configure manualmente se necessario (Sistema > Configuracoes Avancadas)" -ForegroundColor Yellow
} catch {
    Write-Host "  [AVISO] Nao foi possivel verificar memoria" -ForegroundColor Yellow
}

# ========================================
# 8. VERIFICAR E OTIMIZAR DISCO
# ========================================
Write-Host "[8/8] Verificando saúde do disco..." -ForegroundColor Green

try {
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 }
    foreach ($drive in $drives) {
        $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
        $usedSpaceGB = [math]::Round($drive.Used / 1GB, 2)
        $totalSpaceGB = [math]::Round(($drive.Free + $drive.Used) / 1GB, 2)
        $percentFree = [math]::Round(($drive.Free / ($drive.Free + $drive.Used)) * 100, 1)
        
        Write-Host "  [INFO] Disco $($drive.Name): $freeSpaceGB GB livres de $totalSpaceGB GB ($percentFree%)" -ForegroundColor Gray
        
        if ($percentFree -lt 10) {
            Write-Host "    [ATENCAO] Pouco espaco livre! Limpe arquivos desnecessarios." -ForegroundColor Red
        }
    }
} catch {
    Write-Host "  [AVISO] Erro ao verificar disco" -ForegroundColor Yellow
}

# ========================================
# RESUMO E RECOMENDAÇÕES
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OTIMIZAÇÃO CONCLUÍDA!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "RECOMENDACOES ADICIONAIS:" -ForegroundColor Yellow
Write-Host "  1. Feche aplicacoes que nao esta usando" -ForegroundColor White
Write-Host "  2. Desabilite extensoes desnecessarias no Cursor" -ForegroundColor White
Write-Host "  3. Reduza o numero de arquivos abertos no Cursor" -ForegroundColor White
Write-Host "  4. Configure o .cursorignore (ja criado) para ignorar arquivos grandes" -ForegroundColor White
Write-Host "  5. Considere aumentar RAM se possivel (minimo 8GB recomendado)" -ForegroundColor White
Write-Host "  6. Use SSD para melhor performance" -ForegroundColor White
Write-Host ""
Write-Host "Para aplicar todas as otimizacoes, REINICIE o computador." -ForegroundColor Yellow
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

