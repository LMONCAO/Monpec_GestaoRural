@echo off
chcp 65001 >nul
echo ========================================
echo POPULANDO SISTEMA COM DADOS REALISTAS
echo ========================================
echo.
echo Este comando vai popular o sistema com dados realistas do setor pecuário
echo baseados em dados de mercado 2024-2025.
echo.
echo Dados que serão criados:
echo   - Categorias de animais
echo   - Inventário inicial (341 cabeças)
echo   - Movimentações de rebanho (12 meses)
echo   - Planejamento anual
echo   - Dados financeiros (receitas e despesas)
echo   - Compras de suplementação
echo   - Vendas de animais
echo   - Bens patrimoniais
echo   - Funcionários e folha de pagamento
echo   - Pastagens e cochos
echo.
pause

python manage.py popular_dados_pecuaria_realista

echo.
echo ========================================
echo DADOS POPULADOS COM SUCESSO!
echo ========================================
echo.
pause



