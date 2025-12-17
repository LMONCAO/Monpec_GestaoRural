@echo off
chcp 65001 >nul
echo ============================================================
echo PARAR SERVIDOR E EXECUTAR CORRECOES 2022
echo ============================================================
echo.

echo Verificando processos Python em execucao...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo [AVISO] Processos Python encontrados!
    echo.
    echo Processos Python ativos:
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
    echo.
    echo Deseja encerrar todos os processos Python? (S/N)
    set /p resposta="> "
    if /i "%resposta%"=="S" (
        echo.
        echo Encerrando processos Python...
        taskkill /F /IM python.exe /T 2>NUL
        timeout /t 2 /nobreak >NUL
        echo [OK] Processos Python encerrados
    ) else (
        echo.
        echo [AVISO] Processos Python ainda estao rodando
        echo Por favor, feche o servidor Django manualmente e execute novamente
        pause
        exit /b 1
    )
) else (
    echo [OK] Nenhum processo Python encontrado
)

echo.
echo Aguardando 3 segundos para garantir que o banco esta livre...
timeout /t 3 /nobreak >NUL

echo.
echo ============================================================
echo Executando correcoes...
echo ============================================================
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
echo Agora voce pode reiniciar o servidor Django
echo.
pause











