# ========================================
# SCRIPT PARA ORGANIZAR PROJETO
# ========================================
# Este script organiza o projeto criando pastas e movendo/excluindo arquivos

Write-Host "ORGANIZANDO PROJETO" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Yellow
Write-Host ""

# Criar estrutura de pastas
Write-Host "Criando estrutura de pastas..." -ForegroundColor Cyan

$pastas = @(
    "docs",
    "docs/tecnicos",
    "docs/configuracao",
    "scripts/deploy",
    "scripts/manutencao",
    "scripts/temp_para_revisao",
    "deploy/scripts",
    "deploy/config"
)

foreach ($pasta in $pastas) {
    if (-not (Test-Path $pasta)) {
        New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        Write-Host "  [OK] Criada: $pasta" -ForegroundColor Green
    }
}

Write-Host ""

# 1. MOVER DOCUMENTAÇÃO
Write-Host "📄 Organizando documentação..." -ForegroundColor Cyan

$docsGerais = @(
    "README.md",
    "QUICK_START.md",
    "ESTADO_ATUAL_TRABALHO.md",
    "FLUXO_PROJECAO_COMPLETO.md",
    "FLUXO_PROJECAO_RESUMIDO.md",
    "COMO_ACESSAR_SISTEMA_MARCELO_SANGUINO.md",
    "RESUMO_SISTEMA_MARCELO_SANGUINO.md",
    "PLANO_SISTEMA_MARCELO_SANGUINO.md",
    "ANALISE_ARQUIVOS_PROJETO.md"
)

$docsTecnicos = @(
    "CALCULO_VENDAS_BEZERROS.md",
    "SIMULADOR_FLUXO_COMPLETO.md",
    "AUDITORIA_SISTEMA_CURRAL.md",
    "FLUXO_PERFEITO_CURRAL_V3.md",
    "VERIFICACAO_FLUXO_CURRAL_V3.md",
    "FLUXO_CURRAL_V3.md",
    "ESTUDO_RASTREABILIDADE_BOVINA_FORMULARIOS.md",
    "MELHORIAS_PDF_SISBOV.md",
    "DOCUMENTACAO_JUSTIFICATIVA_ENDIVIDAMENTO.md",
    "RELATORIO_ANALISE_SISTEMA.md",
    "RESUMO_LAYOUT_DRE_BALANCO.md",
    "RESUMO_IMPOSTOS_E_EXPORTACAO.md",
    "IMPLEMENTACAO_COMPLETA_RESUMO.md",
    "IMPLEMENTACOES_REALIZADAS.md"
)

$docsConfig = @(
    "CONFIGURACAO_BANCO_DADOS.md",
    "CONFIGURACAO_PADRAO_INVERNADA_GRANDE.md",
    "CONFIGURACAO_PADRAO_FAVO_MEL_GIRASSOL.md",
    "CONFIGURACAO_PADRAO_CANTA_GALO.md",
    "COMO_ATUALIZAR_CEPEA.md",
    "COMO_ATUALIZAR_REPOSITORIO.md",
    "COMO_IMPORTAR_BANCO_OUTRA_MAQUINA.md"
)

$docsResumos = @(
    "RESUMO_CONFIGURACAO.md",
    "RESUMO_FINAL_DADOS_CRIADOS.md",
    "RESUMO_DADOS_HISTORICOS_2022_2025.md",
    "RESUMO_CORRECOES_FATURAMENTO_VACAS.md",
    "RESUMO_CARGA_DADOS_VALIDACAO.md",
    "RESUMO_CORRECOES_FINAIS.md",
    "RESUMO_IMPLEMENTACAO_COMPLETA.md"
)

