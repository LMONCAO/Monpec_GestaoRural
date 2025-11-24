# Script simples para rodar o sistema em localhost
Write-Host "Iniciando servidor Django em localhost..." -ForegroundColor Cyan
Write-Host "Acesse: http://localhost:8000" -ForegroundColor Green
Write-Host ""

# Ativar ambiente virtual se existir
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
} elseif (Test-Path "env\Scripts\Activate.ps1") {
    & .\env\Scripts\Activate.ps1
}

# Rodar servidor
python manage.py runserver 0.0.0.0:8000

