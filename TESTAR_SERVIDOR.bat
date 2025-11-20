@echo off
title Teste Servidor Django
cd /d "%~dp0"
echo Testando servidor...
.\python311\python.exe manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_windows
pause






