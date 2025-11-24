# Script para configurar ambiente local de desenvolvimento
# MONPEC - Sistema de Gestao Rural

Write-Host "Configurando Ambiente Local - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Python nao encontrado!" -ForegroundColor Red
    Write-Host "   Instale Python 3.8 ou superior: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green
Write-Host ""

# Navegar para pasta do projeto
$projectPath = "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orcamentario\Monpec_GestaoRural"
Set-Location $projectPath
Write-Host "Pasta do projeto: $projectPath" -ForegroundColor Green
Write-Host ""

# Criar ambiente virtual
Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "[!] Ambiente virtual ja existe. Pulando criacao..." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Erro ao criar ambiente virtual!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Ambiente virtual criado!" -ForegroundColor Green
}
Write-Host ""

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Erro ao ativar ambiente virtual. Tente executar:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
    Write-Host ""
    Write-Host "   Depois execute novamente este script." -ForegroundColor White
    exit 1
}
Write-Host "[OK] Ambiente virtual ativado!" -ForegroundColor Green
Write-Host ""

# Atualizar pip
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "[OK] pip atualizado!" -ForegroundColor Green
Write-Host ""

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Erro ao instalar dependencias!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Dependencias instaladas!" -ForegroundColor Green
} else {
    Write-Host "[!] Arquivo requirements.txt nao encontrado!" -ForegroundColor Yellow
    Write-Host "   Instalando dependencias basicas..." -ForegroundColor Yellow
    pip install Django==4.2.7 Pillow==10.0.1 python-dateutil==2.8.2 reportlab==4.0.4 openpyxl==3.1.2 stripe==5.4.0
    Write-Host "[OK] Dependencias basicas instaladas!" -ForegroundColor Green
}
Write-Host ""

# Executar migracoes
Write-Host "Executando migracoes..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Erro ao executar migracoes!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Migracoes executadas!" -ForegroundColor Green
Write-Host ""

# Coletar arquivos estaticos
Write-Host "Coletando arquivos estaticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput 2>$null
Write-Host "[OK] Arquivos estaticos coletados!" -ForegroundColor Green
Write-Host ""

# Verificar se existe superusuario
Write-Host "Verificando superusuario..." -ForegroundColor Yellow
$superuserExists = python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('True' if User.objects.filter(is_superuser=True).exists() else 'False')" 2>$null
if ($superuserExists -eq "False") {
    Write-Host "[!] Nenhum superusuario encontrado." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para criar um superusuario, execute:" -ForegroundColor Cyan
    Write-Host "   python manage.py createsuperuser" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[OK] Superusuario encontrado!" -ForegroundColor Green
}
Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Green
Write-Host "  AMBIENTE CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Para iniciar o servidor:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "2. Acesse no navegador:" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:8000/" -ForegroundColor White
Write-Host ""
Write-Host "3. Para criar superusuario (se necessario):" -ForegroundColor Cyan
Write-Host "   python manage.py createsuperuser" -ForegroundColor White
Write-Host ""
Write-Host "4. Para desativar ambiente virtual:" -ForegroundColor Cyan
Write-Host "   deactivate" -ForegroundColor White
Write-Host ""
