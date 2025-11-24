# Script de Instalacao do Google Cloud CLI para Windows
# Este script baixa e instala o Google Cloud SDK automaticamente

Write-Host "Instalacao do Google Cloud CLI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se ja esta instalado
Write-Host "Verificando se ja esta instalado..." -ForegroundColor Yellow
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue

if ($gcloudPath) {
    Write-Host "[OK] Google Cloud CLI ja esta instalado!" -ForegroundColor Green
    Write-Host "   Versao:" -ForegroundColor Yellow
    gcloud version
    Write-Host ""
    Write-Host "Para atualizar, execute: gcloud components update" -ForegroundColor Cyan
    exit 0
}

Write-Host "[!] Google Cloud CLI nao encontrado. Iniciando instalacao..." -ForegroundColor Yellow
Write-Host ""

# Verificar se e PowerShell 5.1 ou superior
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -lt 5) {
    Write-Host "[ERRO] Requer PowerShell 5.1 ou superior!" -ForegroundColor Red
    Write-Host "   Versao atual: $psVersion" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] PowerShell $psVersion detectado" -ForegroundColor Green
Write-Host ""

# URL do instalador
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

Write-Host "Baixando instalador do Google Cloud SDK..." -ForegroundColor Yellow
Write-Host "   URL: $installerUrl" -ForegroundColor Gray
Write-Host "   Destino: $installerPath" -ForegroundColor Gray
Write-Host ""

try {
    # Baixar instalador
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "[OK] Download concluido!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERRO] Erro ao baixar instalador!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternativa: Baixe manualmente em:" -ForegroundColor Cyan
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor White
    exit 1
}

Write-Host "Iniciando instalacao..." -ForegroundColor Yellow
Write-Host "   Isso abrira o instalador grafico." -ForegroundColor Gray
Write-Host "   Siga as instrucoes na tela." -ForegroundColor Gray
Write-Host ""

# Executar instalador
Start-Process -FilePath $installerPath -Wait

Write-Host ""
Write-Host "Aguardando instalacao concluir..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar se foi instalado
Write-Host ""
Write-Host "Verificando instalacao..." -ForegroundColor Yellow

# Atualizar PATH na sessao atual
$gcloudPath1 = "C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"
$gcloudPath2 = "$env:USERPROFILE\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

if (Test-Path $gcloudPath1) {
    $env:Path += ";$gcloudPath1"
    Write-Host "[OK] Google Cloud SDK encontrado em: $gcloudPath1" -ForegroundColor Green
} elseif (Test-Path $gcloudPath2) {
    $env:Path += ";$gcloudPath2"
    Write-Host "[OK] Google Cloud SDK encontrado em: $gcloudPath2" -ForegroundColor Green
} else {
    Write-Host "[!] Caminho padrao nao encontrado. Verifique manualmente." -ForegroundColor Yellow
}

# Verificar se gcloud esta disponivel agora
Start-Sleep -Seconds 2
$gcloudCheck = Get-Command gcloud -ErrorAction SilentlyContinue

if ($gcloudCheck) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  INSTALACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Inicializar o gcloud:" -ForegroundColor Cyan
    Write-Host "   gcloud init" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Fazer login:" -ForegroundColor Cyan
    Write-Host "   gcloud auth login" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Configurar projeto:" -ForegroundColor Cyan
    Write-Host "   gcloud config set project monpec-sistema-rural" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Verificar versao:" -ForegroundColor Cyan
    Write-Host "   gcloud version" -ForegroundColor White
    Write-Host ""
    
    # Tentar mostrar versao
    try {
        Write-Host "Versao instalada:" -ForegroundColor Yellow
        gcloud version
    } catch {
        Write-Host "[!] Reinicie o PowerShell para usar o gcloud" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[!] Instalacao pode ter sido concluida, mas o gcloud nao esta no PATH atual." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Solucoes:" -ForegroundColor Cyan
    Write-Host "   1. Feche e reabra o PowerShell" -ForegroundColor White
    Write-Host "   2. Ou adicione manualmente ao PATH:" -ForegroundColor White
    Write-Host "      C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. Depois execute:" -ForegroundColor White
    Write-Host "      gcloud init" -ForegroundColor Gray
    Write-Host ""
}

# Limpar arquivo temporario
if (Test-Path $installerPath) {
    Write-Host "Limpando arquivo temporario..." -ForegroundColor Yellow
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "[OK] Processo concluido!" -ForegroundColor Green
Write-Host ""
