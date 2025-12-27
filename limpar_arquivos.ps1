# ========================================
# SCRIPT PARA LIMPAR ARQUIVOS DESNECESSARIOS
# ========================================
# IMPORTANTE: Faca backup antes de executar!

Write-Host "LIMPEZA DE ARQUIVOS DESNECESSARIOS" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "ATENCAO: Este script ira EXCLUIR arquivos!" -ForegroundColor Red
Write-Host "Certifique-se de ter feito backup do projeto antes de continuar." -ForegroundColor Yellow
Write-Host ""

$continuar = Read-Host "Deseja continuar? (S/N)"
if ($continuar -ne "S" -and $continuar -ne "s") {
    Write-Host "Operacao cancelada." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "Iniciando limpeza..." -ForegroundColor Cyan
Write-Host ""

$excluidos = 0
$erros = 0

# Funcao para excluir com seguranca
function Excluir-Arquivo {
    param($caminho, $tipo)
    if (Test-Path $caminho) {
        try {
            Remove-Item -Path $caminho -Recurse -Force -ErrorAction Stop
            Write-Host "[OK] Excluido: $tipo - $caminho" -ForegroundColor Green
            $script:excluidos++
        } catch {
            Write-Host "[ERRO] Erro ao excluir $caminho : $_" -ForegroundColor Red
            $script:erros++
        }
    } else {
        Write-Host "[AVISO] Nao encontrado: $caminho" -ForegroundColor Yellow
    }
}

# 1. EXCLUIR PASTAS DUPLICADAS
Write-Host "Excluindo pastas duplicadas..." -ForegroundColor Cyan
$pastasDuplicadas = @(
    "monpec_clean",
    "monpec_local",
    "monpec_projetista_clean",
    "monpec_sistema_completo"
)

foreach ($pasta in $pastasDuplicadas) {
    Excluir-Arquivo $pasta "Pasta duplicada"
}

# 2. EXCLUIR PASTA PYTHON311 (muito grande)
Write-Host ""
Write-Host "Excluindo pasta python311 (ambiente virtual)..." -ForegroundColor Cyan
Excluir-Arquivo "python311" "Ambiente Python"

# 3. EXCLUIR SCRIPTS TEMPORARIOS PYTHON
Write-Host ""
Write-Host "Excluindo scripts Python temporarios..." -ForegroundColor Cyan
$scriptsPython = @(
    "adicionar_arquivos_git.ps1",
    "adicionar_codigo_eletronico_animais.py",
    "adicionar_coluna_tipo_trabalho.py",
    "adicionar_modulos_view.py",
    "adicionar_pesagens_animais.py",
    "adicionar_url_modulos_automatico.py",
    "ajustar_despesas_saldo_liquido_realista.py",
    "ajustar_lancamentos_realistas.py",
    "ajustar_saldo_2022_girassol.py",
    "ajustar_vendas_girassol_com_saldo_final.py",
    "alterar_senha_admin.py",
    "analisar_e_corrigir_sistema_completo.py",
    "analise_profunda_modulos.py",
    "aplicar_atualizacoes.ps1",
    "aplicar_configuracao_girassol_0072.py",
    "aplicar_configuracao_girassol_manual.py",
    "aplicar_navegacao_inteligente.sh",
    "aplicar_sistema_financeiro_completo.sh",
    "atualizar_curral_tela.ps1",
    "atualizar_lancamentos_faturamento.py",
    "atualizar_repositorio.ps1",
    "atualizar_sistema_completo.ps1",
    "atualizar_sistema_final.sh",
    "atualizar_sistema.sh",
    "atualizar_status_bnd_animais.py",
    "atualizar_transferencias_favo_girassol_para_480.py",
    "atualizar_valores_canta_galo.py",
    "atualizar_valores_vendas_existentes.py",
    "backup_antes_demo.ps1",
    "backup_antes_demo.sh",
    "cadastrar_150_animais_estoque.py",
    "cadastrar_clientes.py",
    "cadastrar_fornecedores_nf.py",
    "calcular_e_preencher_impostos_renda.py",
    "carregar_categorias.py",
    "check_tables.py",
    "configurar_banco_marcelo_sanguino.py",
    "configurar_propriedades_marcelo_sanguino.py",
    "configurar_fluxo_transferencias_marcelo_sanguino.py",
    "copiar_movimentacoes_para_planejamento_novo_girassol.py",
    "correcao_coordenada_completa_todas_fazendas.py",
    "corrigir_nginx.sh",
    "corrigir_numero_manejo_animais.py",
    "corrigir_problemas_finais.py",
    "corrigir_problemas_identificados_verificacao.py",
    "corrigir_projecao_invernada_grande_completa.py",
    "corrigir_saldo_negativo_girassol_2026.py",
    "corrigir_saldos_negativos_vacas_descarte.py",
    "converter_transferencias_vacas_descarte_em_vendas.py",
    "criar_animais_teste_619512.py",
    "criar_carga_dados_validacao_emprestimo.py",
    "criar_dados_historicos_completos_2022_2025.py",
    "criar_dividas_scr_marcelo_sanguino.py",
    "criar_pagamentos_2025.py",
    "criar_migracao_status_bnd.py",
    "gerar_codigo_eletronico_animais.py",
    "limpar_e_recriar_lancamentos_corretos.py",
    "limpar_outras_propriedades.py",
    "limpar_outras_propriedades_auto.py",
    "melhorar_realismo_dados.py",
    "migrar_dados_status_bnd.py",
    "mover_animais_para_propriedade_6.py",
    "verificar_animais_cadastrados.py",
    "verificar_dados_criados.py",
    "verificar_e_corrigir_dre_balanco.py",
    "verificar_e_corrigir_tudo.py",
    "vincular_movimentacoes_planejamento_novo_girassol.py",
    "vincular_movimentacoes_novo_planejamento_invernada.py",
    "vincular_todas_correcoes_girassol.py",
    "vincular_todas_movimentacoes_favo_mel.py",
    "vincular_transferencias_favo_girassol_0072.py",
    "vincular_vendas_girassol_planejamento_atual.py",
    "zerar_saldo_invernada_grande_2023.py",
    "zerar_saldo_invernada_grande_2025.py"
)

foreach ($script in $scriptsPython) {
    Excluir-Arquivo $script "Script temporario"
}

# 4. EXCLUIR SCRIPTS DE INSTALACAO ANTIGOS
Write-Host ""
Write-Host "Excluindo scripts de instalacao antigos..." -ForegroundColor Cyan
$scriptsInstalacao = @(
    "criar_sistema_completo.py",
    "desenvolver_sistema_completo.ps1",
    "instalar_manual.sh",
    "SISTEMA_MONPEC_CLEAN.ps1",
    "SISTEMA_MONPEC_COMPLETO.ps1",
    "SISTEMA_SIMPLES_EXPERIENCIA.ps1"
)

foreach ($script in $scriptsInstalacao) {
    Excluir-Arquivo $script "Script de instalacao"
}

# 5. EXCLUIR BACKUP ANTIGO
Write-Host ""
Write-Host "Excluindo backup antigo (backup_curral_refactor)..." -ForegroundColor Cyan
$confirmarBackup = Read-Host "Deseja excluir a pasta backup_curral_refactor? (S/N)"
if ($confirmarBackup -eq "S" -or $confirmarBackup -eq "s") {
    Excluir-Arquivo "backup_curral_refactor" "Backup antigo"
}

# 6. EXCLUIR SCRIPTS DE CARREGAMENTO ANTIGOS
Write-Host ""
Write-Host "Excluindo scripts de carregamento antigos..." -ForegroundColor Cyan
$scriptsCarregamento = @(
    "CARREGAR_DADOS_FINANCEIRO.bat",
    "CARREGAR_DADOS_FINANCEIRO_2022.bat",
    "CARREGAR_DADOS_FINANCEIRO_2023.bat",
    "CARREGAR_DADOS_FINANCEIRO_2024.bat",
    "CARREGAR_DADOS_FINANCEIRO_RAPIDO.bat"
)

foreach ($script in $scriptsCarregamento) {
    Excluir-Arquivo $script "Script de carregamento"
}

# 7. EXCLUIR OUTROS SCRIPTS
Write-Host ""
Write-Host "Excluindo outros scripts temporarios..." -ForegroundColor Cyan
$outrosScripts = @(
    "ABRIR_PROMO_WHATSAPP.ps1",
    "AJUSTAR_VALORES_FINANCEIRO.txt"
)

foreach ($script in $outrosScripts) {
    Excluir-Arquivo $script "Script/arquivo temporario"
}

# RESUMO
Write-Host ""
Write-Host "===================================" -ForegroundColor Yellow
Write-Host "RESUMO DA LIMPEZA" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Yellow
Write-Host "Arquivos/Pastas excluidos: $excluidos" -ForegroundColor Green
Write-Host "Erros encontrados: $erros" -ForegroundColor $(if ($erros -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "Limpeza concluida!" -ForegroundColor Green
Write-Host ""






































