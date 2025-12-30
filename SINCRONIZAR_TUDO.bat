@echo off
REM Script completo para sincronizar tudo com GitHub
REM Este script faz commit e push de todos os arquivos necessarios

setlocal enabledelayedexpansion

echo ==========================================
echo SINCRONIZAR TUDO COM GITHUB
echo ==========================================
echo.

REM Navegar para o diretorio do script
cd /d "%~dp0"

echo [1/5] Verificando se estamos no diretorio correto...
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado!
    echo Certifique-se de executar este script na pasta do projeto.
    pause
    exit /b 1
)
echo [OK] Diretorio correto
echo.

echo [2/5] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git nao encontrado! Instale o Git primeiro.
    pause
    exit /b 1
)
echo [OK] Git encontrado
echo.

echo [3/5] Inicializando Git (se necessario)...
if not exist ".git" (
    echo Inicializando repositorio Git...
    git init
    if errorlevel 1 (
        echo [ERRO] Falha ao inicializar Git
        pause
        exit /b 1
    )
)

REM Configurar remote (ignora erro se ja existe)
git remote add origin https://github.com/LMONCAO/Monpec_GestaoRural.git 2>nul
git remote set-url origin https://github.com/LMONCAO/Monpec_GestaoRural.git 2>nul

echo [OK] Git configurado
echo.

echo [4/5] Adicionando todos os arquivos...
git add -A
if errorlevel 1 (
    echo [AVISO] Alguns arquivos podem nao ter sido adicionados
)

echo Verificando o que sera commitado...
git status --short | findstr /V "Desktop Documents" | findstr /V "AppData" | findstr /V "Music Pictures" | findstr /V "Videos" | findstr /V "Downloads" | findstr /V "Contacts"
echo.

echo [5/5] Fazendo commit...
git commit -m "Adicionar integracao GitHub Actions, scripts de migracao e documentacao completa" 2>nul
if errorlevel 1 (
    echo [AVISO] Nenhuma alteracao para commitar ou commit falhou
    echo Verificando status...
    git status --short | findstr /V "Desktop Documents" | findstr /V "AppData"
    echo.
    echo Deseja continuar mesmo assim? (S/N)
    set /p CONTINUAR=
    if /i not "!CONTINUAR!"=="S" (
        echo Operacao cancelada.
        pause
        exit /b 1
    )
)
echo [OK] Commit realizado
echo.

echo [6/6] Fazendo push para GitHub...
echo Isso pode levar alguns segundos...
git push -u origin master
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao fazer push
    echo.
    echo Possiveis causas:
    echo - Nao esta autenticado no GitHub
    echo - Nao tem permissoes no repositorio
    echo - Branch master nao existe no remoto
    echo.
    echo Tentando criar branch master no remoto...
    git push -u origin master:master --force 2>nul
    if errorlevel 1 (
        echo.
        echo [ERRO] Nao foi possivel fazer push automaticamente
        echo.
        echo SOLUCAO MANUAL:
        echo 1. Abra o terminal nesta pasta
        echo 2. Execute: git push -u origin master
        echo 3. Ou acesse: https://github.com/LMONCAO/Monpec_GestaoRural
        echo    e crie o repositorio se nao existir
        pause
        exit /b 1
    )
)

echo.
echo ==========================================
echo SUCESSO!
echo ==========================================
echo.
echo Todos os arquivos foram sincronizados com o GitHub!
echo.
echo Repositorio: https://github.com/LMONCAO/Monpec_GestaoRural
echo.
echo Proximos passos:
echo 1. Execute: EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat
echo    Para criar as tabelas e o usuario admin no banco
echo.
echo 2. Configure GitHub Actions (opcional):
echo    Siga o guia: GUIA_SINCRONIZAR_GITHUB_GCLOUD.md
echo.
pause

