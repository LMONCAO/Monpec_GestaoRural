@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   FAZER COMMIT DAS CORREÇÕES
echo ========================================
echo.

REM Navegar para o diretório do projeto (onde o script está)
cd /d "%~dp0"

REM Verificar se estamos no diretório correto procurando por manage.py
if not exist "manage.py" (
    REM Tentar encontrar o diretório do projeto
    for /f "delims=" %%i in ('where /r "C:\Users\lmonc\Desktop" manage.py 2^>nul') do (
        cd /d "%%~dpi"
        goto :found
    )
    echo ❌ Não foi possível encontrar o diretório do projeto!
    pause
    exit /b 1
)
:found

REM Verificar se está no diretório correto
if not exist "manage.py" (
    echo ❌ Erro: Execute este script na raiz do projeto!
    echo    O arquivo manage.py deve estar no diretório atual.
    pause
    exit /b 1
)

echo ✅ Diretório do projeto encontrado
echo.

REM Verificar status do git
echo 📋 Verificando status do Git...
git status --short
echo.

REM Adicionar arquivos modificados
echo 📦 Adicionando arquivos modificados...
git add gestao_rural/views.py
git add gestao_rural/views_demo_setup.py
git add INSTRUCOES_DOCKERFILE.txt

REM Verificar se há mudanças para commitar
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo ⚠️  Nenhuma mudança para commitar
    echo    Verificando se os arquivos foram modificados...
    git status gestao_rural/views.py gestao_rural/views_demo_setup.py
) else (
    echo ✅ Arquivos adicionados com sucesso
    echo.
    
    REM Fazer commit
    echo 💾 Fazendo commit...
    git commit -m "Fix: Resolver problemas de deploy - simplificar demo, criar propriedade automaticamente e redirecionar para landing page"
    
    if %errorlevel% equ 0 (
        echo ✅ Commit realizado com sucesso!
        echo.
        echo 📤 Deseja fazer push agora? (S/N)
        set /p resposta=
        if /i "%resposta%"=="S" (
            echo.
            echo 📤 Fazendo push...
            git push origin main
            if %errorlevel% equ 0 (
                echo ✅ Push realizado com sucesso!
            ) else (
                echo ⚠️  Erro no push. Tente manualmente: git push origin main
            )
        ) else (
            echo.
            echo ℹ️  Para fazer push depois, execute:
            echo    git push origin main
        )
    ) else (
        echo ❌ Erro ao fazer commit
    )
)

echo.
echo ========================================
echo ✅ PROCESSO CONCLUÍDO!
echo ========================================
echo.
pause
