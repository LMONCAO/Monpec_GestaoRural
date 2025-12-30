# 🔧 Solução Rápida para Problema de Login

## ✅ O que já foi feito:

1. ✅ Cloud Run configurado
2. ✅ Cloud SQL conectado
3. ✅ Variáveis de ambiente configuradas (incluindo DB_PASSWORD)
4. ✅ Migrações executadas com sucesso
5. ⚠️ Usuário admin ainda precisa ser criado

## 🚀 Solução: Criar Admin via SQL Direto

Como o job está tendo problemas, vamos criar o usuário diretamente no banco:

### Opção 1: Via Cloud SQL Console

1. Acesse: https://console.cloud.google.com/sql/instances/monpec-db/overview
2. Clique em "Abrir Cloud Shell"
3. Execute:

```sql
-- Conectar ao banco
\c monpec_db

-- Criar usuário admin (senha será hash do Django)
-- Primeiro, vamos inserir diretamente na tabela auth_user
INSERT INTO auth_user (username, email, password, is_staff, is_superuser, is_active, date_joined)
VALUES (
    'admin',
    'admin@monpec.com.br',
    'pbkdf2_sha256$600000$...', -- Hash da senha L6171r12@@
    true,
    true,
    true,
    NOW()
) ON CONFLICT (username) DO UPDATE SET
    password = EXCLUDED.password,
    is_staff = true,
    is_superuser = true,
    is_active = true;
```

### Opção 2: Via Script Python Local (Recomendado)

Execute localmente conectando ao Cloud SQL:

```bash
# Instalar Cloud SQL Proxy
# https://cloud.google.com/sql/docs/postgres/connect-instance-cloud-sql-proxy

# Conectar ao banco
cloud_sql_proxy -instances=monpec-sistema-rural:us-central1:monpec-db=tcp:5432

# Em outro terminal, execute:
python criar_admin.py
```

### Opção 3: Via Django Admin no Cloud Run (Mais Simples)

Acesse o site e use o Django admin:

1. Acesse: https://monpec.com.br/admin/
2. Se não tiver usuário, crie via terminal local conectando ao Cloud SQL

## 🔍 Verificar se está funcionando:

1. Acesse: https://monpec.com.br/login/
2. Tente fazer login com:
   - Username: `admin`
   - Senha: `L6171r12@@`

Se ainda não funcionar, o usuário precisa ser criado no banco de dados.













































