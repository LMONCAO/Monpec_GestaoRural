# ========================================
# SCRIPT PARA FINALIZAR ORGANIZACAO
# ========================================

Write-Host "Finalizando organizacao do projeto..." -ForegroundColor Green
Write-Host ""

# Mover arquivos Python restantes para scripts/temp_para_revisao/
Write-Host "Movendo arquivos Python restantes..." -ForegroundColor Cyan

$arquivosPythonRestantes = Get-ChildItem -Path . -Filter "*.py" -File | Where-Object { 
    $_.DirectoryName -eq (Get-Location).Path -and
    $_.Name -ne "manage.py" -and
    $_.Name -ne "limpar_arquivos_desnecessarios.ps1" -and
    $_.Name -ne "organizar_projeto.ps1" -and
    $_.Name -ne "finalizar_organizacao.ps1"
}

$contador = 0
foreach ($arquivo in $arquivosPythonRestantes) {
    try {
        Move-Item -Path $arquivo.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
        Write-Host "  [OK] Movido: $($arquivo.Name)" -ForegroundColor Green
        $contador++
    } catch {
        Write-Host "  [AVISO] Erro ao mover $($arquivo.Name) : $_" -ForegroundColor Yellow
    }
}

Write-Host "  [INFO] $contador arquivos Python movidos" -ForegroundColor Cyan
Write-Host ""

# Mover arquivos .sh e .ps1 restantes (exceto os que já estão organizados)
Write-Host "Movendo scripts restantes..." -ForegroundColor Cyan

$scriptsRestantes = Get-ChildItem -Path . -Include *.sh,*.ps1 -File | Where-Object {
    $_.DirectoryName -eq (Get-Location).Path -and
    $_.Name -notlike "organizar_*" -and
    $_.Name -notlike "limpar_*" -and
    $_.Name -notlike "finalizar_*"
}

$contadorScripts = 0
foreach ($script in $scriptsRestantes) {
    try {
        Move-Item -Path $script.FullName -Destination "scripts/temp_para_revisao/" -Force -ErrorAction Stop
        Write-Host "  [OK] Movido: $($script.Name)" -ForegroundColor Green
        $contadorScripts++
    } catch {
        Write-Host "  [AVISO] Erro ao mover $($script.Name) : $_" -ForegroundColor Yellow
    }
}

Write-Host "  [INFO] $contadorScripts scripts movidos" -ForegroundColor Cyan
Write-Host ""

# Mover outros arquivos de documentação que possam ter ficado
Write-Host "Organizando documentacao restante..." -ForegroundColor Cyan

$docsRestantes = Get-ChildItem -Path . -Filter "*.md" -File | Where-Object {
    $_.DirectoryName -eq (Get-Location).Path
}

foreach ($doc in $docsRestantes) {
    try {
        Move-Item -Path $doc.FullName -Destination "docs/" -Force -ErrorAction Stop
        Write-Host "  [OK] Movido: $($doc.Name)" -ForegroundColor Green
    } catch {
        Write-Host "  [AVISO] Erro ao mover $($doc.Name) : $_" -ForegroundColor Yellow
    }
}

Write-Host ""

# Verificar se existem pastas duplicadas para excluir
Write-Host "Verificando pastas duplicadas..." -ForegroundColor Cyan

$pastasDuplicadas = @("monpec_clean", "monpec_local", "monpec_projetista_clean", "monpec_sistema_completo")

foreach ($pasta in $pastasDuplicadas) {
    if (Test-Path $pasta) {
        Write-Host "  [INFO] Pasta encontrada: $pasta" -ForegroundColor Yellow
        $confirmar = Read-Host "  Deseja excluir $pasta? (S/N)"
        if ($confirmar -eq "S" -or $confirmar -eq "s") {
            try {
                Remove-Item -Path $pasta -Recurse -Force -ErrorAction Stop
                Write-Host "  [OK] Excluida: $pasta" -ForegroundColor Green
            } catch {
                Write-Host "  [AVISO] Erro ao excluir $pasta : $_" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "FINALIZACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Estrutura organizada:" -ForegroundColor Cyan
Write-Host "  - docs/ (documentacao)" -ForegroundColor White
Write-Host "  - scripts/manutencao/ (scripts uteis)" -ForegroundColor White
Write-Host "  - scripts/temp_para_revisao/ (scripts temporarios)" -ForegroundColor White
Write-Host "  - deploy/scripts/ (scripts de deploy)" -ForegroundColor White
Write-Host "  - deploy/config/ (configuracoes)" -ForegroundColor White
Write-Host ""
Write-Host "Total de arquivos organizados: $($contador + $contadorScripts)" -ForegroundColor Green
Write-Host ""



















