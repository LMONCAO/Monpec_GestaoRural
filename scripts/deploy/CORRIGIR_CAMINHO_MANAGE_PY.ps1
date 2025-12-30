# ============================================
# CORRIGIR CAMINHO DO manage.py
# ============================================
# Este script corrige scripts que estão tentando
# acessar manage.py no caminho incorreto
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGINDO CAMINHO DO manage.py" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório raiz
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Join-Path $scriptPath "..\.." | Resolve-Path

Set-Location $rootPath

if (-not (Test-Path "manage.py")) {
    Write-Host "[ERRO] manage.py não encontrado na raiz do projeto!" -ForegroundColor Red
    Write-Host "[INFO] Certifique-se de executar este script a partir da raiz do projeto." -ForegroundColor Yellow
    Read-Host "Pressione Enter para continuar"
    exit 1
}

Write-Host "[OK] manage.py encontrado na raiz do projeto" -ForegroundColor Green
Write-Host "[INFO] Diretório atual: $rootPath" -ForegroundColor Gray
Write-Host ""

# Verificar se há scripts tentando usar o caminho incorreto
Write-Host "[INFO] Verificando scripts em scripts\deploy\..." -ForegroundColor Yellow

$scriptsDeploy = Join-Path $rootPath "scripts\deploy"
$found = $false

Get-ChildItem -Path $scriptsDeploy -Include *.bat,*.ps1,*.sh -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match "scripts[\\/]deploy[\\/]manage\.py") {
        Write-Host "[AVISO] Script encontrado: $($_.Name)" -ForegroundColor Yellow
        $found = $true
    }
}

if (-not $found) {
    Write-Host "[OK] Nenhum script encontrado usando o caminho incorreto" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SOLUÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se você está executando um script de dentro de scripts\deploy\," -ForegroundColor White
Write-Host "certifique-se de que o script muda para o diretório raiz antes" -ForegroundColor White
Write-Host "de executar manage.py, ou use o caminho relativo correto:" -ForegroundColor White
Write-Host ""
Write-Host "  CORRETO: python ..\..\manage.py" -ForegroundColor Green
Write-Host "  CORRETO: cd ..\.. ; python manage.py" -ForegroundColor Green
Write-Host "  INCORRETO: python scripts\deploy\manage.py" -ForegroundColor Red
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Pressione Enter para continuar"

