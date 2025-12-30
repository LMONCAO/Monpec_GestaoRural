# Script Wrapper para Executar DEPLOY_COMPLETO.ps1
# Resolve problemas de caminho e codificação

# Obter o diretório do script atual
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Se não conseguir obter o diretório, tentar encontrar o diretório do projeto
if (-not $ScriptDir -or -not (Test-Path $ScriptDir)) {
    # Tentar caminhos comuns
    $possiblePaths = @(
        "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural",
        "$env:USERPROFILE\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural",
        (Get-Location).Path
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path (Join-Path $path "DEPLOY_COMPLETO.ps1")) {
            $ScriptDir = $path
            break
        }
    }
    
    # Se ainda não encontrou, usar o diretório atual
    if (-not $ScriptDir) {
        $ScriptDir = Get-Location
    }
}

# Navegar para o diretório correto
Set-Location $ScriptDir

# Caminho completo do script de deploy
$DeployScript = Join-Path $ScriptDir "DEPLOY_COMPLETO.ps1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EXECUTANDO DEPLOY COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Diretório do projeto: $ScriptDir" -ForegroundColor Gray
Write-Host "Script de deploy: $DeployScript" -ForegroundColor Gray
Write-Host ""

# Verificar se o arquivo existe
if (-not (Test-Path $DeployScript)) {
    Write-Host "❌ ERRO: Arquivo não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Arquivo esperado: $DeployScript" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Verificando arquivos .ps1 no diretório atual..." -ForegroundColor Yellow
    
    $ps1Files = Get-ChildItem -Path $ScriptDir -Filter "*.ps1" -ErrorAction SilentlyContinue
    if ($ps1Files) {
        Write-Host ""
        Write-Host "Arquivos .ps1 encontrados:" -ForegroundColor Cyan
        foreach ($file in $ps1Files) {
            Write-Host "  - $($file.Name)" -ForegroundColor White
        }
    } else {
        Write-Host "Nenhum arquivo .ps1 encontrado no diretório." -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Solução:" -ForegroundColor Yellow
    Write-Host "1. Certifique-se de estar no diretório correto do projeto" -ForegroundColor White
    Write-Host "2. Execute: cd 'C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural'" -ForegroundColor White
    Write-Host "3. Execute: .\EXECUTAR_DEPLOY.ps1" -ForegroundColor White
    Write-Host ""
    
    exit 1
}

Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
Write-Host ""
Write-Host "Executando deploy completo..." -ForegroundColor Yellow
Write-Host ""

# Executar o script de deploy com os parâmetros passados
try {
    & $DeployScript @args
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Erro durante a execução do deploy" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERRO ao executar o script:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Detalhes:" -ForegroundColor Yellow
    Write-Host $_.Exception -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "✅ Script executado com sucesso!" -ForegroundColor Green

