# Script para rodar o sistema Django em localhost
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MONPEC - Sistema de Gestão Rural" -ForegroundColor Cyan
Write-Host "  Rodando em Localhost" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script na raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.8 ou superior." -ForegroundColor Yellow
    exit 1
}

# Verificar se o ambiente virtual existe
if (Test-Path "venv") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path "env") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\env\Scripts\Activate.ps1
} else {
    Write-Host "AVISO: Ambiente virtual não encontrado." -ForegroundColor Yellow
    Write-Host "Criando ambiente virtual..." -ForegroundColor Cyan
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    Write-Host "Instalando dependências..." -ForegroundColor Cyan
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Verificar se as migrações foram aplicadas
Write-Host ""
Write-Host "Verificando migrações..." -ForegroundColor Cyan
python manage.py migrate --run-syncdb

# Coletar arquivos estáticos (se necessário)
Write-Host ""
Write-Host "Coletando arquivos estáticos..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

# Iniciar servidor
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Servidor iniciando..." -ForegroundColor Green
Write-Host "  Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Acesse: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Rodar servidor Django
python manage.py runserver 0.0.0.0:8000

