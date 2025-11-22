# Script para configurar dominio monpec.com.br no Google Cloud Run
# Execute este script apos configurar o DNS no seu provedor

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR DOMINIO MONPEC.COM.BR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud esta instalado
$gcloudCheck = gcloud --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "X Google Cloud SDK nao encontrado!" -ForegroundColor Red
    Write-Host "  Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "OK Google Cloud SDK encontrado" -ForegroundColor Green
}

# Variaveis
$SERVICE_NAME = "monpec"
$DOMAIN = "monpec.com.br"
$REGION = "us-central1"

Write-Host "Configuracoes:" -ForegroundColor Yellow
Write-Host "  Servico: $SERVICE_NAME" -ForegroundColor White
Write-Host "  Dominio: $DOMAIN" -ForegroundColor White
Write-Host "  Regiao: $REGION" -ForegroundColor White
Write-Host ""

# Verificar se o servico existe
Write-Host "Verificando servico Cloud Run..." -ForegroundColor Yellow
$service = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Servico encontrado: $service" -ForegroundColor Green
} else {
    Write-Host "X Servico nao encontrado!" -ForegroundColor Red
    Write-Host "  Execute primeiro o deploy do servico." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Verificar se o mapeamento ja existe
Write-Host "Verificando mapeamento de dominio existente..." -ForegroundColor Yellow
$existingMapping = gcloud run domain-mappings describe $DOMAIN --region $REGION 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "ATENCAO Mapeamento ja existe!" -ForegroundColor Yellow
    Write-Host "  Deseja continuar mesmo assim? (S/N)" -ForegroundColor Yellow
    $continue = Read-Host
    if ($continue -ne "S" -and $continue -ne "s") {
        Write-Host "Operacao cancelada." -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "OK Nenhum mapeamento existente encontrado" -ForegroundColor Green
}

Write-Host ""

# Criar mapeamento de dominio
Write-Host "Criando mapeamento de dominio..." -ForegroundColor Yellow
Write-Host "  Isso pode levar alguns minutos..." -ForegroundColor Gray

$mappingResult = gcloud run domain-mappings create --service $SERVICE_NAME --domain $DOMAIN --region $REGION 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Mapeamento criado com sucesso!" -ForegroundColor Green
    Write-Host ""
    
    # Extrair informacoes do DNS
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  CONFIGURACAO DNS NECESSARIA" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Configure os seguintes registros DNS no seu provedor:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Registro CNAME:" -ForegroundColor White
    Write-Host "  Nome: @ (ou monpec.com.br)" -ForegroundColor Cyan
    Write-Host "  Tipo: CNAME" -ForegroundColor Cyan
    Write-Host "  Valor: ghs.googlehosted.com" -ForegroundColor Cyan
    Write-Host "  TTL: 3600" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Registro CNAME para www:" -ForegroundColor White
    Write-Host "  Nome: www" -ForegroundColor Cyan
    Write-Host "  Tipo: CNAME" -ForegroundColor Cyan
    Write-Host "  Valor: ghs.googlehosted.com" -ForegroundColor Cyan
    Write-Host "  TTL: 3600" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "IMPORTANTE:" -ForegroundColor Yellow
    Write-Host "  1. Configure o DNS no seu provedor (Registro.br, GoDaddy, etc.)" -ForegroundColor White
    Write-Host "  2. Aguarde a propagacao DNS (1-48 horas, geralmente 1-2 horas)" -ForegroundColor White
    Write-Host "  3. O SSL sera configurado automaticamente apos a propagacao" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "X Erro ao criar mapeamento!" -ForegroundColor Red
    Write-Host $mappingResult -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verificar status do mapeamento
Write-Host "Verificando status do mapeamento..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$mappingStatus = gcloud run domain-mappings describe $DOMAIN --region $REGION --format="value(status.conditions[0].status)" 2>&1
if ($LASTEXITCODE -eq 0) {
    $statusColor = if ($mappingStatus -eq "True") { "Green" } else { "Yellow" }
    Write-Host "Status: $mappingStatus" -ForegroundColor $statusColor
    
    if ($mappingStatus -ne "True") {
        Write-Host ""
        Write-Host "ATENCAO O mapeamento esta aguardando configuracao DNS." -ForegroundColor Yellow
        Write-Host "  Apos configurar o DNS, o status mudara para ACTIVE." -ForegroundColor White
    }
} else {
    Write-Host "ATENCAO Nao foi possivel verificar o status ainda." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PROXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configure o DNS no seu provedor de dominio" -ForegroundColor White
Write-Host "2. Aguarde a propagacao DNS (verifique com: dig monpec.com.br CNAME)" -ForegroundColor White
Write-Host "3. Verifique o status com:" -ForegroundColor White
Write-Host "   gcloud run domain-mappings describe $DOMAIN --region $REGION" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para mais informacoes, consulte: CONFIGURAR_DOMINIO_MONPEC_COM_BR.md" -ForegroundColor DarkGray
Write-Host ""
