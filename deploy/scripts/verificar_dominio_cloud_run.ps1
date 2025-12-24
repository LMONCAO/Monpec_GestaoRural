# Script para verificar status do dominio monpec.com.br no Google Cloud Run

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICAR DOMINIO MONPEC.COM.BR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Variaveis
$DOMAIN = "monpec.com.br"
$REGION = "us-central1"

# Verificar mapeamento no Cloud Run
Write-Host "1. Verificando mapeamento no Cloud Run..." -ForegroundColor Yellow
$mappingResult = gcloud run domain-mappings describe $DOMAIN --region $REGION --format="json" 2>&1
if ($LASTEXITCODE -eq 0) {
    $mapping = $mappingResult | ConvertFrom-Json
    
    if ($mapping) {
        Write-Host "OK Mapeamento encontrado" -ForegroundColor Green
        Write-Host "  Dominio: $($mapping.metadata.name)" -ForegroundColor White
        Write-Host "  Status: $($mapping.status.conditions[0].status)" -ForegroundColor White
        Write-Host "  Tipo: $($mapping.status.conditions[0].type)" -ForegroundColor White
        
        if ($mapping.status.resourceRecords) {
            Write-Host ""
            Write-Host "  Registros DNS necessarios:" -ForegroundColor Yellow
            foreach ($record in $mapping.status.resourceRecords) {
                Write-Host "    Tipo: $($record.type) | Nome: $($record.name) | Valor: $($record.rrdata)" -ForegroundColor Cyan
            }
        }
    }
} else {
    Write-Host "X Mapeamento nao encontrado ou erro ao verificar" -ForegroundColor Red
    Write-Host "  Execute: .\configurar_dominio_cloud_run.ps1" -ForegroundColor Yellow
}

Write-Host ""

# Verificar DNS CNAME
Write-Host "2. Verificando propagacao DNS (CNAME)..." -ForegroundColor Yellow
$dnsResult = nslookup -type=CNAME $DOMAIN 2>&1

if ($dnsResult -match "ghs\.googlehosted\.com") {
    Write-Host "OK DNS CNAME configurado corretamente" -ForegroundColor Green
    Write-Host "  CNAME aponta para: ghs.googlehosted.com" -ForegroundColor White
} else {
    Write-Host "ATENCAO DNS CNAME pode nao estar configurado ou nao propagado ainda" -ForegroundColor Yellow
    Write-Host "  Verifique manualmente com: nslookup -type=CNAME $DOMAIN" -ForegroundColor White
}

Write-Host ""

# Verificar DNS TXT (Google Search Console)
Write-Host "3. Verificando registro TXT (Google Search Console)..." -ForegroundColor Yellow
$txtResult = nslookup -type=TXT $DOMAIN 2>&1
$verificationCode = "vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk"

if ($txtResult -match "google-site-verification" -and $txtResult -match $verificationCode) {
    Write-Host "OK Registro TXT de verificacao encontrado" -ForegroundColor Green
    Write-Host "  Google Search Console pode verificar o dominio" -ForegroundColor White
} else {
    Write-Host "ATENCAO Registro TXT nao encontrado ou nao propagado ainda" -ForegroundColor Yellow
    Write-Host "  Adicione no Registro.br: TXT com valor google-site-verification=$verificationCode" -ForegroundColor White
    Write-Host "  Verifique manualmente com: nslookup -type=TXT $DOMAIN" -ForegroundColor White
}

Write-Host ""

# Verificar acesso HTTP
Write-Host "4. Verificando acesso HTTP..." -ForegroundColor Yellow
$url = "https://$DOMAIN"
try {
    $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10 -ErrorAction SilentlyContinue
    
    if ($response.StatusCode -eq 200) {
        Write-Host "OK Site acessivel via HTTPS" -ForegroundColor Green
        Write-Host "  Status: $($response.StatusCode)" -ForegroundColor White
    } else {
        Write-Host "ATENCAO Site retornou status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    $errorMsg = $_.Exception.Message
    if ($errorMsg -match "SSL") {
        Write-Host "ATENCAO Erro SSL - Certificado pode estar sendo gerado" -ForegroundColor Yellow
    } elseif ($errorMsg -match "timeout") {
        Write-Host "ATENCAO Timeout - DNS pode nao estar propagado ainda" -ForegroundColor Yellow
    } else {
        Write-Host "ATENCAO Site nao acessivel ainda: $errorMsg" -ForegroundColor Yellow
    }
}

Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar manualmente:" -ForegroundColor Yellow
Write-Host "  DNS CNAME: nslookup -type=CNAME $DOMAIN" -ForegroundColor Cyan
Write-Host "  DNS TXT: nslookup -type=TXT $DOMAIN" -ForegroundColor Cyan
Write-Host "  Status: gcloud run domain-mappings describe $DOMAIN --region $REGION" -ForegroundColor Cyan
$urlText = "https://$DOMAIN"
Write-Host "  Acesso: $urlText" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentacao completa:" -ForegroundColor Yellow
Write-Host "  - Configurar dominio: CONFIGURAR_DOMINIO_MONPEC_COM_BR.md" -ForegroundColor Cyan
Write-Host "  - Verificacao Google: CONFIGURAR_VERIFICACAO_GOOGLE_SEARCH_CONSOLE.md" -ForegroundColor Cyan
Write-Host ""
