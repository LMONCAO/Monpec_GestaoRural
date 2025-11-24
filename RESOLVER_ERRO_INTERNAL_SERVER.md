# 🔧 Resolver Internal Server Error

## ❌ Problema Identificado

O site está retornando "Internal Server Error" em:
- `https://monpec-fzzfjppzva-uc.a.run.app`
- `https://monpec-fzzfjppzva-uc.a.run.app/google40933139f3b0d469.html`

---

## 🔍 Passo 1: Verificar Logs do Cloud Run

Execute no Cloud Shell para ver os logs mais recentes:

```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

Ou para ver logs em tempo real:

```bash
gcloud run services logs tail monpec --region us-central1
```

**Procure por:**
- Erros de Django (traceback)
- Erros de banco de dados
- Erros de importação
- Problemas com variáveis de ambiente

---

## 🔍 Passo 2: Verificar Variáveis de Ambiente

Verifique se as variáveis de ambiente estão configuradas corretamente:

```bash
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

---

## 🔍 Passo 3: Verificar Conexão com Banco de Dados

O erro pode ser relacionado ao banco de dados. Verifique:

```bash
# Verificar se a instância do banco existe
gcloud sql instances describe monpec-db

# Verificar connection name
gcloud sql instances describe monpec-db --format="value(connectionName)"
```

---

## 🔍 Passo 4: Verificar Configuração do Serviço

Verifique a configuração completa do serviço:

```bash
gcloud run services describe monpec --region us-central1
```

---

## 🔧 Possíveis Causas e Soluções

### 1. Erro de Conexão com Banco de Dados

**Sintoma:** Erro relacionado a `psycopg2` ou `connection refused`

**Solução:**
- Verificar se o Cloud SQL Proxy está configurado
- Verificar se o `CLOUD_SQL_CONNECTION_NAME` está correto
- Verificar se o Cloud Run tem permissão para acessar o Cloud SQL

### 2. Variáveis de Ambiente Faltando

**Sintoma:** `KeyError` ou `SECRET_KEY` não definido

**Solução:**
- Verificar se todas as variáveis estão configuradas
- Verificar se `DJANGO_SETTINGS_MODULE` está correto

### 3. Erro de Importação

**Sintoma:** `ModuleNotFoundError` ou `ImportError`

**Solução:**
- Verificar se todas as dependências estão em `requirements_producao.txt`
- Verificar se o `Dockerfile` está correto

### 4. Erro de Migração

**Sintoma:** Erro relacionado a `migrations` ou `database`

**Solução:**
- Executar migrações manualmente
- Verificar se o banco está acessível

---

## 🚀 Solução Rápida: Re-executar Deploy

Se os logs não mostrarem nada claro, tente fazer um novo deploy:

```bash
cd ~/Monpec_GestaoRural

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Deploy novamente
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

## 📋 Próximos Passos

1. **Execute o comando de logs** para ver o erro específico
2. **Copie o erro completo** e me envie
3. **Vou ajudar a corrigir** o problema específico

---

**Última atualização:** Novembro 2025














