# 🔧 Resolver Erro "No Space Left on Device"

## ⚠️ Problema Identificado

O Cloud Shell está sem espaço em disco, impedindo o build do Docker.

**Erro:** `no space left on device`

---

## ✅ Solução 1: Limpar Espaço no Cloud Shell

Execute estes comandos no Cloud Shell para liberar espaço:

```bash
# Limpar imagens Docker antigas
docker system prune -a --volumes -f

# Limpar cache do pip
rm -rf ~/.cache/pip

# Limpar arquivos temporários
rm -rf /tmp/*

# Verificar espaço disponível
df -h
```

---

## ✅ Solução 2: Usar Cloud Build Diretamente (Recomendado)

Em vez de fazer build no Cloud Shell, use o Cloud Build diretamente (que tem mais espaço):

```bash
cd ~/Monpec_GestaoRural

# Atualizar código
git pull origin master

# Build usando Cloud Build (não usa espaço do Cloud Shell)
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

**Vantagem:** O Cloud Build roda em servidores dedicados com muito mais espaço.

---

## ✅ Solução 3: Limpar Builds Antigos

Limpe builds antigos do Cloud Build:

```bash
# Listar builds antigos
gcloud builds list --limit=10

# Deletar builds antigos (substitua BUILD_ID pelo ID do build)
# gcloud builds delete BUILD_ID
```

---

## ✅ Solução 4: Otimizar Dockerfile

Se ainda houver problemas, podemos otimizar o Dockerfile para usar menos espaço:

1. Usar imagens base menores
2. Limpar cache durante o build
3. Usar multi-stage builds

---

## 📋 Passo a Passo Recomendado

### 1. Limpar Espaço no Cloud Shell:
```bash
docker system prune -a --volumes -f
rm -rf ~/.cache/pip
df -h
```

### 2. Usar Cloud Build (não Docker local):
```bash
cd ~/Monpec_GestaoRural
git pull origin master
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

### 3. Fazer Deploy:
```bash
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

---

## 🔍 Verificar Espaço Disponível

Para verificar quanto espaço você tem:

```bash
# Ver espaço no Cloud Shell
df -h ~

# Ver espaço usado por Docker
docker system df
```

---

## ⚠️ Importante

O comando `gcloud builds submit` **não usa espaço do Cloud Shell** - ele envia o código para o Cloud Build, que faz o build em servidores dedicados com muito mais espaço.

**Use sempre `gcloud builds submit` em vez de `docker build` localmente no Cloud Shell!**

---

**Última atualização:** Novembro 2025

