@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script para validar se a atualizacao foi aplicada no servidor

echo ========================================
echo   VALIDAR ATUALIZACAO DO SERVIDOR
echo ========================================
echo.

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo [1/4] Verificando revisao mais recente...
echo.
gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=1 --format="table(metadata.name,status.conditions[0].status,spec.containers[0].image,metadata.creationTimestamp)" --project=%PROJECT_ID%
echo.

echo [2/4] Verificando imagem usada...
for /f "tokens=*" %%i in ('gcloud run revisions list --service=%SERVICE_NAME% --region=%REGION% --limit=1 --format="value(spec.containers[0].image)" --project=%PROJECT_ID% 2^>^&1') do set CURRENT_IMAGE=%%i
echo Imagem atual: !CURRENT_IMAGE!
echo.

echo [3/4] Verificando build mais recente...
echo.
gcloud builds list --limit=1 --format="table(id,status,createTime,source.repoSource.branchName)" --project=%PROJECT_ID%
echo.

echo [4/4] Verificando URL do servico...
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)" --project=%PROJECT_ID% 2^>^&1') do set SERVICE_URL=%%i

if not "!SERVICE_URL!"=="" (
    echo URL: !SERVICE_URL!
    echo.
    echo ========================================
    echo   COMO VALIDAR A ATUALIZACAO
    echo ========================================
    echo.
    echo 1. Acesse: !SERVICE_URL!
    echo 2. Pressione Ctrl+F5 (ou Ctrl+Shift+R) para limpar cache do navegador
    echo 3. Verifique se suas mudancas aparecem
    echo.
    echo Se as mudancas nao aparecerem:
    echo - Execute: FORCAR_ATUALIZACAO_COMPLETA.bat
    echo - Aguarde 2-3 minutos
    echo - Limpe o cache do navegador novamente
    echo.
) else (
    echo [ERRO] Nao foi possivel obter a URL do servico
)

echo ========================================
echo.
pause

endlocal

