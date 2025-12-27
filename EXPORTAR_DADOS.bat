@echo off
chcp 65001 >nul
title MONPEC - EXPORTAR DADOS
color 0C

echo ========================================
echo   MONPEC - EXPORTAR DADOS
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

REM ========================================
REM CRIAR PASTA DE BACKUP
REM ========================================
set BACKUP_DIR=backups\export_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

if not exist "backups" mkdir "backups"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo [INFO] Exportando dados para: %BACKUP_DIR%
echo.

REM ========================================
REM EXPORTAR BANCO DE DADOS
REM ========================================
echo [1/3] Exportando banco de dados...
if exist "db.sqlite3" (
    copy /Y "db.sqlite3" "%BACKUP_DIR%\db.sqlite3"
    echo [OK] Banco de dados exportado
) else (
    echo [AVISO] Banco de dados não encontrado
)
echo.

REM ========================================
REM EXPORTAR DADOS VIA DJANGO
REM ========================================
echo [2/3] Exportando dados do sistema...
%PYTHON_CMD% manage.py dumpdata --indent 2 --output "%BACKUP_DIR%\dados_exportados.json" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Falha ao exportar dados JSON
) else (
    echo [OK] Dados exportados em JSON
)
echo.

REM ========================================
REM CRIAR ARQUIVO DE INFORMAÇÕES
REM ========================================
echo [3/3] Criando arquivo de informações...
(
    echo Data da Exportação: %date% %time%
    echo Sistema: MONPEC Gestão Rural
    echo.
    echo Arquivos exportados:
    echo - db.sqlite3
    echo - dados_exportados.json
    echo.
    echo Para importar, use IMPORTAR_DADOS.bat
) > "%BACKUP_DIR%\INFO_EXPORTACAO.txt"
echo [OK] Arquivo de informações criado
echo.

echo ========================================
echo   EXPORTAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Dados exportados para: %BACKUP_DIR%
echo.
echo ========================================
pause















<<<<<<< HEAD











=======
>>>>>>> 82f662d03a852eab216d20cd9d12193f5dbd2881





































