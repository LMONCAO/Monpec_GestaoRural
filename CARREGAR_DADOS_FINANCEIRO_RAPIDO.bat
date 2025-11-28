@echo off
chcp 65001 >nul
REM ========================================
REM CARREGAR DADOS FINANCEIROS - MODO RÁPIDO
REM Usa valores padrão (primeira propriedade, ano atual, 12 meses)
REM ========================================
title MONPEC - Carregar Dados Financeiros (Rápido)

echo ========================================
echo   CARREGAR DADOS FINANCEIROS - RÁPIDO
echo ========================================
echo.
echo Usando configuração padrão:
echo   - Propriedade: Primeira disponível
echo   - Ano: Ano atual
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

REM Executar o comando com valores padrão
python manage.py carregar_dados_financeiro_realista

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   CARGA CONCLUÍDA COM SUCESSO!
    echo ========================================
    echo.
    echo Os dados foram gerados e estão disponíveis em:
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


