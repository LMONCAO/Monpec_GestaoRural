@echo off
chcp 65001 >nul
title MONPEC - IMPORTAR BANCO DE OUTRA MAQUINA
color 0E

echo ========================================
echo   MONPEC - IMPORTAR BANCO DE OUTRA MAQUINA
echo   Sistema de Gestão Rural
echo ========================================
echo.

cd /d "%~dp0"

REM ========================================
REM FAZER BACKUP DO BANCO ATUAL
REM ========================================
echo [1/4] Fazendo backup do banco atual...
if exist "db.sqlite3" (
    set BACKUP_ATUAL=backups\db_backup_antes_importacao_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sqlite3
    set BACKUP_ATUAL=%BACKUP_ATUAL: =0%
    
    if not exist "backups" mkdir "backups"
    copy /Y "db.sqlite3" "%BACKUP_ATUAL%" >nul 2>&1
    echo [OK] Backup criado: %BACKUP_ATUAL%
) else (
    echo [INFO] Nenhum banco atual para fazer backup
)
echo.

REM ========================================
REM SOLICITAR CAMINHO DO BANCO
REM ========================================
echo [2/4] Localizar banco de dados da outra máquina
echo.
echo Opções:
echo 1. Copiar arquivo db.sqlite3 para esta pasta
echo 2. Informar caminho do arquivo
echo.
set /p OPCAO="Escolha a opção (1 ou 2): "

if "%OPCAO%"=="1" (
    echo.
    echo [INFO] Aguardando arquivo db.sqlite3 na pasta atual...
    echo [INFO] Pressione qualquer tecla quando o arquivo estiver na pasta...
    pause >nul
    
    if not exist "db.sqlite3" (
        echo [ERRO] Arquivo db.sqlite3 não encontrado na pasta atual!
        pause
        exit /b 1
    )
    echo [OK] Arquivo db.sqlite3 encontrado
) else if "%OPCAO%"=="2" (
    echo.
    set /p CAMINHO_BANCO="Digite o caminho completo do arquivo db.sqlite3: "
    
    if not exist "%CAMINHO_BANCO%" (
        echo [ERRO] Arquivo não encontrado: %CAMINHO_BANCO%
        pause
        exit /b 1
    )
    
    copy /Y "%CAMINHO_BANCO%" "db.sqlite3" >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Falha ao copiar arquivo!
        pause
        exit /b 1
    )
    echo [OK] Arquivo copiado com sucesso
) else (
    echo [ERRO] Opção inválida!
    pause
    exit /b 1
)
echo.

REM ========================================
REM VERIFICAR PYTHON
REM ========================================
echo [3/4] Verificando Python...
if exist "python311\python.exe" (
    set PYTHON_CMD=python311\python.exe
) else (
    set PYTHON_CMD=python
)
echo [OK] Python encontrado
echo.

REM ========================================
REM VERIFICAR BANCO IMPORTADO
REM ========================================
echo [4/4] Verificando banco importado...
%PYTHON_CMD% verificar_banco_correto.py
if errorlevel 1 (
    echo.
    echo [AVISO] O banco pode não ter os dados esperados
    echo [AVISO] Mas continuando mesmo assim...
)
echo.

REM ========================================
REM APLICAR MIGRAÇÕES
REM ========================================
echo [EXTRA] Aplicando migrações...
%PYTHON_CMD% manage.py migrate --noinput
if errorlevel 1 (
    echo [AVISO] Algumas migrações podem ter falhado
) else (
    echo [OK] Migrações aplicadas
)
echo.

echo ========================================
echo   IMPORTAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Próximos passos:
echo 1. Execute INICIAR.bat para iniciar o servidor
echo 2. Verifique se os dados foram importados corretamente
echo 3. Acesse http://localhost:8000
echo.
echo ========================================
pause



