@echo off
REM ========================================
REM CORRIGIR SISTEMA - EXECUTAR COMO ADMIN
REM Remove tarefa antiga e instala a correta
REM ========================================

REM Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ========================================
    echo   ERRO: PRECISA DE PRIVILEGIOS DE ADMIN
    echo ========================================
    echo.
    echo Clique com botao direito neste arquivo
    echo e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   CORRIGINDO SISTEMA MONPEC
echo   Removendo tarefa antiga e instalando correta
echo ========================================
echo.

REM Ir para o diretório do script
cd /d "%~dp0"

REM Parar processos Python
echo [1/4] Parando processos Python...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python311\python.exe 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Processos parados
echo.

REM Parar e remover tarefa antiga
echo [2/4] Removendo tarefa agendada antiga...
schtasks /Stop /TN "MONPEC_Servidor_Django" 2>nul
schtasks /Delete /TN "MONPEC_Servidor_Django" /F 2>nul
if %errorLevel% equ 0 (
    echo [OK] Tarefa antiga removida
) else (
    echo [INFO] Tarefa nao encontrada ou ja removida
)
echo.

REM Verificar banco de dados
echo [3/4] Verificando banco de dados...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)

%PYTHON_CMD% verificar_banco_canta_galo.py 2>nul
if %errorLevel% equ 0 (
    echo [OK] Banco de dados correto (Marcelo Sanguino / Fazenda Canta Galo)
) else (
    echo [AVISO] Nao foi possivel verificar o banco
)
echo.

REM Executar script PowerShell de instalação
echo [4/4] Instalando servidor permanente correto...
powershell -ExecutionPolicy Bypass -File "INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1"
if %errorLevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar servidor permanente
    echo [INFO] Execute manualmente: INSTALAR_SERVIDOR_PERMANENTE_MONPEC.ps1 (como Admin)
    pause
    exit /b 1
)

echo.
echo ========================================
echo   CORRECAO CONCLUIDA!
echo ========================================
echo.
echo O sistema foi configurado corretamente:
echo   - Tarefa antiga removida
echo   - Nova tarefa criada (diretorio correto)
echo   - Banco: db.sqlite3 (Marcelo Sanguino / Fazenda Canta Galo)
echo.
echo O servidor sera iniciado automaticamente no proximo login.
echo.
pause













