@echo off
title MONPEC PROJETISTA - Servidor Django
color 0A
echo.
echo ==========================================
echo   MONPEC PROJETISTA
echo   Sistema de Gestao Rural
echo ==========================================
echo.

REM Parar processos Python
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

cd /d "C:\Monpec_projetista"

echo Criando banco de dados...
python manage.py migrate

echo.
echo ==========================================
echo Iniciando servidor na porta 8000...
echo.
echo Acesse: http://localhost:8000/
echo ==========================================
echo.

python manage.py runserver 8000

pause


