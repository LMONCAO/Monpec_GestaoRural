@echo off
chcp 65001 >nul
echo ==========================================
echo INSTALADOR MONPEC GESTAO RURAL
echo ==========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Criar ambiente virtual (opcional, mas recomendado)
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [AVISO] Nao foi possivel criar ambiente virtual. Continuando sem ele...
    ) else (
        echo [OK] Ambiente virtual criado
        echo [INFO] Ativando ambiente virtual...
        call venv\Scripts\activate.bat
    )
) else (
    echo [INFO] Ambiente virtual ja existe. Ativando...
    call venv\Scripts\activate.bat
)
echo.

REM Atualizar pip
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependências
echo [INFO] Instalando dependencias do projeto...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Verificar se arquivo .env existe
if not exist ".env" (
    echo [INFO] Arquivo .env nao encontrado. Criando arquivo de exemplo...
    (
        echo # Configuracoes do Sistema
        echo DEBUG=True
        echo SECRET_KEY=django-insecure-change-in-production
        echo ALLOWED_HOSTS=127.0.0.1,localhost
        echo.
        echo # Banco de Dados - SQLite ^(padrao para desenvolvimento^)
        echo DB_ENGINE=sqlite3
        echo.
        echo # Para usar PostgreSQL, descomente e configure:
        echo # DB_ENGINE=postgresql
        echo # DB_NAME=sistema_rural
        echo # DB_USER=django_user
        echo # DB_PASSWORD=sua_senha
        echo # DB_HOST=localhost
        echo # DB_PORT=5432
    ) > .env
    echo [OK] Arquivo .env criado. Configure conforme necessario.
) else (
    echo [OK] Arquivo .env ja existe
)
echo.

REM Verificar se banco de dados existe
if exist "db.sqlite3" (
    echo [INFO] Banco de dados SQLite encontrado
) else (
    echo [INFO] Banco de dados nao encontrado. Criando...
)

REM Executar migrações
echo [INFO] Executando migracoes do banco de dados...
python manage.py migrate
if errorlevel 1 (
    echo [ERRO] Falha ao executar migracoes!
    pause
    exit /b 1
)
echo [OK] Migracoes executadas
echo.

REM Coletar arquivos estáticos
echo [INFO] Coletando arquivos estaticos...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [AVISO] Nao foi possivel coletar arquivos estaticos. Continuando...
)
echo.

REM Criar superusuário (se não existir)
echo [INFO] Verificando se existe superusuario...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superusuario existe' if User.objects.filter(is_superuser=True).exists() else 'Nenhum superusuario encontrado')" 2>nul
echo.

echo ==========================================
echo INSTALACAO CONCLUIDA!
echo ==========================================
echo.
echo Para iniciar o servidor, execute:
echo   INICIAR.bat
echo.
echo Ou manualmente:
echo   python manage.py runserver
echo.
pause

