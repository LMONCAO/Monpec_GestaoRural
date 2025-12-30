@echo off
chcp 65001 >nul
echo ========================================================================
echo BACKUP COMPLETO DO SISTEMA - MonPEC Gestão Rural
echo ========================================================================
echo.
echo Este script faz backup completo do sistema:
echo   - Banco de dados principal
echo   - Bancos de dados dos tenants
echo   - Arquivos media (uploads, certificados, etc.)
echo   - Arquivos static (opcional)
echo.
pause

echo.
echo [1/2] Executando backup completo...
cd /d "%~dp0\..\.."
python manage.py backup_completo --compress

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo BACKUP CONCLUÍDO COM SUCESSO!
    echo ========================================================================
    echo.
    echo Os backups foram salvos no diretório: backups\
    echo.
) else (
    echo.
    echo ========================================================================
    echo ERRO AO EXECUTAR BACKUP!
    echo ========================================================================
    echo.
    echo Verifique os logs acima para mais detalhes.
    echo.
)

pause






