@echo off
chcp 65001 >nul
echo ========================================
echo DEPLOY NO APP ENGINE - MONPEC
echo ========================================
echo.

echo [1/3] Criando aplicação App Engine...
gcloud app create --region=southamerica-east1
if errorlevel 1 (
    echo [AVISO] App Engine pode já estar criado ou erro ao criar
)
echo.

echo [2/3] Copiando app.yaml...
if not exist "app.yaml" (
    if exist "deploy\config\app.yaml" (
        copy "deploy\config\app.yaml" "app.yaml"
        echo [OK] app.yaml copiado
    ) else (
        echo [ERRO] app.yaml não encontrado
        pause
        exit /b 1
    )
) else (
    echo [OK] app.yaml já existe
)
echo.

echo [3/3] Fazendo deploy no App Engine...
echo Isso pode levar alguns minutos...
echo.
gcloud app deploy --quiet

if errorlevel 1 (
    echo.
    echo [ERRO] Deploy falhou
    pause
    exit /b 1
)

echo.
echo ========================================
echo DEPLOY CONCLUÍDO COM SUCESSO!
echo ========================================
echo.
echo Obtendo URL...
gcloud app browse --no-launch-browser
echo.
echo Próximos passos:
echo 1. Configurar variáveis de ambiente no GCP Console
echo 2. Executar migrações
echo 3. Criar superusuário
echo.
pause






