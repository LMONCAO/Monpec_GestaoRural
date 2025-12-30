@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para verificar status do deploy no Google Cloud Run

echo ========================================
echo   VERIFICAR STATUS DO DEPLOY
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo [CONFIG] Projeto: %PROJECT_ID%
echo [CONFIG] Servico: %SERVICE_NAME%
echo [CONFIG] Regiao: %REGION%
echo.

REM ========================================
REM VERIFICAR STATUS DO SERVICO
REM ========================================
echo [1/4] Verificando status do servico...
echo.

for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if "!SERVICE_URL!"=="" (
    echo [ERRO] Servico nao encontrado ou nao esta rodando!
    echo Verifique se o deploy foi concluido.
    pause
    exit /b 1
)

echo [OK] URL do servico: !SERVICE_URL!
echo.

REM Verificar condicoes do servico
echo Verificando condicoes do servico...
gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="table(status.conditions[0].type,status.conditions[0].status,status.conditions[0].message)" --project=%PROJECT_ID%
echo.

REM ========================================
REM VERIFICAR REVISOES (VERSOES)
REM ========================================
echo [2/4] Verificando revisoes (versoes) do servico...
echo.

gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=5 --format="table(metadata.name,status.conditions[0].status,spec.containers[0].image,metadata.creationTimestamp)" --project=%PROJECT_ID%
echo.

REM ========================================
REM VERIFICAR LOGS RECENTES
REM ========================================
echo [3/4] Verificando logs recentes (ultimas 30 linhas)...
echo.
echo ========================================
echo   LOGS DO SERVICO
echo ========================================
echo.

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=30 --format="table(timestamp,severity,textPayload,jsonPayload.message)" --project=%PROJECT_ID% 2>&1 | findstr /V "Listed 0\|^$" || echo Nenhum log encontrado ainda. O servico pode estar inicializando.
echo.

REM ========================================
REM TESTAR ACESSO AO SERVICO
REM ========================================
echo [4/4] Testando acesso ao servico...
echo.

echo Tentando acessar: !SERVICE_URL!
echo.

REM Usar curl se disponivel, senao usar PowerShell
where curl >nul 2>&1
if errorlevel 1 (
    echo Usando PowerShell para testar conexao...
    powershell -Command "try { $response = Invoke-WebRequest -Uri '!SERVICE_URL!' -Method Get -TimeoutSec 10 -UseBasicParsing; Write-Host '[OK] Servico respondendo! Status:' $response.StatusCode } catch { Write-Host '[ERRO] Servico nao esta respondendo:' $_.Exception.Message }"
) else (
    echo Usando curl para testar conexao...
    curl -s -o nul -w "Status HTTP: %%{http_code}\n" "!SERVICE_URL!" 2>&1 || echo [AVISO] Nao foi possivel testar conexao. Verifique manualmente.
)
echo.

REM ========================================
REM RESUMO E INFORMACOES
REM ========================================
echo ========================================
echo   RESUMO
echo ========================================
echo.
echo URL do servico: !SERVICE_URL!
echo.
echo Para ver mais logs:
echo   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --limit=100
echo.
echo Para ver detalhes do servico:
echo   gcloud run services describe %SERVICE_NAME% --region=%REGION%
echo.
echo Para ver todas as revisoes:
echo   gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION%
echo.
echo ========================================
echo   TESTE MANUAL
echo ========================================
echo.
echo 1. Abra no navegador: !SERVICE_URL!
echo 2. Verifique se a landing page carrega
echo 3. Tente fazer login:
echo    Usuario: admin
echo    Senha: L6171r12@@
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM Perguntar se quer ver mais detalhes
echo.
echo Deseja ver logs em tempo real? (S/N)
set /p VER_LOGS=
if /i "!VER_LOGS!"=="S" (
    echo.
    echo Mostrando logs em tempo real (Ctrl+C para parar)...
    echo.
    gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --project=%PROJECT_ID%
    echo.
    echo Logs finalizados ou interrompidos.
    pause
)

endlocal

