@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Exportando dados do banco local...
python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Exportação concluída com sucesso!
    echo Arquivo criado: dados_backup.json
    echo.
    echo Próximos passos:
    echo 1. Faça upload do arquivo dados_backup.json para o Google Cloud Shell
    echo 2. No Cloud Shell, execute: python3 manage.py loaddata dados_backup.json
) else (
    echo.
    echo ❌ Erro na exportação. Verifique se:
    echo - O banco de dados local está acessível
    echo - O Django está instalado corretamente
    echo - Você está no diretório correto do projeto
)
pause
