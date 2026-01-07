@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM  ENVIAR_DADOS_SISTEMA.bat
REM
REM  O que este script faz:
REM   1) Exporta dados do Django via manage.py dumpdata (JSON)
REM   2) Inclui media/ e (se existir) db.sqlite3 e tenants/
REM   3) Compacta tudo em um .zip
REM   4) Envia o .zip via:
REM      - Google Cloud Storage (gsutil)  OU
REM      - SCP (scp)                     OU
REM      - Só gera o .zip (se não configurar upload)
REM
REM  Pré-requisitos:
REM   - Windows com PowerShell disponível
REM   - Python/venv do projeto funcionando para rodar manage.py
REM   - Se usar GCS: gcloud + gsutil configurados e autenticados
REM   - Se usar SCP: scp disponível (Git Bash, OpenSSH no Windows, etc.)
REM ============================================================

REM ====== AJUSTE AQUI ======
REM Caminho do projeto (por padrão, pasta onde está este .bat)
set "PROJECT_DIR=%~dp0"

REM Comando do Python (ex: python, py -3, caminho completo)
set "PYTHON_CMD=python"

REM Se você usa venv no Windows, coloque o caminho do activate aqui (opcional).
REM Ex: set "VENV_ACTIVATE=%PROJECT_DIR%\.venv\Scripts\activate.bat"
set "VENV_ACTIVATE="

REM --- Modo 1 (recomendado): Enviar para Google Cloud Storage ---
REM Ex: gs://meu-bucket/backup-monpec
set "GS_DESTINATION="

REM --- Modo 2: Enviar por SCP ---
REM Ex: usuario@IP:/caminho/no/servidor/
set "SCP_DESTINATION="
REM Ex (opcional): caminho do scp.exe. Se vazio, usa "scp" do PATH.
set "SCP_CMD="

REM Nome base do arquivo (sem extensão)
set "ARQUIVO_BASE=monpec_export"
REM =========================

REM Ir para a pasta do projeto
cd /d "%PROJECT_DIR%" || (echo ERRO: nao consegui acessar "%PROJECT_DIR%" & exit /b 1)

REM Ativar venv se configurado
if not "%VENV_ACTIVATE%"=="" (
  if exist "%VENV_ACTIVATE%" (
    call "%VENV_ACTIVATE%"
  ) else (
    echo AVISO: VENV_ACTIVATE configurado, mas nao encontrado: "%VENV_ACTIVATE%"
  )
)

REM Timestamp seguro para nome de pasta/arquivo
for /f "tokens=1-3 delims=/- " %%a in ("%date%") do (
  set "D1=%%a"
  set "D2=%%b"
  set "D3=%%c"
)
for /f "tokens=1-3 delims=:., " %%a in ("%time%") do (
  set "T1=%%a"
  set "T2=%%b"
  set "T3=%%c"
)
set "STAMP=%D3%-%D2%-%D1%_%T1%-%T2%-%T3%"
set "STAMP=%STAMP: =0%"

set "OUT_DIR=%PROJECT_DIR%\_export_%STAMP%"
set "ZIP_PATH=%PROJECT_DIR%\%ARQUIVO_BASE%_%STAMP%.zip"

echo.
echo ===== MONPEC - EXPORTAR E ENVIAR DADOS =====
echo Projeto: "%PROJECT_DIR%"
echo Saida:   "%OUT_DIR%"
echo ZIP:     "%ZIP_PATH%"
echo.

if exist "%OUT_DIR%" (
  echo ERRO: pasta de saida ja existe: "%OUT_DIR%"
  exit /b 1
)
mkdir "%OUT_DIR%" || (echo ERRO: nao consegui criar "%OUT_DIR%" & exit /b 1)

REM 1) Exportar dados do Django
echo [1/4] Exportando dados do Django (dumpdata)...
if not exist "%PROJECT_DIR%\manage.py" (
  echo ERRO: manage.py nao encontrado em "%PROJECT_DIR%"
  exit /b 1
)

REM Excluir tabelas “barulhentas”/derivadas (ajuste se quiser)
set "DUMP_EXCLUDES=--exclude auth.permission --exclude contenttypes --exclude admin.logentry --exclude sessions"

REM Gera JSON único com praticamente tudo
%PYTHON_CMD% "%PROJECT_DIR%\manage.py" dumpdata --natural-foreign --natural-primary --indent 2 %DUMP_EXCLUDES% --output "%OUT_DIR%\dados.json"
if errorlevel 1 (
  echo ERRO: dumpdata falhou. Verifique se o ambiente/DB local esta OK.
  exit /b 1
)

REM 2) Incluir banco SQLite se existir (opcional)
echo [2/4] Coletando arquivos locais (db.sqlite3 / media / tenants)...
if exist "%PROJECT_DIR%\db.sqlite3" (
  copy /y "%PROJECT_DIR%\db.sqlite3" "%OUT_DIR%\db.sqlite3" >nul
)

if exist "%PROJECT_DIR%\media" (
  xcopy "%PROJECT_DIR%\media" "%OUT_DIR%\media\" /E /I /H /Y >nul
)

if exist "%PROJECT_DIR%\tenants" (
  xcopy "%PROJECT_DIR%\tenants" "%OUT_DIR%\tenants\" /E /I /H /Y >nul
)

REM 3) Compactar em ZIP
echo [3/4] Compactando ZIP...
if exist "%ZIP_PATH%" del /f /q "%ZIP_PATH%" >nul 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Compress-Archive -Path '%OUT_DIR%\*' -DestinationPath '%ZIP_PATH%' -Force"
if errorlevel 1 (
  echo ERRO: falha ao criar ZIP.
  exit /b 1
)

echo OK: ZIP gerado: "%ZIP_PATH%"

REM 4) Enviar
echo [4/4] Enviando...

set "UPLOADED=0"

REM 4a) Enviar para GCS se configurado
if not "%GS_DESTINATION%"=="" (
  echo Enviando para GCS: %GS_DESTINATION%
  gsutil -q cp "%ZIP_PATH%" "%GS_DESTINATION%/" && set "UPLOADED=1"
  if not "!UPLOADED!"=="1" (
    echo ERRO: falha ao enviar via gsutil. Verifique gcloud/gsutil e permissao no bucket.
    exit /b 1
  )
)

REM 4b) Enviar por SCP se configurado (e se nao enviou por GCS)
if "!UPLOADED!"=="0" (
  if not "%SCP_DESTINATION%"=="" (
    if "%SCP_CMD%"=="" (
      set "SCP_CMD=scp"
    )
    echo Enviando por SCP: %SCP_DESTINATION%
    "%SCP_CMD%" "%ZIP_PATH%" "%SCP_DESTINATION%"
    if errorlevel 1 (
      echo ERRO: falha ao enviar via scp. Verifique scp/ssh e destino.
      exit /b 1
    )
    set "UPLOADED=1"
  )
)

if "!UPLOADED!"=="1" (
  echo.
  echo ✅ Envio concluido com sucesso.
) else (
  echo.
  echo ⚠️  ZIP gerado, mas nenhum destino de upload foi configurado.
  echo    Configure GS_DESTINATION (gs://...) ou SCP_DESTINATION e rode de novo.
)

echo.
echo Pronto.
exit /b 0

