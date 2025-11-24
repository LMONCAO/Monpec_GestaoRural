# 🔧 Resolver Conflito Git no Cloud Shell

## ⚠️ Erro Atual

```
error: The following untracked working tree files would be overwritten by merge: deploy_agora_corrigido.sh
Please move or remove them before you merge.
```

## ✅ Solução Rápida

Execute este comando no Cloud Shell para limpar e fazer deploy:

```bash
cd ~ && rm -rf Monpec_GestaoRural && git clone https://github.com/LMONCAO/Monpec_GestaoRural.git && cd ~/Monpec_GestaoRural && set +H && CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)" 2>/dev/null) && SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec && gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025"'!'",CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10 && gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

---

## 📋 Ou Use o Script (Recomendado)

O arquivo `DEPLOY_PASSO_A_PASSO.sh` foi atualizado para resolver isso automaticamente.

1. Copie o conteúdo de `DEPLOY_PASSO_A_PASSO.sh`
2. Cole no Cloud Shell
3. Execute

---

## 🔍 O que o comando faz:

1. **Remove a pasta antiga** (`rm -rf Monpec_GestaoRural`)
2. **Clona do zero** (sem conflitos)
3. **Desabilita expansão de histórico** (`set +H`) - resolve problema do `!`
4. **Faz build e deploy** automaticamente

---

**Tempo estimado: ~15-20 minutos**













