# Instalar Google Cloud SDK
# Script para instalar o gcloud CLI no Windows

Write-Host "INSTALANDO GOOGLE CLOUD SDK" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Verificar se ja esta instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if ($gcloudPath) {
    Write-Host "Google Cloud SDK ja esta instalado!" -ForegroundColor Green
    gcloud --version
    exit 0
}

Write-Host "Baixando instalador do Google Cloud SDK..." -ForegroundColor Yellow

# URL do instalador
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

try {
    # Baixar instalador
    Write-Host "  Baixando de: $installerUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Host "Download concluido!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando instalacao..." -ForegroundColor Yellow
    Write-Host "  (Siga as instrucoes na janela que abrir)" -ForegroundColor Gray
    Write-Host ""
    
    # Executar instalador
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host ""
    Write-Host "Aguardando instalacao..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Verificar instalacao
    Start-Sleep -Seconds 3
    $gcloudCheck = Get-Command gcloud -ErrorAction SilentlyContinue
    
    if ($gcloudCheck) {
        Write-Host ""
        Write-Host "Google Cloud SDK instalado com sucesso!" -ForegroundColor Green
        Write-Host ""
        gcloud --version
        Write-Host ""
        Write-Host "Proximos passos:" -ForegroundColor Cyan
        Write-Host "  1. Reinicie o terminal/PowerShell" -ForegroundColor Gray
        Write-Host "  2. Execute: gcloud init" -ForegroundColor Gray
        Write-Host "  3. Execute: gcloud auth login" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host "Instalacao concluida, mas gcloud nao foi encontrado no PATH" -ForegroundColor Yellow
        Write-Host "  Tente reiniciar o terminal e executar: gcloud --version" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Ou adicione manualmente ao PATH:" -ForegroundColor Gray
        Write-Host "  C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "Erro ao baixar/instalar:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternativa: Instale manualmente" -ForegroundColor Yellow
    Write-Host "  1. Acesse: https://cloud.google.com/sdk/docs/install" -ForegroundColor Gray
    Write-Host "  2. Baixe o instalador para Windows" -ForegroundColor Gray
    Write-Host "  3. Execute o instalador" -ForegroundColor Gray
    exit 1
}
