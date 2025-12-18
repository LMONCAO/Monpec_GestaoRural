@echo off
echo ================================================================================
echo EXECUTAR APOS GERAR NOVA PROJECAO
echo ================================================================================
echo.
echo Este script vai:
echo   1. Verificar se as correcoes ainda existem
echo   2. Recriar correcoes necessarias
echo   3. Garantir que transferencias estejam balanceadas
echo   4. Verificar saldos negativos
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

cd /d "%~dp0"

echo.
echo [1] Verificando vinculacao das correcoes...
python verificar_vinculacao_correcoes_planejamento.py

echo.
echo [2] Garantindo correcoes apos nova projecao...
python garantir_correcoes_apos_nova_projecao.py

echo.
echo [3] Verificando saldos negativos...
python verificar_saldos_negativos_todas_fazendas.py

echo.
echo [4] Verificando balanceamento de transferencias...
python verificar_balanceamento_transferencias.py

echo.
echo ================================================================================
echo CONCLUIDO!
echo ================================================================================
pause




