$docsCorrecoes = @(
    "CORRECAO_SIMULADOR_BRINCOS_ESTOQUE.md",
    "CORRECOES_SIMULADOR_CARREGAMENTO.md",
    "CORRIGIR_SISTEMA_CORRETO.md",
    "DIAGNOSTICO_RAPIDO_503.md",
    "PROBLEMAS_ENCONTRADOS_E_CORRECOES.md",
    "SOLUCAO_DEPLOY_CURRAL_V3.md",
    "SOLUCAO_ATUALIZAR_TELA_CURRAL.md",
    "SOLUCAO_404_CURRAL_V3.md",
    "INSTRUCOES_CORRECAO.md",
    "NOVA_REGRA_FAVO_MEL_2025.md",
    "AJUSTES_VISUAIS_TEMPLATE.md"
)

function Mover-Arquivo {
    param($arquivo, $destino)
    if (Test-Path $arquivo) {
        try {
            Move-Item -Path $arquivo -Destination $destino -Force -ErrorAction Stop
            Write-Host "  [OK] Movido: $arquivo -> $destino" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Erro ao mover $arquivo : $_" -ForegroundColor Yellow
        }
    }
}

foreach ($doc in $docsGerais) {
    Mover-Arquivo $doc "docs/"
}

foreach ($doc in $docsTecnicos) {
    Mover-Arquivo $doc "docs/tecnicos/"
}

foreach ($doc in $docsConfig) {
    Mover-Arquivo $doc "docs/configuracao/"
}

foreach ($doc in ($docsResumos + $docsCorrecoes)) {
    Mover-Arquivo $doc "docs/"
}

Write-Host ""

# 2. MOVER SCRIPTS DE DEPLOY
Write-Host "Organizando scripts de deploy..." -ForegroundColor Cyan

$scriptsDeploy = @(
    "deploy_*.ps1",
    "deploy_*.sh",
    "DEPLOY_*.sh",
    "DEPLOY_*.ps1",
    "ATUALIZAR_GITHUB.*",
    "atualizar_github.*",
    "atualizar_repositorio.*",
    "sincronizar_github.*",
    "fazer_push_github.*",
    "puxar_github.*",
    "VERIFICAR_STATUS_CLOUD_RUN.*",
    "verificar_deploy_*.*",
    "verificar_pre_deploy.*",
    "configurar_dominio.*",
    "CONFIGURAR_DOMINIO_CLOUD_RUN.*",
    "verificar_dominio_cloud_run.*",
    "DEPLOY_PASSO_A_PASSO.*",
    "COMANDOS_CLOUD_SHELL_PRONTOS.*",
    "COMANDOS_DEPLOY_COMPLETO.*",
    "CORRIGIR_REQUIREMENTS_DEPLOY.*",
    "CORRIGIR_AGORA_CLOUD_SHELL.*",
    "fix_deploy_issues.*",
    "fix_and_deploy.*"
)

foreach ($pattern in $scriptsDeploy) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        Mover-Arquivo $_.Name "deploy/scripts/"
    }
}

# Mover arquivos de configuração de deploy
$configDeploy = @("app.yaml", "cloudbuild.yaml")
foreach ($config in $configDeploy) {
    if (Test-Path $config) {
        Mover-Arquivo $config "deploy/config/"
    }
}

Write-Host ""

# 3. MOVER SCRIPTS DE MANUTENCAO UTEIS
Write-Host "Organizando scripts de manutencao..." -ForegroundColor Cyan

$scriptsManutencao = @(
    "backup_automatico.py",
    "INICIAR.*",
    "INSTALAR.*",
    "IMPORTAR_DADOS.*",
    "EXPORTAR_DADOS.*",
    "IMPORTAR_BANCO_OUTRA_MAQUINA.*"
)

foreach ($pattern in $scriptsManutencao) {
    Get-ChildItem -Path . -Filter $pattern -File | ForEach-Object {
        Mover-Arquivo $_.Name "scripts/manutencao/"
    }
}

Write-Host ""

# 4. MOVER SCRIPTS TEMPORARIOS PARA REVISAO
Write-Host "Movendo scripts temporarios para revisao..." -ForegroundColor Cyan

