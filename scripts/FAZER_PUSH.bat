@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   FAZER PUSH DAS CORREÇÕES
echo ========================================
echo.

REM Procurar o diretório do projeto
for /f "delims=" %%i in ('dir /s /b "C:\Users\lmonc\Desktop\*manage.py" 2^>nul ^| findstr /i "Monpec_GestaoRural"') do (
    cd /d "%%~dpi"
    goto :found
)

echo ❌ Diretório não encontrado!
pause
exit /b 1

:found
echo ✅ Diretório: %CD%
echo.

echo 📥 Fazendo pull para sincronizar...
git pull origin master --no-edit

if %errorlevel% neq 0 (
    echo ⚠️  Conflitos detectados ou erro no pull
    echo    Tentando pull com rebase...
    git pull --rebase origin master
)

echo.
echo 📤 Fazendo push...
git push origin master

if %errorlevel% equ 0 (
    echo.
    echo ✅✅✅ PUSH REALIZADO COM SUCESSO! ✅✅✅
    echo.
    echo 🚀 O workflow GitHub Actions vai iniciar automaticamente!
    echo    Você pode acompanhar em: https://github.com/LMONCAO/Monpec_GestaoRural/actions
) else (
    echo.
    echo ⚠️  Erro no push
    echo    Tente manualmente: git push origin master
)

echo.
pause
