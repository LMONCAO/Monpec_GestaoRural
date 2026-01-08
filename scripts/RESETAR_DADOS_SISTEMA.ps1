# Script para resetar todos os dados do sistema
# Mantém apenas usuários admin e estruturas básicas

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  RESET COMPLETO DO SISTEMA" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Este script irá excluir:" -ForegroundColor Red
Write-Host "  - Todas as fazendas (propriedades)" -ForegroundColor Red
Write-Host "  - Todos os produtores rurais" -ForegroundColor Red
Write-Host "  - Todos os animais e movimentações" -ForegroundColor Red
Write-Host "  - Todas as vendas e compras" -ForegroundColor Red
Write-Host "  - Todos os funcionários" -ForegroundColor Red
Write-Host "  - Todos os dados financeiros" -ForegroundColor Red
Write-Host "  - Todas as assinaturas e tenants" -ForegroundColor Red
Write-Host ""
Write-Host "Será mantido:" -ForegroundColor Green
Write-Host "  - Usuários admin e superusers" -ForegroundColor Green
Write-Host "  - Planos de assinatura (configurações)" -ForegroundColor Green
Write-Host "  - Categorias padrão do sistema" -ForegroundColor Green
Write-Host ""

$confirmacao = Read-Host "Digite 'RESETAR' para confirmar (ou qualquer outra coisa para cancelar)"

if ($confirmacao -ne "RESETAR") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "Executando reset do sistema..." -ForegroundColor Cyan
Write-Host ""

# Executar o comando Django
python manage.py resetar_dados_sistema --confirmar

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  RESET CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ERRO AO EXECUTAR RESET" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Verifique os erros acima." -ForegroundColor Red
}


