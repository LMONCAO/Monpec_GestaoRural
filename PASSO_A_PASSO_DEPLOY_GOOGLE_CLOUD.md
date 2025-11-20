# 🚀 PASSO A PASSO COMPLETO - Deploy no Google Cloud

## 📋 **PRÉ-REQUISITOS**

1. ✅ Conta Google Cloud criada
2. ✅ Billing ativado (cartão de crédito)
3. ✅ Cloud Shell Editor aberto (ou gcloud CLI instalado)

---

## **PASSO 1: Preparar Ambiente** ⏱️ 5 minutos

### 1.1 Autenticar no Google Cloud

No **Cloud Shell Editor** (terminal na parte inferior):

```bash
# Autenticar
gcloud auth login

# Isso abrirá o navegador para você fazer login
```

### 1.2 Criar Projeto

```bash
# Criar projeto (se ainda não criou)
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural"

# Definir como projeto ativo
gcloud config set project monpec-sistema-rural

# Verificar
gcloud config list
```

### 1.3 Habilitar Billing

**Via Console Web:**
1. Acesse: https://console.cloud.google.com/billing
2. Vincule uma conta de faturamento ao projeto `monpec-sistema-rural`

---

## **PASSO 2: Habilitar APIs Necessárias** ⏱️ 2 minutos

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    containerregistry.googleapis.com
```

**Aguarde alguns segundos** para as APIs serem habilitadas.

---

## **PASSO 3: Criar Banco de Dados Cloud SQL** ⏱️ 10 minutos

### 3.1 Criar Instância PostgreSQL

```bash
gcloud sql instances create monpec-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=Monpec2025!
```

**⏳ Aguarde 5-10 minutos** - A criação da instância leva tempo.

### 3.2 Criar Banco de Dados

```bash
# Criar banco de dados
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user \
    --instance=monpec-db \
    --password=Monpec2025!
```

### 3.3 Obter Connection Name

```bash
# Obter connection name (IMPORTANTE - anote isso!)
gcloud sql instances describe monpec-db --format="value(connectionName)"

# Exemplo de saída: monpec-sistema-rural:us-central1:monpec-db
# ⚠️ ANOTE ESSE VALOR - você vai precisar dele!
```

---

## **PASSO 4: Preparar Código** ⏱️ 5 minutos

### 4.1 Upload do Código

**Opção A: Via Cloud Shell Editor (Recomendado)**
1. No Cloud Shell Editor, clique no ícone de **pasta** (File Explorer)
2. Clique com botão direito na pasta raiz
3. Selecione **"Upload Files"** ou **"Upload Folder"**
4. Faça upload da pasta `Monpec_projetista` completa

**Opção B: Via Git (Se tiver repositório)**
```bash
git clone SEU_REPOSITORIO_URL
cd Monpec_projetista
```

**Opção C: Via gcloud (do seu PC)**
```bash
# No seu PC, instalar gcloud CLI e fazer upload
gcloud compute scp --recurse ./Monpec_projetista cloud-shell:~/Monpec_projetista
```

### 4.2 Navegar até a Pasta

```bash
cd Monpec_projetista
ls -la  # Verificar se os arquivos estão lá
```

---

## **PASSO 5: Build da Imagem Docker** ⏱️ 10-15 minutos

### 5.1 Verificar Arquivos

```bash
# Verificar se Dockerfile existe
ls -la Dockerfile

# Verificar se requirements_producao.txt existe
ls -la requirements_producao.txt
```

### 5.2 Fazer Build

```bash
# Build da imagem Docker
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# ⏳ Isso pode levar 10-15 minutos na primeira vez
```

**O que está acontecendo:**
- Cloud Build está criando a imagem Docker
- Instalando todas as dependências
- Coletando arquivos estáticos
- Criando a imagem final

---

## **PASSO 6: Deploy no Cloud Run** ⏱️ 5 minutos

### 6.1 Preparar Variáveis

```bash
# Definir variáveis (substitua CONNECTION_NAME pelo valor que você anotou)
CONNECTION_NAME="monpec-sistema-rural:us-central1:monpec-db"

# Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# Verificar
echo "Connection: $CONNECTION_NAME"
echo "Secret Key: $SECRET_KEY"
```

### 6.2 Fazer Deploy

```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

**⏳ Aguarde 2-3 minutos** para o deploy completar.

### 6.3 Obter URL do Serviço

```bash
# Obter URL
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')
echo "🌐 Seu site está em: $SERVICE_URL"

# Extrair host (sem https://)
CLOUD_RUN_HOST=$(echo $SERVICE_URL | sed 's|https://||')
echo "Host: $CLOUD_RUN_HOST"
```

### 6.4 Atualizar CLOUD_RUN_HOST

```bash
# Atualizar variável de ambiente com o host correto
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars CLOUD_RUN_HOST=$CLOUD_RUN_HOST
```

---

## **PASSO 7: Executar Migrações** ⏱️ 5 minutos

### 7.1 Criar Job de Migração

