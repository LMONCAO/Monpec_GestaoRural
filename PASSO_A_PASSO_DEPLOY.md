# 📋 PASSO A PASSO - Deploy no Google Cloud

## 🎯 Objetivo
Fazer o deploy do sistema MONPEC no Google Cloud Run para que funcione em `monpec.com.br`

---

## ✅ PRÉ-REQUISITOS (Já verificados - tudo OK!)

- ✅ gcloud CLI instalado
- ✅ Autenticado: l.moncaosilva@gmail.com
- ✅ Projeto configurado: monpec-sistema-rural
- ✅ APIs habilitadas
- ✅ Cloud SQL configurado: monpec-db

---

## 🚀 PASSO A PASSO COMPLETO

### **PASSO 1: Abrir Cloud Shell**

1. Acesse: https://console.cloud.google.com/cloudshell
2. Ou no console do Google Cloud: Menu ☰ (três linhas) → Cloud Shell
3. Aguarde o terminal abrir (pode levar alguns segundos)

---

### **PASSO 2: Preparar Ambiente no Cloud Shell**

No terminal do Cloud Shell, execute:

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Verificar se está correto
gcloud config get-value project
```

**Resultado esperado:** `monpec-sistema-rural`

---

### **PASSO 3: Fazer Upload do Projeto**

Você tem 3 opções:

#### **Opção A: Usar Git (se o projeto estiver no Git)**

```bash
# Clone o repositório
git clone SEU_REPOSITORIO_URL
cd Monpec_GestaoRural
```

#### **Opção B: Upload Manual (mais fácil)**

1. No Cloud Shell, clique no ícone de **⚙️ Configurações** (três pontos no canto superior direito)
2. Clique em **"Fazer upload de arquivo"**
3. Selecione todos os arquivos do projeto (ou crie um ZIP primeiro)
4. Aguarde o upload terminar

#### **Opção C: Usar gcloud storage (se tiver muitos arquivos)**

```bash
# Criar bucket temporário
gsutil mb gs://monpec-temp-upload

# Fazer upload (do seu computador local)
# gsutil -m cp -r . gs://monpec-temp-upload/

# Baixar no Cloud Shell
# gsutil -m cp -r gs://monpec-temp-upload/* .
```

---

### **PASSO 4: Verificar Arquivos Essenciais**

No Cloud Shell, verifique se os arquivos existem:

```bash
# Verificar se está no diretório correto
pwd

# Listar arquivos importantes
ls -la Dockerfile.prod
ls -la requirements.txt
ls -la manage.py
ls -la sistema_rural/settings_gcp.py
```

**Todos devem existir!** Se algum estiver faltando, faça upload novamente.

---

### **PASSO 5: Fazer Build da Imagem Docker**

```bash
# Build da imagem (pode levar 5-10 minutos)
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
```

**O que está acontecendo:**
- Google Cloud está criando uma imagem Docker com seu código
- Instalando todas as dependências do `requirements.txt`
- Preparando tudo para rodar no Cloud Run

**Aguarde até ver:** `SUCCESS`

---

### **PASSO 6: Fazer Deploy no Cloud Run**

```bash
# Deploy completo
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

**O que está acontecendo:**
- Criando o serviço Cloud Run
- Configurando variáveis de ambiente
- Conectando ao Cloud SQL
- Configurando recursos (memória, CPU)

**Aguarde até ver:** `Service [monpec] revision [monpec-xxxxx] has been deployed`

**IMPORTANTE:** Anote a URL que aparecerá, algo como:
```
https://monpec-xxxxx-uc.a.run.app
```

---

### **PASSO 7: Aplicar Migrações do Banco de Dados**

```bash
# Criar job de migração
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600

# Executar o job
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

**Aguarde até ver:** `Job execution completed successfully`

---

### **PASSO 8: Obter URL do Serviço**

```bash
# Obter URL
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

**Copie a URL que aparecer!** Você vai precisar dela.

---

### **PASSO 9: Testar o Sistema**

1. Abra a URL no navegador (a que você copiou no passo anterior)
2. Você deve ver a página inicial do sistema
3. Teste fazer login

**Se aparecer erro:**
- Veja o passo 10 para verificar logs

---

### **PASSO 10: Verificar Logs (se houver problemas)**

```bash
# Ver últimos logs
gcloud run services logs read monpec --region us-central1 --limit=50
```

**Procure por erros** e anote para corrigir.

---

### **PASSO 11: Configurar Domínio Personalizado (monpec.com.br)**

```bash
# Criar mapeamento de domínio
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

**Isso vai retornar instruções de DNS.** Você precisará:

1. Acessar seu provedor de domínio (onde comprou monpec.com.br)
2. Adicionar um registro CNAME apontando para o endereço fornecido
3. Aguardar propagação DNS (pode levar até 24 horas, geralmente 1-2 horas)

---

## 📝 RESUMO DOS COMANDOS (Copy & Paste)

Se quiser copiar tudo de uma vez, aqui estão os comandos principais:

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# 3. Deploy
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

# 4. Migrações
gcloud run jobs create migrate-monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600

gcloud run jobs execute migrate-monpec --region us-central1 --wait

# 5. Obter URL
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

---

## ⚠️ PROBLEMAS COMUNS E SOLUÇÕES

### Erro: "Permission denied"
```bash
# Verificar permissões
gcloud projects get-iam-policy monpec-sistema-rural
```

### Erro: "Image not found"
- Verifique se o build foi concluído com sucesso
- Execute o build novamente

### Erro: "Database connection failed"
```bash
# Verificar Cloud SQL
gcloud sql instances describe monpec-db
```

### Erro: "Build failed"
- Verifique se o `requirements.txt` está correto
- Verifique se o `Dockerfile.prod` existe
- Veja os logs: `gcloud builds list --limit=1`

---

## ✅ CHECKLIST FINAL

- [ ] Cloud Shell aberto
- [ ] Projeto configurado
- [ ] Arquivos do projeto no Cloud Shell
- [ ] Build concluído com sucesso
- [ ] Deploy concluído com sucesso
- [ ] Migrações aplicadas
- [ ] URL do serviço obtida
- [ ] Sistema testado no navegador
- [ ] Domínio configurado (opcional)

---

## 🎉 PRONTO!

Se seguiu todos os passos, seu sistema está no ar! 🚀

**URL do serviço:** (será mostrada após o deploy)

**Próximos passos:**
1. Testar todas as funcionalidades
2. Configurar domínio personalizado
3. Monitorar logs regularmente

---

**Dúvidas?** Consulte `GUIA_COMPLETO_GOOGLE_CLOUD.md` para mais detalhes.









