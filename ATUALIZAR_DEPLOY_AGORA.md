# 🚀 Atualizar Deploy - Versão Atualizada

Como o terminal está tendo problemas com caracteres especiais no caminho, execute o script de deploy diretamente:

## Opção 1: Script Automático (Recomendado)

Execute o arquivo **`DEPLOY_TUDO_AUTOMATICO.bat`** que está na raiz do projeto.

Este script vai:
1. ✅ Fazer build da imagem Docker usando `Dockerfile.prod`
2. ✅ Fazer deploy no Cloud Run com todas as configurações
3. ✅ Garantir que a versão atualizada seja colocada no ar

## Opção 2: Cloud Shell

1. Abra o Google Cloud Shell
2. Entre na pasta do projeto:
   ```bash
   cd Monpec_GestaoRural
   ```
3. Execute:
   ```bash
   gcloud config set project monpec-sistema-rural
   gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest --config cloudbuild-config.yaml --substitutions=_PROJECT_ID=monpec-sistema-rural,_COMMIT_SHA=latest
   gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec:latest --region us-central1 --platform managed --allow-unauthenticated --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" --memory=2Gi --cpu=2 --timeout=300 --max-instances=10
   ```

## Opção 3: PowerShell (Direto)

Se estiver no PowerShell, execute:

```powershell
.\DEPLOY_TUDO_AUTOMATICO.bat
```

Ou use o script PowerShell equivalente se existir.

---

**Importante**: O script `DEPLOY_TUDO_AUTOMATICO.bat` já está configurado para usar o `Dockerfile.prod` corretamente e fazer tudo automaticamente.

