# Script para atualizar preços dos planos
$ErrorActionPreference = "Stop"

# Obter o diretório do script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Executar o script Python
python atualizar_precos_temp.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao executar o script. Verifique se o Python e Django estão configurados corretamente." -ForegroundColor Red
    exit $LASTEXITCODE
}

















