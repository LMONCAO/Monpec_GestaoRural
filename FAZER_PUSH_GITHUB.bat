@echo off
REM Script para fazer push dos arquivos novos para o GitHub
REM Execute este script quando quiser fazer commit e push das alteracoes

echo ==========================================
echo FAZER PUSH PARA GITHUB
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/4] Adicionando arquivos novos...
git add .github/workflows/deploy-google-cloud.yml
git add GUIA_SINCRONIZAR_GITHUB_GCLOUD.md
git add RESUMO_SINCRONIZACAO_GITHUB.md
git add executar_migracoes_e_criar_admin.sh
git add executar_migracoes_e_criar_admin_cloud_run.sh
git add EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat
git add FAZER_PUSH_GITHUB.bat

if errorlevel 1 (
    echo [ERRO] Falha ao adicionar arquivos
    pause
    exit /b 1
)

echo [OK] Arquivos adicionados
echo.

echo [2/4] Verificando status...
git status --short

echo.
echo [3/4] Fazendo commit...
git commit -m "Adicionar integracao GitHub Actions com Google Cloud e scripts para migracoes/admin"

if errorlevel 1 (
    echo [AVISO] Nenhuma alteracao para commitar ou commit falhou
    echo Verifique o status com: git status
    pause
    exit /b 1
)

echo [OK] Commit realizado
echo.

echo [4/4] Fazendo push para GitHub...
git push origin master

if errorlevel 1 (
    echo [ERRO] Falha ao fazer push
    echo Verifique se o branch existe e se voce tem permissoes
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCESSO!
echo ==========================================
echo.
echo Arquivos enviados para o GitHub com sucesso!
echo.
pause

