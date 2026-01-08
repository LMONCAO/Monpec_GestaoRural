# 🔍 Diagnosticar Erro 500 no Sistema

Este guia ajuda a identificar e resolver o erro 500 (Server Error) no sistema Monpec.

## 🚨 Passo 1: Verificar Logs do Cloud Run

### No Google Cloud Shell, execute:

```bash
# Ver logs recentes do serviço
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=100 --format="table(timestamp,severity,textPayload,jsonPayload.message)"

# Ver apenas erros
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50

# Ver logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec"
```

### Ver logs mais detalhados:

```bash
# Ver últimos 200 logs com mais detalhes
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=200 --format=json | jq -r '.[] | "\(.timestamp) [\(.severity)] \(.textPayload // .jsonPayload.message // .jsonPayload)"'
```

---

## 🔧 Passo 2: Verificar Problemas Comuns

### 1. Verificar se o banco de dados está acessível

```bash
# Verificar status da instância Cloud SQL
gcloud sql instances describe monpec-db

# Verificar conexão
gcloud sql connect monpec-db --user=monpec_user --database=monpec_db
```

### 2. Verificar se as migrations foram aplicadas

```bash
# Criar job para verificar migrations
gcloud run jobs create verificar-migrations \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && python manage.py showmigrations" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

# Executar
gcloud run jobs execute verificar-migrations --region=us-central1 --wait

# Limpar
gcloud run jobs delete verificar-migrations --region=us-central1 --quiet
```

### 3. Verificar variáveis de ambiente do serviço

```bash
# Ver configuração atual do serviço
gcloud run services describe monpec --region=us-central1 --format=yaml
```

### 4. Verificar se o serviço está rodando

```bash
# Ver status do serviço
gcloud run services list --region=us-central1

# Ver detalhes do serviço
gcloud run services describe monpec --region=us-central1
```

---

## 🛠️ Passo 3: Aplicar Correções Comuns

### Correção 1: Aplicar Migrations Pendentes

```bash
# Criar job para aplicar migrations
gcloud run jobs create aplicar-migrations \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

# Executar
gcloud run jobs execute aplicar-migrations --region=us-central1 --wait

# Limpar
gcloud run jobs delete aplicar-migrations --region=us-central1 --quiet
```

### Correção 2: Verificar e Corrigir ALLOWED_HOSTS

O erro 500 pode ser causado por ALLOWED_HOSTS. Verifique se o domínio está configurado:

```bash
# Ver logs específicos de ALLOWED_HOSTS
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND textPayload=~\"ALLOWED_HOSTS\"" --limit=20
```

### Correção 3: Habilitar DEBUG Temporariamente (para ver erro completo)

⚠️ **ATENÇÃO**: Isso expõe informações sensíveis. Use apenas para diagnóstico!

```bash
# Atualizar serviço com DEBUG=True temporariamente
gcloud run services update monpec \
  --region=us-central1 \
  --update-env-vars="DEBUG=True" \
  --quiet

# Após diagnosticar, desabilitar novamente:
gcloud run services update monpec \
  --region=us-central1 \
  --update-env-vars="DEBUG=False" \
  --quiet
```

### Correção 4: Verificar Conexão com Banco de Dados

```bash
# Testar conexão com banco
gcloud run jobs create testar-banco \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute('SELECT 1'); print('✅ Conexão com banco OK!')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

# Executar
gcloud run jobs execute testar-banco --region=us-central1 --wait

# Limpar
gcloud run jobs delete testar-banco --region=us-central1 --quiet
```

---

## 📋 Passo 4: Script Completo de Diagnóstico

Execute este script no Cloud Shell para diagnóstico completo:

```bash
#!/bin/bash
echo "============================================================"
echo "🔍 DIAGNÓSTICO COMPLETO - ERRO 500"
echo "============================================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"

# 1. Verificar status do serviço
echo "1️⃣ Verificando status do serviço..."
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.conditions)" 2>/dev/null || echo "❌ Serviço não encontrado"

# 2. Ver últimos erros
echo ""
echo "2️⃣ Últimos erros nos logs..."
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=10 --format="table(timestamp,severity,textPayload)"

# 3. Verificar Cloud SQL
echo ""
echo "3️⃣ Verificando Cloud SQL..."
gcloud sql instances describe monpec-db --format="value(state)" 2>/dev/null || echo "❌ Instância não encontrada"

# 4. Verificar variáveis de ambiente
echo ""
echo "4️⃣ Variáveis de ambiente do serviço..."
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(spec.template.spec.containers[0].env)" | head -20

echo ""
echo "============================================================"
echo "✅ Diagnóstico concluído!"
echo "============================================================"
```

---

## 🎯 Soluções Rápidas

### Solução Rápida 1: Reiniciar o Serviço

```bash
# Forçar novo deploy (reinicia o serviço)
gcloud run services update monpec \
  --region=us-central1 \
  --no-traffic \
  --quiet

# Depois voltar o tráfego
gcloud run services update monpec \
  --region=us-central1 \
  --to-latest \
  --quiet
```

### Solução Rápida 2: Aplicar Migrations e Reiniciar

```bash
# Aplicar migrations
gcloud run jobs create aplicar-migrations-rapido \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

gcloud run jobs execute aplicar-migrations-rapido --region=us-central1 --wait
gcloud run jobs delete aplicar-migrations-rapido --region=us-central1 --quiet

# Reiniciar serviço
gcloud run services update monpec --region=us-central1 --to-latest --quiet
```

---

## 📞 Próximos Passos

Após executar o diagnóstico:

1. **Se o erro for de banco de dados**: Verifique conexão e migrations
2. **Se o erro for de ALLOWED_HOSTS**: Verifique configuração do serviço
3. **Se o erro for de código**: Verifique os logs detalhados
4. **Se o erro for de variáveis de ambiente**: Verifique configuração do Cloud Run

---

## 🔗 Links Úteis

- [Google Cloud Console - Logs](https://console.cloud.google.com/logs)
- [Google Cloud Console - Cloud Run](https://console.cloud.google.com/run)
- [Google Cloud Console - Cloud SQL](https://console.cloud.google.com/sql)
