@echo off
echo ====================================
echo CORRIGINDO E INICIANDO SISTEMA MONPEC
echo ====================================
echo.

REM Matar processos Python anteriores
taskkill /f /im python.exe >nul 2>&1

echo Aguardando 2 segundos...
timeout /t 2 >nul

echo Verificando sintaxe do arquivo...
python -c "import ast; ast.parse(open('gestao_rural/views_exportacao.py', encoding='utf-8').read()); print('Sintaxe OK!')"

if %errorlevel% neq 0 (
    echo ERRO: Problema de sintaxe detectado!
    echo Por favor, execute: python fix_indentation.py
    pause
    exit /b 1
)

echo.
echo Aplicando migracoes do banco de dados...
python manage.py migrate

echo.
echo ====================================
echo INICIANDO SERVIDOR DJANGO NA PORTA 8000
echo ====================================
echo.
echo Acesse: http://127.0.0.1:8000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python manage.py runserver 8000

pause

