@echo off
echo ============================================
echo DEPLOY MONPEC COMPLETO 2026
echo ============================================
echo Inclui: 1300 animais, planejamento, filtros funcionais
echo ============================================

echo 🔧 Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado. Instale Python 3.11+
    pause
    exit /b 1
)

echo 📋 Verificando requirements_producao.txt...
if not exist requirements_producao.txt (
    echo Criando requirements_producao.txt...
    copy requirements.txt requirements_producao.txt >nul 2>&1
    echo openpyxl>=3.1.5 >> requirements_producao.txt
)

echo 🚀 Executando deploy...
python DEPLOY_MONPEC_COMPLETO_2026.py

if %errorlevel% equ 0 (
    echo.
    echo ✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅
    echo.
    echo 📋 Proximos passos:
    echo 1. Acesse a URL fornecida
    echo 2. Login: admin / L6171r12@@
    echo 3. Va para /propriedade/5/pecuaria/ para ver a demo
    echo.
) else (
    echo.
    echo ❌ DEPLOY FALHOU
    echo.
    echo 🔧 Verifique:
    echo - gcloud CLI instalado e configurado
    echo - Docker rodando
    echo - Credenciais do Google Cloud validas
    echo - Projeto 'monpec-sistema-rural' existe
    echo.
)

echo Pressione qualquer tecla para continuar...
pause >nul