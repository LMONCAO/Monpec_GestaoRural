@echo off
chcp 65001 >nul
echo ========================================
echo   CRIAR ADMIN - SOLUCAO RAPIDA
echo ========================================
echo.
echo Este script vai tentar criar o usuario admin
echo de varias formas diferentes.
echo.
pause

REM Tentar executar o script Python localmente
echo.
echo Tentativa 1: Executando script Python local...
python corrigir_senha_admin.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCESSO! Admin criado localmente
    pause
    exit /b 0
)

echo.
echo Tentativa 2: Executando script simplificado...
python criar_admin_simples.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCESSO! Admin criado
    pause
    exit /b 0
)

echo.
echo ❌ Nenhuma tentativa funcionou
echo.
echo SOLUCOES ALTERNATIVAS:
echo.
echo 1. Acesse o Cloud Shell no Google Cloud Console
echo 2. Execute: gcloud run services proxy monpec --region us-central1 --port 8080
echo 3. Em outro terminal, execute: python manage.py shell
echo 4. Execute o codigo Python do arquivo SOLUCAO_ADMIN.md
echo.
echo OU
echo.
echo 1. Acesse o Cloud SQL no console
echo 2. Conecte ao banco monpec_db
echo 3. Execute o SQL do arquivo CRIAR_ADMIN_URGENTE.md
echo.
pause
