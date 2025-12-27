@echo off
REM Script para redefinir senha de usuário no Windows
echo 🔐 Redefinindo senha do usuário...
echo.

python redefinir_senha_usuario.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Senha redefinida com sucesso!
) else (
    echo.
    echo ❌ Erro ao redefinir senha
    pause
    exit /b 1
)

pause






































