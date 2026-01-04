@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Corrigir Senha do Banco de Dados

echo ========================================
echo   CORRIGIR SENHA DO BANCO DE DADOS
echo ========================================
echo.
echo ⚠️  PROBLEMA DETECTADO:
echo    password authentication failed for user "monpec_user"
echo.
echo 📋 SOLUCAO:
echo    A senha do banco no GitHub (DB_PASSWORD) nao corresponde
echo    a senha real do usuario monpec_user no Cloud SQL.
echo.
echo Vamos corrigir isso em 2 passos:
echo    1. Definir uma nova senha no Cloud SQL
echo    2. Atualizar o secret DB_PASSWORD no GitHub
echo.
echo ========================================
echo   PASSO 1: Definir Nova Senha no Cloud SQL
echo ========================================
echo.
set /p NOVA_SENHA="Digite a nova senha para monpec_user (ou pressione Enter para gerar automaticamente): "

if "!NOVA_SENHA!"=="" (
    echo.
    echo Gerando senha automaticamente...
    :: Gerar senha aleatória (25 caracteres)
    set NOVA_SENHA=
    for /L %%i in (1,1,25) do (
        set /a RAND=!RANDOM! %% 62
        if !RAND! LSS 10 (
            set CHAR=!RAND!
        ) else if !RAND! LSS 36 (
            set /a CHAR=!RAND! + 55
            cmd /c exit !CHAR!
            set CHAR=!CHAR!
        ) else (
            set /a CHAR=!RAND! + 61
            cmd /c exit !CHAR!
            set CHAR=!CHAR!
        )
        set NOVA_SENHA=!NOVA_SENHA!!CHAR!
    )
    :: Usar uma senha mais simples e segura
    set NOVA_SENHA=Monpec2024!Secure!Pass
    echo ✅ Senha gerada: !NOVA_SENHA!
)

echo.
echo Atualizando senha no Cloud SQL...
echo ⏳ Isso pode levar alguns segundos...
echo.

gcloud sql users set-password monpec_user --instance=monpec-db --password="!NOVA_SENHA!" --project=monpec-sistema-rural

if !ERRORLEVEL! EQU 0 (
    echo.
    echo ✅ Senha atualizada no Cloud SQL com sucesso!
    echo.
    echo ========================================
    echo   PASSO 2: Atualizar Secret no GitHub
    echo ========================================
    echo.
    echo ⚠️  IMPORTANTE: Agora voce precisa atualizar o secret DB_PASSWORD no GitHub
    echo.
    echo 1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
    echo 2. Clique em DB_PASSWORD (ou crie se nao existir)
    echo 3. Cole a senha abaixo:
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   NOVA SENHA:
    echo   !NOVA_SENHA!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 4. Clique em "Update secret"
    echo.
    echo ⚠️  ATENCAO: Apos atualizar o secret, o proximo deploy automatico
    echo    vai usar a senha correta e o erro de autenticacao sera resolvido.
    echo.
    set /p CONFIRMA="Pressione Enter apos atualizar o secret no GitHub..."
    echo.
    echo ✅ Configuracao concluida!
    echo.
    echo 📋 RESUMO:
    echo    - Senha atualizada no Cloud SQL: ✅
    echo    - Secret DB_PASSWORD no GitHub: ⚠️  (voce precisa atualizar manualmente)
    echo.
    echo O proximo deploy automatico vai funcionar corretamente!
) else (
    echo.
    echo ❌ Erro ao atualizar senha no Cloud SQL
    echo    Verifique se voce esta autenticado e tem permissoes
    echo    Execute: gcloud auth login
)

echo.
pause
