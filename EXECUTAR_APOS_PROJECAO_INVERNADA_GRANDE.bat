@echo off
REM ============================================================================
REM Script para executar apos gerar nova projecao da Invernada Grande
REM ============================================================================
REM Este script garante que a configuracao padrao seja aplicada automaticamente
REM ============================================================================

echo ============================================================================
echo EXECUTAR CONFIGURACAO PADRAO INVERNADA GRANDE
echo ============================================================================
echo.
echo Este script aplica a configuracao padrao apos nova projecao:
echo - Sem inventario inicial
echo - Recebe 512 vacas descarte da Canta Galo em 2022
echo - Vende 80 cabecas mensais ate zerar
echo - Saldo zerado em 2023, 2024, 2025
echo.
echo ============================================================================
echo.

cd /d "%~dp0"

echo [INFO] Executando script de configuracao padrao...
python garantir_configuracao_invernada_grande_apos_projecao.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================================
    echo [SUCESSO] Configuracao padrao aplicada!
    echo ============================================================================
    echo.
    echo [IMPORTANTE] Recarregue a pagina no navegador com Ctrl+Shift+R
    echo.
) else (
    echo.
    echo ============================================================================
    echo [ERRO] Falha ao aplicar configuracao padrao
    echo ============================================================================
    echo.
)

pause




















