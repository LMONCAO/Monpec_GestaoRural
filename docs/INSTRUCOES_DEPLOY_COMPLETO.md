# 🚀 INSTRUÇÕES COMPLETAS PARA DEPLOY

## ✅ TUDO PRONTO! Execute o deploy agora:

### 📋 OPÇÃO 1: Script Automático (Recomendado)

1. **Abra o PowerShell no diretório do projeto**
2. **Execute:**
   ```powershell
   .\EXECUTAR_DEPLOY_AGORA.ps1
   ```

O script fará tudo automaticamente:
- ✅ Configurar projeto
- ✅ Habilitar APIs
- ✅ Build da imagem Docker (5-10 min)
- ✅ Deploy no Cloud Run (2-5 min)

---

### 📋 OPÇÃO 2: Comandos Manuais

Execute estes comandos no PowerShell, um por vez:

```powershell
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com sqladmin.googleapis.com --quiet

# 3. Build da imagem (5-10 minutos)
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest .

# 4. Deploy no Cloud Run (2-5 minutos)
gcloud run deploy monpec `
    --image gcr.io/monpec-sistema-rural/monpec:latest `
    --region us-central1 `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="monpec-sistema-rural:us-central1:monpec-db" `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --min-instances=1 `
    --max-instances=10 `
    --port=8080
```

---

### 📋 OPÇÃO 3: Google Cloud Shell (Alternativa)

Se preferir usar o Cloud Shell:

1. Acesse: https://shell.cloud.google.com
2. Faça upload do código ou clone do Git
3. Execute os comandos do arquivo `COMANDOS_DEPLOY_CLOUD_SHELL.txt`

---

## ⚠️ IMPORTANTE - Após o Deploy

### 1. Aplicar Migrações no Cloud SQL

**IMPORTANTE:** Você precisa aplicar as 108 migrações no Cloud SQL!

Execute este comando para criar um job de migração:

```powershell
gcloud run jobs create migrate-job `
    --image gcr.io/monpec-sistema-rural/monpec:latest `
    --region us-central1 `
    --add-cloudsql-instances="monpec-sistema-rural:us-central1:monpec-db" `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
    --command="python" `
    --args="manage.py,migrate" `
    --memory=2Gi `
    --cpu=2

# Executar o job
gcloud run jobs execute migrate-job --region us-central1 --wait
```

### 2. Obter URL do Serviço

```powershell
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

### 3. Testar Sistema

- Acesse a URL do serviço
- Teste criação de usuário demo
- Teste sistema de assinaturas
- Acesse `/admin` para criar superusuário se necessário

### 4. Ver Logs

```powershell
gcloud run services logs read monpec --region us-central1 --limit=50
```

---

## ✅ Status Atual

- ✅ Google Cloud SDK instalado e configurado
- ✅ Projeto configurado: `monpec-sistema-rural`
- ✅ Conta autenticada: `l.moncaosilva@gmail.com`
- ✅ APIs habilitadas
- ✅ Dockerfile.prod pronto
- ✅ Configurações de produção prontas
- ✅ 108 migrações prontas para aplicar

---

## 🚀 EXECUTE AGORA!

**Recomendação:** Use a **OPÇÃO 1** (script automático) - é a mais simples!

```powershell
.\EXECUTAR_DEPLOY_AGORA.ps1
```

**Tempo estimado total:** 7-15 minutos
- Build: 5-10 minutos
- Deploy: 2-5 minutos

**Boa sorte! 🎉**


