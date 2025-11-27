# Script para Iniciar o Sistema Completo
# Este script configura e inicia o sistema Django a partir desta pasta

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando Sistema Monpec Gestao Rural" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Parar todos os processos Python existentes
Write-Host "[INFO] Parando processos Python existentes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verificar se ainda há processos
$processosPython = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
if ($processosPython) {
    Write-Host "[AVISO] Ainda há processos Python rodando. Tentando parar novamente..." -ForegroundColor Yellow
    taskkill /F /IM python.exe 2>$null | Out-Null
    Start-Sleep -Seconds 2
}

Write-Host "[OK] Processos Python parados" -ForegroundColor Green
Write-Host ""

# Verificar se Python esta instalado
# Primeiro tenta usar o Python local na pasta python311
$pythonCmd = $null
if (Test-Path "python311\python.exe") {
    $pythonCmd = "python311\python.exe"
    Write-Host "[INFO] Usando Python local (python311\python.exe)" -ForegroundColor Cyan
} else {
    # Tenta encontrar Python no sistema
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonInstalled) {
        $pythonCmd = "python"
    } else {
        Write-Host "[ERRO] Python nao esta instalado ou nao esta no PATH!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Instale Python 3.8 ou superior: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit
    }
}

$pythonVersion = & $pythonCmd --version 2>&1
Write-Host "[OK] Python encontrado: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Verificar se estamos na pasta correta
if (-not (Test-Path "manage.py")) {
    Write-Host "[ERRO] Arquivo manage.py nao encontrado!" -ForegroundColor Red
    Write-Host "Execute este script na pasta raiz do projeto (Monpec_GestaoRural)" -ForegroundColor Yellow
    exit
}

# Verificar se requirements.txt existe
if (-not (Test-Path "requirements.txt")) {
    Write-Host "[AVISO] Arquivo requirements.txt nao encontrado!" -ForegroundColor Yellow
    Write-Host "Continuando sem instalar dependencias..." -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Verificando dependencias..." -ForegroundColor Cyan
    
    # Verificar se Django esta instalado
    & $pythonCmd -c "import django" 2>$null | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[AVISO] Django nao esta instalado" -ForegroundColor Yellow
        $response = Read-Host "Deseja instalar as dependencias agora? (s/n)"
        
        if ($response -eq 's' -or $response -eq 'S') {
            Write-Host ""
            Write-Host "[INFO] Instalando dependencias..." -ForegroundColor Cyan
            & $pythonCmd -m pip install -r requirements.txt
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Dependencias instaladas com sucesso!" -ForegroundColor Green
            } else {
                Write-Host "[ERRO] Erro ao instalar dependencias" -ForegroundColor Red
                exit
            }
        }
    } else {
        Write-Host "[OK] Dependencias ja instaladas" -ForegroundColor Green
    }
}

Write-Host ""

# Verificar se o banco de dados existe
if (-not (Test-Path "db.sqlite3")) {
    Write-Host "[INFO] Banco de dados nao encontrado. Criando..." -ForegroundColor Cyan
    
    Write-Host "Executando migracoes..." -ForegroundColor Cyan
    & $pythonCmd manage.py migrate 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Banco de dados criado!" -ForegroundColor Green
    } else {
        Write-Host "[AVISO] Algumas migracoes podem ter falhado, mas continuando..." -ForegroundColor Yellow
        Write-Host "Se houver problemas, voce pode precisar corrigir o banco de dados manualmente" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "[INFO] Verificando superusuario..." -ForegroundColor Cyan
    $response = Read-Host "Deseja criar um superusuario agora? (s/n)"
    
    if ($response -eq 's' -or $response -eq 'S') {
        & $pythonCmd manage.py createsuperuser
    }
} else {
    Write-Host "[OK] Banco de dados encontrado" -ForegroundColor Green
    
    # Verificar migracoes pendentes
    Write-Host "Verificando migracoes pendentes..." -ForegroundColor Cyan
    & $pythonCmd manage.py migrate --check 2>$null | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[AVISO] Ha migracoes pendentes ou problemas no banco" -ForegroundColor Yellow
        $response = Read-Host "Deseja tentar executar as migracoes agora? (s/n)"
        
        if ($response -eq 's' -or $response -eq 'S') {
            & $pythonCmd manage.py migrate 2>&1 | Out-String
            Write-Host "[INFO] Migracoes concluidas (alguns erros podem ser normais)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "[OK] Banco de dados atualizado" -ForegroundColor Green
    }
}

Write-Host ""

# Verificar qual configuração usar
# PADRÃO: Usar DESENVOLVIMENTO (sistema_rural.settings)
$settings = "sistema_rural.settings"
$envVar = $env:DJANGO_ENV

# Verificar se deve usar produção (se variável de ambiente estiver definida)
if ($envVar -eq "production" -or $envVar -eq "producao") {
    if (Test-Path "sistema_rural\settings_producao.py") {
        $settings = "sistema_rural.settings_producao"
        Write-Host "[INFO] Usando configurações de PRODUÇÃO (forçado por variável de ambiente)" -ForegroundColor Yellow
    } else {
        Write-Host "[ERRO] settings_producao.py não encontrado, mas DJANGO_ENV=production foi definido" -ForegroundColor Red
        exit
    }
} else {
    # Por padrão, usar desenvolvimento
    $settings = "sistema_rural.settings"
    Write-Host "[INFO] Usando configurações de DESENVOLVIMENTO (padrão)" -ForegroundColor Green
    Write-Host "[DICA] Para usar produção, defina: `$env:DJANGO_ENV='production'" -ForegroundColor Gray
}

# Coletar arquivos estaticos (se necessario)
if (Test-Path "sistema_rural\settings.py") {
    Write-Host "[INFO] Verificando arquivos estaticos..." -ForegroundColor Cyan
    & $pythonCmd manage.py collectstatic --noinput --settings=$settings 2>$null | Out-Null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando servidor Django..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] ⚙️  CONFIGURAÇÃO SELECIONADA: $settings" -ForegroundColor Cyan -BackgroundColor DarkBlue
Write-Host ""
Write-Host "[INFO] O sistema estara disponivel em:" -ForegroundColor Green
Write-Host "   http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "   http://localhost:8000/" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Para parar o servidor, pressione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Verificar se a porta 8000 está livre
$porta8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($porta8000) {
    Write-Host "[AVISO] Porta 8000 já está em uso!" -ForegroundColor Red
    Write-Host "[INFO] Tentando liberar a porta..." -ForegroundColor Yellow
    $processoPorta = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($processoPorta) {
        Stop-Process -Id $processoPorta -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# Iniciar servidor
Write-Host "[INFO] 🚀 Iniciando servidor Django com settings: $settings" -ForegroundColor Green
& $pythonCmd manage.py runserver --settings=$settings

