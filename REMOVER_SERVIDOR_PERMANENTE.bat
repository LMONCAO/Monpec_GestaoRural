@echo off
REM ========================================
REM REMOVER SERVIDOR PERMANENTE MONPEC
REM Remove a tarefa agendada do Windows
REM ========================================
title Remover Servidor Permanente MONPEC

echo ========================================
echo   REMOVER SERVIDOR PERMANENTE MONPEC
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

echo [INFO] Removendo tarefa agendada...
schtasks /Delete /TN "MONPEC_Desenvolvimento_Permanente" /F

if %errorLevel% equ 0 (
    echo [OK] Tarefa agendada removida com sucesso!
) else (
    echo [AVISO] Tarefa agendada nao encontrada ou ja foi removida.
)

REM Parar processos Python do MONPEC
echo.
echo [INFO] Parando processos Python do MONPEC...
taskkill /F /IM python.exe 2>nul
if %errorLevel% equ 0 (
    echo [OK] Processos Python parados.
) else (
    echo [INFO] Nenhum processo Python encontrado.
)

echo.
echo [OK] Servidor permanente removido!
echo.
pause

