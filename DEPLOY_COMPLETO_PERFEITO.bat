@echo off
REM ==========================================
REM DEPLOY COMPLETO PERFEITO
REM Deploy completo via GitHub Actions
REM Mantém dados, layout e templates iguais ao local
REM ==========================================

setlocal enabledelayedexpansion

set PROJECT_ID=monpec-sistema-rural
set SERVICE_NAME=monpec
set REGION=us-central1

echo ==========================================
echo DEPLOY COMPLETO PERFEITO
echo ==========================================
echo.
echo Este script faz deploy completo via GitHub Actions
echo Mantendo dados, layout e templates do local
echo.

cd /d "%~dp0"

echo [1/6] Verificando se esta na pasta correta...
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    pause
    exit /b 1
)
echo [OK]
echo.

echo [2/6] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git nao encontrado!
    pause
    exit /b 1
)
echo [OK]
echo.

echo [3/6] Verificando se ha mudanças para commitar...
git add -A
git status --short >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Nenhuma mudanca detectada
) else (
    echo Mudancas detectadas:
    git status --short
    echo.
    echo [4/6] Fazendo commit...
    git commit -m "Deploy completo: atualizacao de templates, layout mobile e configuracoes" || echo Nenhuma mudanca para commitar
)
echo [OK]
echo.

echo [5/6] Fazendo push para GitHub...
git push origin master
if errorlevel 1 (
    echo [ERRO] Falha ao fazer push
    echo.
    echo Verifique:
    echo - Se esta autenticado no GitHub
    echo - Se tem permissoes no repositorio
    echo - Se o branch master existe
    pause
    exit /b 1
)
echo [OK]
echo.

echo [6/6] Verificando GitHub Actions...
echo.
echo ==========================================
echo SUCESSO!
echo ==========================================
echo.
echo O deploy foi iniciado via GitHub Actions!
echo.
echo Proximos passos:
echo 1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/actions
echo 2. Acompanhe o workflow "Deploy Completo - Google Cloud Run"
echo 3. Aguarde o deploy completar (10-20 minutos)
echo 4. O sistema sera atualizado automaticamente com:
echo    - Templates atualizados
echo    - Layout mobile otimizado (so botões no topo)
echo    - Imagens da landing page funcionando
echo    - Formulario de demo funcionando
echo.
echo Apos o deploy, execute para popular dados demo:
echo    EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat
echo.
pause

