# 🔧 Corrigir "Service Unavailable"

## ❌ Problema

O erro "Service Unavailable" significa que o serviço Cloud Run não está rodando ou está com problemas.

## ✅ Soluções

### 1. Verificar Status do Serviço

Execute no **Cloud Shell**:

```bash
# Ver status do serviço
gcloud run services describe monpec --region=us-central1

# Ver logs de erro
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
    --limit=20 \
    --format="table(timestamp,severity,textPayload)"
```

### 2. Verificar se o Serviço Está Rodando

```bash
# Listar serviços
gcloud run services list --region=us-central1

# Ver URL do serviço
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

### 3. Possíveis Causas e Soluções

#### Causa 1: Serviço Não Existe ou Foi Deletado

**Solução:** Fazer deploy novamente:

```bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"

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

#### Causa 2: Erro na Aplicação (Crash no Startup)

**Solução:** Verificar logs e corrigir:

```bash
# Ver últimos logs
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)"
```

#### Causa 3: Problema com Banco de Dados

**Solução:** Verificar conexão com o banco:

```bash
# Verificar se a instância do banco está rodando
gcloud sql instances describe monpec-db

# Verificar se o usuário existe
gcloud sql users list --instance=monpec-db
```

#### Causa 4: Timeout ou Recursos Insuficientes

**Solução:** Aumentar recursos:

```bash
gcloud run services update monpec \
    --region=us-central1 \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600
```

### 4. Redeploy Completo (Solução Mais Segura)

Execute este comando completo para fazer um redeploy:

```bash
PROJECT_ID="monpec-sistema-rural" && SERVICE_NAME="monpec" && REGION="us-central1" && DB_PASSWORD="L6171r12@@jjms" && echo "🔧 Verificando senha do banco..." && gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>/dev/null || echo "⚠️ Aviso: Não foi possível atualizar senha do banco" && gcloud config set project $PROJECT_ID && grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt && TIMESTAMP=$(date +%Y%m%d%H%M%S) && echo "🔨 Buildando..." && gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP && echo "🚀 Deployando..." && gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" --memory=2Gi --cpu=2 --timeout=600 && echo "✅✅✅ CONCLUÍDO! ✅✅✅" && SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)") && echo "🔗 URL: $SERVICE_URL"
```

## 🔍 Diagnóstico Rápido

Execute este comando para ver o que está acontecendo:

```bash
# Ver status completo
gcloud run services describe monpec --region=us-central1

# Ver últimas 20 linhas de log
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
    --limit=20 \
    --format="value(textPayload)" \
    | tail -20
```

## 📝 Checklist

- [ ] Serviço existe? `gcloud run services list --region=us-central1`
- [ ] Serviço está rodando? Ver status no console
- [ ] Logs mostram erros? Verificar logs acima
- [ ] Banco de dados está acessível? Verificar Cloud SQL
- [ ] Variáveis de ambiente estão corretas? Verificar no console

## 🎯 Próximos Passos

1. Execute o comando de diagnóstico acima
2. Verifique os logs para identificar o erro específico
3. Se necessário, faça um redeploy completo usando o comando da seção 4
4. Aguarde 1-2 minutos após o deploy
5. Tente acessar novamente


