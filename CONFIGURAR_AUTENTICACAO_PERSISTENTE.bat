@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   CONFIGURAR AUTENTICACAO PERSISTENTE
echo   Google Cloud - Nao pede senha toda hora
echo ========================================
echo.

REM ========================================
REM CONFIGURACOES
REM ========================================
set PROJECT_ID=monpec-sistema-rural

echo [INFO] Este script vai configurar a autenticacao persistente
echo [INFO] Voce so precisara fazer login UMA VEZ
echo [INFO] Depois disso, os scripts funcionarao automaticamente
echo.
echo.

REM ========================================
REM PASSO 1: VERIFICAR gcloud
REM ========================================
echo [1/4] Verificando Google Cloud SDK...
where gcloud >nul 2>&1
if errorlevel 1 (
    echo [ERRO] gcloud nao encontrado!
    echo.
    echo Baixe e instale o Google Cloud SDK:
    echo https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)
echo [OK] Google Cloud SDK encontrado
echo.

REM ========================================
REM PASSO 2: CONFIGURAR AUTENTICACAO PRINCIPAL
REM ========================================
echo [2/4] Configurando autenticacao principal...
echo.
echo IMPORTANTE: Isso vai abrir o navegador para fazer login
echo Voce so precisa fazer isso UMA VEZ
echo.
pause

gcloud auth login --no-launch-browser
if errorlevel 1 (
    echo [ERRO] Falha na autenticacao principal!
    echo Tente novamente ou execute: gcloud auth login
    pause
    exit /b 1
)
echo [OK] Autenticacao principal configurada
echo.

REM ========================================
REM PASSO 3: CONFIGURAR APPLICATION DEFAULT CREDENTIALS
REM ========================================
echo [3/4] Configurando credenciais padrao (Application Default Credentials)...
echo.
echo IMPORTANTE: Isso vai abrir o navegador novamente
echo Voce so precisa fazer isso UMA VEZ
echo.
pause

gcloud auth application-default login --no-launch-browser
if errorlevel 1 (
    echo [ERRO] Falha na configuracao de credenciais padrao!
    echo Tente novamente ou execute: gcloud auth application-default login
    pause
    exit /b 1
)
echo [OK] Credenciais padrao configuradas
echo.

REM ========================================
REM PASSO 4: CONFIGURAR PROJETO
REM ========================================
echo [4/4] Configurando projeto padrao...
gcloud config set project %PROJECT_ID%
if errorlevel 1 (
    echo [ERRO] Falha ao configurar projeto!
    pause
    exit /b 1
)
echo [OK] Projeto configurado: %PROJECT_ID%
echo.

REM ========================================
REM VERIFICAR CONFIGURACAO
REM ========================================
echo ========================================
echo   VERIFICANDO CONFIGURACAO
echo ========================================
echo.

echo Contas autenticadas:
gcloud auth list
echo.

echo Projeto atual:
gcloud config get-value project
echo.

echo Verificando credenciais padrao:
gcloud auth application-default print-access-token >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Credenciais padrao podem nao estar funcionando
    echo Tente executar: gcloud auth application-default login
) else (
    echo [OK] Credenciais padrao funcionando corretamente
)
echo.

echo ========================================
echo   CONFIGURACAO CONCLUIDA!
echo ========================================
echo.
echo [SUCESSO] Autenticacao persistente configurada!
echo.
echo Agora voce pode:
echo - Executar scripts de deploy sem precisar digitar senha
echo - Os comandos gcloud funcionarao automaticamente
echo - A autenticacao vai persistir entre sessoes
echo.
echo IMPORTANTE:
echo - Se mudar de computador, precisa configurar novamente
echo - Se as credenciais expirarem (apos varios meses), execute este script novamente
echo.
echo ========================================
echo.
pause

endlocal

