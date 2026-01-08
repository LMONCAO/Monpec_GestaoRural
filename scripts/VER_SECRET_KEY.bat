@echo off
chcp 65001 >nul
echo ========================================
echo   SECRET_KEY - ONDE EST?? E COMO VER
echo ========================================
echo.
echo ???? ONDE EST?? SUA SECRET_KEY:
echo    ??? GitHub Secrets (Actions)
echo       https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
echo.
echo    L?? voc?? vai ver o secret "SECRET_KEY" configurado
echo    (mas n??o consegue ver o valor por seguran??a)
echo.
echo ???? COMO VER O VALOR:
echo    1. Acesse o link acima
echo    2. Clique em "Edit" no secret SECRET_KEY
echo    3. Voc?? ver?? o valor (mas n??o pode copiar diretamente)
echo    4. Ou use o m??todo abaixo para gerar uma nova
echo.
echo ???? GERAR NOVA SECRET_KEY:
echo    Execute: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo.
echo ???? IMPORTANTE:
echo    - A SECRET_KEY atual est?? nos GitHub Secrets
echo    - O GitHub Actions usa ela automaticamente
echo    - N??o precisa fazer nada manualmente
echo    - Aguarde o deploy do GitHub Actions completar
echo.
pause