@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title TESTE - RESOLVER TUDO DEPLOY

echo ========================================
echo   TESTE - RESOLVER TUDO DEPLOY
echo ========================================
echo.
echo Este e um teste para verificar o que esta acontecendo.
echo.
echo Pressione qualquer tecla para comecar...
pause
echo.
echo OK, voce pressionou a tecla. Continuando...
echo.
timeout /t 2
echo.
echo Teste 1: Verificando se estamos aqui...
echo.
echo Pressione qualquer tecla para continuar o teste...
pause
echo.
echo Teste 2: Ainda estamos aqui!
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.
echo Teste 3: Continuando...
echo.
echo Vamos verificar autenticacao...
gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.
echo Teste 4: Verificando projeto...
gcloud config get-value project 2>&1
echo.
echo Pressione qualquer tecla para continuar...
pause
echo.
echo ========================================
echo   TESTE CONCLUIDO
echo ========================================
echo.
echo Se voce chegou ate aqui, o script esta funcionando!
echo.
echo Pressione qualquer tecla para FECHAR...
pause
echo.
echo Fechando em 3 segundos...
timeout /t 3
exit
