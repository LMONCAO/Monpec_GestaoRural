# 🔧 Corrigir Senha do Banco de Dados

## ❌ Problema Identificado

O erro `password authentication failed for user "monpec_user"` indica que a senha do banco de dados PostgreSQL no Cloud SQL não corresponde à senha configurada no Cloud Run.

## 🔍 Solução: Verificar e Corrigir a Senha

### Opção 1: Verificar Senha Atual no Cloud SQL

1. **Acesse o Console do Google Cloud**
2. **Vá para SQL** → **Instâncias** → `monpec-db`
3. **Clique em "Usuários"** para ver os usuários do banco
4. **Verifique** se o usuário `monpec_user` existe

### Opção 2: Redefinir Senha do Banco de Dados

Execute no **Cloud Shell**:

```bash
# 1. Definir variáveis
PROJECT_ID="monpec-sistema-rural"
INSTANCE_NAME="monpec-db"
DB_USER="monpec_user"
NOVA_SENHA="L6171r12@@jjms"  # OU a senha que você quiser usar

# 2. Redefinir senha do usuário
gcloud sql users set-password $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$NOVA_SENHA

echo "✅ Senha do banco de dados atualizada!"
```

### Opção 3: Criar Usuário Se Não Existir

Se o usuário não existir, crie-o:

```bash
PROJECT_ID="monpec-sistema-rural"
INSTANCE_NAME="monpec-db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"

# Criar usuário
gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD

echo "✅ Usuário criado!"
```

## 🔄 Atualizar Cloud Run com a Senha Correta

Após corrigir a senha no Cloud SQL, atualize o Cloud Run:

### Método 1: Atualizar Variável de Ambiente

```bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"  # Use a senha que você configurou no Cloud SQL

# Atualizar apenas a variável DB_PASSWORD
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars "DB_PASSWORD=$DB_PASSWORD"
```

### Método 2: Fazer Deploy Completo com Senha Correta

```bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"  # Use a senha correta do Cloud SQL

gcloud config set project $PROJECT_ID

TIMESTAMP=$(date +%Y%m%d%H%M%S)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP

gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"
```

## ✅ Verificar se Funcionou

Após atualizar, verifique os logs:

```bash
# Ver logs do Cloud Run
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
    --limit=10 \
    --format="table(timestamp,severity,textPayload)"
```

Se não houver mais erros de autenticação, o problema foi resolvido!

## 🔐 Senhas Padrão do Sistema

Para referência, as senhas padrão do sistema são:

- **Banco de Dados (monpec_user)**: `L6171r12@@jjms`
- **Admin Django**: `L6171r12@@`

**⚠️ IMPORTANTE**: Se você alterou essas senhas, use as senhas que você configurou!

## 🎯 Passo a Passo Completo

1. **Verificar/Criar usuário no Cloud SQL:**
   ```bash
   gcloud sql users list --instance=monpec-db
   ```

2. **Se não existir, criar:**
   ```bash
   gcloud sql users create monpec_user --instance=monpec-db --password=L6171r12@@jjms
   ```

3. **Se existir mas senha errada, redefinir:**
   ```bash
   gcloud sql users set-password monpec_user --instance=monpec-db --password=L6171r12@@jjms
   ```

4. **Atualizar Cloud Run:**
   ```bash
   gcloud run services update monpec \
       --region=us-central1 \
       --update-env-vars "DB_PASSWORD=L6171r12@@jjms"
   ```

5. **Verificar logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=5
   ```

## 🐛 Troubleshooting

### Erro: "User does not exist"
Crie o usuário primeiro usando o comando da Opção 3.

### Erro: "Permission denied"
Verifique se você tem permissões no projeto:
```bash
gcloud projects get-iam-policy monpec-sistema-rural
```

### Erro: "Instance not found"
Verifique se a instância existe:
```bash
gcloud sql instances list
```


