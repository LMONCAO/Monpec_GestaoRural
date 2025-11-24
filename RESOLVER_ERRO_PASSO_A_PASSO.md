# 🔧 Resolver Internal Server Error - Passo a Passo

## 🎯 Objetivo
Identificar e corrigir o erro "Internal Server Error" no Cloud Run.

---

## 📋 Passo 1: Verificar Logs (IMPORTANTE)

Execute no Cloud Shell para ver o erro específico:

```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

**Procure por:**
- `DisallowedHost` (problema com ALLOWED_HOSTS)
- `OperationalError` (problema com banco de dados)
- `ImportError` ou `ModuleNotFoundError` (problema com dependências)
- `KeyError` (variável de ambiente faltando)
- Qualquer `Traceback` ou `Exception`

**Copie o erro completo e me envie!**

---

## 🔍 Possíveis Problemas e Soluções

### Problema 1: DisallowedHost

**Sintoma nos logs:**
```
Invalid HTTP_HOST header: 'monpec-fzzfjppzva-uc.a.run.app'. You may need to add 'monpec-fzzfjppzva-uc.a.run.app' to ALLOWED_HOSTS.
```

**Solução:**
O host do Cloud Run não está em `ALLOWED_HOSTS`. Vou corrigir isso agora.

---

### Problema 2: Erro de Banco de Dados

**Sintoma nos logs:**
```
OperationalError: could not connect to server
```

**Solução:**
- Verificar se o Cloud SQL está acessível
- Verificar se o `CLOUD_SQL_CONNECTION_NAME` está correto
- Verificar se o Cloud Run tem permissão para acessar o Cloud SQL

---

### Problema 3: Variável de Ambiente Faltando

**Sintoma nos logs:**
```
KeyError: 'SECRET_KEY'
```

**Solução:**
- Verificar se todas as variáveis de ambiente estão configuradas
- Re-executar o deploy com todas as variáveis

---

## 🚀 Solução Rápida: Corrigir ALLOWED_HOSTS

Se o erro for `DisallowedHost`, execute este comando para adicionar o host:

```bash
cd ~/Monpec_GestaoRural

# Obter o host atual do Cloud Run
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
HOST=$(echo $SERVICE_URL | sed 's|https\?://||' | sed 's|/.*||')

echo "Host do Cloud Run: $HOST"

# Fazer deploy novamente com o host adicionado
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,CLOUD_RUN_HOST=$HOST" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

---

## 📝 Próximos Passos

1. **Execute o comando de logs** (Passo 1)
2. **Copie o erro completo**
3. **Me envie o erro** para eu ajudar a corrigir especificamente

---

**Última atualização:** Novembro 2025














