@echo off
chcp 65001 >nul
title DEPLOY MONPEC - LOCAWEB
color 0A

echo.
echo ╔════════════════════════════════════════════╗
echo ║   🌐 DEPLOY MONPEC PARA LOCAWEB            ║
echo ╚════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Verificar se está no diretório correto
if not exist manage.py (
    echo [ERRO] Arquivo manage.py não encontrado!
    echo Execute este script na raiz do projeto Django.
    pause
    exit /b 1
)

echo [INFO] Diretório do projeto: %CD%
echo.

REM Verificar se PowerShell está disponível
powershell -Command "exit 0" >nul 2>&1
if errorlevel 1 (
    echo [ERRO] PowerShell não encontrado!
    pause
    exit /b 1
)

echo [INFO] Iniciando deploy...
echo.

REM Executar script PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0DEPLOY_LOCAWEB.ps1" -IP "10.1.1.234" -Usuario "ubuntu" -ChaveSSH "@MONPEC.key (1-28)"

if errorlevel 1 (
    echo.
    echo [ERRO] Deploy falhou!
    echo.
    echo Verifique:
    echo 1. Se a VM está rodando no painel da Locaweb
    echo 2. Se o IP está correto (10.1.1.234)
    echo 3. Se a chave SSH está no diretório
    echo 4. Se o SSH está configurado corretamente
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Deploy concluído com sucesso!
echo.
echo 📋 Próximos passos:
echo 1. Acesse http://10.1.1.234 para testar
echo 2. Configure o DNS do domínio monpec.com.br
echo 3. Configure SSL com: certbot --nginx -d monpec.com.br
echo.
pause







