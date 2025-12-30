@echo off
echo ========================================
echo SETUP COMPLETO DO SISTEMA MONPEC
echo ========================================
echo.

echo [1/5] Criando pasta scripts...
if not exist "scripts" mkdir scripts
echo OK - Pasta scripts criada
echo.

echo [2/5] Organizando arquivos temporarios...
python -c "import os, shutil, re; from pathlib import Path; base = Path('.'); scripts = base / 'scripts'; scripts.mkdir(exist_ok=True); [shutil.move(str(f), str(scripts / f.name)) for f in base.glob('*.py') if f.is_file() and re.match(r'^(testar_|verificar_|corrigir_|criar_admin|atualizar_|aplicar_|executar_|fix_|redefinir_|diagnosticar_|configurar_|autenticar_|fazer_|listar_|create_superuser)', f.name, re.I) and f.name not in ['manage.py', 'SETUP_COMPLETO.py']]"
echo OK - Arquivos temporarios organizados
echo.

echo [3/5] Verificando arquivo .env...
if not exist ".env" (
    echo Criando .env a partir do template...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo OK - Arquivo .env criado
    ) else (
        echo AVISO - .env.example nao encontrado
    )
) else (
    echo OK - Arquivo .env ja existe
)
echo.

echo [4/5] Verificando ferramentas de qualidade...
if exist "requirements-dev.txt" (
    echo Instalando ferramentas de desenvolvimento...
    pip install -r requirements-dev.txt --quiet
    echo OK - Ferramentas instaladas
) else (
    echo AVISO - requirements-dev.txt nao encontrado
)
echo.

echo [5/5] Verificando configuracoes...
if exist ".pylintrc" echo OK - Pylint configurado
if exist ".flake8" echo OK - Flake8 configurado
if exist "pyproject.toml" echo OK - Black/Isort configurado
echo.

echo ========================================
echo SETUP CONCLUIDO!
echo ========================================
echo.
echo PROXIMOS PASSOS:
echo 1. Edite o arquivo .env com seus valores reais
echo 2. Execute: python manage.py runserver
echo 3. Revise os arquivos em scripts/
echo.
pause






