@echo off
chcp 65001 >nul
echo ========================================================================
echo CRIAR BACKUP E SISTEMA MARCELO SANGUINO
echo ========================================================================
echo.
echo Este script vai:
echo 1. Criar backup completo do sistema atual
echo 2. Criar estrutura de pastas para o novo sistema
echo 3. Preparar sistema multi-propriedade
echo.
pause

echo.
echo [1/3] Criando backup do sistema atual...
set BACKUP_DIR=..\Monpec_GestaoRural_BACKUP_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo Copiando arquivos...
xcopy /E /I /H /Y "gestao_rural" "%BACKUP_DIR%\gestao_rural"
xcopy /E /I /H /Y "templates" "%BACKUP_DIR%\templates"
xcopy /E /I /H /Y "static" "%BACKUP_DIR%\static"
xcopy /E /I /H /Y "sistema_rural" "%BACKUP_DIR%\sistema_rural"
copy /Y "db.sqlite3" "%BACKUP_DIR%\db.sqlite3"
copy /Y "manage.py" "%BACKUP_DIR%\manage.py"
copy /Y "requirements.txt" "%BACKUP_DIR%\requirements.txt"

echo.
echo [OK] Backup criado em: %BACKUP_DIR%

echo.
echo [2/3] Criando estrutura de pastas para novo sistema...
set NOVO_SISTEMA=..\Monpec_Marcelo_Sanguino

if not exist "%NOVO_SISTEMA%" mkdir "%NOVO_SISTEMA%"
if not exist "%NOVO_SISTEMA%\gestao_rural" mkdir "%NOVO_SISTEMA%\gestao_rural"
if not exist "%NOVO_SISTEMA%\templates" mkdir "%NOVO_SISTEMA%\templates"
if not exist "%NOVO_SISTEMA%\static" mkdir "%NOVO_SISTEMA%\static"
if not exist "%NOVO_SISTEMA%\sistema_rural" mkdir "%NOVO_SISTEMA%\sistema_rural"
if not exist "%NOVO_SISTEMA%\relatorios" mkdir "%NOVO_SISTEMA%\relatorios"
if not exist "%NOVO_SISTEMA%\relatorios\rebanho" mkdir "%NOVO_SISTEMA%\relatorios\rebanho"
if not exist "%NOVO_SISTEMA%\relatorios\bens" mkdir "%NOVO_SISTEMA%\relatorios\bens"
if not exist "%NOVO_SISTEMA%\relatorios\financeiro" mkdir "%NOVO_SISTEMA%\relatorios\financeiro"
if not exist "%NOVO_SISTEMA%\relatorios\contabil" mkdir "%NOVO_SISTEMA%\relatorios\contabil"

echo.
echo [OK] Estrutura de pastas criada em: %NOVO_SISTEMA%

echo.
echo [3/3] Copiando arquivos base do sistema...
xcopy /E /I /H /Y "gestao_rural" "%NOVO_SISTEMA%\gestao_rural"
xcopy /E /I /H /Y "templates" "%NOVO_SISTEMA%\templates"
xcopy /E /I /H /Y "static" "%NOVO_SISTEMA%\static"
xcopy /E /I /H /Y "sistema_rural" "%NOVO_SISTEMA%\sistema_rural"
copy /Y "manage.py" "%NOVO_SISTEMA%\manage.py"
copy /Y "requirements.txt" "%NOVO_SISTEMA%\requirements.txt"

echo.
echo ========================================================================
echo CONCLUIDO!
echo ========================================================================
echo.
echo Backup criado em: %BACKUP_DIR%
echo Novo sistema criado em: %NOVO_SISTEMA%
echo.
echo Proximo passo: Configurar o novo sistema para multi-propriedade
echo.
pause


