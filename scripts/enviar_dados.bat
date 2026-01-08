@echo off
setlocal

:: --- CONFIGURAÇÕES DO GOOGLE CLOUD ---
set INSTANCE_CONNECTION=monpec-sistema-rural:us-central1:monpec-db
set DB_CLOUD=monpec_db
set USER_CLOUD=postgres

:: --- CONFIGURAÇÕES DO SEU PC ---
set DB_LOCAL=monpec_db_local
set USER_LOCAL=postgres

:: --- CONFIGURAÇÃO DE SENHA ÚNICA ---
set PGPASSWORD=L6171r12@@jjms

echo [1/3] Abrindo conexao segura com Google Cloud...
:: Mata qualquer proxy travado antes de iniciar
taskkill /IM cloud-sql-proxy.exe /F >nul 2>&1
start /b "" "cloud-sql-proxy.exe" --address 127.0.0.1 --port 5433 %INSTANCE_CONNECTION%

:: Aguarda 10 segundos para o tunel estabilizar bem
timeout /t 10 /nobreak > nul

echo [2/3] Transferindo ESTRUTURA E DADOS para a nuvem...
echo (Isso pode demorar alguns minutos dependendo do volume de dados...)

:: O comando abaixo limpa o destino e ignora erros de 'owner' (dono)
pg_dump -h localhost -p 5432 -U %USER_LOCAL% -d %DB_LOCAL% --clean --if-exists --no-owner --no-privileges | psql -h 127.0.0.1 -p 5433 -U %USER_CLOUD% -d %DB_CLOUD%

echo [3/3] Sincronizacao de dados e tabelas concluida!
:: Limpa a senha da memoria por seguranca
set PGPASSWORD=
pause