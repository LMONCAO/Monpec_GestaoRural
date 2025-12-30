@echo off
REM Script simples para criar usuário admin usando o comando Django
REM Execute: CRIAR_ADMIN_SIMPLES.bat

echo ============================================================
echo CRIAR USUARIO ADMINISTRADOR - SISTEMA MONPEC
echo ============================================================
echo.

REM Verificar se o ambiente virtual existe
if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else if exist "python311\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call python311\Scripts\activate.bat
) else (
    echo Aviso: Ambiente virtual nao encontrado. Continuando...
)

echo.
echo Opcoes:
echo 1. Criar admin com senha padrao (L6171r12@@)
echo 2. Criar admin com senha personalizada
echo 3. Criar admin com username e email personalizados
echo.
set /p opcao="Escolha uma opcao (1-3): "

if "%opcao%"=="1" (
    echo.
    echo Criando admin com senha padrao...
    python manage.py garantir_admin
) else if "%opcao%"=="2" (
    echo.
    set /p senha="Digite a senha (minimo 12 caracteres): "
    echo.
    echo Criando admin com senha personalizada...
    python manage.py garantir_admin --senha "%senha%"
) else if "%opcao%"=="3" (
    echo.
    set /p username="Digite o username (ou Enter para 'admin'): "
    if "%username%"=="" set username=admin
    set /p email="Digite o email (ou Enter para 'admin@monpec.com.br'): "
    if "%email%"=="" set email=admin@monpec.com.br
    set /p senha="Digite a senha (minimo 12 caracteres): "
    echo.
    echo Criando admin personalizado...
    python manage.py garantir_admin --username "%username%" --email "%email%" --senha "%senha%"
) else (
    echo.
    echo Opcao invalida! Criando admin com senha padrao...
    python manage.py garantir_admin
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCESSO! Usuario admin criado.
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERRO ao criar usuario admin.
    echo ============================================================
)

echo.
pause

