# 🔄 Atualizar Sistema Existente no Google Cloud

## Entendendo a Situação

Você está **atualizando** um sistema que já está rodando no Google Cloud Run, não fazendo um deploy do zero. Isso significa:

- ✅ Serviço `monpec` já existe
- ✅ Domínios já estão configurados
- ✅ Job de migração já existe
- ⚠️ Precisa atualizar a imagem e variáveis de ambiente
- ⚠️ Precisa executar novas migrações

## 📋 Passo a Passo para Atualização

### 1. Fazer Build e Deploy da Nova Versão

```bash
# Build da nova imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# Deploy da nova versão (atualiza o serviço existente)
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi --cpu 1 --timeout 300 --max-instances 10 --min-instances 1 --port 8080
```

### 2. Atualizar Variáveis de Ambiente (se necessário)

Se você adicionou novas variáveis ou precisa atualizar existentes:

```bash
gcloud run services update monpec --region us-central1 \
  --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940,MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3"
```

**Para adicionar variáveis sem sobrescrever as existentes:**
```bash
# Ver variáveis atuais
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"

# Atualizar apenas as novas
gcloud run services update monpec --region us-central1 \
  --update-env-vars "NOVA_VARIAVEL=valor"
```

### 3. Atualizar Job de Migração e Executar

```bash
# Atualizar o job com a nova imagem
gcloud run jobs update migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1

# Copiar variáveis de ambiente do serviço para o job
# Primeiro, obtenha as variáveis do serviço
SERVICE_ENV=$(gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)")

# Atualizar o job com as mesmas variáveis
gcloud run jobs update migrate-monpec --region us-central1 --update-env-vars "$SERVICE_ENV"

# Executar migrações
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

### 4. Verificar Atualização

```bash
# Ver URL do serviço
gcloud run services describe monpec --region us-central1 --format="value(status.url)"

# Ver logs recentes
gcloud run services logs read monpec --region us-central1 --limit 50

# Verificar versão da imagem
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].image)"
```

## 🚀 Script Rápido de Atualização

Execute estes comandos em sequência:

```bash
# 1. Build e Deploy
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest && \
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi --cpu 1 --timeout 300 --max-instances 10 --min-instances 1 --port 8080

# 2. Atualizar job e executar migrações
gcloud run jobs update migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 && \
SERVICE_ENV=$(gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)") && \
gcloud run jobs update migrate-monpec --region us-central1 --update-env-vars "$SERVICE_ENV" && \
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

## ⚠️ Problema da Migração

Se a migração falhar, é porque o job precisa das variáveis de ambiente do banco de dados. Execute:

```bash
# Obter variáveis do serviço
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"

# Copiar manualmente as variáveis DB_* para o job
gcloud run jobs update migrate-monpec --region us-central1 \
  --update-env-vars "DB_NAME=valor,DB_USER=valor,DB_PASSWORD=valor,DB_HOST=valor,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
```

## 📝 Checklist de Atualização

- [ ] Build da nova imagem
- [ ] Deploy da nova versão (atualiza serviço)
- [ ] Verificar se variáveis de ambiente estão corretas
- [ ] Atualizar job de migração com nova imagem
- [ ] Copiar variáveis de ambiente para o job
- [ ] Executar migrações
- [ ] Verificar logs para erros
- [ ] Testar sistema em produção

## 🔍 Comandos Úteis

```bash
# Ver status do serviço
gcloud run services describe monpec --region us-central1

# Ver histórico de revisões
gcloud run revisions list --service monpec --region us-central1

# Ver logs em tempo real
gcloud run services logs read monpec --region us-central1 --follow

# Fazer rollback para versão anterior (se necessário)
gcloud run services update-traffic monpec --region us-central1 --to-revisions REVISION_NAME=100
```





















