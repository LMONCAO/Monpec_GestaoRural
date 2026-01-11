@echo off
REM DIAGNOSTICO E CORREÇÃO DAS MIGRAÇÕES

echo ========================================
echo DIAGNOSTICO MIGRAÇÕES MONPEC
echo ========================================
echo.
echo COPIE E COLE estes comandos no Google Cloud Shell:
echo.
echo ========================================
echo.
echo # 1. VER DETALHES DO ERRO
echo gcloud run jobs executions describe migrate-final-lxq4w --region=us-central1
echo.
echo # 2. VER LOGS DETALHADOS
echo gcloud run jobs executions logs read migrate-final-lxq4w --region=us-central1
echo.
echo ========================================
echo.
echo # 3. VERIFICAR CLOUD SQL
echo gcloud sql instances describe monpec-db --project=monpec-sistema-rural
echo.
echo ========================================
echo.
echo # 4. SE O BANCO NÃO EXISTIR, CRIAR:
echo.
echo # Criar instância Cloud SQL
echo gcloud sql instances create monpec-db \
echo   --database-version=POSTGRESQL_15 \
echo   --tier=db-f1-micro \
echo   --region=us-central1 \
echo   --project=monpec-sistema-rural
echo.
echo # Criar banco
echo gcloud sql databases create monpec_db --instance=monpec-db --project=monpec-sistema-rural
echo.
echo # Criar usuário
echo gcloud sql users create monpec_user \
echo   --instance=monpec-db \
echo   --password=L6171r12@@jjms \
echo   --project=monpec-sistema-rural
echo.
echo ========================================
echo.
echo # 5. TENTAR MIGRAÇÕES NOVAMENTE
echo gcloud run jobs create migrate-final-v2 \
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
echo gcloud run jobs execute migrate-final-v2 --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 6. APÓS SUCESSO, POPULAR DADOS
echo gcloud run jobs create populate-final-v2 \
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
echo gcloud run jobs execute populate-final-v2 --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 7. TESTAR FINAL
echo curl https://monpec-29862706245.us-central1.run.app/
echo.
echo ========================================

pause