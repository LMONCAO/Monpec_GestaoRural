@echo off
REM CORRIGIR DEPLOY MONPEC - EXECUTAR NO GOOGLE CLOUD SHELL
REM Cole estes comandos no Cloud Shell

echo ========================================
echo CORRECAO DEPLOY MONPEC
echo ========================================
echo.
echo Execute estes comandos no Google Cloud Shell:
echo.
echo # 1. Executar migracoes
echo gcloud run jobs create migrate-monpec-final \
echo   --image gcr.io/monpec-sistema-rural/monpec:latest \
echo   --region us-central1 \
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" \
echo   --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
echo   --command="python" \
echo   --args="manage.py,migrate,--noinput" \
echo   --memory=2Gi \
echo   --cpu=1 \
echo   --max-retries=3 \
echo   --task-timeout=600
echo.
echo gcloud run jobs execute migrate-monpec-final --region=us-central1 --wait
echo.
echo # 2. Popular dados
echo gcloud run jobs create populate-monpec-final \
echo   --image gcr.io/monpec-sistema-rural/monpec:latest \
echo   --region us-central1 \
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" \
echo   --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
echo   --command="python" \
echo   --args="popular_dados_producao.py" \
echo   --memory=2Gi \
echo   --cpu=1 \
echo   --max-retries=3 \
echo   --task-timeout=600
echo.
echo gcloud run jobs execute populate-monpec-final --region=us-central1 --wait
echo.
echo # 3. Verificar se funcionou
echo curl https://monpec-29862706245.us-central1.run.app/
echo.
echo ========================================

pause