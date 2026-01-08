@echo off
chcp 65001 >nul
echo ========================================
echo   DIAGN??STICO: SERVICE UNAVAILABLE
echo ========================================
echo.
echo ??? PROBLEMA ENCONTRADO:
echo    SECRET_KEY n??o configurada!
echo    Faltam vari??veis de ambiente no Cloud Run
echo.
echo ??? SOLU????O EM ANDAMENTO:
echo    GitHub Actions est?? fazendo novo build
echo    Quando completar, vai fazer deploy com TODAS as vari??veis
echo.
echo ??????  AGUARDE:
echo    Build em andamento (5-10 minutos)
echo    Depois deploy autom??tico (2-3 minutos)
echo    Total: ~10-15 minutos
echo.
echo ???? ACOMPANHE:
echo    https://github.com/LMONCAO/Monpec_GestaoRural/actions
echo.
echo ???? O QUE VAI ACONTECER:
echo    1. Build completa (com collectstatic)
echo    2. Deploy com todas as vari??veis:
echo       - SECRET_KEY
echo       - DB_NAME, DB_USER, DB_PASSWORD
echo       - CLOUD_SQL_CONNECTION_NAME
echo       - GOOGLE_CLOUD_PROJECT
echo       - DEMO_USER_PASSWORD
echo    3. Sistema funcionando!
echo.
pause