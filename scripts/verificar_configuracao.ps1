# Verificação de Configuração
Write-Host "Verificando configuração..." -ForegroundColor Cyan

$erros = @()
$sucessos = @()

# Arquivos essenciais
$essenciais = @("manage.py", "requirements.txt", "entrypoint.sh", "Dockerfile", "Dockerfile.prod")
foreach ($f in $essenciais) {
    if (Test-Path $f) { $sucessos += " $f" } else { $erros += " $f" }
}

# Pastas essenciais
$pastas = @("sistema_rural", "gestao_rural", "templates", "static")
foreach ($p in $pastas) {
    if (Test-Path $p) { $sucessos += " Pasta $p" } else { $erros += " Pasta $p" }
}

Write-Host "`nSucessos: $($sucessos.Count)" -ForegroundColor Green
Write-Host "Erros: $($erros.Count)" -ForegroundColor Red
