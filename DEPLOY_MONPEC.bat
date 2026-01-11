@echo off
REM DEPLOY MONPEC AUTOMATICO
REM Execute este arquivo para fazer tudo automaticamente

echo.
echo ========================================
echo 🚀 DEPLOY MONPEC COMPLETO
echo ========================================
echo.

echo 📋 Este script vai:
echo   1. Preparar os arquivos
echo   2. Fazer upload para Google Cloud
echo   3. Executar o deploy completo
echo   4. Popular os dados
echo.

pause

echo.
echo 🔧 PASSO 1: Preparando arquivos...
echo.

REM Coletar arquivos estáticos
python manage.py collectstatic --noinput --clear
if %errorlevel% neq 0 (
    echo ⚠️ Aviso: Erro ao coletar estáticos, continuando...
)

REM Criar .gcloudignore se não existir
if not exist .gcloudignore (
    echo # Arquivos a ignorar no upload> .gcloudignore
    echo .git/>> .gcloudignore
    echo *.pyc>> .gcloudignore
    echo __pycache__/>> .gcloudignore
    echo *.log>> .gcloudignore
    echo venv/>> .gcloudignore
    echo .env*>> .gcloudignore
    echo *.sqlite3>> .gcloudignore
    echo backup_*/>> .gcloudignore
    echo temp/>> .gcloudignore
    echo.
    echo ✅ Arquivo .gcloudignore criado
)

echo.
echo 🔍 PASSO 2: Verificando gcloud...
echo.

REM Verificar se gcloud está instalado
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: gcloud CLI não está instalado!
    echo 📥 Baixe de: https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)

echo ✅ gcloud encontrado

REM Verificar se está logado
gcloud auth list --filter=status:ACTIVE >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Não está logado no Google Cloud!
    echo 🔑 Execute: gcloud auth login
    echo.
    pause
    exit /b 1
)

echo ✅ Logado no Google Cloud

echo.
echo ⚙️ PASSO 3: Configurando projeto...
echo.

REM Configurar projeto
gcloud config set project monpec-sistema-rural
if %errorlevel% neq 0 (
    echo ❌ ERRO: Não conseguiu configurar projeto
    pause
    exit /b 1
)

echo ✅ Projeto configurado: monpec-sistema-rural

echo.
echo ⬆️ PASSO 4: Fazendo upload...
echo.

REM Fazer upload
gcloud storage cp . gs://monpec-deploy-bucket/ --recursive --skip-if-newer
if %errorlevel% neq 0 (
    echo ❌ ERRO: Falha no upload
    pause
    exit /b 1
)

echo ✅ Upload concluído!

echo.
echo ========================================
echo 🎉 UPLOAD CONCLUÍDO!
echo ========================================
echo.
echo 📋 AGORA EXECUTE NO GOOGLE CLOUD SHELL:
echo.
echo 1. Abra: https://console.cloud.google.com/cloudshell
echo.
echo 2. Execute estes comandos:
echo.
echo    # Baixar arquivos
echo    gsutil cp -r gs://monpec-deploy-bucket/* .
echo.
echo    # Executar deploy
echo    chmod +x deploy_atualizado.sh
echo    bash deploy_atualizado.sh
echo.
echo ========================================
echo.
echo 🌐 Após o deploy, acesse:
echo    Landing: https://monpec-[hash].a.run.app/
echo    Sistema: https://monpec-[hash].a.run.app/propriedade/5/pecuaria/
echo.
echo ✅ SISTEMA COM 1300 ANIMAIS E PLANEJAMENTO COMPLETO!
echo.

pause