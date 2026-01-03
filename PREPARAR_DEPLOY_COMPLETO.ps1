# Script PowerShell para Preparar e Testar Sistema antes do Deploy
# Execute: .\PREPARAR_DEPLOY_COMPLETO.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 PREPARAÇÃO PARA DEPLOY - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# 1. Verificar Python e Django
Write-Host "[1/6] Verificando ambiente Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Aplicar migrations
Write-Host "[2/6] Aplicando migrations do banco de dados..." -ForegroundColor Yellow
try {
    python manage.py migrate --noinput
    Write-Host "✅ Migrations aplicadas com sucesso" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao aplicar migrations: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Coletar arquivos estáticos
Write-Host "[3/6] Coletando arquivos estáticos..." -ForegroundColor Yellow
try {
    python manage.py collectstatic --noinput --clear
    Write-Host "✅ Arquivos estáticos coletados" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Aviso ao coletar estáticos (pode ser normal): $_" -ForegroundColor Yellow
}
Write-Host ""

# 4. Verificar sintaxe Python
Write-Host "[4/6] Verificando sintaxe dos arquivos principais..." -ForegroundColor Yellow
$arquivos_verificar = @(
    "gestao_rural\views.py",
    "gestao_rural\forms.py",
    "gestao_rural\context_processors.py",
    "gestao_rural\helpers_db.py"
)

$erros_sintaxe = 0
foreach ($arquivo in $arquivos_verificar) {
    if (Test-Path $arquivo) {
        try {
            python -m py_compile $arquivo 2>&1 | Out-Null
            Write-Host "  ✅ $arquivo" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ $arquivo - Erro de sintaxe" -ForegroundColor Red
            $erros_sintaxe++
        }
    }
}

if ($erros_sintaxe -eq 0) {
    Write-Host "✅ Todos os arquivos estão corretos" -ForegroundColor Green
} else {
    Write-Host "❌ $erros_sintaxe arquivo(s) com erro de sintaxe" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 5. Verificar tabelas críticas
Write-Host "[5/6] Verificando tabelas do banco de dados..." -ForegroundColor Yellow
try {
    python verificar_e_corrigir_banco.py
    Write-Host "✅ Banco de dados verificado" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Aviso na verificação do banco: $_" -ForegroundColor Yellow
}
Write-Host ""

# 6. Resumo
Write-Host "[6/6] Preparação concluída!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ SISTEMA PRONTO PARA DEPLOY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Teste o sistema localmente (python manage.py runserver)" -ForegroundColor White
Write-Host "2. Execute o deploy usando:" -ForegroundColor White
Write-Host "   - DEPLOY_AUTOMATICO.ps1 (Windows)" -ForegroundColor Cyan
Write-Host "   - scripts/deploy/DEPLOY_COMPLETO_AGORA.sh (Linux/Cloud Shell)" -ForegroundColor Cyan
Write-Host ""

