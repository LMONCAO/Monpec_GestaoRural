# 🚀 Comandos para Atualizar no Google Cloud

## ⚠️ IMPORTANTE: Se Der Erro de Senha do Banco

Se você ver o erro `password authentication failed for user "monpec_user"`, execute primeiro:

```bash
# Corrigir senha do banco de dados
gcloud sql users set-password monpec_user --instance=monpec-db --password=L6171r12@@jjms
```

Depois continue com o deploy abaixo.

## 📋 Comandos Rápidos

### Opção 1: Comando Único (Mais Rápido)

Execute este comando completo no **Cloud Shell**:

```bash
PROJECT_ID="monpec-sistema-rural" && SERVICE_NAME="monpec" && REGION="us-central1" && DB_PASSWORD="L6171r12@@jjms" && echo "🔧 Verificando senha do banco..." && gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>/dev/null || echo "⚠️ Aviso: Não foi possível atualizar senha do banco (pode ser normal se já estiver correta)" && gcloud config set project $PROJECT_ID && grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt && TIMESTAMP=$(date +%Y%m%d%H%M%S) && echo "🔨 Buildando..." && gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP && echo "🚀 Deployando..." && gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" && echo "✅✅✅ CONCLUÍDO! ✅✅✅"
```

### Opção 2: Passo a Passo (Mais Controle)

```bash
# 1. Configurar variáveis
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

# 2. Configurar projeto
gcloud config set project $PROJECT_ID

# 3. Garantir que openpyxl está no requirements
grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt

# 4. Gerar timestamp para a imagem
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"

# 5. Build da imagem
echo "🔨 Buildando imagem..."
gcloud builds submit --tag $IMAGE_TAG

# 6. Deploy no Cloud Run
echo "🚀 Deployando..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

# 7. Verificar URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "✅ Deploy concluído!"
echo "🔗 URL: $SERVICE_URL"
```

## 🔧 Comandos Adicionais Úteis

### Verificar Status do Deploy

```bash
gcloud run services describe monpec --region=us-central1
```

### Ver Logs

```bash
# Últimos logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50 --format="table(timestamp,severity,textPayload)"

# Logs de erro apenas
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=20
```

### Verificar URL do Serviço

```bash
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

### Garantir Admin (Se necessário)

```bash
gcloud run jobs execute garantir-admin \
  --region=us-central1 \
  --args python,manage.py,garantir_admin
```

### Executar Migrações Manualmente

```bash
gcloud run jobs execute migrate-monpec \
  --region=us-central1 \
  --wait
```

## 📝 Variáveis de Ambiente Importantes

Se precisar atualizar variáveis de ambiente:

```bash
gcloud run services update monpec \
  --region=us-central1 \
  --update-env-vars "NOVA_VARIAVEL=valor"
```

### Variáveis Comuns

- `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`
- `DEBUG=False`
- `CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db`
- `DB_NAME=monpec_db`
- `DB_USER=monpec_user`
- `DB_PASSWORD=L6171r12@@jjms`
- `SECRET_KEY=sua-secret-key-aqui` (se configurada)
- `DJANGO_SUPERUSER_PASSWORD=L6171r12@@` (senha do admin)

## ⚡ Deploy Rápido (Usando Latest)

Se quiser usar a tag `latest` (mais rápido, mas menos controle):

```bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

gcloud config set project $PROJECT_ID

# Build e marcar como latest
TIMESTAMP=$(date +%Y%m%d%H%M%S)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP
gcloud container images add-tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --quiet

# Deploy usando latest
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"
```

## 🎯 Checklist Pós-Deploy

Após o deploy, verifique:

1. ✅ **Serviço está rodando**: `gcloud run services describe monpec --region=us-central1`
2. ✅ **Acessar URL**: Teste a URL retornada
3. ✅ **Login funciona**: Teste login com `admin` / `L6171r12@@`
4. ✅ **Verificar logs**: Se houver erros, verifique os logs
5. ✅ **Admin criado**: Se não conseguir fazer login, execute `garantir_admin`

## 🐛 Troubleshooting

### Erro: "Build failed"
- Verifique se todos os arquivos necessários estão no diretório
- Verifique se `requirements_producao.txt` existe e tem `openpyxl`

### Erro: "Service not found"
- Verifique se o projeto está correto: `gcloud config get-value project`
- Verifique se o serviço existe: `gcloud run services list --region=us-central1`

### Erro: "Permission denied"
- Verifique permissões: `gcloud projects get-iam-policy monpec-sistema-rural`
- Faça login novamente: `gcloud auth login`

### Admin não funciona após deploy
- Execute: `gcloud run jobs execute garantir-admin --region=us-central1 --args python,manage.py,garantir_admin`

## 📚 Mais Informações

- **Guia Completo**: Veja `GUIA_DEPLOY_RAPIDO.md`
- **Troubleshooting**: Veja `TROUBLESHOOTING_CLOUD_RUN.md`
- **Admin Automático**: Veja `MELHORIAS_ADMIN_AUTOMATICO.md`

