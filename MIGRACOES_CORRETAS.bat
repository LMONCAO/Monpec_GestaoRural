@echo off
REM MIGRAÇÕES COM CONFIGURAÇÕES CORRETAS

echo ========================================
echo MIGRAÇÕES COM BANCO EXISTENTE
echo ========================================
echo.
echo CONFIGURAÇÕES CORRETAS:
echo - Instância: monpec-db
echo - Usuário: postgres
echo - Senha: L6171r12@@jjms
echo - Banco: monpec_db
echo.
echo ========================================
echo.
echo COPIE E COLE no Google Cloud Shell:
echo.
echo ========================================
echo.
echo # 1. EXECUTAR MIGRAÇÕES COM USUÁRIO POSTGRES
echo gcloud run jobs create migrate-final-v3 \
echo   --image gcr.io/monpec-sistema-rural/monpec:latest \
echo   --region us-central1 \
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" \
echo   --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
echo   --command="python" \
echo   --args="manage.py,migrate,--noinput" \
echo   --memory=2Gi \
echo   --cpu=1 \
echo   --max-retries=3 \
echo   --task-timeout=600
echo.
echo gcloud run jobs execute migrate-final-v3 --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 2. POPULAR DADOS COM USUÁRIO CORRETO
echo gcloud run jobs create populate-final-v3 \
echo   --image gcr.io/monpec-sistema-rural/monpec:latest \
echo   --region us-central1 \
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" \
echo   --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
echo   --command="python" \
echo   --args="popular_dados_producao.py" \
echo   --memory=2Gi \
echo   --cpu=1 \
echo   --max-retries=3 \
echo   --task-timeout=600
echo.
echo gcloud run jobs execute populate-final-v3 --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 3. ATUALIZAR SERVIÇO COM USUÁRIO CORRETO
echo gcloud run services update monpec \
echo   --region=us-central1 \
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" \
echo   --memory=2Gi \
echo   --cpu=2 \
echo   --timeout=300
echo.
echo ========================================
echo.
echo # 4. TESTAR SE FUNCIONOU
echo curl https://monpec-29862706245.us-central1.run.app/
echo.
echo ========================================
echo.
echo URLs APÓS CORREÇÃO:
echo.
echo Landing:     https://monpec-29862706245.us-central1.run.app/
echo Admin:       https://monpec-29862706245.us-central1.run.app/admin/
echo Dashboard:   https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/
echo Planejamento: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/planejamento/
echo.
echo ========================================

pause