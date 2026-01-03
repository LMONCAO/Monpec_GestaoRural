# 🔐 Como Criar Admin no Cloud Shell

## Problema
O script está tentando conectar ao banco local (127.0.0.1) mas precisa conectar ao Cloud SQL.

## Solução 1: Usar Cloud SQL Proxy (Recomendado)

### Passo 1: Instalar Cloud SQL Proxy no Cloud Shell
```bash
# Cloud SQL Proxy já está disponível no Cloud Shell, mas vamos verificar
which cloud_sql_proxy
```

### Passo 2: Obter informações do Cloud SQL
```bash
# Listar instâncias
gcloud sql instances list

# Obter connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"

# Obter informações de conexão
gcloud sql instances describe monpec-db
```

### Passo 3: Conectar via Cloud SQL Proxy (em um terminal separado)
```bash
# Em uma nova aba do Cloud Shell
gcloud sql instances describe monpec-db --format="value(connectionName)"
# Isso retornará algo como: projeto:regiao:instancia

# Iniciar proxy
cloud_sql_proxy -instances=PROJETO:REGIAO:INSTANCIA=tcp:5432 &
```

### Passo 4: Configurar variáveis de ambiente e executar script
```bash
# Configurar variáveis
export DB_NAME=monpec_db
export DB_USER=monpec_user
export DB_PASSWORD=SUA_SENHA_AQUI
export DB_HOST=127.0.0.1
export DB_PORT=5432

# Executar script
python criar_admin_producao.py
```

## Solução 2: Configurar Variáveis de Ambiente Diretamente

### Opção A: Via gcloud run jobs (Mais Simples)

```bash
# Criar job temporário
gcloud run jobs create create-admin \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --command python \
  --args criar_admin_producao.py \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
  --set-env-vars DB_NAME=monpec_db \
  --set-env-vars DB_USER=monpec_user \
  --set-env-vars DB_PASSWORD=SUA_SENHA_DO_BANCO \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db \
  --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
  --max-retries 1 \
  --task-timeout 600

# Executar o job
gcloud run jobs execute create-admin --region us-central1 --wait
```

### Opção B: Conectar diretamente ao IP do Cloud SQL

```bash
# Obter IP público do Cloud SQL
INSTANCE_IP=$(gcloud sql instances describe monpec-db --format="value(ipAddresses[0].ipAddress)")
echo "IP do Cloud SQL: $INSTANCE_IP"

# Configurar variáveis
export DB_HOST=$INSTANCE_IP
export DB_NAME=monpec_db
export DB_USER=monpec_user
export DB_PASSWORD=SUA_SENHA_AQUI
export DB_PORT=5432

# Executar script
python criar_admin_producao.py
```

**⚠️ IMPORTANTE:** Para conectar diretamente ao IP, você precisa:
1. Autorizar o IP do Cloud Shell na lista de IPs autorizados do Cloud SQL
2. Ou usar o Cloud SQL Proxy (mais seguro)

## Solução 3: Usar o Script Atualizado

Use o arquivo `criar_admin_cloud_sql.py` que tenta obter as configurações automaticamente:

```bash
# Configurar apenas a senha
export DB_PASSWORD=SUA_SENHA_AQUI

# Executar
python criar_admin_cloud_sql.py
```

## Verificação Final

Após executar qualquer método, teste o login:
- URL: https://monpec-29862706245.us-central1.run.app/login/
- Usuário: admin
- Senha: L6171r12@@








