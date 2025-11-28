@echo off
chcp 65001 >nul
REM ========================================
REM CARREGAR DADOS FINANCEIROS PARA 2022
REM Configuração específica para o ano 2022
REM ========================================
title MONPEC - Carregar Dados Financeiros 2022

echo ========================================
echo   CARREGAR DADOS FINANCEIROS - 2022
echo ========================================
echo.
echo Configuração:
echo   - Propriedade: Primeira disponível
echo   - Ano: 2022
echo   - Meses: 12
echo   - Receita Média: R$ 500.000,00
echo   - Despesa Média: R$ 450.000,00
echo.
echo ========================================
echo   EXECUTANDO...
echo ========================================
echo.

REM Verificar se está na pasta correta
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py não encontrado!
    echo [ERRO] Execute este script na pasta raiz do projeto Django.
    echo.
    pause
    exit /b 1
)

REM Executar o comando para 2022
python manage.py carregar_dados_financeiro_realista --ano 2022

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   CARGA CONCLUÍDA COM SUCESSO!
    echo ========================================
    echo.
    echo Os dados para 2022 foram gerados e estão disponíveis em:
    echo   - Dashboard Financeiro
    echo   - Relatório DRE
    echo   - Lançamentos Financeiros
    echo.
) else (
    echo.
    echo ========================================
    echo   ERRO NA EXECUÇÃO
    echo ========================================
    echo.
    echo Verifique os erros acima e tente novamente.
    echo.
)

pause


