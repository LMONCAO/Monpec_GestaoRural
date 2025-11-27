@echo off
REM ========================================
REM PARAR TODOS OS SISTEMAS MONPEC
REM ========================================
title Parar Todos os Sistemas MONPEC

echo ========================================
echo   PARANDO TODOS OS SISTEMAS MONPEC
echo ========================================
echo.

echo [INFO] Parando todos os processos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
taskkill /F /IM python3.13.exe 2>nul
timeout /t 2 /nobreak >nul

echo [INFO] Desabilitando tarefa agendada...
schtasks /Change /TN "MONPEC_Servidor_Django" /Disable 2>nul

echo.
echo [OK] Todos os sistemas foram parados!
echo.
echo IMPORTANTE: Para remover a tarefa agendada permanentemente,
echo execute como Administrador:
echo   schtasks /Delete /TN "MONPEC_Servidor_Django" /F
echo.
pause

