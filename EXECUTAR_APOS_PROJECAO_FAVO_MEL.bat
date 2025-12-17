@echo off
REM ============================================================================
REM SCRIPT PARA APLICAR CONFIGURACAO PADRAO FAVO DE MEL APOS NOVA PROJECAO
REM ============================================================================
REM
REM Este script DEVE ser executado apos cada nova geracao de projecao
REM para garantir que as transferencias sejam criadas corretamente.
REM
REM CONFIGURACAO PADRAO:
REM - Recebe garrotes da Canta Galo
REM - Transfere 480 cabecas para Girassol a cada 90 dias
REM - Sempre respeita saldo disponivel
REM
REM ============================================================================

echo.
echo ============================================================================
echo APLICAR CONFIGURACAO PADRAO FAVO DE MEL
echo ============================================================================
echo.
echo Este script aplica a configuracao padrao apos nova projecao:
echo   - Recebe garrotes da Canta Galo
echo   - Transfere 480 cabecas para Girassol a cada 90 dias
echo   - Sempre respeita saldo disponivel
echo.
echo ============================================================================
echo.

cd /d "%~dp0"

REM Executar script Python
python garantir_configuracao_favo_mel_apos_projecao.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao executar script!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Limpando cache do Django...
echo ============================================================================
echo.

python limpar_cache_completo_django.py

echo.
echo ============================================================================
echo [SUCESSO] Configuracao padrao aplicada!
echo ============================================================================
echo.
echo IMPORTANTE:
echo   1. Recarregue a pagina no navegador com Ctrl+Shift+R
echo   2. Se ainda nao funcionar, feche e abra o navegador novamente
echo.
pause