```bash
# Criar job para executar migrações
gcloud run jobs create migrate-db \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --command python \
    --args manage.py,migrate \
    --max-retries=1 \
    --memory=512Mi \
    --cpu=1
```

### 7.2 Executar Job

```bash
# Executar o job
gcloud run jobs execute migrate-db --region us-central1

# Ver logs
gcloud run jobs executions describe migrate-db-XXXXX --region us-central1
```

---

## **PASSO 8: Criar Superusuário (Opcional)** ⏱️ 2 minutos

```bash
# Criar job para criar superusuário
gcloud run jobs create createsuperuser \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD=Monpec2025!,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --command python \
    --args manage.py,createsuperuser \
    --max-retries=1 \
    --memory=512Mi \
    --cpu=1

# Executar (será interativo - não funciona bem em jobs)
# Melhor criar superusuário via shell local conectando ao banco
```

**Alternativa: Criar superusuário via Python script:**

```bash
# Criar script temporário
cat > create_superuser.py << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com.br', 'Monpec2025!')
    print('Superusuário criado!')
else:
    print('Superusuário já existe!')
EOF

# Executar via job (ajustar conforme necessário)
```

---

## **PASSO 9: Testar o Site** ⏱️ 2 minutos

### 9.1 Acessar URL

```bash
# Obter URL
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Abrir no navegador
# A URL será algo como: https://monpec-xxxxx-uc.a.run.app
```

### 9.2 Verificar Logs

```bash
# Ver logs em tempo real
gcloud run services logs tail monpec --region us-central1

# Ver últimas 50 linhas
gcloud run services logs read monpec --region us-central1 --limit 50
```

---

## **PASSO 10: Configurar Domínio (Opcional)** ⏱️ 10 minutos

### 10.1 Mapear Domínio

```bash
# Mapear monpec.com.br
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

### 10.2 Configurar DNS

**No seu provedor de domínio (Registro.br, GoDaddy, etc.):**

1. Adicionar registro **CNAME**:
   - **Nome**: `@` (ou `monpec.com.br`)
   - **Valor**: `ghs.googlehosted.com`
   - **TTL**: 3600

2. Para www:
   - **Nome**: `www`
   - **Valor**: `ghs.googlehosted.com`
   - **TTL**: 3600

3. **Aguardar propagação** (pode levar até 48h, geralmente 1-2h)

---

## ✅ **VERIFICAÇÃO FINAL**

### Checklist:

- [ ] Site acessível via URL do Cloud Run
- [ ] Migrações executadas com sucesso
- [ ] Logs sem erros críticos
- [ ] Arquivos estáticos carregando (CSS, JS, imagens)
- [ ] Banco de dados conectado
- [ ] Superusuário criado (se necessário)
- [ ] Domínio configurado (se aplicável)

---

## 🆘 **RESOLUÇÃO DE PROBLEMAS**

### Erro: "502 Bad Gateway"
```bash
# Ver logs detalhados
gcloud run services logs read monpec --region us-central1 --limit 100

# Verificar se migrações foram executadas
gcloud run jobs executions list --job=migrate-db --region us-central1
```

### Erro: "Database connection failed"
```bash
# Verificar connection name
echo $CONNECTION_NAME

# Verificar se instância está rodando
gcloud sql instances describe monpec-db
```

### Erro: "Static files not found"
```bash
# Verificar se collectstatic foi executado no build
# Ver logs do build
gcloud builds list --limit=1
gcloud builds log BUILD_ID
```

### Erro: "DisallowedHost"
```bash
# Atualizar CLOUD_RUN_HOST
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars CLOUD_RUN_HOST=SEU_HOST_AQUI
```

---

## 📊 **MONITORAMENTO**

### Ver Status do Serviço
```bash
gcloud run services describe monpec --region us-central1
```

### Ver Métricas
```bash
# Acesse: https://console.cloud.google.com/run
# Selecione o serviço "monpec"
# Veja métricas de requisições, latência, erros, etc.
```

---

## 💰 **CUSTOS**

- **Cloud Run**: ~R$ 0,40 por milhão de requisições + R$ 0,10/GB-hora
- **Cloud SQL (db-f1-micro)**: ~R$ 30/mês
- **Cloud Build**: Primeiros 120 minutos/dia grátis
- **Total estimado**: R$ 30-50/mês para tráfego baixo/médio

---

## 🎉 **PRONTO!**

Seu site está no ar! Acesse a URL do Cloud Run e comece a usar.

**Próximos passos:**
1. Migrar dados do servidor antigo (se houver)
2. Configurar backup automático do banco
3. Configurar alertas de monitoramento
4. Configurar CI/CD para deploy automático

---

**📚 Documentação Adicional:**
- `VERIFICACAO_PRE_DEPLOY.md` - Checklist de verificação
- `COMANDOS_RAPIDOS_GOOGLE_CLOUD.md` - Referência rápida
- `GUIA_DEPLOY_GOOGLE_CLOUD_PASSO_A_PASSO.md` - Guia completo






