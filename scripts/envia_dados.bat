@echo off
setlocal

:: --- CONFIGURAÇÕES DO GOOGLE CLOUD ---
set INSTANCE_CONNECTION=monpec-sistema-rural:us-central1:monpec-db
set DB_CLOUD=postgres
set USER_CLOUD=postgres

:: --- CONFIGURAÇÕES DO SEU PC ---
:: ATENÇÃO: Mude 'meu_banco_local' para o nome que aparece no seu pgAdmin
set DB_LOCAL=meu_banco_local
set USER_LOCAL=postgres

echo [1/3] Abrindo conexao segura com Google Cloud...
start /b "" "cloud-sql-proxy.exe" --address 127.0.0.1 --port 5433 %INSTANCE_CONNECTION%

:: Aguarda o tunel estabilizar
timeout /t 5 /nobreak > nul

echo [2/3] Transferindo dados (Local -> Nuvem)...
echo Digite a senha do banco LOCAL e depois a da NUVEM quando solicitado.

:: Comando que extrai do local e injeta na nuvem
pg_dump -h localhost -p 5432 -U %USER_LOCAL% -d %DB_LOCAL% | psql -h 127.0.0.1 -p 5433 -U %USER_CLOUD% -d %DB_CLOUD%

echo [3/3] Processo finalizado!
pause