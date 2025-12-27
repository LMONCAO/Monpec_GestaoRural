# ⚡ INÍCIO RÁPIDO - Cloud Shell Aberto

## 🎯 Você já está no Cloud Shell!

Perfeito! Agora siga estes passos:

---

## 📋 PASSO 1: Fazer Upload dos Arquivos

### Opção A: Upload Manual (Mais Fácil)

1. No Cloud Shell Editor (parte superior), clique no ícone de **pasta** (Explorer) no menu lateral esquerdo
2. Clique com botão direito na área de arquivos
3. Selecione **"Upload..."**
4. Selecione todos os arquivos do projeto ou crie um ZIP primeiro
5. Aguarde o upload terminar

### Opção B: Usar Git (Se o projeto estiver no Git)

```bash
git clone SEU_REPOSITORIO_URL
cd Monpec_GestaoRural
```

---

## 📋 PASSO 2: Verificar Arquivos

No terminal do Cloud Shell (parte inferior), execute:

```bash
ls -la manage.py Dockerfile.prod requirements.txt
```

**Todos devem aparecer!** Se algum estiver faltando, faça upload novamente.

---

## 📋 PASSO 3: Executar Deploy

Você tem 2 opções:

### Opção A: Script Automático (Recomendado)

```bash
# Dar permissão de execução
chmod +x EXECUTAR_AGORA_CLOUD_SHELL.sh

# Executar
./EXECUTAR_AGORA_CLOUD_SHELL.sh
```

### Opção B: Comandos Manuais

Abra o arquivo `COMANDOS_COPIAR_COLAR.txt` e copie cada comando, um de cada vez.

---

## 🚀 COMANDOS RÁPIDOS (Copy & Paste)

### 1. Configurar projeto
```bash
gcloud config set project monpec-sistema-rural
```

### 2. Build
```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
```
⏱️ **Aguarde 5-10 minutos**

### 3. Deploy
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
⏱️ **Aguarde 2-3 minutos**

### 4. Obter URL
```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

### 5. Migrações
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

---

## ✅ PRONTO!

Após executar todos os comandos, seu sistema estará no ar!

**URL será mostrada após o deploy.**

---

## 🆘 PRECISA DE AJUDA?

- Veja `PASSO_A_PASSO_DEPLOY.md` para instruções detalhadas
- Veja `COMANDOS_COPIAR_COLAR.txt` para todos os comandos
- Verifique logs: `gcloud run services logs read monpec --region us-central1`









