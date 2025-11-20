param(
    [string]$Python = "python",
    [string]$Usuario = "admin",
    [int]$Ano = (Get-Date).Year
)

Write-Host "==> Aplicando migrações (manage.py migrate)"
& $Python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao aplicar migrações."
}

Write-Host "==> Executando seed do planejamento (usuario=$Usuario ano=$Ano)"
& $Python manage.py seed_planejamento --usuario $Usuario --ano $Ano
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao executar seed_planejamento."
}

Write-Host ""
Write-Host "Rotina finalizada. Acesse http://localhost:8000 após iniciar o servidor (manage.py runserver)."










