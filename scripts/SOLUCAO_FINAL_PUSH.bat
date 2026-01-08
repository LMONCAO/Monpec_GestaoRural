@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Solucao Final - Push para GitHub

echo ========================================
echo   SOLUCAO FINAL - PUSH PARA GITHUB
echo ========================================
echo.
echo O GitHub esta bloqueando o push porque o arquivo github-actions-key.json
echo esta em commits antigos no historico do Git.
echo.
echo SOLUCAO RAPIDA (Recomendada):
echo.
echo 1. O arquivo github-actions-key.json NAO deve estar no repositorio
echo 2. O conteudo do arquivo deve estar no secret GCP_SA_KEY do GitHub
echo 3. Vamos permitir temporariamente o push usando os links do GitHub
echo.
echo ⚠️  IMPORTANTE:
echo    - Apos permitir, o arquivo NAO deve ser commitado novamente
echo    - O .gitignore ja esta configurado para ignorar o arquivo
echo    - O arquivo deve ser copiado apenas para os secrets do GitHub
echo.
echo Para permitir o push, acesse os links abaixo no navegador:
echo.
echo Link 1:
echo https://github.com/LMONCAO/Monpec_GestaoRural/security/secret-scanning/unblock-secret/37mjXWAXoIZdfe18NROsOcaJUIh
echo.
echo Link 2:
echo https://github.com/LMONCAO/Monpec_GestaoRural/security/secret-scanning/unblock-secret/37mjXYxgSLZV6sxSWGq9vxRF7I3
echo.
echo Apos permitir nos dois links, pressione qualquer tecla para tentar push novamente...
pause >nul
echo.
echo Tentando push novamente...
git push origin master
if !ERRORLEVEL! EQU 0 (
    echo.
    echo ✅ Push realizado com sucesso!
    echo.
    echo ⚠️  LEMBRE-SE:
    echo    - O arquivo github-actions-key.json NAO deve ser commitado
    echo    - O conteudo deve estar no secret GCP_SA_KEY do GitHub
    echo    - O .gitignore ja esta configurado corretamente
) else (
    echo.
    echo ⚠️  Push ainda bloqueado
    echo    Certifique-se de ter permitido o secret nos dois links acima
)
echo.
pause
