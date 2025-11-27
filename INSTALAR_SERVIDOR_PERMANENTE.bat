@echo off
REM ========================================
REM INSTALAR MONPEC COMO SERVIDOR PERMANENTE
REM Cria uma tarefa agendada do Windows para iniciar automaticamente
REM ========================================
title Instalar MONPEC como Servidor Permanente

echo ========================================
echo   INSTALAR MONPEC COMO SERVIDOR PERMANENTE
echo ========================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [AVISO] Este script precisa ser executado como Administrador!
    echo.
    echo Clique com o botao direito no arquivo e selecione:
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

REM Obter o caminho completo do script
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%MONPEC_DESENVOLVIMENTO_PERMANENTE.bat

REM Verificar se o arquivo existe
if not exist "%SCRIPT_PATH%" (
    echo [ERRO] Arquivo MONPEC_DESENVOLVIMENTO_PERMANENTE.bat nao encontrado!
    pause
    exit /b 1
)

echo [INFO] Criando tarefa agendada do Windows...
echo [INFO] Nome da tarefa: MONPEC_Desenvolvimento_Permanente
echo [INFO] Script: %SCRIPT_PATH%
echo.

REM Remover tarefa existente se houver
schtasks /Delete /TN "MONPEC_Desenvolvimento_Permanente" /F >nul 2>&1

REM Criar nova tarefa agendada
REM A tarefa será executada quando o usuário fizer login
schtasks /Create /TN "MONPEC_Desenvolvimento_Permanente" /TR "\"%SCRIPT_PATH%\"" /SC ONLOGON /RL HIGHEST /F

if %errorLevel% equ 0 (
    echo [OK] Tarefa agendada criada com sucesso!
    echo.
    echo [INFO] O servidor MONPEC sera iniciado automaticamente quando voce fizer login.
    echo [INFO] Para iniciar manualmente agora, execute: MONPEC_DESENVOLVIMENTO_PERMANENTE.bat
    echo.
    echo [INFO] Para remover a tarefa agendada, execute:
    echo        schtasks /Delete /TN "MONPEC_Desenvolvimento_Permanente"
) else (
    echo [ERRO] Falha ao criar tarefa agendada!
    echo [INFO] Voce pode executar manualmente: MONPEC_DESENVOLVIMENTO_PERMANENTE.bat
)

echo.
pause

