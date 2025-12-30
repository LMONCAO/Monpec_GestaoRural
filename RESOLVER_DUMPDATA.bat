@echo off
REM ============================================
REM RESOLVER PROBLEMAS COM DUMPDATA
REM ============================================
REM Este script:
REM 1. Aplica migrações pendentes
REM 2. Cria migrações se necessário
REM 3. Faz dump com encoding UTF-8
REM ============================================

chcp 65001 >nul
title MONPEC - Resolver Dumpdata

echo.
echo ========================================
echo   RESOLVER PROBLEMAS COM DUMPDATA
echo ========================================
echo.

REM Verificar se manage.py existe
if not exist "manage.py" (
    echo [ERRO] manage.py não encontrado!
    echo [INFO] Certifique-se de executar este script na raiz do projeto.
    echo [INFO] Diretório atual: %CD%
    pause
    exit /b 1
)

echo [OK] Diretório raiz encontrado: %CD%
echo.

REM Configurar encoding UTF-8
set PYTHONIOENCODING=utf-8

REM 1. Criar migrações se necessário
echo [1/4] Verificando e criando migrações...
echo.
python manage.py makemigrations
if errorlevel 1 (
    echo.
    echo [AVISO] Erro ao criar migrações. Continuando...
    echo.
)

REM 2. Aplicar migrações
echo.
echo [2/4] Aplicando migrações...
echo.
python manage.py migrate
if errorlevel 1 (
    echo.
    echo [ERRO] Erro ao aplicar migrações!
    echo [INFO] Verifique os erros acima.
    set /p continuar="Deseja continuar mesmo assim? (s/n): "
    if /i not "%continuar%"=="s" (
        pause
        exit /b 1
    )
)

REM 3. Criar tabela diretamente se não existir
echo.
echo [3/5] Verificando e criando tabela anexolancamentofinanceiro...
echo [INFO] Usando método direto (sem rollback de migrações)
echo.
python criar_tabela_simples.py
if errorlevel 1 (
    echo.
    echo [AVISO] Tabela não foi criada. Continuando mesmo assim...
    echo [INFO] O dump pode falhar se a tabela for necessária.
    echo.
)

REM 4. Verificar status das migrações
echo.
echo [4/5] Verificando status das migrações...
echo.
python manage.py showmigrations gestao_rural | findstr "0034"

REM 5. Fazer dump com encoding UTF-8
echo.
echo [5/5] Fazendo dump dos dados (UTF-8)...
echo [INFO] Usando script Python com encoding UTF-8 forçado
echo.
set OUTPUT_FILE=dados_backup.json

REM Remover arquivo anterior se existir
if exist "%OUTPUT_FILE%" (
    echo [INFO] Removendo arquivo anterior: %OUTPUT_FILE%
    del "%OUTPUT_FILE%"
)

echo [INFO] Executando dumpdata com encoding UTF-8...
echo [INFO] Arquivo de saída: %OUTPUT_FILE%
echo.

REM Usar script Python que força UTF-8 (versão v2 com subprocess)
python fazer_dump_utf8_v2.py
if errorlevel 1 (
    echo.
    echo [ERRO] Erro ao fazer dump dos dados!
    echo [INFO] Verifique os erros acima.
    pause
    exit /b 1
)

REM Verificar se arquivo foi criado
if exist "%OUTPUT_FILE%" (
    for %%A in ("%OUTPUT_FILE%") do (
        set size=%%~zA
    )
    echo.
    echo ========================================
    echo   [OK] DUMP CRIADO COM SUCESSO!
    echo ========================================
    echo.
    echo Arquivo: %OUTPUT_FILE%
    echo Tamanho: %size% bytes
    echo.
) else (
    echo.
    echo [ERRO] Arquivo de dump não foi criado!
    pause
    exit /b 1
)

echo.
pause

