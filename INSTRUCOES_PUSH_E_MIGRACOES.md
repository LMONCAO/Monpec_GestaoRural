# 📋 Instruções: Push para GitHub e Criar Admin/Migrações

## 🚀 Passo 1: Fazer Push para GitHub

### Opção A: Usar o Script Automático (Recomendado)
Execute o arquivo `FAZER_PUSH_GITHUB.bat` que criamos:
```cmd
FAZER_PUSH_GITHUB.bat
```

### Opção B: Fazer Manualmente
Execute estes comandos no terminal na pasta do projeto:

```bash
# Adicionar arquivos
git add .github/workflows/deploy-google-cloud.yml
git add GUIA_SINCRONIZAR_GITHUB_GCLOUD.md
git add RESUMO_SINCRONIZACAO_GITHUB.md
git add executar_migracoes_e_criar_admin.sh
git add executar_migracoes_e_criar_admin_cloud_run.sh
git add EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat

# Commit
git commit -m "Adicionar integração GitHub Actions com Google Cloud e scripts para migrações/admin"

# Push
git push origin master
```

---

## 🗄️ Passo 2: Executar Migrações e Criar Admin no Google Cloud

Após fazer o push, você precisa executar as migrações e criar o usuário admin no banco de dados do Google Cloud.

### Opção A: Usar o Script .bat (Windows)
Execute o arquivo:
```cmd
EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat
```

Este script vai:
1. Criar/atualizar um Cloud Run Job
2. Executar as migrações do Django
3. Criar o usuário admin

### Opção B: Usar o Script .sh (Linux/Mac/Cloud Shell)
Execute o arquivo:
```bash
chmod +x executar_migracoes_e_criar_admin_cloud_run.sh
./executar_migracoes_e_criar_admin_cloud_run.sh
```

### Opção C: Executar Manualmente no Cloud Shell

1. Abra o Google Cloud Shell
2. Execute estes comandos:

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Criar o job
gcloud run jobs create migrate-and-create-admin \
    --image=gcr.io/monpec-sistema-rural/monpec:latest \
    --region=us-central1 \
    --platform=managed \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DJANGO_SUPERUSER_PASSWORD=L6171r12@@,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=1800 \
    --task-timeout=1800 \
    --max-retries=1 \
    --command=sh \
    --args=-c,"python manage.py migrate --noinput && python manage.py garantir_admin --senha $DJANGO_SUPERUSER_PASSWORD && echo '✅ Migrações e admin criado com sucesso!'"

# Executar o job
gcloud run jobs execute migrate-and-create-admin \
    --region=us-central1 \
    --wait
```

---

## ✅ Credenciais do Admin

Após executar as migrações, o usuário admin será criado com:

- **Username:** `admin`
- **Senha:** `L6171r12@@`
- **Email:** `admin@monpec.com.br`

---

## 🔍 Verificar se Funcionou

### Verificar Logs do Job:
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-and-create-admin" --limit=50
```

### Verificar Tabelas no Banco:
```bash
gcloud sql connect monpec-db --user=monpec_user --database=monpec_db
```

Depois de conectar, execute no PostgreSQL:
```sql
\dt
```

Isso vai listar todas as tabelas criadas pelas migrações.

---

## ⚠️ Problemas Comuns

### Erro: "Job não encontrado"
- Execute o script novamente - ele cria o job se não existir

### Erro: "Imagem não encontrada"
- Certifique-se de que já fez deploy da imagem Docker antes
- Execute: `DEPLOY_GARANTIR_VERSAO_CORRETA.bat` primeiro

### Erro: "Conexão com banco falhou"
- Verifique se o Cloud SQL está rodando
- Verifique se as credenciais estão corretas
- Verifique se o IP está autorizado (se necessário)

### Erro: "Migrações já aplicadas"
- Isso é normal se você já executou as migrações antes
- O script continua e cria o admin mesmo assim

---

## 📝 Próximos Passos

Após executar as migrações e criar o admin:

1. ✅ Acesse a URL do seu sistema Cloud Run
2. ✅ Faça login com as credenciais do admin
3. ✅ Verifique se tudo está funcionando corretamente
4. ✅ Configure a integração GitHub Actions (se ainda não fez)

Para mais informações sobre a integração GitHub Actions, consulte:
- `GUIA_SINCRONIZAR_GITHUB_GCLOUD.md` - Guia completo
- `RESUMO_SINCRONIZACAO_GITHUB.md` - Resumo rápido

---

**✅ Pronto! Agora você tem:**
- ✅ Arquivos prontos para push no GitHub
- ✅ Scripts para executar migrações e criar admin
- ✅ Integração CI/CD configurada

