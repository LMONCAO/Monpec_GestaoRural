# 🚀 Deploy Completo - Seu Caso Específico

Guia personalizado com comandos exatos para seu projeto.

---

## 📋 Suas Informações

- **Google Cloud Project:** `monpec-sistema-rural`
- **Repositório GitHub:** `https://github.com/LMONCAO/Monpec_GestaoRural`
- **Pasta Local:** `C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural`

---

## 🔄 Passo 1: Sincronizar Local → GitHub

**No seu computador (PowerShell):**

```powershell
# 1. Entrar na pasta do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# 2. Verificar status
git status

# 3. Adicionar arquivos corrigidos
git add requirements_producao.txt Dockerfile

# 4. Adicionar novos arquivos de documentação (se quiser)
git add CONFIGURAR_DOMINIO_MONPEC_COM_BR.md
git add CONFIGURAR_VERIFICACAO_GOOGLE_SEARCH_CONSOLE.md
git add deploy_cloud_shell.sh
# ... outros arquivos novos

# 5. Fazer commit
git commit -m "Corrigir: remover django-logging, adicionar documentação de deploy e verificação Google Search Console"

# 6. Fazer push para GitHub
git push origin master
# ou: git push origin main (depende da sua branch)
```

---

## 🚀 Passo 2: Clonar no Cloud Shell

**No Google Cloud Shell:**

```bash
# 1. Clonar repositório
git clone https://github.com/LMONCAO/Monpec_GestaoRural.git

# 2. Entrar na pasta
cd Monpec_GestaoRural

# 3. Verificar se os arquivos corrigidos estão lá
grep -n "django-logging" requirements_producao.txt || echo "✅ Correto: django-logging não encontrado"

# 4. Verificar Dockerfile
grep -n "gunicorn" Dockerfile
```

---

## 🔧 Passo 3: Configurar e Fazer Deploy

**No Google Cloud Shell:**

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Habilitar APIs (se ainda não habilitou)
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
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)" 2>/dev/null || echo "")
if [ -z "$CONNECTION_NAME" ]; then
    echo "⚠️  Instância de banco não encontrada. Continuando sem banco..."
    USE_DB=false
else
    echo "✅ Connection Name: $CONNECTION_NAME"
    USE_DB=true
fi

# 5. Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "✅ SECRET_KEY gerada"

# 6. Build da imagem (10-15 minutos)
echo "🔨 Fazendo build da imagem Docker..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 7. Deploy no Cloud Run (2-3 minutos)
echo "🚀 Fazendo deploy no Cloud Run..."
if [ "$USE_DB" = true ]; then
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
else
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars \
            DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
            DEBUG=False,\
            SECRET_KEY=$SECRET_KEY \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
fi

# 8. Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo ""
echo "========================================"
echo "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "🌐 URL do serviço:"
echo "   $SERVICE_URL"
echo ""
echo "📋 Próximos passos:"
echo "   1. Teste: $SERVICE_URL"
echo "   2. Verifique meta tag: $SERVICE_URL (Ctrl+U para ver código-fonte)"
echo "   3. Teste arquivo HTML: $SERVICE_URL/google40933139f3b0d469.html"
echo "   4. Verifique no Google Search Console usando esta URL"
echo ""
```

---

## ✅ Passo 4: Verificar Deploy

**No navegador:**

1. Acesse a URL retornada (ex: `https://monpec-xxxxx-uc.a.run.app`)
2. Veja o código-fonte (Ctrl+U)
3. Procure por: `google-site-verification`
4. Deve aparecer: `<meta name="google-site-verification" content="vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk" />`

---

## 🔄 Passo 5: Sincronizar Mudanças do Cloud Shell → GitHub (Opcional)

**Se você fizer mudanças no Cloud Shell:**

```bash
# No Cloud Shell
cd Monpec_GestaoRural

# Configurar Git (primeira vez)
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"

# Fazer mudanças
nano arquivo.py

# Commit e push
git add arquivo.py
git commit -m "Descrição da mudança"
git push origin master
```

**Depois, no seu computador local:**

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
git pull origin master
```

---

## 🌐 Passo 6: Configurar Domínio (Depois do Deploy)

**No Cloud Shell:**

```bash
# Criar mapeamento de domínio
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

**No Registro.br:**
- Campo "Endereço do site": `ghs.googlehosted.com`
- Tipo: Nome Alternativo (CNAME)

---

## 📝 Comandos Rápidos de Referência

### **No Computador Local:**
```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
git status
git add .
git commit -m "Mensagem"
git push origin master
git pull origin master
```

### **No Cloud Shell:**
```bash
cd Monpec_GestaoRural
git pull origin master
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1
```

---

## ✅ Checklist Completo

- [ ] Fazer commit e push no computador local
- [ ] Clonar repositório no Cloud Shell
- [ ] Verificar arquivos corrigidos
- [ ] Executar deploy
- [ ] Verificar URL do serviço
- [ ] Testar meta tag no código-fonte
- [ ] Testar arquivo HTML de verificação
- [ ] Verificar no Google Search Console
- [ ] Configurar domínio (quando DNS propagar)

---

**Última atualização:** Dezembro 2025

