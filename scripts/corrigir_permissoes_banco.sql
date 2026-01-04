-- Script para corrigir permissões do usuário monpec_user no PostgreSQL
-- Execute este script como usuário postgres (superuser)

-- Conectar ao banco monpec_db
\c monpec_db

-- Garantir que o usuário monpec_user tem permissões no schema public
GRANT USAGE ON SCHEMA public TO monpec_user;
GRANT CREATE ON SCHEMA public TO monpec_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO monpec_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO monpec_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO monpec_user;

-- Conceder permissões em tabelas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO monpec_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO monpec_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO monpec_user;

-- Tornar o usuário owner do schema (opcional, mas garante todas as permissões)
ALTER SCHEMA public OWNER TO monpec_user;

-- Verificar permissões (para debug)
\du monpec_user

-- Mostrar tabelas para verificar se as permissões foram aplicadas
\dt



