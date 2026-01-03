@echo off
REM Script para criar usuário admin no Windows
echo 🔐 Criando usuário administrador...
echo.

python criar_admin.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Usuário admin criado com sucesso!
    echo.
    echo Credenciais de acesso:
    echo   Username: admin
    echo   Senha: L6171r12@@
) else (
    echo.
    echo ❌ Erro ao criar usuário admin
    pause
    exit /b 1
)

pause













































