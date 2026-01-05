@echo off
chcp 65001 >nul
echo ========================================
echo Adicionar DATABASE_URL no Fly.io
echo ========================================
echo.
echo IMPORTANTE: Você precisa da URL do PostgreSQL!
echo.
echo Para obter a URL:
echo 1. Acesse: https://fly.io/dashboard
echo 2. Vá para o app do PostgreSQL
echo 3. Settings -^> Connection String
echo 4. Copie a URL completa
echo.
echo OU execute: fly postgres connect -a ^<nome-do-postgres^>
echo.
echo ========================================
echo.
set /p DATABASE_URL="Cole a DATABASE_URL aqui: "

if "%DATABASE_URL%"=="" (
    echo ❌ DATABASE_URL não pode estar vazio!
    pause
    exit /b 1
)

echo.
echo Adicionando DATABASE_URL...
fly secrets set DATABASE_URL="%DATABASE_URL%" -a monpec-gestaorural

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DATABASE_URL adicionado com sucesso!
) else (
    echo.
    echo ❌ Erro ao adicionar DATABASE_URL
    echo Verifique se você está logado: fly auth login
)

echo.
pause
