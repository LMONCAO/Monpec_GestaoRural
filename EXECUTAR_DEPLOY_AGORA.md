# 🚀 Executar Deploy Agora - Guia Simples

## ⚡ Opção Mais Rápida: Copiar e Colar

### Passo 1: Abrir Cloud Shell
1. Acesse: https://console.cloud.google.com/
2. Clique no ícone do **Cloud Shell** (terminal) no topo da página
3. Aguarde o terminal abrir

### Passo 2: Copiar e Colar o Script Completo

**Copie TODO o conteúdo do arquivo `DEPLOY_AGORA_COPIAR_COLAR.sh` e cole no Cloud Shell, depois pressione Enter.**

O script vai:
- ✅ Clonar/atualizar o repositório do GitHub
- ✅ Fazer build da imagem Docker
- ✅ Fazer deploy no Cloud Run
- ✅ Mostrar a URL do serviço

**Tempo estimado: 15-20 minutos**

---

## 📋 Ou Execute Comando por Comando

Se preferir, execute um por vez:

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Clonar/atualizar repositório
cd ~
git clone https://github.com/LMONCAO/Monpec_GestaoRural.git || (cd Monpec_GestaoRural && git pull origin master)
cd ~/Monpec_GestaoRural

# 3. Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# 4. Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# 5. Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 6. Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10

# 7. Obter URL
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

---

## ✅ Verificar Depois

Após o deploy, acesse a URL retornada no navegador.

Se houver problemas, veja os logs:
```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

---

**Dica:** O script `DEPLOY_AGORA_COPIAR_COLAR.sh` faz tudo automaticamente! 🚀