$scriptsTemp = @(
    "*corrigir*.py",
    "*corrigir*.ps1",
    "*corrigir*.sh",
    "*ajustar*.py",
    "*atualizar_*.py",
    "*configurar_*.py",
    "*criar_*.py",
    "*cadastrar_*.py",
    "*verificar_*.py",
    "*migrar_*.py",
    "*limpar_*.py",
    "*vincular_*.py",
    "*zerar_*.py",
    "*mover_*.py",
    "*gerar_*.py",
    "*melhorar_*.py",
    "*converter_*.py",
    "*copiar_*.py",
    "*completar_*.ps1",
    "*desenvolver_*.ps1",
    "*instalar_*.sh",
    "*CORRIGIR_*.bat",
    "*CORRIGIR_*.ps1",
    "*CORRIGIR_*.sh",
    "*EXECUTAR_*.bat",
    "*FORCAR_*.bat",
    "*FORCAR_*.ps1",
    "*INICIAR_*.bat",
    "*PARAR_*.bat",
    "*REGERAR_*.bat",
    "*REGERAR_*.bat",
    "*INTEGRAR_*.bat",
    "*CRIAR_BACKUP_*.bat",
    "*VERIFICAR_*.ps1",
    "*VERIFICAR_*.sh",
    "*testar_*.sh",
    "*diagnostico_*.sh",
    "*diagnostico_*.ps1",
    "*resolver_*.sh",
    "*reiniciar_*.sh",
    "*reiniciar_*.ps1",
    "*otimizar_*.sh",
    "*sistema_*.sh",
    "*setup_*.sh",
    "*setup_*.ps1",
    "*executar_*.ps1",
    "*executar_*.sh",
    "*finalizar_*.sh",
    "*enviar_*.ps1",
    "*django_*.sh",
    "*deploy_*.ps1",
    "*deploy_*.sh",
    "*criar_*.ps1",
    "*criar_*.sh",
    "*rodar_*.ps1",
    "*sincronizar_*.ps1",
    "*atualizar_*.ps1",
    "*corrigir_*.ps1",
    "*aplicar_*.ps1",
    "*forcar_*.ps1",
    "*verificar_*.ps1",
    "*ABRIR_*.ps1",
    "*CARREGAR_*.bat",
    "*MONPEC*.bat",
    "*REGERAR_*.bat"
)

$contadorTemp = 0
foreach ($pattern in $scriptsTemp) {
    Get-ChildItem -Path . -Filter $pattern -File | Where-Object { 
        $_.DirectoryName -eq (Get-Location).Path 
    } | ForEach-Object {
        Mover-Arquivo $_.Name "scripts/temp_para_revisao/"
        $script:contadorTemp++
    }
}

Write-Host "  [INFO] $contadorTemp scripts movidos para revisao" -ForegroundColor Cyan
Write-Host ""

# 5. EXCLUIR PASTAS DUPLICADAS
Write-Host "Excluindo pastas duplicadas..." -ForegroundColor Cyan

$pastasParaExcluir = @(
    "monpec_clean",
    "monpec_local",
    "monpec_projetista_clean",
    "monpec_sistema_completo"
)

