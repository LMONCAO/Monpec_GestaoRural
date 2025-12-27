# Solução para o Problema de Build

## Problema Identificado

O gcloud está tentando acessar um arquivo PNG que não existe:
```
.\\.cursor\\projects\\...\\assets\\c__Users_lmonc_AppData_Roaming_Cursor_User_workspaceStorage_62980869224a1fb3e1a8f58fdfa76a0f_images_image-1397ce09-c893-40a5-9562-ebb3940fb8b9.png
```

## Correção Aplicada

✅ **Corrigido o erro no `settings_gcp.py`** (linha 256-258) relacionado ao `GOOGLE_ANALYTICS_ID`

## Soluções Possíveis

### Opção 1: Executar o build via Cloud Shell (Recomendado)

1. Acesse o Google Cloud Shell: https://shell.cloud.google.com/
2. Clone ou faça upload do código
3. Execute o script de deploy:

```bash
gcloud config set project monpec-sistema-rural
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest --timeout=20m
```

### Opção 2: Usar Cloud Build API diretamente

Você pode usar a interface web do Cloud Build no Console do Google Cloud:
1. Acesse: https://console.cloud.google.com/cloud-build/builds
2. Clique em "Criar build"
3. Configure o build usando o `cloudbuild-config.yaml`

### Opção 3: Limpar cache e tentar novamente

Execute no PowerShell:

```powershell
# Limpar cache do gcloud
gcloud config unset app/cloud_build_timeout
gcloud info --run-diagnostics

# Tentar build novamente
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest --timeout=20m
```

### Opção 4: Executar deploy manual via script

O script `deploy-completo-agora.sh` foi criado e está pronto para uso. 
Você pode executá-lo via Git Bash ou WSL no Windows.

## Próximos Passos Após o Build

Depois que o build for concluído, execute:

```bash
# Deploy do serviço
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1" \
    --add-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080

# Executar migrações
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```




