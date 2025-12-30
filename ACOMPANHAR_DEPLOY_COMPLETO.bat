@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script COMPLETO para acompanhar todo o processo de deploy
REM Mostra build, deploy e logs em uma única tela

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

:MENU
cls
echo ========================================
echo   ACOMPANHAR DEPLOY COMPLETO
echo ========================================
echo.
echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM MOSTRAR RESUMO RAPIDO
REM ========================================
echo [RESUMO RAPIDO]
echo ----------------------------------------
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo [AVISO] Servico nao encontrado ou ainda nao foi deployado
) else (
    echo [OK] URL: !SERVICE_URL!
)

echo.
echo Ultimo build:
gcloud builds list --limit=1 --format="value(status)" --project=%PROJECT_ID% 2>nul
echo.
echo ========================================
echo   OPCOES DE ACOMPANHAMENTO
echo ========================================
echo.
echo 1. Acompanhar BUILD em tempo real
echo 2. Acompanhar LOGS do servico em tempo real
echo 3. Ver status completo do servico
echo 4. Ver erros especificos
echo 5. Monitorar servidor (atualiza automaticamente)
echo 6. Sair
echo.
set /p OPCAO="Escolha uma opcao (1-6): "

if "!OPCAO!"=="1" (
    cls
    echo ========================================
    echo   ACOMPANHAR BUILD EM TEMPO REAL
    echo   Pressione Ctrl+C para parar
    echo ========================================
    echo.
    echo Acompanhando build mais recente...
    echo.
    gcloud builds log --stream --project=%PROJECT_ID%
    echo.
    echo Build finalizado ou interrompido.
    pause
    goto :MENU
) else if "!OPCAO!"=="2" (
    cls
    echo ========================================
    echo   LOGS DO SERVIDOR - TEMPO REAL
    echo   Pressione Ctrl+C para parar
    echo ========================================
    echo.
    echo Mostrando logs em tempo real...
    echo.
    gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --project=%PROJECT_ID%
    echo.
    echo Logs finalizados ou interrompidos.
    pause
    goto :MENU
) else if "!OPCAO!"=="3" (
    cls
    call VERIFICAR_DEPLOY.bat
    pause
    goto :MENU
) else if "!OPCAO!"=="4" (
    cls
    call VERIFICAR_ERROS_DEPLOY.bat
    pause
    goto :MENU
) else if "!OPCAO!"=="5" (
    cls
    echo ========================================
    echo   MONITORAR SERVIDOR - TEMPO REAL
    echo   Pressione Ctrl+C para voltar ao menu
    echo ========================================
    echo.
    echo Iniciando monitoramento...
    echo Use o script: MONITORAR_SERVIDOR_SIMPLES.bat
    echo Ou: MONITORAR_SERVIDOR_TEMPO_REAL.bat
    echo.
    echo Pressione qualquer tecla para voltar ao menu...
    pause >nul
    goto :MENU
) else (
    echo Saindo...
    exit /b 0
)

goto :MENU
