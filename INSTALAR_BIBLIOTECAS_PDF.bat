@echo off
chcp 65001 > nul
setlocal

echo ======================================================================
echo INSTALANDO BIBLIOTECAS PARA PROCESSAMENTO DE PDFs
echo ======================================================================
echo.
echo As bibliotecas PyPDF2 e pdfplumber sao necessarias para:
echo - Importar arquivos SCR do Banco Central
echo - Processar PDFs de dividas bancarias
echo - Extrair dados de documentos financeiros
echo.
echo [PASSO 1/2] Instalando PyPDF2...
python -m pip install PyPDF2
if %errorlevel% neq 0 (
    echo Erro ao instalar PyPDF2.
    goto :eof
)

echo.
echo [PASSO 2/2] Instalando pdfplumber...
python -m pip install pdfplumber
if %errorlevel% neq 0 (
    echo Erro ao instalar pdfplumber.
    goto :eof
)

echo.
echo ======================================================================
echo INSTALACAO CONCLUIDA COM SUCESSO!
echo ======================================================================
echo.
echo As bibliotecas foram instaladas. Agora voce pode:
echo - Importar arquivos SCR do Banco Central
echo - Processar PDFs de dividas bancarias
echo - Extrair dados de documentos financeiros
echo.
pause
endlocal














