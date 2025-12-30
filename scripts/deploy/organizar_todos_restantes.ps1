# ========================================
# ORGANIZAR TODOS OS ARQUIVOS RESTANTES
# ========================================

Write-Host "Organizando TODOS os arquivos restantes na raiz..." -ForegroundColor Green
Write-Host ""

# Definir arquivos que devem FICAR na raiz (essenciais)
$arquivosEssenciais = @(
    "manage.py",
    "requirements.txt",
    ".gitignore",
    ".dockerignore",
    ".env_producao",
    "Dockerfile",
    "vercel.json",
    "db.sqlite3",
    "organizar_projeto.ps1",
    "limpar_arquivos_desnecessarios.ps1",
    "organizar_todos_restantes.ps1"
)

# Garantir que as pastas existam
$pastasDestino = @(
    "scripts/temp_para_revisao",
    "scripts/manutencao",
    "deploy/scripts",
    "docs"
)

foreach ($pasta in $pastasDestino) {
    if (-not (Test-Path $pasta)) {
        New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        Write-Host "[OK] Criada pasta: $pasta" -ForegroundColor Green
    }
}

Write-Host ""

# 1. Mover TODOS os scripts .ps1, .bat, .sh (exceto os essenciais)
Write-Host "Movendo scripts .ps1, .bat, .sh..." -ForegroundColor Cyan

$extensoesScripts = @("*.ps1", "*.bat", "*.sh")
$contadorScripts = 0

foreach ($extensao in $extensoesScripts) {
    $arquivos = Get-ChildItem -Path . -Filter $extensao -File | Where-Object {
        $arquivosEssenciais -notcontains $_.Name -and
        $_.DirectoryName -eq (Get-Location).Path
    }
    
    foreach ($arquivo in $arquivos) {
        try {
            Move-Item -Path $arquivo.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
            Write-Host "  [OK] Movido: $($arquivo.Name)" -ForegroundColor Green
            $contadorScripts++
        } catch {
            Write-Host "  [ERRO] Erro ao mover $($arquivo.Name) : $_" -ForegroundColor Red
        }
    }
}

Write-Host "  Total de scripts movidos: $contadorScripts" -ForegroundColor Cyan
Write-Host ""

# 2. Mover TODOS os arquivos Python (exceto manage.py)
Write-Host "Movendo arquivos Python..." -ForegroundColor Cyan

$arquivosPython = Get-ChildItem -Path . -Filter "*.py" -File | Where-Object {
    $_.Name -ne "manage.py" -and
    $_.DirectoryName -eq (Get-Location).Path
}

$contadorPython = 0
foreach ($arquivo in $arquivosPython) {
    try {
        Move-Item -Path $arquivo.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
        Write-Host "  [OK] Movido: $($arquivo.Name)" -ForegroundColor Green
        $contadorPython++
    } catch {
        Write-Host "  [ERRO] Erro ao mover $($arquivo.Name) : $_" -ForegroundColor Red
    }
}

Write-Host "  Total de arquivos Python movidos: $contadorPython" -ForegroundColor Cyan
Write-Host ""

# 3. Mover arquivos de documentação (.md, .pdf)
Write-Host "Movendo arquivos de documentacao..." -ForegroundColor Cyan

$extensoesDocs = @("*.md", "*.pdf")
$contadorDocs = 0

foreach ($extensao in $extensoesDocs) {
    $arquivos = Get-ChildItem -Path . -Filter $extensao -File | Where-Object {
        $_.DirectoryName -eq (Get-Location).Path
    }
    
    foreach ($arquivo in $arquivos) {
        try {
            Move-Item -Path $arquivo.FullName -Destination "docs/" -Force -ErrorAction Stop
            Write-Host "  [OK] Movido: $($arquivo.Name)" -ForegroundColor Green
            $contadorDocs++
        } catch {
            Write-Host "  [ERRO] Erro ao mover $($arquivo.Name) : $_" -ForegroundColor Red
        }
    }
}

Write-Host "  Total de documentos movidos: $contadorDocs" -ForegroundColor Cyan
Write-Host ""

# 4. Mover arquivos .json, .js, .html (exceto vercel.json)
Write-Host "Movendo arquivos JSON, JS, HTML..." -ForegroundColor Cyan

$arquivosJson = Get-ChildItem -Path . -Filter "*.json" -File | Where-Object {
    $_.Name -ne "vercel.json" -and
    $_.DirectoryName -eq (Get-Location).Path
}

$arquivosJs = Get-ChildItem -Path . -Filter "*.js" -File | Where-Object {
    $_.DirectoryName -eq (Get-Location).Path
}

$arquivosHtml = Get-ChildItem -Path . -Filter "*.html" -File | Where-Object {
    $_.DirectoryName -eq (Get-Location).Path
}

$contadorOutros = 0
$todosArquivos = @()
$todosArquivos += $arquivosJson
$todosArquivos += $arquivosJs
$todosArquivos += $arquivosHtml

foreach ($arquivo in $todosArquivos) {
    try {
        Move-Item -Path $arquivo.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
        Write-Host "  [OK] Movido: $($arquivo.Name)" -ForegroundColor Green
        $contadorOutros++
    } catch {
        Write-Host "  [ERRO] Erro ao mover $($arquivo.Name) : $_" -ForegroundColor Red
    }
}

Write-Host "  Total de outros arquivos movidos: $contadorOutros" -ForegroundColor Cyan
Write-Host ""

# 5. Mover arquivos .zip, .tar.gz
Write-Host "Movendo arquivos compactados..." -ForegroundColor Cyan

$arquivosCompactados = Get-ChildItem -Path . -Include *.zip,*.tar.gz -File | Where-Object {
    $_.DirectoryName -eq (Get-Location).Path
}

$contadorCompactados = 0
foreach ($arquivo in $arquivosCompactados) {
    try {
        Move-Item -Path $arquivo.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
        Write-Host "  [OK] Movido: $($arquivo.Name)" -ForegroundColor Green
        $contadorCompactados++
    } catch {
        Write-Host "  [ERRO] Erro ao mover $($arquivo.Name) : $_" -ForegroundColor Red
    }
}

Write-Host "  Total de arquivos compactados movidos: $contadorCompactados" -ForegroundColor Cyan
Write-Host ""

# RESUMO
$totalMovidos = $contadorScripts + $contadorPython + $contadorDocs + $contadorOutros + $contadorCompactados

Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "ORGANIZACAO COMPLETA!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Resumo:" -ForegroundColor Cyan
Write-Host "  Scripts (.ps1, .bat, .sh): $contadorScripts" -ForegroundColor White
Write-Host "  Arquivos Python (.py): $contadorPython" -ForegroundColor White
Write-Host "  Documentacao (.md, .pdf): $contadorDocs" -ForegroundColor White
Write-Host "  Outros (.json, .js, .html): $contadorOutros" -ForegroundColor White
Write-Host "  Compactados (.zip, .tar.gz): $contadorCompactados" -ForegroundColor White
Write-Host ""
Write-Host "TOTAL: $totalMovidos arquivos organizados" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivos que permanecem na raiz (essenciais):" -ForegroundColor Cyan
foreach ($essencial in $arquivosEssenciais) {
    if (Test-Path $essencial) {
        Write-Host "  - $essencial" -ForegroundColor White
    }
}
Write-Host ""












































