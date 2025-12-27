# Script completo de deploy para produção - Sistema MONPEC (Windows/PowerShell)
# Execute este script no servidor Windows para fazer o deploy completo

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY COMPLETO - SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se está no diretório correto
Write-Host "Verificando diretório do projeto..." -ForegroundColor Yellow
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: manage.py não encontrado! Execute este script no diretório raiz do projeto." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Diretório correto" -ForegroundColor Green

# 2. Ativar ambiente virtual se existir
Write-Host "Verificando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Write-Host "✓ Ambiente virtual ativado" -ForegroundColor Green
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual (.venv)..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✓ Ambiente virtual ativado" -ForegroundColor Green
} else {
    Write-Host "Ambiente virtual não encontrado, usando Python do sistema" -ForegroundColor Yellow
}

# 3. Verificar Python e Django
Write-Host "Verificando Python e Django..." -ForegroundColor Yellow
python --version
$djangoCheck = python -c "import django; print(f'Django {django.get_version()}')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Django não está instalado!" -ForegroundColor Red
    exit 1
}
Write-Host $djangoCheck
Write-Host "✓ Python e Django OK" -ForegroundColor Green

# 4. Instalar/atualizar dependências
Write-Host "Instalando dependências..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements.txt
    Write-Host "✓ Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "ERRO: requirements.txt não encontrado!" -ForegroundColor Red
    exit 1
}

# 5. Verificar arquivo .env_producao
Write-Host "Verificando configurações de ambiente..." -ForegroundColor Yellow
if (-not (Test-Path ".env_producao")) {
    Write-Host "ERRO: .env_producao não encontrado!" -ForegroundColor Red
    Write-Host "Criando arquivo .env_producao de exemplo..." -ForegroundColor Yellow
    @"
# Configurações de Produção - Sistema MONPEC
DEBUG=False
SECRET_KEY=django-insecure-sistema-rural-ia-2025-producao-segura-123456789
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=Monpec2025!
DB_HOST=localhost
DB_PORT=5432
"@ | Out-File -FilePath ".env_producao" -Encoding UTF8
    Write-Host "Arquivo .env_producao criado. POR FAVOR, EDITE COM AS CONFIGURAÇÕES CORRETAS!" -ForegroundColor Yellow
}

# 6. Criar diretórios necessários
Write-Host "Criando diretórios necessários..." -ForegroundColor Yellow
$directories = @("staticfiles", "media", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Diretórios criados" -ForegroundColor Green

# 7. Aplicar migrações
Write-Host "Aplicando migrações do banco de dados..." -ForegroundColor Yellow
python manage.py migrate --settings=sistema_rural.settings_producao --noinput
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrações aplicadas" -ForegroundColor Green
} else {
    Write-Host "ERRO ao aplicar migrações!" -ForegroundColor Red
    exit 1
}

# 8. Coletar arquivos estáticos
Write-Host "Coletando arquivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput --clear
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Arquivos estáticos coletados" -ForegroundColor Green
} else {
    Write-Host "AVISO: Erro ao coletar arquivos estáticos (pode ser normal se não houver arquivos)" -ForegroundColor Yellow
}

# 9. Verificar configurações
Write-Host "Verificando configurações..." -ForegroundColor Yellow
python manage.py check --settings=sistema_rural.settings_producao --deploy
if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: Erros encontrados nas configurações. Verifique acima." -ForegroundColor Yellow
}

# 10. Executar diagnóstico
Write-Host "Executando diagnóstico..." -ForegroundColor Yellow
if (Test-Path "diagnosticar_erro_producao.py") {
    python diagnosticar_erro_producao.py
}

# 11. Verificar superusuário
Write-Host "Verificando superusuário..." -ForegroundColor Yellow
$superuserCheck = python manage.py shell --settings=sistema_rural.settings_producao -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superusuários:', User.objects.filter(is_superuser=True).count())" 2>&1
Write-Host $superuserCheck

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure o servidor web para usar:"
Write-Host "   - DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao"
Write-Host "   - WSGI: sistema_rural.wsgi.application"
Write-Host ""
Write-Host "2. Reinicie o servidor web"
Write-Host ""
Write-Host "3. Teste o acesso em http://monpec.com.br"
Write-Host ""
Write-Host "4. Verifique os logs em logs/django.log"
Write-Host ""









