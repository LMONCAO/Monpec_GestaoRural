@echo off
chcp 65001 >nul
echo ============================================================
echo CORRECAO DE DADOS 2022 - VENDAS E TRANSFERENCIAS
echo ============================================================
echo.
echo Este script ira executar:
echo 1. Correcao de vendas - Invernada Grande (512 vacas descarte)
echo 2. Correcao de transferencias - Favo de Mel para Girassol (1180 garrotes)
echo.
echo IMPORTANTE: Certifique-se de que o servidor Django esta PARADO
echo antes de executar este script!
echo.
pause

echo.
echo [1/2] Executando correcao de vendas - Invernada Grande...
echo ============================================================
python corrigir_vendas_invernada_grande_2022.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao executar correcao de vendas
    echo Verifique o erro acima e tente novamente
    pause
    exit /b 1
)

echo.
echo [2/2] Executando correcao de transferencias - Favo de Mel para Girassol...
echo ============================================================
python corrigir_transferencias_favo_mel_girassol_2022.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao executar correcao de transferencias
    echo Verifique o erro acima e tente novamente
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [OK] Todas as correcoes foram executadas com sucesso!
echo ============================================================
echo.
echo Resumo:
echo - Vendas mensais de 80 cabecas criadas na Invernada Grande
echo - Transferencias a cada 3 meses de 350 cabecas criadas (Favo de Mel -^> Girassol)
echo.
pause
























