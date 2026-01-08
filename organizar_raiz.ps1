# Script para organizar arquivos da raiz do projeto
# Move arquivos para pastas apropriadas mantendo apenas o essencial na raiz

Write-Host "Organizando arquivos da raiz do projeto..." -ForegroundColor Green

# Criar estrutura de pastas se não existir
$pastas = @("scripts", "bin", "docs\deploy", "backups")
foreach ($pasta in $pastas) {
    if (-not (Test-Path $pasta)) {
        New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        Write-Host "Criada pasta: $pasta" -ForegroundColor Yellow
    }
}

# Mover scripts .bat para scripts/
Write-Host "Movendo scripts .bat..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.bat" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "scripts\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Mover scripts .ps1 para scripts/
Write-Host "Movendo scripts .ps1..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.ps1" -File | ForEach-Object {
    if ($_.Name -ne "organizar_raiz.ps1") {
        Move-Item -Path $_.FullName -Destination "scripts\" -Force
        Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
    }
}

# Mover scripts .sh para scripts/
Write-Host "Movendo scripts .sh..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.sh" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "scripts\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Mover DLLs para bin/
Write-Host "Movendo arquivos .dll..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.dll" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "bin\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Mover executáveis para bin/
Write-Host "Movendo executáveis..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.exe" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "bin\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Mover arquivo cloud-sql-proxy.exe.exe se existir
if (Test-Path "cloud-sql-proxy.exe.exe") {
    Move-Item -Path "cloud-sql-proxy.exe.exe" -Destination "bin\" -Force
    Write-Host "  Movido: cloud-sql-proxy.exe.exe" -ForegroundColor Gray
}

# Mover arquivos de documentação .txt para docs/deploy/
Write-Host "Movendo arquivos de documentação .txt..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.txt" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "docs\deploy\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Mover arquivos SQL para backups/
Write-Host "Movendo arquivos .sql..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.sql" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "backups\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Remover arquivos temporários
Write-Host "Removendo arquivos temporários..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "temp_*.txt" -File | ForEach-Object {
    Remove-Item -Path $_.FullName -Force
    Write-Host "  Removido: $($_.Name)" -ForegroundColor Gray
}

# Mover arquivos .md de documentação para docs/ (exceto README)
Write-Host "Movendo arquivos de documentação .md..." -ForegroundColor Cyan
Get-ChildItem -Path "." -Filter "*.md" -File | ForEach-Object {
    if ($_.Name -notlike "README*") {
        Move-Item -Path $_.FullName -Destination "docs\" -Force
        Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
    }
}

# Mover scripts Python para scripts/ (exceto manage.py e arquivos de configuração importantes)
Write-Host "Movendo scripts Python..." -ForegroundColor Cyan
$scriptsPython = @("atualizar_senha_env.py", "configurar_postgres_agora.py", "criar_banco_e_migrar.py", 
                   "diagnosticar_e_corrigir_sistema.py", "diagnosticar_fotos_cloud.py", "fix_database.py",
                   "setup_postgres.py", "testar_criacao_demo_completo.py", "testar_criacao_usuario_demo.py",
                   "verificar_e_corrigir_banco.py")
foreach ($script in $scriptsPython) {
    if (Test-Path $script) {
        Move-Item -Path $script -Destination "scripts\" -Force
        Write-Host "  Movido: $script" -ForegroundColor Gray
    }
}

# Mover arquivos de configuração para pasta config/ (se necessário)
# Manter arquivos essenciais como Dockerfile, app.yaml, etc na raiz

# Mover github-actions-key.json para scripts/ (se existir)
if (Test-Path "github-actions-key.json") {
    Move-Item -Path "github-actions-key.json" -Destination "scripts\" -Force
    Write-Host "  Movido: github-actions-key.json" -ForegroundColor Gray
}

# Mover arquivos .conf e .service para scripts/config/
if (-not (Test-Path "scripts\config")) {
    New-Item -ItemType Directory -Path "scripts\config" -Force | Out-Null
}
Get-ChildItem -Path "." -Filter "*.conf" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "scripts\config\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}
Get-ChildItem -Path "." -Filter "*.service" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "scripts\config\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

# Mover arquivos PDF para docs/
Get-ChildItem -Path "." -Filter "*.pdf" -File | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "docs\" -Force
    Write-Host "  Movido: $($_.Name)" -ForegroundColor Gray
}

Write-Host "`nOrganizacao concluida!" -ForegroundColor Green
Write-Host "`nArquivos mantidos na raiz (essenciais):" -ForegroundColor Yellow
Write-Host "  - manage.py" -ForegroundColor White
Write-Host "  - requirements.txt, requirements-dev.txt, requirements_producao.txt" -ForegroundColor White
Write-Host "  - pyproject.toml, pytest.ini" -ForegroundColor White
Write-Host "  - entrypoint.sh" -ForegroundColor White
Write-Host "  - README_POSTGRESQL.md" -ForegroundColor White
Write-Host "  - Pastas do projeto (api/, gestao_rural/, sistema_rural/, etc.)" -ForegroundColor White

Write-Host "`nArquivos organizados:" -ForegroundColor Yellow
Write-Host "  - Scripts (.bat, .ps1, .sh) -> scripts/" -ForegroundColor White
Write-Host "  - DLLs e executáveis -> bin/" -ForegroundColor White
Write-Host "  - Documentação (.txt) -> docs/deploy/" -ForegroundColor White
Write-Host "  - Arquivos SQL -> backups/" -ForegroundColor White
Write-Host "  - Arquivos temporários -> removidos" -ForegroundColor White

