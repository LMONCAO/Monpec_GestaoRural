@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   VERIFICAR E FAZER COMMIT
echo ========================================
echo.

REM Encontrar o diretório do projeto (onde está manage.py)
for /f "delims=" %%i in ('where /r "C:\Users\lmonc\Desktop" manage.py 2^>nul ^| findstr /i "Monpec_GestaoRural"') do (
    cd /d "%%~dpi"
    goto :found
)

echo ❌ Não foi possível encontrar o diretório do projeto!
pause
exit /b 1

:found
echo ✅ Diretório encontrado: %CD%
echo.

REM Verificar se há repositório git aqui
if not exist ".git" (
    echo ❌ Não há repositório Git neste diretório!
    echo    Verificando se há repositório git no diretório pai...
    cd ..
    if exist ".git" (
        echo ✅ Repositório Git encontrado no diretório pai
    ) else (
        echo ❌ Repositório Git não encontrado!
        pause
        exit /b 1
    )
)

echo.
echo 📋 Status atual do Git:
git status --short
echo.

REM Verificar se os arquivos foram modificados
git diff --quiet gestao_rural/views.py gestao_rural/views_demo_setup.py
if %errorlevel% equ 0 (
    echo ⚠️  Os arquivos não foram modificados ou já estão commitados
    echo    Verificando último commit...
    git log -1 --oneline
    echo.
    echo    Verificando se as mudanças estão no último commit...
    git show HEAD --name-only | findstr /i "views.py views_demo_setup.py"
) else (
    echo ✅ Arquivos foram modificados!
    echo.
    echo 📦 Adicionando arquivos ao stage...
    git add gestao_rural/views.py
    git add gestao_rural/views_demo_setup.py
    if exist "INSTRUCOES_DOCKERFILE.txt" (
        git add INSTRUCOES_DOCKERFILE.txt
    )
    echo.
    echo 💾 Fazendo commit...
    git commit -m "Fix: Resolver problemas de deploy - simplificar demo, criar propriedade automaticamente e redirecionar para landing page"
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅✅✅ COMMIT REALIZADO COM SUCESSO! ✅✅✅
        echo.
        echo 📤 Deseja fazer push agora? (S/N)
        set /p resposta=
        if /i "%resposta%"=="S" (
            echo.
            echo 📤 Fazendo push para origin main...
            git push origin main
            if %errorlevel% equ 0 (
                echo.
                echo ✅✅✅ PUSH REALIZADO COM SUCESSO! ✅✅✅
                echo    O workflow GitHub Actions vai iniciar automaticamente!
            ) else (
                echo.
                echo ⚠️  Erro no push. Tente manualmente:
                echo    git push origin main
            )
        ) else (
            echo.
            echo ℹ️  Para fazer push depois, execute:
            echo    git push origin main
        )
    ) else (
        echo.
        echo ❌ Erro ao fazer commit
        echo    Verifique se há mudanças para commitar
    )
)

echo.
echo ========================================
echo ✅ VERIFICAÇÃO CONCLUÍDA!
echo ========================================
echo.
pause
