@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   Upload para Google Cloud Storage
echo ========================================
echo.

REM Verificar se gsutil está instalado
where gsutil >nul 2>&1
if errorlevel 1 (
    echo ERRO: gsutil não encontrado!
    echo.
    echo Para instalar o gsutil:
    echo 1. Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install
    echo 2. Execute: gcloud init
    echo 3. Execute: gcloud auth login
    exit /b 1
)

REM Verificar autenticação
echo Verificando autenticação...
for /f "tokens=*" %%i in ('gcloud auth list --filter=status:ACTIVE --format="value(account)" 2^>^&1') do set AUTH_ACCOUNT=%%i

if "!AUTH_ACCOUNT!"=="" (
    echo ERRO: Você precisa fazer login no Google Cloud!
    echo Execute: gcloud auth login
    exit /b 1
)

echo Autenticado como: !AUTH_ACCOUNT!
echo.

REM Solicitar nome do bucket
set /p BUCKET_NAME="Digite o nome do bucket (ex: monpec-static ou monpec-backup): "
if "!BUCKET_NAME!"=="" (
    echo ERRO: Nome do bucket é obrigatório!
    exit /b 1
)

REM Verificar se o bucket existe
echo Verificando bucket '!BUCKET_NAME!'...
gsutil ls -b "gs://!BUCKET_NAME!" >nul 2>&1
if errorlevel 1 (
    echo Bucket não encontrado. Deseja criar? (S/N)
    set /p CREATE_BUCKET=
    if /i "!CREATE_BUCKET!"=="S" (
        echo Criando bucket '!BUCKET_NAME!'...
        for /f "tokens=*" %%i in ('gcloud config get-value project 2^>^&1') do set PROJECT_ID=%%i
        gsutil mb -p !PROJECT_ID! -l us-central1 "gs://!BUCKET_NAME!"
        if errorlevel 1 (
            echo ERRO: Não foi possível criar o bucket!
            exit /b 1
        )
        echo Bucket criado com sucesso!
    ) else (
        echo Operação cancelada.
        exit /b 0
    )
) else (
    echo Bucket encontrado!
)
echo.

REM Perguntar sobre exclusões
echo Deseja excluir arquivos/pastas específicos do upload? (S/N)
set /p EXCLUIR_ARQUIVOS=
set EXCLUDE_ARGS=-x "venv/**" -x "__pycache__/**" -x ".git/**" -x "node_modules/**" -x "*.pyc" -x ".env" -x "logs/**" -x "temp/**"

if /i "!EXCLUIR_ARQUIVOS!"=="S" (
    echo.
    echo Pastas/arquivos que serão EXCLUÍDOS automaticamente:
    echo   - venv/ (ambiente virtual Python)
    echo   - __pycache__/ (cache Python)
    echo   - .git/ (repositório Git)
    echo   - node_modules/ (dependências Node)
    echo   - *.pyc (arquivos compilados Python)
    echo   - .env (variáveis de ambiente)
    echo   - logs/ (arquivos de log)
    echo   - temp/ (arquivos temporários)
    echo.
    echo Deseja adicionar mais exclusões? (S/N)
    set /p ADICIONAR_EXCLUSOES=
    
    if /i "!ADICIONAR_EXCLUSOES!"=="S" (
        echo Digite os padrões a excluir (um por linha, deixe vazio para terminar):
        echo Exemplos: backups/, *.log, staticfiles/
        :loop_exclusoes
        set /p PATTERN="Padrão: "
        if not "!PATTERN!"=="" (
            set EXCLUDE_ARGS=!EXCLUDE_ARGS! -x "!PATTERN!"
            goto loop_exclusoes
        )
    )
)

REM Perguntar sobre modo de upload
echo.
echo Escolha o modo de upload:
echo 1. Sincronizar (rsync) - mais rápido, só envia arquivos novos/modificados
echo 2. Copiar completo - envia tudo novamente
set /p MODO_UPLOAD="Digite 1 ou 2 (padrão: 1): "

if "!MODO_UPLOAD!"=="" set MODO_UPLOAD=1

REM Obter diretório atual e nome do projeto
for %%i in ("%CD%") do set PROJECT_NAME=%%~ni

echo.
echo ========================================
echo   Iniciando upload...
echo ========================================
echo Origem: %CD%
echo Destino: gs://!BUCKET_NAME!/!PROJECT_NAME!/
echo.

REM Executar upload
if "!MODO_UPLOAD!"=="1" (
    echo Modo: Sincronização (rsync)
    echo Isso pode levar alguns minutos dependendo do tamanho da pasta...
    echo.
    gsutil -m rsync -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!PROJECT_NAME!/"
) else (
    echo Modo: Cópia completa
    echo Isso pode levar vários minutos dependendo do tamanho da pasta...
    echo.
    gsutil -m cp -r !EXCLUDE_ARGS! . "gs://!BUCKET_NAME!/!PROJECT_NAME!/"
)

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Erro durante o upload!
    echo ========================================
    echo Verifique as mensagens de erro acima.
    exit /b 1
) else (
    echo.
    echo ========================================
    echo   Upload concluído com sucesso!
    echo ========================================
    echo.
    echo Seus arquivos estão disponíveis em:
    echo gs://!BUCKET_NAME!/!PROJECT_NAME!/
    echo.
    echo Para verificar os arquivos:
    echo gsutil ls -r gs://!BUCKET_NAME!/!PROJECT_NAME!/
)

endlocal

