# ============================================
# AUTENTICAÇÃO MANUAL NO GOOGLE CLOUD
# ============================================
# Execute este script se o navegador não abrir automaticamente
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTENTICAÇÃO MANUAL GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se já está autenticado
Write-Host "Verificando autenticação atual..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1 | Where-Object { $_ -and $_ -notmatch "ERROR" -and $_ -notmatch "Listed 0 items" }

if ($authCheck) {
    Write-Host "✅ Você já está autenticado!" -ForegroundColor Green
    Write-Host "   Conta: $authCheck" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Pode continuar o deploy normalmente." -ForegroundColor Green
    exit 0
}

Write-Host "❌ Não autenticado. Iniciando processo de login..." -ForegroundColor Yellow
Write-Host ""

# Método 1: Tentar com navegador
Write-Host "Tentando abrir navegador automaticamente..." -ForegroundColor Cyan
Write-Host ""

$result = gcloud auth login 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Autenticação concluída com sucesso!" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# Se falhar, tentar método alternativo
Write-Host ""
Write-Host "Navegador não abriu automaticamente. Usando método alternativo..." -ForegroundColor Yellow
Write-Host ""

# Gerar link de autenticação
Write-Host "Siga estes passos:" -ForegroundColor Cyan
Write-Host "1. Execute o comando abaixo:" -ForegroundColor White
Write-Host "   gcloud auth login --no-launch-browser" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Copie o link que aparecer" -ForegroundColor White
Write-Host "3. Cole no navegador e faça login" -ForegroundColor White
Write-Host "4. Depois execute o deploy novamente" -ForegroundColor White
Write-Host ""

# Tentar executar o comando com --no-launch-browser
Write-Host "Executando comando para obter link..." -ForegroundColor Yellow
gcloud auth login --no-launch-browser

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Após fazer login no navegador, execute:" -ForegroundColor Yellow
Write-Host "  .\DEPLOY_DEFINITIVO_LOCAL.ps1" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""



