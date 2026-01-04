@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Remover Secret do Historico do Git

echo ========================================
echo   REMOVENDO SECRET DO HISTORICO DO GIT
echo ========================================
echo.
echo ⚠️  ATENCAO: Este script vai reescrever o historico do Git
echo    Isso e necessario para remover o arquivo secreto dos commits antigos
echo.
echo O arquivo github-actions-key.json esta em commits antigos e precisa
echo ser removido do historico completo.
echo.
echo Opcoes:
echo 1. Remover do historico (recomendado)
echo 2. Permitir o secret no GitHub (nao recomendado)
echo.
set /p OPCAO="Escolha uma opcao (1 ou 2): "

if "!OPCAO!"=="1" (
    echo.
    echo Removendo github-actions-key.json do historico do Git...
    echo Isso pode levar alguns minutos...
    echo.
    
    :: Usar git filter-branch para remover o arquivo do historico
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch github-actions-key.json" --prune-empty --tag-name-filter cat -- --all
    
    if !ERRORLEVEL! EQU 0 (
        echo.
        echo ✅ Arquivo removido do historico!
        echo.
        echo Fazendo push forçado (necessario apos reescrever historico)...
        echo ⚠️  ATENCAO: Isso vai sobrescrever o historico no GitHub
        echo.
        set /p CONFIRMA="Confirma push forçado? (S/N): "
        if /i "!CONFIRMA!"=="S" (
            git push origin --force --all
            if !ERRORLEVEL! EQU 0 (
                echo ✅ Push realizado com sucesso!
            ) else (
                echo ⚠️  Erro no push forçado
            )
        ) else (
            echo Push cancelado. Execute manualmente: git push origin --force --all
        )
    ) else (
        echo ❌ Erro ao remover do historico
    )
) else if "!OPCAO!"=="2" (
    echo.
    echo Para permitir o secret no GitHub, acesse os links:
    echo https://github.com/LMONCAO/Monpec_GestaoRural/security/secret-scanning/unblock-secret/37mjXWAXoIZdfe18NROsOcaJUIh
    echo https://github.com/LMONCAO/Monpec_GestaoRural/security/secret-scanning/unblock-secret/37mjXYxgSLZV6sxSWGq9vxRF7I3
    echo.
    echo ⚠️  NAO RECOMENDADO: Permitir secrets no repositorio e um risco de seguranca
) else (
    echo Opcao invalida
)

echo.
pause
