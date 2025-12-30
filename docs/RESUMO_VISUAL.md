# 🎯 RESUMO VISUAL - Deploy Rápido

## 📍 Onde Estamos

```
✅ Seu Computador (Windows)
   └─> Arquivos do projeto prontos
   └─> gcloud configurado
   └─> Tudo verificado

⏭️ PRÓXIMO PASSO

🌐 Google Cloud Shell (Navegador)
   └─> Fazer upload dos arquivos
   └─> Executar comandos de deploy
   └─> Sistema no ar!
```

---

## 🚀 3 PASSOS PRINCIPAIS

### 1️⃣ **Abrir Cloud Shell**
```
https://console.cloud.google.com/cloudshell
```

### 2️⃣ **Fazer Upload e Build**
```bash
# No Cloud Shell:
gcloud config set project monpec-sistema-rural
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
```

### 3️⃣ **Fazer Deploy**
```bash
# No Cloud Shell:
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
```

---

## 📋 COMANDOS COMPLETOS (Copiar e Colar)

### **Passo 1: Configurar**
```bash
gcloud config set project monpec-sistema-rural
```

### **Passo 2: Build**
```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
```
⏱️ **Tempo:** 5-10 minutos

### **Passo 3: Deploy**
```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
```
⏱️ **Tempo:** 2-3 minutos

### **Passo 4: Migrações**
```bash
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600

gcloud run jobs execute migrate-monpec --region us-central1 --wait
```
⏱️ **Tempo:** 1-2 minutos

### **Passo 5: Obter URL**
```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

---

## 🎯 FLUXO COMPLETO

```
1. Abrir Cloud Shell
   ↓
2. Upload dos arquivos
   ↓
3. Build (5-10 min)
   ↓
4. Deploy (2-3 min)
   ↓
5. Migrações (1-2 min)
   ↓
6. ✅ Sistema no ar!
```

---

## 📝 CHECKLIST

- [ ] Cloud Shell aberto
- [ ] Arquivos do projeto no Cloud Shell
- [ ] Build executado e concluído
- [ ] Deploy executado e concluído
- [ ] Migrações aplicadas
- [ ] URL obtida e testada

---

## ⚡ DICA RÁPIDA

**Abra o arquivo `PASSO_A_PASSO_DEPLOY.md`** para instruções detalhadas de cada passo!

---

## 🆘 PRECISA DE AJUDA?

1. Veja `PASSO_A_PASSO_DEPLOY.md` - Guia completo
2. Veja `GUIA_COMPLETO_GOOGLE_CLOUD.md` - Documentação técnica
3. Verifique logs: `gcloud run services logs read monpec --region us-central1`

---

**Tempo total estimado:** 10-15 minutos ⏱️
















