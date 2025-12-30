@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Script SIMPLES para upload rápido - sem perguntas
REM Uso: upload_para_google_cloud_simples.bat BUCKET_NAME [PROJECT_NAME] [sync|copy]

if "%~1"=="" (
    echo ERRO: Especifique o nome do bucket!
    echo.
    echo Uso: %~nx0 BUCKET_NAME [PROJECT_NAME] [sync^|copy]
    echo.
    echo Exemplos:
    echo   %~nx0 meu-bucket
    echo   %~nx0 meu-bucket monpec
    echo   %~nx0 meu-bucket monpec sync
    exit /b 1
)

set BUCKET_NAME=%~1
set PROJECT_NAME=%~2
set UPLOAD_MODE=%~3

REM Se não especificar nome do projeto, usar nome da pasta atual
if "!PROJECT_NAME!"=="" (
    for %%i in ("%CD%") do set PROJECT_NAME=%%~ni
)

REM Se não especificar modo, usar sync
if "!UPLOAD_MODE!"=="" set UPLOAD_MODE=sync

echo Upload para Google Cloud Storage...
echo Bucket: !BUCKET_NAME!
echo Projeto: !PROJECT_NAME!
echo Modo: !UPLOAD_MODE!
echo.

REM Verificar gsutil
where gsutil >nul 2>&1
if errorlevel 1 (
    echo ERRO: gsutil não encontrado! Instale o Google Cloud SDK.
    exit /b 1
)

REM Excluir arquivos desnecessários
set EXCLUDE_ARGS=-x "venv/**" -x "__pycache__/**" -x ".git/**" -x "node_modules/**" -x "*.pyc" -x ".env" -x "logs/**" -x "temp/**" -x "staticfiles/**" -x "*.log"

echo Iniciando upload para gs://!BUCKET_NAME!/!PROJECT_NAME!/ ...
echo.

if /i "!UPLOAD_MODE!"=="sync" (
    gsutil -m rsync -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!PROJECT_NAME!/"
) else (
    gsutil -m cp -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!PROJECT_NAME!/"
)

if errorlevel 1 (
    echo.
    echo Erro no upload!
    exit /b 1
) else (
    echo.
    echo Upload concluído!
)

endlocal

