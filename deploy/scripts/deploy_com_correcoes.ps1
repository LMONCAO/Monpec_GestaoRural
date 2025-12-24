# Script para fazer deploy após build completar
Write-Host "Verificando status do build..." -ForegroundColor Cyan

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $status = (gcloud builds list --limit=1 --project=monpec-sistema-rural --format="value(status)" --sort-by=~createTime)
    
    if ($status -eq "SUCCESS") {
        Write-Host "Build concluido! Fazendo deploy..." -ForegroundColor Green
        gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --platform managed --allow-unauthenticated --project=monpec-sistema-rural
        
        Write-Host ""
        Write-Host "Deploy concluido!" -ForegroundColor Green
        Write-Host "Acesse: https://monpec-29862706245.us-central1.run.app" -ForegroundColor Cyan
        break
    }
    elseif ($status -eq "FAILURE") {
        Write-Host "Build falhou. Verifique os logs." -ForegroundColor Red
        break
    }
    else {
        $attempt++
        Write-Host "Build em andamento... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Host "Timeout aguardando build. Execute novamente mais tarde." -ForegroundColor Yellow
}

