# 🚀 Deploy Completo - Google Cloud Shell

## Passo a Passo

### 1. No Cloud Shell, faça upload dos arquivos do projeto

```bash
# Clone ou faça upload do projeto para o Cloud Shell
# Se já estiver no diretório do projeto, pule esta etapa
```

### 2. Executar o deploy

```bash
chmod +x deploy_cloud_shell.sh
./deploy_cloud_shell.sh
```

Este script irá:
- ✅ Habilitar APIs necessárias
- ✅ Fazer build da imagem Docker
- ✅ Fazer push para Container Registry
- ✅ Fazer deploy no Cloud Run

### 3. Configurar variáveis de ambiente

```bash
chmod +x CONFIGURAR_VARIAVEIS_CLOUD_RUN.sh
./CONFIGURAR_VARIAVEIS_CLOUD_RUN.sh
```

Ou configure manualmente:

```bash
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940,MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3,SECRET_KEY=SUA_SECRET_KEY_AQUI,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME"
```

### 4. Configurar domínio

```bash
chmod +x CONFIGURAR_DOMINIO.sh
./CONFIGURAR_DOMINIO.sh
```

### 5. Aplicar migrações

```bash
chmod +x APLICAR_MIGRACOES_CLOUD_RUN.sh
./APLICAR_MIGRACOES_CLOUD_RUN.sh
```

## ✅ Pronto!

Acesse: https://monpec.com.br

## Comandos Úteis

### Ver logs
```bash
gcloud run services logs read monpec --region us-central1
```

### Ver URL do serviço
```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

### Atualizar serviço
```bash
gcloud run services update monpec --region us-central1
```



