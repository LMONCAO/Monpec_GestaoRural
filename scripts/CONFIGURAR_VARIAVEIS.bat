@echo off
chcp 65001 >nul
echo ========================================
echo   CONFIGURAR VARI??VEIS DE AMBIENTE
echo ========================================
echo.
echo ??????  IMPORTANTE: Este script precisa das vari??veis de ambiente.
echo    Elas devem estar configuradas no GitHub Secrets ou voc?? precisa
echo    fornec??-las manualmente.
echo.
echo ???? Vari??veis necess??rias:
echo    - SECRET_KEY
echo    - DB_NAME
echo    - DB_USER
echo    - DB_PASSWORD
echo    - CLOUD_SQL_CONNECTION_NAME
echo    - GOOGLE_CLOUD_PROJECT
echo.
echo ???? SOLU????O R??PIDA:
echo    Configure as vari??veis no Cloud Run Console:
echo    https://console.cloud.google.com/run/detail/us-central1/monpec/variables-and-secrets?project=monpec-sistema-rural
echo.
echo    OU execute o deploy via GitHub Actions que j?? tem tudo configurado.
echo.
pause