@echo off
echo ========================================
echo    SISTEMA MONPEC - GESTAO RURAL
echo ========================================
echo.
echo Iniciando o servidor...
echo.

REM Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Iniciar servidor Django (aceita conexões da rede - celular)
echo.
echo ========================================
echo   ACESSO PELO CELULAR:
echo   http://192.168.100.4:8000
echo ========================================
echo.
echo Certifique-se de que o celular está na mesma rede Wi-Fi!
echo.
python manage.py runserver 0.0.0.0:8000

pause
