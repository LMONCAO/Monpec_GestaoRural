@echo off
REM Arquivo de configuração do banco oficial Monpec
REM Este arquivo configura automaticamente as variáveis de ambiente

echo [CONFIG] Configurando banco oficial monpec_oficial...

REM Configurações do banco PostgreSQL oficial
set DEBUG=False
set SECRET_KEY=django-insecure-monpec-oficial-2025-secreta-key-123456789
set DB_NAME=monpec_oficial
set DB_USER=postgres
set DB_PASSWORD=L6171r12@@jjms
set DB_HOST=localhost
set DB_PORT=5432

echo [CONFIG] Banco: %DB_NAME%
echo [CONFIG] Usuario: %DB_USER%
echo [CONFIG] Host: %DB_HOST%:%DB_PORT%
echo [CONFIG] Status: PRODUÇÃO (DEBUG=False)


