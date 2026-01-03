@echo off
REM Script para verificar logs e diagnosticar erro 500 no Cloud Run
REM Execute no Google Cloud Shell

echo ============================================================
echo 🔍 DIAGNOSTICAR ERRO 500 - SISTEMA MONPEC
echo ============================================================
echo.

echo 📋 Verificando logs recentes do Cloud Run...
echo.

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50 --format="table(timestamp,severity,textPayload)"

echo.
echo ============================================================
echo 📊 Verificando status do serviço...
echo ============================================================
echo.

gcloud run services describe monpec --region=us-central1 --format="value(status.conditions)"

echo.
echo ============================================================
echo 💾 Verificando Cloud SQL...
echo ============================================================
echo.

gcloud sql instances describe monpec-db --format="value(state)"

echo.
echo ============================================================
echo ✅ Diagnóstico concluído!
echo ============================================================
echo.
echo 💡 Próximos passos:
echo    1. Verifique os erros acima
echo    2. Se houver erros de migrations, execute: aplicar_migracoes_agora.bat
echo    3. Se houver erros de conexão, verifique as variáveis de ambiente
echo.

pause
