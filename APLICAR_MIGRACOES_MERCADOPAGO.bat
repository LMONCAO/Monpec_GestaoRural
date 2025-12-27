@echo off
chcp 65001 >nul
echo 🔄 Aplicando migrações do Mercado Pago...
echo.

cd /d "%~dp0"

echo 📍 Diretório atual:
cd

echo.
echo 🔄 Criando migrações...
python manage.py makemigrations gestao_rural

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao criar migrações!
    pause
    exit /b 1
)

echo.
echo 🔄 Aplicando migrações...
python manage.py migrate gestao_rural

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro ao aplicar migrações!
    pause
    exit /b 1
)

echo.
echo ✅ Migrações aplicadas com sucesso!
echo.
echo Os novos campos do Mercado Pago foram adicionados ao banco de dados.
echo.
pause






















