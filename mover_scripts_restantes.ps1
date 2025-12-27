# Mover todos os scripts restantes para scripts/temp_para_revisao/

$scriptsRestantes = Get-ChildItem -Path . -Include *.ps1,*.sh,*.bat -File | Where-Object { 
    $_.DirectoryName -eq (Get-Location).Path -and
    $_.Name -ne "manage.py" -and
    $_.Name -notlike "organizar_*" -and
    $_.Name -notlike "limpar_*" -and
    $_.Name -notlike "finalizar_*" -and
    $_.Name -notlike "mover_*"
}

foreach ($script in $scriptsRestantes) {
    try {
        Move-Item -Path $script.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
        Write-Host "[OK] Movido: $($script.Name)" -ForegroundColor Green
    } catch {
        Write-Host "[ERRO] Erro ao mover $($script.Name) : $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Total movido: $($scriptsRestantes.Count) scripts" -ForegroundColor Cyan





































