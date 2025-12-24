# 🚀 Deploy Completo - Passo a Passo

## Execute no Cloud Shell

### Opção 1: Script Completo (Recomendado)

```bash
# 1. Dar permissão de execução
chmod +x DEPLOY_COMPLETO.sh

# 2. Executar deploy completo
./DEPLOY_COMPLETO.sh
```

Este script faz **TUDO** automaticamente:
- ✅ Habilita APIs necessárias
- ✅ Faz build da imagem Docker
- ✅ Faz deploy no Cloud Run
- ✅ Configura domínio (monpec.com.br e www.monpec.com.br)
- ✅ Aplica migrações do banco de dados

### Opção 2: Passo a Passo Manual

#### 1. Habilitar APIs
```bash
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com sqladmin.googleapis.com
```

#### 2. Build e Deploy
```bash
# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi --cpu 1 --timeout 300 --max-instances 10 --min-instances 1 --port 8080
```

#### 3. Configurar Variáveis de Ambiente
```bash
chmod +x CONFIGURAR_VARIAVEIS_COMPLETO.sh
./CONFIGURAR_VARIAVEIS_COMPLETO.sh
```

Ou manualmente:
```bash
gcloud run services update monpec --region us-central1 \
    --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940,MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3,SECRET_KEY=SUA_SECRET_KEY,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME"
```

#### 4. Configurar Domínio
```bash
gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

#### 5. Aplicar Migrações
```bash
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --command python \
    --args "manage.py,migrate" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

## ✅ Verificação

### Ver URL do serviço
```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

### Ver logs
```bash
gcloud run services logs read monpec --region us-central1
```

### Verificar variáveis de ambiente
```bash
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

## 🔧 Troubleshooting

### Se o deploy falhar
1. Verifique os logs: `gcloud run services logs read monpec --region us-central1`
2. Verifique se todas as APIs estão habilitadas
3. Verifique se as variáveis de ambiente estão configuradas

### Se o domínio não funcionar
1. Verifique os registros DNS no seu provedor de domínio
2. Aguarde a propagação DNS (pode levar até 48 horas)
3. Verifique o mapeamento: `gcloud run domain-mappings list --region us-central1`

### Se as migrações falharem
1. Verifique se as variáveis de banco de dados estão configuradas
2. Execute manualmente: `gcloud run jobs execute migrate-monpec --region us-central1 --wait`
3. Verifique os logs do job: `gcloud run jobs executions list --job migrate-monpec --region us-central1`

## 📋 Checklist Final

- [ ] Build da imagem concluído
- [ ] Deploy no Cloud Run concluído
- [ ] Variáveis de ambiente configuradas
- [ ] Domínio configurado
- [ ] Migrações aplicadas
- [ ] Sistema acessível em https://monpec.com.br
- [ ] Teste de login funcionando
- [ ] Teste de pagamento funcionando


