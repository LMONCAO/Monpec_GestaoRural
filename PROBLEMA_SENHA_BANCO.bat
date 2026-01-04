@echo off
chcp 65001 >nul
echo ========================================
echo   PROBLEMA: SENHA DO BANCO INCORRETA
echo ========================================
echo.

echo ??? ERRO ENCONTRADO:
echo    password authentication failed for user "monpec_user"
echo.

echo ???? CAUSA:
echo    A senha do banco que usei no deploy pode estar diferente
echo    da senha real configurada no Cloud SQL.
echo.

echo ??? SOLU????O:
echo    1. Verifique a senha correta nos GitHub Secrets:
echo       https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
echo.
echo    2. Ou aguarde o GitHub Actions fazer o deploy
echo       (ele usa a senha correta dos secrets)
echo.

echo ???? A senha que tentei usar foi: Django2025@
echo    (do arquivo .env_gcp)
echo    Mas pode ser diferente no Cloud SQL real.
echo.

pause