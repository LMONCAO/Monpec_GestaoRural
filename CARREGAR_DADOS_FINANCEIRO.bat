@echo off
chcp 65001 >nul
REM ========================================
REM CARREGAR DADOS FINANCEIROS REALISTAS
REM Gera dados com variação mensal e fluxo de caixa controlado
REM ========================================
title MONPEC - Carregar Dados Financeiros

echo ========================================
echo   CARREGAR DADOS FINANCEIROS REALISTAS
echo ========================================
echo.
echo Este comando irá gerar:
echo   - Fornecedores
echo   - Centros de Custo
echo   - Categorias Financeiras
echo   - Contas Financeiras
echo   - Lançamentos Financeiros (Receitas e Despesas)
echo   - Notas Fiscais associadas
echo   - Variação mensal realista
echo   - Fluxo de caixa controlado
echo.
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

REM Solicitar parâmetros
set /p PROPRIEDADE_ID="ID da Propriedade (Enter para usar a primeira): "
set /p ANO="Ano (Enter para usar ano atual): "
set /p MESES="Número de meses (Enter para 12): "
set /p RECEITA_MEDIA="Receita média mensal em R$ (Enter para 500000): "
set /p DESPESA_MEDIA="Despesa média mensal em R$ (Enter para 450000): "

echo.
echo ========================================
echo   CONFIGURAÇÃO ESCOLHIDA
echo ========================================
if "%PROPRIEDADE_ID%"=="" (
    echo Propriedade: Primeira disponível
    set PARAM_PROPIEDADE=
) else (
    echo Propriedade ID: %PROPRIEDADE_ID%
    set PARAM_PROPIEDADE=--propriedade-id %PROPRIEDADE_ID%
)

if "%ANO%"=="" (
    echo Ano: Ano atual
    set PARAM_ANO=
) else (
    echo Ano: %ANO%
    set PARAM_ANO=--ano %ANO%
)

if "%MESES%"=="" (
    echo Meses: 12
    set PARAM_MESES=
) else (
    echo Meses: %MESES%
    set PARAM_MESES=--meses %MESES%
)

if "%RECEITA_MEDIA%"=="" (
    echo Receita Média: R$ 500.000,00
    set PARAM_RECEITA=
) else (
    echo Receita Média: R$ %RECEITA_MEDIA%
    set PARAM_RECEITA=--receita-media %RECEITA_MEDIA%
)

if "%DESPESA_MEDIA%"=="" (
    echo Despesa Média: R$ 450.000,00
    set PARAM_DESPESA=
) else (
    echo Despesa Média: R$ %DESPESA_MEDIA%
    set PARAM_DESPESA=--despesa-media %DESPESA_MEDIA%
)

echo.
echo ========================================
echo   EXECUTANDO COMANDO...
echo ========================================
echo.

REM Executar o comando
python manage.py carregar_dados_financeiro_realista %PARAM_PROPIEDADE% %PARAM_ANO% %PARAM_MESES% %PARAM_RECEITA% %PARAM_DESPESA%

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













