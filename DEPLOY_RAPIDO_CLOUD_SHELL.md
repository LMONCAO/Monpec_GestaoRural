# 🚀 Deploy Rápido - Cloud Shell

## ⚡ Método Mais Rápido (1 comando)

1. **Abra o Cloud Shell:** https://console.cloud.google.com/ (clique no ícone do terminal no topo)

2. **Copie e cole este comando completo:**

```
cd ~ && git clone https://github.com/LMONCAO/Monpec_GestaoRural.git 2>/dev/null || (cd Monpec_GestaoRural && git pull origin master) && cd ~/Monpec_GestaoRural && CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)" 2>/dev/null) && SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec && gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10 && gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

3. **Pressione Enter e aguarde** (~15-20 minutos)

4. **A URL do serviço será exibida no final**

---

## 📋 Ou use o arquivo de comando

O arquivo `COMANDO_DEPLOY_UNICO.txt` contém o mesmo comando para copiar facilmente.

---

**Tempo total: ~15-20 minutos** (build + deploy)












