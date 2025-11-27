@echo off
chcp 65001 >nul
echo ========================================================================
echo REGERANDO DADOS FINANCEIROS 2022 COM VALORES REALISTAS
echo ========================================================================
echo.
echo Este script vai:
echo 1. Excluir todos os lancamentos financeiros de 2022
echo 2. Regenerar com valores mais realistas:
echo    - Receita media mensal: R$ 200.000 (ao inves de R$ 500.000)
echo    - Despesa media mensal: R$ 180.000 (ao inves de R$ 450.000)
echo.
echo Isso resultara em aproximadamente:
echo    - Receitas anuais: R$ 2.400.000 a R$ 2.880.000
echo    - Despesas anuais: R$ 1.728.000 a R$ 2.808.000
echo.
pause

echo.
echo [1/2] Excluindo lancamentos de 2022...
python excluir_dados_2022.py --yes

echo.
echo [2/2] Gerando novos dados com valores realistas...
python manage.py carregar_dados_financeiro_realista --ano 2022 --receita-media 200000 --despesa-media 180000 --meses 12

echo.
echo ========================================================================
echo CONCLUIDO!
echo ========================================================================
echo.
echo Agora os valores devem estar mais realistas:
echo - Receitas: aproximadamente R$ 2.400.000 a R$ 2.880.000 por ano
echo - Despesas: aproximadamente R$ 1.728.000 a R$ 2.808.000 por ano
echo.
pause

