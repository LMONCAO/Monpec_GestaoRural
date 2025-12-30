@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para acompanhar o progresso do BUILD em tempo real

echo ========================================
echo   ACOMPANHAR BUILD EM TEMPO REAL
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural

echo [CONFIG] Projeto: %PROJECT_ID%
echo.
echo Mostrando builds em tempo real...
echo Pressione Ctrl+C para parar
echo.

REM Mostrar builds recentes
echo ========================================
echo   BUILDS RECENTES
echo ========================================
echo.
gcloud builds list --limit=5 --format="table(id,status,createTime,duration,source.repoSource.branchName)" --project=%PROJECT_ID%
echo.

REM Perguntar se quer acompanhar um build especifico
echo Deseja acompanhar um build especifico? (S/N)
set /p ACOMPANHAR_BUILD=

if /i "!ACOMPANHAR_BUILD!"=="S" (
    echo.
    echo Digite o ID do build (ou deixe em branco para acompanhar o mais recente):
    set /p BUILD_ID=
    
    if "!BUILD_ID!"=="" (
        echo Acompanhando o build mais recente...
        echo.
        gcloud builds log --stream --project=%PROJECT_ID%
    ) else (
        echo Acompanhando build !BUILD_ID!...
        echo.
        gcloud builds log !BUILD_ID! --stream --project=%PROJECT_ID%
    )
) else (
    echo.
    echo Para acompanhar um build especifico, execute:
    echo   gcloud builds log [BUILD_ID] --stream
    echo.
    echo Ou para ver logs do build mais recente:
    echo   gcloud builds log --stream
    echo.
    echo Ou use o script: ACOMPANHAR_BUILD_TEMPO_REAL.bat
    echo.
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul

endlocal

