@echo off
REM DEPLOY FINAL MONPEC - COPIE E COLE NO CLOUD SHELL

echo ========================================
echo DEPLOY FINAL MONPEC
echo ========================================
echo.
echo COPIE E COLE estes comandos no Google Cloud Shell:
echo.
echo ========================================
echo.
echo # 1. MIGRAÇÕES
echo gcloud run jobs create migrate-final ^\
echo   --image gcr.io/monpec-sistema-rural/monpec:latest ^\
echo   --region us-central1 ^\
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" ^\
echo   --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db ^\
echo   --command="python" ^\
echo   --args="manage.py,migrate,--noinput" ^\
echo   --memory=2Gi ^\
echo   --cpu=1 ^\
echo   --max-retries=3 ^\
echo   --task-timeout=600
echo.
echo gcloud run jobs execute migrate-final --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 2. POPULAR DADOS
echo gcloud run jobs create populate-final ^\
echo   --image gcr.io/monpec-sistema-rural/monpec:latest ^\
echo   --region us-central1 ^\
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" ^\
echo   --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db ^\
echo   --command="python" ^\
echo   --args="popular_dados_producao.py" ^\
echo   --memory=2Gi ^\
echo   --cpu=1 ^\
echo   --max-retries=3 ^\
echo   --task-timeout=600
echo.
echo gcloud run jobs execute populate-final --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 3. TESTAR
echo curl https://monpec-29862706245.us-central1.run.app/
echo.
echo ========================================
echo.
echo URLs APOS CORREÇÃO:
echo.
echo Landing:     https://monpec-29862706245.us-central1.run.app/
echo Admin:       https://monpec-29862706245.us-central1.run.app/admin/
echo Dashboard:   https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/
echo Planejamento: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/planejamento/
echo.
echo ========================================

pause