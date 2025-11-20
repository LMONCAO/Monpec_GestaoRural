@echo off
echo ========================================
echo   MONPEC - ACESSO PELO CELULAR
echo ========================================
echo.
echo Iniciando servidor para acesso via rede...
echo.

cd /d "%~dp0"

REM Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo ========================================
echo   ENDERECOS PARA ACESSAR:
echo   Local:    http://127.0.0.1:8000
echo   Celular:  http://192.168.100.4:8000
echo ========================================
echo.
echo IMPORTANTE:
echo - Celular deve estar na mesma rede Wi-Fi
echo - Firewall do Windows pode bloquear acesso
echo - Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver 0.0.0.0:8000

pause

