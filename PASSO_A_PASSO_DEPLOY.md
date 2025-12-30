# 🚀 Passo a Passo - Deploy no Google Cloud Run

## 📋 Resumo

Para fazer deploy no Google Cloud Run, você precisa de um arquivo chamado `Dockerfile` (o Google Cloud busca esse nome por padrão). Você tem `Dockerfile.prod`, então vamos criar uma cópia chamada `Dockerfile`.

---

## ✅ Passo 1: Entrar na Pasta do Projeto

No Cloud Shell, certifique-se de estar na pasta correta:

```bash
cd Monpec_GestaoRural
```

---

## ✅ Passo 2: Criar o Dockerfile

O Google Cloud Run precisa de um arquivo chamado `Dockerfile` (sem extensão). Você já tem `Dockerfile.prod`, então vamos criar uma cópia:

```bash
cp Dockerfile.prod Dockerfile
```

**Ou se preferir renomear:**

```bash
mv Dockerfile.prod Dockerfile
```

> ⚠️ **Nota**: Se você quiser manter ambos os arquivos, use `cp`. Se quiser renomear completamente, use `mv`.

---

## ✅ Passo 3: Deploy no Cloud Run

Agora execute o deploy. O comando `--source .` faz tudo automaticamente (build + deploy):

```bash
gcloud run deploy monpec \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10
```

**O que vai acontecer:**

1. ✅ O Cloud Run detecta o `Dockerfile` automaticamente
2. ✅ Faz o build da imagem Docker (5-10 minutos)
3. ✅ Faz o deploy no Cloud Run (2-5 minutos)
4. ✅ Configura as variáveis de ambiente
5. ✅ Conecta ao banco de dados Cloud SQL

**Quando perguntado:**

- **Permitir chamadas não autenticadas?** → Digite `y` (sim) para tornar público
- **Região:** → Pressione Enter para usar `us-central1` ou escolha outra

---

## ✅ Passo 4: Verificar o Deploy

Após o deploy concluir, obtenha a URL:

```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

Você verá uma URL como:
```
https://monpec-XXXXX-uc.a.run.app
```

---

## 🎯 Comando Único (Tudo de Uma Vez)

Se quiser fazer tudo de uma vez, copie e cole este comando completo no Cloud Shell:

```bash
cd Monpec_GestaoRural && \
cp Dockerfile.prod Dockerfile && \
gcloud config set project monpec-sistema-rural && \
gcloud run deploy monpec \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10
```

---

## 🔍 Alternativa: Usar Dockerfile.prod Diretamente

Se preferir não criar uma cópia, você pode especificar o Dockerfile no comando:

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest --dockerfile Dockerfile.prod
```

E depois fazer o deploy:

```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10
```

> ⚠️ **Nota**: A opção `--source .` não permite especificar outro Dockerfile, então você precisaria fazer o build separado.

---

## 📊 Verificar Status e Logs

### Ver status do serviço:

```bash
gcloud run services describe monpec --region us-central1
```

### Ver logs:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=20
```

### Ver logs em tempo real:

```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec"
```

---

## ⚠️ Troubleshooting

### Erro: "Dockerfile not found"

Certifique-se de que criou o Dockerfile:

```bash
ls -la Dockerfile
```

Se não existir:

```bash
cp Dockerfile.prod Dockerfile
```

### Erro: "Permission denied"

Verifique autenticação:

```bash
gcloud auth list
```

Se não estiver autenticado:

```bash
gcloud auth login
```

### Erro: "Project not found"

Configure o projeto:

```bash
gcloud config set project monpec-sistema-rural
```

### Erro: "Cloud SQL instance not found"

Verifique se o banco existe:

```bash
gcloud sql instances list
```

---

## ✅ Pronto!

Após o deploy, seu sistema estará disponível na URL retornada. O sistema executará automaticamente:

1. ✅ Migrações do banco de dados
2. ✅ Criação do usuário admin (se não existir)
3. ✅ Coleta de arquivos estáticos
4. ✅ Inicialização do servidor Gunicorn

Aguarde 1-2 minutos após o deploy para que tudo inicialize completamente.
