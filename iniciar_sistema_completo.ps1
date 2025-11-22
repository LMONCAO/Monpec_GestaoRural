# Script para Iniciar o Sistema Completo
# Este script configura e inicia o sistema Django a partir desta pasta

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando Sistema Monpec Gestao Rural" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
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

# Coletar arquivos estaticos (se necessario)
if (Test-Path "sistema_rural\settings.py") {
    Write-Host "[INFO] Verificando arquivos estaticos..." -ForegroundColor Cyan
    & $pythonCmd manage.py collectstatic --noinput 2>$null | Out-Null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando servidor Django..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] O sistema estara disponivel em:" -ForegroundColor Green
Write-Host "   http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "   http://localhost:8000/" -ForegroundColor White
Write-Host ""
Write-Host "[INFO] Para parar o servidor, pressione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
& $pythonCmd manage.py runserver

