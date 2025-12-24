@echo off
echo Iniciando servidor Django...
cd /d "%~dp0"
python manage.py runserver
pause