foreach ($pasta in $pastasParaExcluir) {
    if (Test-Path $pasta) {
        try {
            Remove-Item -Path $pasta -Recurse -Force -ErrorAction Stop
            Write-Host "  [OK] Excluida: $pasta" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Erro ao excluir $pasta : $_" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# 6. EXCLUIR PASTA PYTHON311 (ambiente virtual - muito grande)
Write-Host "Excluindo pasta python311 (ambiente virtual)..." -ForegroundColor Cyan
if (Test-Path "python311") {
    Write-Host "  [ATENCAO] Esta pasta e muito grande (6230+ arquivos)!" -ForegroundColor Yellow
    $confirmar = Read-Host "  Deseja excluir python311? (S/N)"
    if ($confirmar -eq "S" -or $confirmar -eq "s") {
        try {
            Remove-Item -Path "python311" -Recurse -Force -ErrorAction Stop
            Write-Host "  [OK] Excluida: python311" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Erro ao excluir python311 : $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [INFO] Pasta python311 mantida (adicione ao .gitignore)" -ForegroundColor Cyan
    }
}
Write-Host ""

# 7. EXCLUIR BACKUP ANTIGO
Write-Host "Verificando backup antigo..." -ForegroundColor Cyan
if (Test-Path "backup_curral_refactor") {
    $confirmarBackup = Read-Host "  Deseja excluir backup_curral_refactor? (S/N)"
    if ($confirmarBackup -eq "S" -or $confirmarBackup -eq "s") {
        try {
            Remove-Item -Path "backup_curral_refactor" -Recurse -Force -ErrorAction Stop
            Write-Host "  [OK] Excluido: backup_curral_refactor" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Erro ao excluir backup_curral_refactor : $_" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# 8. EXCLUIR SCRIPTS ANTIGOS ESPECIFICOS
Write-Host "Excluindo scripts de instalacao antigos..." -ForegroundColor Cyan

$scriptsAntigos = @(
    "criar_sistema_completo.py",
    "SISTEMA_MONPEC_CLEAN.ps1",
    "SISTEMA_MONPEC_COMPLETO.ps1",
    "SISTEMA_SIMPLES_EXPERIENCIA.ps1",
    "backup_antes_demo.ps1",
    "backup_antes_demo.sh",
    "AJUSTAR_VALORES_FINANCEIRO.txt"
)

foreach ($script in $scriptsAntigos) {
    if (Test-Path $script) {
        try {
            Remove-Item -Path $script -Force -ErrorAction Stop
            Write-Host "  [OK] Excluido: $script" -ForegroundColor Green
        } catch {
            Write-Host "  [AVISO] Erro ao excluir $script : $_" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# 9. ATUALIZAR .GITIGNORE
Write-Host "Atualizando .gitignore..." -ForegroundColor Cyan

$gitignoreContent = @"
# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# Environment variables
.env
.env.local
.env.*.local

# Virtual Environment
venv/
env/
ENV/
python311/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Scripts temporários (revisar antes de commitar)
scripts/temp_para_revisao/

# Backups (opcional)
# backups/

# Django migrations (opcional - você pode querer manter)
# */migrations/*.py
# !*/migrations/__init__.py

# Static files coletados (podem ser recriados)
staticfiles/
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8 -Force
Write-Host "  [OK] .gitignore atualizado" -ForegroundColor Green
Write-Host ""

# RESUMO
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host "ORGANIZACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Estrutura criada:" -ForegroundColor Cyan
Write-Host "  - docs/ (documentacao geral)" -ForegroundColor White
Write-Host "  - docs/tecnicos/ (documentacao tecnica)" -ForegroundColor White
Write-Host "  - docs/configuracao/ (guias de configuracao)" -ForegroundColor White
Write-Host "  - scripts/manutencao/ (scripts uteis)" -ForegroundColor White
Write-Host "  - scripts/deploy/ (scripts de deploy)" -ForegroundColor White
Write-Host "  - scripts/temp_para_revisao/ (scripts temporarios - revisar antes de excluir)" -ForegroundColor White
Write-Host "  - deploy/scripts/ (scripts de deploy organizados)" -ForegroundColor White
Write-Host "  - deploy/config/ (configuracoes de deploy)" -ForegroundColor White
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "  1. Revise os arquivos em scripts/temp_para_revisao/" -ForegroundColor White
Write-Host "  2. Mova scripts uteis para scripts/manutencao/" -ForegroundColor White
Write-Host "  3. Exclua scripts que nao sao mais necessarios" -ForegroundColor White
Write-Host "  4. Teste o sistema para garantir que tudo funciona" -ForegroundColor White
Write-Host ""


















