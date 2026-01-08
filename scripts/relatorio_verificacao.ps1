Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RELATÓRIO DE VERIFICAÇÃO COMPLETA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Arquivos Essenciais
Write-Host "1. ARQUIVOS ESSENCIAIS:" -ForegroundColor Yellow
$essenciais = @{
    "manage.py" = "Script Django"
    "requirements.txt" = "Dependências principais"
    "requirements-dev.txt" = "Dependências desenvolvimento"
    "requirements_producao.txt" = "Dependências produção"
    "entrypoint.sh" = "Script entrada container"
    "Dockerfile" = "Configuração Docker"
    "Dockerfile.prod" = "Configuração Docker produção"
    "app.yaml" = "Configuração GCP"
    ".gitignore" = "Git ignore"
    "README.md" = "Documentação"
}
foreach ($item in $essenciais.GetEnumerator()) {
    $status = if (Test-Path $item.Key) { "" } else { "" }
    Write-Host "  $status $($item.Key) - $($item.Value)" -ForegroundColor $(if ($status -eq "") { "Green" } else { "Red" })
}

# 2. Estrutura de Pastas
Write-Host "`n2. ESTRUTURA DE PASTAS:" -ForegroundColor Yellow
$pastas = @("sistema_rural", "gestao_rural", "templates", "static", "scripts", "docs", "bin")
foreach ($pasta in $pastas) {
    $status = if (Test-Path $pasta) { "" } else { "" }
    Write-Host "  $status $pasta/" -ForegroundColor $(if ($status -eq "") { "Green" } else { "Red" })
}

# 3. Verificação Requirements
Write-Host "`n3. VERIFICAÇÃO REQUIREMENTS:" -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $req = Get-Content "requirements.txt" | Where-Object { $_ -match "^[A-Za-z]" }
    Write-Host "   requirements.txt: $($req.Count) dependências" -ForegroundColor Green
}
if (Test-Path "requirements_producao.txt") {
    $reqProd = Get-Content "requirements_producao.txt" | Where-Object { $_ -match "^[A-Za-z]" }
    Write-Host "   requirements_producao.txt: $($reqProd.Count) dependências" -ForegroundColor Green
}

# 4. Verificação Dockerfiles
Write-Host "`n4. VERIFICAÇÃO DOCKERFILES:" -ForegroundColor Yellow
if (Test-Path "Dockerfile") {
    $docker = Get-Content "Dockerfile" -Raw
    if ($docker -match "requirements") { Write-Host "   Dockerfile referencia requirements" -ForegroundColor Green }
    if ($docker -match "entrypoint") { Write-Host "   Dockerfile usa entrypoint.sh" -ForegroundColor Green }
}
if (Test-Path "Dockerfile.prod") {
    $dockerProd = Get-Content "Dockerfile.prod" -Raw
    if ($dockerProd -match "requirements") { Write-Host "   Dockerfile.prod referencia requirements" -ForegroundColor Green }
}

# 5. Verificação Settings Django
Write-Host "`n5. VERIFICAÇÃO SETTINGS DJANGO:" -ForegroundColor Yellow
$settings = @("sistema_rural\settings.py", "sistema_rural\settings_gcp.py", "sistema_rural\wsgi.py")
foreach ($s in $settings) {
    $status = if (Test-Path $s) { "" } else { "" }
    Write-Host "  $status $s" -ForegroundColor $(if ($status -eq "") { "Green" } else { "Yellow" })
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "VERIFICAÇÃO CONCLUÍDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
