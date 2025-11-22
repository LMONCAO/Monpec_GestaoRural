# 🚀 GUIA COMPLETO - Publicar Site no Google Cloud

## 📋 Pré-requisitos

Você já tem:
- ✅ Conta no GitHub
- ✅ Google Cloud Platform
- ✅ Domínio: monpec.com.br

## 🎯 Passo a Passo Completo

### **PASSO 1: Preparar o Projeto no GitHub** (5 minutos)

1. **Fazer commit e push do código para o GitHub:**
   ```powershell
   # No PowerShell, na pasta do projeto
   git add .
   git commit -m "Preparar para deploy no Google Cloud"
   git push origin main
   ```

### **PASSO 2: Configurar o Google Cloud** (10 minutos)

1. **Acesse o Console do Google Cloud:**
   - Vá para: https://console.cloud.google.com
   - Faça login com sua conta Google

2. **Criar um Projeto:**
   - Clique em "Selecionar projeto" → "NOVO PROJETO"
   - Nome: `monpec-sistema-rural`
   - Clique em "CRIAR"

3. **Habilitar Faturamento:**
   - Vá em "Faturamento" no menu lateral
   - Vincule uma conta de faturamento (cartão de crédito)
   - ⚠️ **IMPORTANTE:** O Google Cloud oferece $300 de crédito grátis por 90 dias

4. **Habilitar APIs Necessárias:**
   - Vá em "APIs e Serviços" → "Biblioteca"
   - Habilite estas APIs:
     - Cloud Run API
     - Cloud SQL API
     - Cloud Build API
     - Container Registry API

### **PASSO 3: Instalar Google Cloud SDK** (10 minutos)

**No Windows (PowerShell como Administrador):**

```powershell
# Baixar e instalar Google Cloud SDK
# Acesse: https://cloud.google.com/sdk/docs/install
# Ou use Chocolatey:
choco install gcloudsdk

# Ou baixe manualmente de:
# https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
```

**Após instalar, autenticar:**
```powershell
gcloud auth login
gcloud config set project monpec-sistema-rural
```

### **PASSO 4: Criar Banco de Dados PostgreSQL** (15 minutos)

```powershell
# Criar instância do banco de dados
gcloud sql instances create monpec-db `
    --database-version=POSTGRES_14 `
    --tier=db-f1-micro `
    --region=us-central1 `
    --root-password=Monpec2025!

# Aguardar criação (pode levar 5-10 minutos)
# Verificar status:
gcloud sql instances describe monpec-db

# Criar banco de dados
gcloud sql databases create monpec_db --instance=monpec-db

# Criar usuário
gcloud sql users create monpec_user `
    --instance=monpec-db `
    --password=Monpec2025!
```

### **PASSO 5: Fazer Deploy da Aplicação** (20 minutos)

**Opção A: Usando Cloud Run (Recomendado)**

```powershell
# 1. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# 2. Obter connection name do banco
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)"
Write-Host "Connection Name: $CONNECTION_NAME"

# 3. Build da imagem Docker
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# 4. Deploy no Cloud Run
gcloud run deploy monpec `
    --image gcr.io/monpec-sistema-rural/monpec `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars `
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
        DEBUG=False,`
        DB_NAME=monpec_db,`
        DB_USER=monpec_user,`
        DB_PASSWORD=Monpec2025!,`
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME `
    --memory=512Mi `
    --cpu=1 `
    --timeout=300 `
    --max-instances=10

# 5. Obter URL do site
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

**Opção B: Usando App Engine (Alternativa)**

```powershell
# Deploy direto
gcloud app deploy app.yaml

# Abrir no navegador
gcloud app browse
```

### **PASSO 6: Executar Migrações do Banco de Dados** (5 minutos)

```powershell
# Conectar ao Cloud Run e executar migrações
# Primeiro, obter o nome do serviço
$SERVICE_URL = gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

# Executar migrações via Cloud Run Jobs ou Cloud Shell
# Opção 1: Via Cloud Shell
gcloud sql connect monpec-db --user=monpec_user --database=monpec_db

# Opção 2: Criar um job temporário para migrações
gcloud run jobs create migrate `
    --image gcr.io/monpec-sistema-rural/monpec `
    --region us-central1 `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars `
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
        DB_NAME=monpec_db,`
        DB_USER=monpec_user,`
        DB_PASSWORD=Monpec2025!,`
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME `
    --command python `
    --args manage.py,migrate

