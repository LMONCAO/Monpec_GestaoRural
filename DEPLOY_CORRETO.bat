@echo off
REM DEPLOY FINAL COM NOMES CORRETOS

echo ========================================
echo DEPLOY FINAL MONPEC - NOMES CORRETOS
echo ========================================
echo.
echo CONFIGURAÇÕES CORRETAS:
echo - Instância Cloud SQL: monpec-db
echo - Banco de dados: monpec_db
echo - Usuário: postgres
echo - Senha: L6171r12@@jjms
echo.
echo ========================================
echo.
echo EXECUTE estes comandos no Google Cloud Shell:
echo.
echo ========================================
echo.
echo # 1. MIGRAÇÕES COM NOMES CORRETOS
echo gcloud run jobs create migrate-final-correto \
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
echo gcloud run jobs execute migrate-final-correto --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 2. POPULAR DADOS
echo gcloud run jobs create populate-final-correto \
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
echo gcloud run jobs execute populate-final-correto --region=us-central1 --wait
echo.
echo ========================================
echo.
echo # 3. ATUALIZAR SERVIÇO
echo gcloud run services update monpec \
echo   --region=us-central1 \
echo   --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False" \
echo   --memory=2Gi \
echo   --cpu=2 \
echo   --timeout=300
echo.
echo ========================================
echo.
echo # 4. TESTAR SISTEMA
echo echo "=== TESTANDO SISTEMA ==="
echo curl -s https://monpec-29862706245.us-central1.run.app/ ^| grep -i "monpec\\|gestao" ^| head -5
echo.
echo echo "=== TESTANDO DASHBOARD ==="
echo curl -s https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/ ^| grep -i "dashboard\\|pecuaria" ^| head -3
echo.
echo ========================================
echo.
echo SISTEMA PRONTO! ACESSE:
echo.
echo 🌐 Landing: https://monpec-29862706245.us-central1.run.app/
echo 🔐 Admin:   https://monpec-29862706245.us-central1.run.app/admin/
echo 📊 Sistema: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/
echo.
echo ========================================
echo.
echo LOGIN:
echo Usuario: admin
echo Senha: [sua senha]
echo.
echo ========================================

pause