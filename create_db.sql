SELECT 'CREATE DATABASE monpec_db_local'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'monpec_db_local')\gexec





