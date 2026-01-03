@echo off
REM ============================================
REM CORRIGIR TODOS OS SCRIPTS .BAT
REM ============================================
REM Este script corrige todos os scripts .bat
REM que estão tentando acessar manage.py do
REM diretório incorreto
REM ============================================

echo.
echo ========================================
echo   CORRIGINDO TODOS OS SCRIPTS .BAT
echo ========================================
echo.

REM Ir para o diretório raiz do projeto
cd /d "%~dp0\..\.."

if not exist "manage.py" (
    echo [ERRO] manage.py nao encontrado na raiz do projeto!
    pause
    exit /b 1
)

echo [OK] Diretorio raiz encontrado: %CD%
echo.

REM Contador de scripts corrigidos
set CORRIGIDOS=0

REM Corrigir todos os scripts .bat em scripts/deploy
echo [INFO] Procurando scripts .bat em scripts\deploy\...
echo.

for %%f in ("scripts\deploy\*.bat") do (
    echo [VERIFICANDO] %%~nxf
    
    REM Verificar se o script tem "cd /d %~dp0" sem "..\.."
    findstr /C:"cd /d \"%%~dp0\"" "%%f" >nul 2>&1
    if errorlevel 1 (
        REM Verificar se tem "cd /d %~dp0" sem aspas
        findstr /C:"cd /d %%~dp0" "%%f" >nul 2>&1
        if errorlevel 1 (
            echo   [PULADO] Nao precisa de correcao
        ) else (
            echo   [CORRIGINDO] %%~nxf
            REM Criar backup
            copy "%%f" "%%f.bak" >nul 2>&1
            REM Substituir cd /d "%~dp0" por cd /d "%~dp0\..\.."
            powershell -Command "(Get-Content '%%f') -replace 'cd /d \"%%~dp0\"', 'cd /d \"%%~dp0\..\..\"' | Set-Content '%%f'"
            set /a CORRIGIDOS+=1
            echo   [OK] Corrigido
        )
    ) else (
        REM Verificar se já tem "..\.."
        findstr /C:"cd /d \"%%~dp0\..\..\"" "%%f" >nul 2>&1
        if errorlevel 1 (
            echo   [CORRIGINDO] %%~nxf
            REM Criar backup
            copy "%%f" "%%f.bak" >nul 2>&1
            REM Substituir cd /d "%~dp0" por cd /d "%~dp0\..\.."
            powershell -Command "(Get-Content '%%f') -replace 'cd /d \"%%~dp0\"', 'cd /d \"%%~dp0\..\..\"' | Set-Content '%%f'"
            set /a CORRIGIDOS+=1
            echo   [OK] Corrigido
        ) else (
            echo   [PULADO] Ja esta correto
        )
    )
    echo.
)

echo ========================================
echo   RESUMO
echo ========================================
echo.
echo [OK] Scripts corrigidos: %CORRIGIDOS%
echo [INFO] Backups criados com extensao .bak
echo.
echo ========================================
echo.
pause