# Executar o job
gcloud run jobs execute migrate --region us-central1

# Criar superusuário
gcloud run jobs create createsuperuser `
    --image gcr.io/monpec-sistema-rural/monpec `
    --region us-central1 `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars `
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
        DB_NAME=monpec_db,`
        DB_USER=monpec_user,`
        DB_PASSWORD=Monpec2025!,`
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME `
    --command python `
    --args manage.py,createsuperuser

# Executar (será interativo - você precisará inserir dados do admin)
gcloud run jobs execute createsuperuser --region us-central1
```

### **PASSO 7: Configurar Domínio Customizado** (10 minutos)

1. **No Console do Google Cloud:**
   - Vá em "Cloud Run" → Selecione o serviço `monpec`
   - Clique em "GERENCIAR DOMÍNIOS CUSTOMIZADOS"
   - Clique em "ADICIONAR Mapeamento de Domínio"
   - Digite: `monpec.com.br`
   - Clique em "CONTINUAR"

2. **Configurar DNS no seu provedor de domínio:**
   - O Google Cloud fornecerá registros DNS para adicionar
   - Exemplo de registros:
     ```
     Tipo: A
     Nome: @
     Valor: [IP fornecido pelo Google]
     
     Tipo: CNAME
     Nome: www
     Valor: [valor fornecido pelo Google]
     ```
   - Adicione esses registros no painel do seu provedor de domínio
   - Aguarde propagação (pode levar até 48 horas, geralmente 1-2 horas)

3. **Verificar configuração:**
   ```powershell
   gcloud run domain-mappings describe monpec.com.br --region us-central1
   ```

### **PASSO 8: Configurar SSL/HTTPS** (Automático)

O Google Cloud Run configura SSL automaticamente quando você mapeia um domínio customizado. Não é necessário fazer nada adicional!

### **PASSO 9: Verificar se Está Funcionando** (5 minutos)

1. Acesse: `https://monpec.com.br`
2. Verifique se o site carrega corretamente
3. Teste o login com o superusuário criado

## 🔧 Comandos Úteis para Manutenção

### **Ver logs do serviço:**
```powershell
gcloud run services logs read monpec --region us-central1
```

### **Atualizar o serviço após mudanças no código:**
```powershell
# 1. Fazer commit e push no GitHub
git add .
git commit -m "Atualização"
git push

# 2. Rebuild e redeploy
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1
```

### **Conectar ao banco de dados:**
```powershell
gcloud sql connect monpec-db --user=monpec_user --database=monpec_db
```

### **Fazer backup do banco:**
```powershell
gcloud sql export sql monpec-db gs://[SEU-BUCKET]/backup-$(Get-Date -Format "yyyyMMdd").sql --database=monpec_db
```

## ⚠️ Troubleshooting

### **Erro 502 Bad Gateway:**
- Verifique os logs: `gcloud run services logs read monpec --region us-central1`
- Verifique se as migrações foram executadas
- Verifique se o banco de dados está acessível

### **Erro de conexão com banco:**
- Verifique se o Cloud SQL está rodando
- Verifique se o connection name está correto
- Verifique as variáveis de ambiente

### **Domínio não funciona:**
- Aguarde a propagação DNS (pode levar até 48 horas)
- Verifique os registros DNS no seu provedor
- Use: https://dnschecker.org para verificar propagação

## 💰 Custos Estimados

- **Cloud Run:** ~$0-10/mês (dependendo do tráfego)
- **Cloud SQL (db-f1-micro):** ~$7-10/mês
- **Cloud Build:** Gratuito até 120 minutos/dia
- **Total estimado:** ~$10-20/mês para começar

## 📞 Próximos Passos

1. ✅ Site publicado e funcionando
2. ⬜ Configurar backup automático do banco
3. ⬜ Configurar monitoramento e alertas
4. ⬜ Otimizar performance
5. ⬜ Configurar CI/CD automático com GitHub Actions

## 🎉 Pronto!

Seu site estará acessível em `https://monpec.com.br` após completar todos os passos!


