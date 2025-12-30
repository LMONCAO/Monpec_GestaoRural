@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   UPLOAD COMPLETO AUTOMATICO
echo   Enviando pasta inteira para Google Cloud
echo ========================================
echo.

REM Verificar gsutil
where gsutil >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gsutil nao encontrado!
    echo.
    echo Instale o Google Cloud SDK:
    echo https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Obter projeto atual do gcloud
for /f "tokens=*" %%i in ('gcloud config get-value project 2^>^&1') do set PROJECT_ID=%%i
if "!PROJECT_ID!"=="" (
    echo [ERRO] Nenhum projeto configurado no gcloud!
    echo Execute: gcloud config set project SEU_PROJECT_ID
    pause
    exit /b 1
)

echo Projeto Google Cloud: !PROJECT_ID!
echo.

REM Nome do bucket (usar nome do projeto + -backup)
set BUCKET_NAME=!PROJECT_ID!-backup-completo

REM Nome da pasta no bucket (usar nome da pasta atual)
for %%i in ("%CD%") do set FOLDER_NAME=%%~ni
echo Pasta local: %CD%
echo Pasta no Cloud: !FOLDER_NAME!
echo Bucket: !BUCKET_NAME!
echo.

REM Verificar se bucket existe, se nao existir, criar
echo Verificando bucket...
gsutil ls -b "gs://!BUCKET_NAME!" >nul 2>&1
if errorlevel 1 (
    echo Bucket nao existe. Criando...
    gsutil mb -p !PROJECT_ID! -l us-central1 "gs://!BUCKET_NAME!"
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar o bucket!
        pause
        exit /b 1
    )
    echo Bucket criado com sucesso!
) else (
    echo Bucket ja existe!
)
echo.

REM Excluir arquivos desnecessarios
set EXCLUDE_ARGS=-x "venv/**" -x "__pycache__/**" -x ".git/**" -x "node_modules/**" -x "*.pyc" -x ".env" -x "logs/**" -x "temp/**" -x "staticfiles/**" -x "*.log" -x ".gitignore" -x "*.md" -x "docs/**"

echo ========================================
echo   INICIANDO UPLOAD...
echo   Isso pode levar varios minutos!
echo ========================================
echo.
echo Excluindo automaticamente:
echo   - venv, __pycache__, .git, node_modules
echo   - *.pyc, .env, logs, temp, staticfiles
echo   - *.log, .gitignore, *.md, docs
echo.

REM Fazer upload usando rsync (sincronizacao - mais rapido)
echo Fazendo upload...
gsutil -m rsync -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!FOLDER_NAME!/"

if errorlevel 1 (
    echo.
    echo ========================================
    echo   [ERRO] Falha no upload!
    echo ========================================
    echo Verifique as mensagens de erro acima.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   UPLOAD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Seus arquivos estao em:
echo gs://!BUCKET_NAME!/!FOLDER_NAME!/
echo.
echo Para verificar:
echo gsutil ls -r gs://!BUCKET_NAME!/!FOLDER_NAME!/
echo.
pause

endlocal

