# 🚀 Deploy Direto no Google Cloud Shell

Guia passo a passo para fazer upload do código e deploy direto no Cloud Shell.

---

## 📋 Passo 1: Fazer Upload do Código

### **Opção A: Upload via Interface (Mais Fácil)**

1. No Cloud Shell, clique no ícone **"⋮"** (três pontos) no canto superior direito
2. Selecione **"Upload file"** ou **"Upload folder"**
3. Selecione a pasta do projeto: `Monpec_GestaoRural`
4. Aguarde o upload completar

### **Opção B: Upload via Git (Se estiver no GitHub)**

```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO
```

### **Opção C: Upload via gcloud (Arquivo ZIP)**

No seu computador Windows:
```powershell
# Criar ZIP do projeto
Compress-Archive -Path "Monpec_GestaoRural\*" -DestinationPath "monpec.zip"

# Fazer upload (via navegador ou gcloud)
```

No Cloud Shell:
```bash
# Extrair ZIP
unzip monpec.zip
cd Monpec_GestaoRural
```

---

## 📋 Passo 2: Verificar Arquivos

```bash
# Verificar se está na pasta correta
ls -la

# Deve aparecer: manage.py, Dockerfile, requirements_producao.txt, etc.
```

---

## 📋 Passo 3: Executar Deploy

### **Método Rápido: Usar Script**

```bash
# Tornar script executável
chmod +x DEPLOY_AGORA.sh

# Executar deploy
./DEPLOY_AGORA.sh
```

### **Método Manual: Comandos Individuais**

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com

# 3. Definir variáveis
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="Monpec2025!"

# 4. Obter connection name do banco
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"

# 5. Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "Secret Key gerada"

# 6. Build da imagem (10-15 minutos)
echo "🔨 Fazendo build da imagem Docker..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 7. Deploy no Cloud Run (2-3 minutos)
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        DB_NAME=$DB_NAME,\
        DB_USER=$DB_USER,\
        DB_PASSWORD=$DB_PASSWORD,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10

# 8. Obter URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "✅ Deploy concluído!"
echo "🌐 URL: $SERVICE_URL"
```

---

## ✅ Passo 4: Verificar Deploy

```bash
# Obter URL do serviço
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Testar no navegador
# A URL será algo como: https://monpec-xxxxx-uc.a.run.app
```

---

## 🔍 Passo 5: Verificar Meta Tag e Arquivo HTML

Após o deploy, teste:

1. **Meta Tag:**
   - Acesse a URL do serviço no navegador
   - Veja código-fonte (Ctrl+U)
   - Procure: `google-site-verification`

2. **Arquivo HTML:**
   - Acesse: `https://sua-url/google40933139f3b0d469.html`
   - Deve retornar: `google-site-verification: google40933139f3b0d469.html`

---

## 📝 Comandos Úteis

```bash
# Ver logs do serviço
gcloud run services logs read monpec --region us-central1 --limit 50

# Ver status do serviço
gcloud run services describe monpec --region us-central1

# Atualizar serviço (após mudanças no código)
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1
```

---

## 🆘 Troubleshooting

### **Erro: "Project not found"**
```bash
# Listar projetos
gcloud projects list

# Configurar projeto correto
gcloud config set project monpec-sistema-rural
```

### **Erro: "Permission denied"**
```bash
# Verificar permissões
gcloud projects get-iam-policy monpec-sistema-rural
```

### **Erro: "Dockerfile not found"**
```bash
# Verificar se está na pasta correta
pwd
ls -la Dockerfile
```

---

## ✅ Checklist

- [ ] Código enviado para Cloud Shell
- [ ] Script executado ou comandos manuais rodados
- [ ] Build concluído com sucesso
- [ ] Deploy concluído com sucesso
- [ ] URL do serviço obtida
- [ ] Site acessível no navegador
- [ ] Meta tag visível no código-fonte
- [ ] Arquivo HTML acessível

---

**Última atualização:** Dezembro 2025

