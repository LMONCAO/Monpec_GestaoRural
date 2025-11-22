# 🚀 Deploy Rápido - Passo a Passo

Guia simplificado para fazer deploy do MONPEC no Google Cloud Run com as atualizações (meta tag e arquivo HTML de verificação).

---

## 📋 Pré-requisitos

- ✅ Conta Google Cloud ativa
- ✅ Google Cloud SDK instalado ou acesso ao Cloud Shell
- ✅ Projeto no Google Cloud criado
- ✅ Billing habilitado

---

## ⚡ Opção 1: Usar Google Cloud Shell (Recomendado - Mais Fácil)

### **Passo 1: Abrir Cloud Shell**

1. Acesse: https://console.cloud.google.com
2. Clique no ícone do terminal no canto superior direito (Cloud Shell)

### **Passo 2: Fazer Upload do Código**

Se o código não estiver no GitHub:

1. No Cloud Shell, clique nos 3 pontos → "Upload file"
2. Faça upload de todos os arquivos do projeto
3. Ou use `git clone` se estiver no GitHub

### **Passo 3: Executar Deploy**

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Habilitar APIs necessárias
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

# 6. Build da imagem Docker (10-15 minutos)
echo "🔨 Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 7. Deploy no Cloud Run (2-3 minutos)
echo "🚀 Fazendo deploy..."
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

# 8. Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "✅ Deploy concluído!"
echo "🌐 URL do serviço: $SERVICE_URL"
```

---

## 💻 Opção 2: Usar PowerShell no Windows

### **Passo 1: Verificar Google Cloud SDK**

```powershell
gcloud --version
```

Se não estiver instalado: https://cloud.google.com/sdk/docs/install

### **Passo 2: Autenticar**

```powershell
gcloud auth login
gcloud config set project monpec-sistema-rural
```

### **Passo 3: Executar Script de Deploy**

Se você tiver o script `deploy_google_cloud.ps1`:

```powershell
.\deploy_google_cloud.ps1
```

Ou execute os comandos manualmente (similar ao Cloud Shell).

---

## ✅ Verificar após o Deploy

### **1. Testar URL do Serviço**

```bash
# Obter URL
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Testar no navegador
# https://monpec-xxxxx-uc.a.run.app
```

### **2. Verificar Meta Tag**

1. Acesse a URL do serviço no navegador
2. Veja o código-fonte (Ctrl+U ou F12)
3. Procure por: `<meta name="google-site-verification"`
4. Deve aparecer: `content="vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk"`

### **3. Verificar Arquivo HTML**

Acesse: `https://monpec-xxxxx-uc.a.run.app/google40933139f3b0d469.html`

Deve retornar: `google-site-verification: google40933139f3b0d469.html`

### **4. Verificar no Google Search Console**

1. Acesse: https://search.google.com/search-console
2. Vá em "Verificar propriedade"
3. Selecione "Tag HTML"
4. Clique em "VERIFICAR"
5. ✅ Deve verificar com sucesso!

---

## 🔄 Atualizar Deployment Existente

Se você já tem um deployment e quer apenas atualizar:

```bash
# 1. Build da nova imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# 2. Deploy atualizado
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --platform managed
```

---

## 🆘 Troubleshooting

### **Erro: "Project not found"**

```bash
# Listar projetos
gcloud projects list

# Configurar projeto correto
gcloud config set project SEU_PROJECT_ID
```

### **Erro: "Permission denied"**

```bash
# Verificar permissões
gcloud projects get-iam-policy monpec-sistema-rural

# Ou usar conta de serviço com permissões adequadas
```

### **Erro: "Database connection failed"**

Verifique:
- ✅ Instância Cloud SQL está rodando
- ✅ Connection name está correto
- ✅ Credenciais (DB_USER, DB_PASSWORD) estão corretas
- ✅ Cloud Run tem acesso à Cloud SQL (flag `--add-cloudsql-instances`)

### **Erro no Build**

Verifique:
- ✅ Dockerfile existe
- ✅ requirements_producao.txt existe
- ✅ Código está completo

---

## 📝 Checklist Final

- [ ] Build da imagem completado
- [ ] Deploy no Cloud Run concluído
- [ ] URL do serviço obtida
- [ ] Site acessível via URL do Cloud Run
- [ ] Meta tag visível no código-fonte
- [ ] Arquivo HTML de verificação acessível
- [ ] Google Search Console verificado com sucesso
- [ ] DNS CNAME configurado (após deploy)
- [ ] Domínio monpec.com.br funcionando (após propagação DNS)

---

## 🎯 Próximos Passos

Após o deploy bem-sucedido:

1. **Configurar domínio personalizado:**
   ```bash
   gcloud run domain-mappings create \
       --service monpec \
       --domain monpec.com.br \
       --region us-central1
   ```

2. **Verificar DNS:**
   ```powershell
   .\verificar_dominio_cloud_run.ps1
   ```

3. **Executar migrações** (se necessário):
   - Acesse o serviço via URL
   - Ou crie um job no Cloud Run

---

**Última atualização:** Dezembro 2025

