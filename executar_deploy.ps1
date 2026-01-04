# Script temporário para executar o deploy
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "========================================"
Write-Host "INICIANDO DEPLOY DAS CORRECOES"
Write-Host "========================================"
Write-Host ""
Write-Host "Diretorio atual: $PWD"
Write-Host ""

if (Test-Path "DEPLOY_GARANTIR_VERSAO_CORRETA.bat") {
    Write-Host "Script encontrado! Executando..."
    Write-Host ""
    Write-Host "IMPORTANTE: Este processo pode levar 10-25 minutos"
    Write-Host "Por favor, aguarde e NAO feche esta janela!"
    Write-Host ""
    
    & cmd.exe /c "DEPLOY_GARANTIR_VERSAO_CORRETA.bat"
} else {
    Write-Host "ERRO: Script DEPLOY_GARANTIR_VERSAO_CORRETA.bat nao encontrado!"
    Write-Host "Verifique se voce esta no diretorio correto do projeto."
    exit 1
}


