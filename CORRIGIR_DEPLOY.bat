@echo off
chcp 65001 >nul
echo ========================================
echo CORREÇÃO COMPLETA DE DEPLOY
echo ========================================
echo.

echo [1/5] Verificando autenticação no Google Cloud...
gcloud auth list --filter=status:ACTIVE --format="value(account)"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erro: Execute 'gcloud auth login' primeiro
    pause
    exit /b 1
)
echo ✅ Autenticado
echo.

echo [2/5] Verificando projeto...
gcloud config set project monpec-sistema-rural
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erro ao configurar projeto
    pause
    exit /b 1
)
echo ✅ Projeto configurado: monpec-sistema-rural
echo.

echo [3/5] Verificando Service Account...
gcloud iam service-accounts describe github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com --project=monpec-sistema-rural >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Service Account não existe. Criando...
    gcloud iam service-accounts create github-actions-deploy --display-name="GitHub Actions Deploy" --project=monpec-sistema-rural
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Erro ao criar Service Account
        pause
        exit /b 1
    )
    echo ✅ Service Account criado
) else (
    echo ✅ Service Account existe
)
echo.

echo [4/5] Configurando permissões do Service Account...
echo    Atribuindo roles necessárias...
gcloud projects add-iam-policy-binding monpec-sistema-rural --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" --role="roles/run.admin" --quiet
gcloud projects add-iam-policy-binding monpec-sistema-rural --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor" --quiet
gcloud projects add-iam-policy-binding monpec-sistema-rural --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" --role="roles/storage.admin" --quiet
gcloud projects add-iam-policy-binding monpec-sistema-rural --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser" --quiet
gcloud projects add-iam-policy-binding monpec-sistema-rural --member="serviceAccount:github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com" --role="roles/artifactregistry.writer" --quiet
echo ✅ Permissões configuradas
echo.

echo [5/5] Gerando chave JSON do Service Account...
if exist github-actions-key.json (
    echo ⚠️  Arquivo github-actions-key.json já existe
    echo    Deseja sobrescrever? (S/N)
    set /p overwrite=
    if /i not "%overwrite%"=="S" (
        echo Operação cancelada
        goto :end
    )
)

gcloud iam service-accounts keys create github-actions-key.json --iam-account=github-actions-deploy@monpec-sistema-rural.iam.gserviceaccount.com --project=monpec-sistema-rural
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erro ao gerar chave
    pause
    exit /b 1
)
echo ✅ Chave JSON gerada: github-actions-key.json
echo.

:end
echo ========================================
echo PRÓXIMOS PASSOS:
echo ========================================
echo.
echo 1. Adicione o conteúdo de 'github-actions-key.json' como secret 'GCP_SA_KEY' no GitHub:
echo    https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
echo.
echo 2. Verifique se todos os secrets estão configurados:
echo    - GCP_SA_KEY (conteúdo do arquivo JSON gerado)
echo    - SECRET_KEY
echo    - DB_NAME
echo    - DB_USER
echo    - DB_PASSWORD
echo    - DJANGO_SUPERUSER_PASSWORD
echo.
echo 3. Faça um novo push para triggerar o deploy:
echo    git push origin master
echo.
echo 4. Acompanhe o deploy em:
echo    https://github.com/LMONCAO/Monpec_GestaoRural/actions
echo.
pause
