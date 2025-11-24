# Script para aplicar atualizações após pull do GitHub
# Executa migrações e coleta arquivos estáticos

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  APLICANDO ATUALIZAÇÕES DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script na raiz do projeto." -ForegroundColor Yellow
    exit 1
}

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    exit 1
}

# Ativar ambiente virtual se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path "env\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\env\Scripts\Activate.ps1
}

# Executar migrações
Write-Host "`n[1/3] Executando migrações do banco de dados..." -ForegroundColor Cyan
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: Erro ao executar migrações." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Migrações aplicadas com sucesso!" -ForegroundColor Green
}

# Coletar arquivos estáticos
Write-Host "`n[2/3] Coletando arquivos estáticos..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: Erro ao coletar arquivos estáticos." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Arquivos estáticos coletados!" -ForegroundColor Green
}

# Verificar templates atualizados
Write-Host "`n[3/3] Verificando templates atualizados..." -ForegroundColor Cyan
$templateCount = (Get-ChildItem -Path "templates" -Recurse -Filter "*.html" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "Total de templates encontrados: $templateCount" -ForegroundColor Green

# Verificar se há templates novos ou modificados recentemente
$recentTemplates = Get-ChildItem -Path "templates" -Recurse -Filter "*.html" -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } | 
    Select-Object -First 10

if ($recentTemplates) {
    Write-Host "`nTemplates modificados recentemente:" -ForegroundColor Yellow
    $recentTemplates | ForEach-Object {
        Write-Host "  - $($_.FullName.Replace((Get-Location).Path + '\', ''))" -ForegroundColor Gray
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ATUALIZAÇÕES APLICADAS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "O sistema está atualizado e pronto para uso." -ForegroundColor Cyan
Write-Host "Execute '.\rodar_localhost.ps1' para iniciar o servidor." -ForegroundColor Yellow

