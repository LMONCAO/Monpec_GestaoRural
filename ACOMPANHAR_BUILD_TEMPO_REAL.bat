@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para acompanhar build em tempo real
REM Fica aberto mostrando o progresso do build

echo ========================================
echo   ACOMPANHAR BUILD - TEMPO REAL
echo   Pressione Ctrl+C para sair
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural

echo [CONFIG] Projeto: %PROJECT_ID%
echo.

REM Mostrar builds recentes primeiro
echo ========================================
echo   BUILDS RECENTES
echo ========================================
echo.
gcloud builds list --limit=5 --format="table(id,status,createTime,duration)" --project=%PROJECT_ID%
echo.

REM Perguntar qual build acompanhar
echo.
echo Digite o ID do build para acompanhar (ou deixe em branco para o mais recente):
set /p BUILD_ID=

if "!BUILD_ID!"=="" (
    echo.
    echo Acompanhando o build mais recente em tempo real...
    echo Pressione Ctrl+C para parar
    echo.
    echo ========================================
    echo.
    gcloud builds log --stream --project=%PROJECT_ID%
) else (
    echo.
    echo Acompanhando build !BUILD_ID! em tempo real...
    echo Pressione Ctrl+C para parar
    echo.
    echo ========================================
    echo.
    gcloud builds log !BUILD_ID! --stream --project=%PROJECT_ID%
)

REM Se o comando acima terminar, mostrar mensagem
echo.
echo ========================================
echo Build finalizado ou erro ao conectar
echo ========================================
pause

endlocal

