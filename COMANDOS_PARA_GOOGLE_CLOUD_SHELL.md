# 🚀 Comandos para Deploy Direto no Google Cloud Shell

## 📋 Como Usar

1. Abra o **Google Cloud Shell** (ícone `>_` no canto superior direito do console)
2. Faça upload dos arquivos do projeto para o Cloud Shell (ou clone do repositório)
3. Navegue até o diretório do projeto
4. **Configure o projeto e autenticação** (se necessário - veja abaixo)
5. Execute um dos comandos abaixo

### ⚠️ Primeiro Passo: Configuração do Projeto

**Se você receber erro "You do not currently have an active account selected":**

**No Cloud Shell você já está autenticado automaticamente!** Você só precisa configurar o projeto:

```bash
gcloud config set project monpec-sistema-rural
```

**Verifique se está tudo certo:**
```bash
gcloud config list
```

Você deve ver `project = monpec-sistema-rural` na lista.

Agora você pode executar os comandos abaixo!

---

## ⚡ Opção 1: Script Completo (Recomendado)

### Copie e cole este código no Cloud Shell:

```bash
#!/bin/bash
# Deploy direto no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
DJANGO_SUPERUSER_PASSWORD="L6171r12@@"

# Configurar projeto
gcloud config set project $PROJECT_ID

# Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build da imagem (sem cache)
IMAGE_NAME="gcr.io/$PROJECT_ID/sistema-rural"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="$IMAGE_NAME:v$TIMESTAMP"

echo "Fazendo build da imagem: $IMAGE_TAG"
gcloud builds submit --no-cache --tag $IMAGE_TAG --tag $IMAGE_NAME:latest .

# Deploy no Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:$DB_INSTANCE \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DB_INSTANCE,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --max-instances=10 \
    --min-instances=0

# Obter URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "✅ Deploy concluído!"
echo "🌐 URL: $SERVICE_URL"
```

---

## ⚡ Opção 2: Comandos Individuais

### 1. Configurar Projeto
```bash
gcloud config set project monpec-sistema-rural
```

### 2. Habilitar APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Build da Imagem (sem cache)
```bash
gcloud builds submit --no-cache \
    --tag gcr.io/monpec-sistema-rural/sistema-rural:latest \
    .
```

### 4. Deploy no Cloud Run
```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/sistema-rural:latest \
    --region=us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DJANGO_SUPERUSER_PASSWORD=L6171r12@@,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --max-instances=10 \
    --min-instances=0
```

### 5. Ver URL do Serviço
```bash
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
```

---

## 📦 Pré-requisitos

Antes de executar, certifique-se de que:

1. ✅ Você está no diretório correto (onde está o `Dockerfile.prod`)
2. ✅ Todos os arquivos do projeto estão no Cloud Shell
3. ✅ O arquivo `Dockerfile.prod` existe
4. ✅ O arquivo `requirements_producao.txt` existe
5. ✅ O arquivo `manage.py` existe

---

## 🔍 Verificar Arquivos

```bash
# Verificar se está no diretório correto
ls -la | grep -E "Dockerfile|manage.py|requirements"

# Ver conteúdo do diretório
ls -la
```

---

## 📊 Acompanhar o Deploy

### Ver Builds
```bash
gcloud builds list --limit=5
```

### Acompanhar Build em Tempo Real
```bash
gcloud builds log --stream
```

### Ver Logs do Serviço
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec"
```

### Ver Erros
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=50
```

---

## 🌐 Links do Google Cloud Console

Após executar o deploy, você pode acompanhar em:

- **Cloud Build:** https://console.cloud.google.com/cloud-build/builds?project=monpec-sistema-rural
- **Cloud Run:** https://console.cloud.google.com/run/detail/us-central1/monpec?project=monpec-sistema-rural
- **Logs:** https://console.cloud.google.com/logs/query?project=monpec-sistema-rural

---

## ⚠️ Troubleshooting

### Erro: "Dockerfile.prod não encontrado"
```bash
# Verificar diretório atual
pwd

# Listar arquivos
ls -la

# Navegar para o diretório correto
cd /caminho/para/projeto
```

### Erro: "Projeto não encontrado"
```bash
# Listar projetos disponíveis
gcloud projects list

# Configurar projeto correto
gcloud config set project monpec-sistema-rural
```

### Erro: "APIs não habilitadas"
```bash
# Habilitar todas as APIs necessárias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## ✅ Após o Deploy

1. Aguarde 1-2 minutos para o serviço inicializar
2. Acesse a URL mostrada no final do deploy
3. Teste o login com:
   - Usuário: `admin`
   - Senha: `L6171r12@@`

---

## 📝 Notas Importantes

- O build pode levar **15-25 minutos** (especialmente com `--no-cache`)
- O deploy pode levar **5-10 minutos**
- Aguarde alguns minutos após o deploy para o serviço inicializar completamente
- Use `--no-cache` para garantir que a versão mais recente seja deployada

---

## 📊 MIGRAR DADOS DO LOCALHOST PARA O CLOUD SQL

Após fazer o deploy, você pode migrar seus dados do banco local (SQLite) para o Cloud SQL (PostgreSQL).

### ⚡ Migração Rápida (Recomendado)

#### 1. No seu computador local, exporte os dados:

```bash
# Dentro da pasta do projeto local
python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
```

#### 2. Faça upload do arquivo `dados_backup.json` para o Cloud Shell

Use a interface de upload do Cloud Shell (ícone de upload na barra superior).

#### 3. No Cloud Shell, importe os dados:

```bash
cd ~/Monpec_GestaoRural

# Executar migrações primeiro (se ainda não foi feito)
python3 manage.py migrate

# Importar dados
python3 manage.py loaddata dados_backup.json

# Carregar categorias padrão
python3 manage.py carregar_categorias
```

### 📚 Documentação Completa

Para mais detalhes e outras opções de migração, consulte:
- **GUIA_MIGRACAO_DADOS_LOCAL_PARA_CLOUD_SQL.md** (guia completo com todas as opções)
- **INSTRUCOES_MIGRACAO_DADOS.md** (instruções do script de deploy)

---

## 🔧 EXECUTAR MIGRATIONS E COLECTSTATIC

**💡 IMPORTANTE:** O `Dockerfile.prod` já executa `migrate` e `collectstatic` automaticamente quando o container inicia! Se você fez deploy recentemente, os comandos já foram executados.

Se você precisa executar novamente, use uma das opções abaixo:

---

### ⚡ SOLUÇÃO DIRETA: gcloud builds submit (COM DIRETÓRIO CORRETO!)

**Agora que você está autenticado (`gcloud auth login`), este comando deve funcionar!**

**⚠️ IMPORTANTE:** Antes de executar, certifique-se de estar no diretório do projeto no Cloud Shell:
```bash
cd ~/Monpec_GestaoRural
# Ou navegue até o diretório onde está seu projeto
```

Execute este comando único que faz tudo (migrate + collectstatic + criar admin):

```bash
gcloud builds submit --config <(cat <<'EOF'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    cd /app && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
EOF
) .
```

**✅ A diferença:** Adicionei `cd /app &&` no início para garantir que estamos no diretório correto onde o `manage.py` está localizado no container.

**⚠️ IMPORTANTE:** Copie TODO o bloco acima (desde `gcloud builds submit` até `.`) e cole de uma vez no Cloud Shell.

**⏱️ Aguarde 3-5 minutos** até aparecer `STATUS: SUCCESS`.

**Depois, faça login com:**
- Usuário: `admin`
- Senha: `L6171r12@@`

---

### ⚡ SOLUÇÃO ALTERNATIVA: Forçar Reinicialização (Recomendado se o acima falhar)

Como o Dockerfile já executa os comandos na inicialização, a forma mais simples é forçar uma reinicialização:

**Use o script:**
```bash
bash FORCAR_REINICIALIZACAO.sh
```

**Ou execute manualmente:**
```bash
# Força uma nova revisão que executa migrate e collectstatic
gcloud run services update monpec --region us-central1 --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" --no-traffic
gcloud run services update-traffic monpec --region us-central1 --to-latest
```

### ⚡ SOLUÇÃO ALTERNATIVA: Redeploy Completo

Se a reinicialização não funcionar, faça um redeploy completo:

**Use o script:**
```bash
bash SOLUCAO_REDEPLOY_SIMPLES.sh
```

**Ou manualmente:**
```bash
# 1. Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/sistema-rural:latest .

# 2. Deploy (vai executar migrate e collectstatic automaticamente)
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/sistema-rural:latest --region us-central1
```

---

### 🚨 SE O USUÁRIO ADMIN NÃO FOI CRIADO

Se o job `create-admin` falhar, use este script alternativo:

```bash
bash CRIAR_ADMIN_COM_SCRIPT_PYTHON.sh
```

Ou execute este comando direto (cria admin usando comando Python inline):

```bash
gcloud run jobs create create-admin-inline \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp'); import django; django.setup(); from django.contrib.auth.models import User; u, c = User.objects.get_or_create(username='admin'); u.set_password('L6171r12@@'); u.is_superuser = True; u.is_staff = True; u.email = 'admin@example.com'; u.save(); print('Admin criado!' if c else 'Admin atualizado!')" \
  --memory=2Gi \
  --cpu=2

gcloud run jobs execute create-admin-inline --region=us-central1 --wait
```

---

### 🔧 SOLUÇÕES ALTERNATIVAS (Se o redeploy não for opção)

Se você não quiser fazer redeploy, pode tentar as opções abaixo. **NOTA:** Se você receber erros de autenticação no Cloud Shell, o redeploy acima é a solução recomendada.

### ⚠️ IMPORTANTE: Por que isso é necessário?

- **Formulário**: O erro "Erro ao processar solicitação" acontece porque o banco de dados tenta salvar dados em tabelas que ainda não existem. O `migrate` cria essas tabelas.
- **Slides**: Os slides dependem de arquivos JavaScript. O `collectstatic` organiza esses arquivos para que o navegador consiga carregá-los corretamente, fazendo as fotos voltarem a passar.

---

## ⚡ OPÇÃO 1: Comando Único (Tudo de Uma Vez)

Esta é a forma mais rápida - executa migrate, collectstatic e cria o admin em um único comando.

### 🎯 Método Mais Simples (Recomendado):

**💡 DICA:** Se você tem o arquivo `COMANDO_MIGRATE_COPIAR_COLAR.txt` no projeto, abra ele e siga as instruções - é mais fácil!

**⚠️ IMPORTANTE: Execute em DUAS etapas separadas para evitar quebras de linha!**

#### 📌 ETAPA 1: Criar o arquivo de configuração

Copie e cole este comando completo:

```bash
cat > /tmp/cloudbuild-migrate.yaml <<'YAML'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
YAML
```

**Aguarde o prompt `$` aparecer novamente** (indicando que a ETAPA 1 terminou).

#### 📌 ETAPA 2: Executar o build

Agora copie e cole este comando COMPLETO (certifique-se de copiar a linha inteira):

```bash
gcloud builds submit --config=/tmp/cloudbuild-migrate.yaml .
```

**💡 DICA:** O script `executar_migrate_simples.sh` já configura o projeto automaticamente!

**Aguarde** (leva 3-5 minutos)

---

### 🎯 MÉTODO MAIS FÁCIL: Usar Script Executável (RECOMENDADO)

**⭐ RECOMENDADO: Use o script `executar_migrate_FINAL.sh` (versão mais recente e corrigida):**

```bash
bash executar_migrate_FINAL.sh
```

**Ou use a versão anterior:**
```bash
bash executar_com_cloud_run_jobs.sh
```

**Este script:**
- ✅ Usa Cloud Run Jobs (mais confiável que gcloud builds submit)
- ✅ Tem acesso garantido ao Cloud SQL
- ✅ Não depende de autenticação explícita
- ✅ Configura tudo automaticamente
- ✅ Cria jobs reutilizáveis para o futuro

**Ou use o script com gcloud builds submit:**
```bash
bash SOLUCAO_COMPLETA_MIGRATE.sh
```

**✅ Este script:**
- Configura o projeto automaticamente
- Cria o arquivo YAML
- Executa o build
- Limpa arquivos temporários

**Tudo automático, sem precisar copiar comandos longos!**

**Ou use o arquivo de script:** Se você fez upload do arquivo `executar_migrate_collectstatic_admin.sh` para o Cloud Shell, execute:

```bash
bash executar_migrate_collectstatic_admin.sh
```

### 📋 Método Alternativo: Usar Arquivo de Script

Se o método acima der erro, você pode criar um arquivo de script:

1. **Crie o arquivo** no Cloud Shell:

```bash
nano /tmp/migrate.sh
```

2. **Cole este conteúdo** no editor (Ctrl+Shift+V para colar):

```bash
cat > /tmp/cloudbuild-migrate.yaml <<'YAML'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
YAML
gcloud builds submit --config=/tmp/cloudbuild-migrate.yaml .
```

3. **Salve e saia:** Pressione Ctrl+X, depois Y, depois Enter
4. **Execute:** `bash /tmp/migrate.sh`

```bash
gcloud builds submit --config <(cat <<'EOF'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
EOF
) .
```

### 📝 INSTRUÇÕES IMPORTANTES:

**⚠️ ATENÇÃO:** Quando você copiar o comando acima:
1. Copie TODO o bloco de código (do `cat > /tmp/...` até o `gcloud builds submit...`)
2. Cole no Cloud Shell
3. Pressione Enter UMA vez
4. Aguarde o comando executar

**❌ NÃO copie:**
- As palavras "```bash" ou "```"
- Números de seção como "1.", "2.", etc.
- Texto explicativo entre os blocos de código

**✅ COPIE apenas:**
- O código que está dentro do bloco cinza (entre as três aspas)

**✅ O que este comando faz:**
- Executa `migrate` para criar todas as tabelas do banco de dados
- Executa `collectstatic` para organizar arquivos JavaScript e estáticos
- Cria ou atualiza o usuário admin (usuário: `admin`, senha: `L6171r12@@`)
- Tudo em um único comando!

**⏱️ Tempo estimado:** 3-5 minutos

**⚠️ NOTA:** Se este comando não funcionar (erro de conexão com banco), use a **Opção 2** abaixo que usa Cloud Run Jobs e tem garantia de acesso ao Cloud SQL.

---

## 🎯 OPÇÃO 2: Cloud Run Jobs (Recomendado - Acesso Garantido ao Cloud SQL)

Esta opção usa Cloud Run Jobs que tem acesso garantido ao Cloud SQL e é mais confiável:

### 2️⃣ Criar Cloud Run Job para Migrate + Collectstatic

Primeiro, verifique qual é o nome correto da sua imagem. Use o comando abaixo (substitua `monpec` ou `sistema-rural` pelo nome correto da sua imagem):

```bash
# Verificar imagens disponíveis
gcloud container images list --repository=gcr.io/monpec-sistema-rural
```

**Opção A: Se sua imagem é `monpec` (mais provável):**

```bash
gcloud run jobs create migrate-collectstatic \
  --image=gcr.io/monpec-sistema-rural/monpec:latest \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,python manage.py migrate --noinput && python manage.py collectstatic --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2
```

**Opção B: Se sua imagem é `sistema-rural`:**

```bash
gcloud run jobs create migrate-collectstatic \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,python manage.py migrate --noinput && python manage.py collectstatic --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2
```

### 3️⃣ Executar o Job

```bash
gcloud run jobs execute migrate-collectstatic --region=us-central1 --wait
```

**⏱️ Tempo estimado:** 3-5 minutos

**✅ Quando terminar:** Você verá o status `SUCCEEDED`. Após isso, o erro do formulário deve desaparecer e os slides devem voltar a funcionar.

### 4️⃣ Criar Cloud Run Job para Criar Usuário Admin

```bash
# Opção A: Se sua imagem é monpec
gcloud run jobs create create-admin \
  --image=gcr.io/monpec-sistema-rural/monpec:latest \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,shell,-c,from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

# Opção B: Se sua imagem é sistema-rural
gcloud run jobs create create-admin \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,shell,-c,from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2
```

### 5️⃣ Executar o Job para Criar Admin

**IMPORTANTE:** Execute este comando APENAS após o primeiro job ter terminado com sucesso.

```bash
gcloud run jobs execute create-admin --region=us-central1 --wait
```

**✅ O que este comando faz:**
- Remove qualquer usuário admin existente (se houver)
- Cria um novo usuário superusuário com:
  - **Usuário:** `admin`
  - **Email:** `admin@example.com`
  - **Senha:** `L6171r12@@`

**⏱️ Tempo estimado:** 1-2 minutos

---

## 🔍 Verificar se Funcionou

Após executar os comandos (Opção 1 ou Opção 2):

1. Acesse a URL do seu serviço Cloud Run
2. Teste o formulário - o erro deve ter desaparecido
3. Verifique os slides - as fotos devem voltar a passar
4. Faça login com:
   - Usuário: `admin`
   - Senha: `L6171r12@@`

### 📊 Verificar Status dos Jobs

```bash
# Listar jobs
gcloud run jobs list --region=us-central1

# Ver execuções do job migrate-collectstatic
gcloud run jobs executions list --job=migrate-collectstatic --region=us-central1

# Ver execuções do job create-admin
gcloud run jobs executions list --job=create-admin --region=us-central1

# Ver logs de uma execução específica
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-collectstatic" --limit=50
```

### 🗑️ Limpar Jobs (Opcional - após executar com sucesso)

Se quiser remover os jobs após usar (para economizar recursos):

```bash
gcloud run jobs delete migrate-collectstatic --region=us-central1
gcloud run jobs delete create-admin --region=us-central1
```

### ❓ Troubleshooting

**Erro: "unrecognized arguments: --add-cloudsql-instances"**
- ✅ **Corrigido!** O script `executar_com_cloud_run_jobs.sh` foi atualizado para usar `--set-cloudsql-instances`
- Faça upload da versão atualizada do script

**Erro: "No credentialed accounts" ou "You do not currently have an active account selected"**

**Solução:** No Cloud Shell, mesmo com este erro, os comandos geralmente funcionam usando Application Default Credentials. Se não funcionar, tente:
```bash
bash SOLUCAO_COMPLETA_MIGRATE.sh
```

Se quiser diagnosticar manualmente, execute:

```bash
# 1. Verificar contas disponíveis
gcloud auth list

# 2. Verificar configuração atual
gcloud config list

# 3. Configurar projeto
gcloud config set project monpec-sistema-rural

# 4. Se necessário, fazer login (normalmente não é necessário no Cloud Shell)
# gcloud auth login
```

**Soluções:**
- **Solução 1:** Execute `gcloud config set project monpec-sistema-rural` antes de executar o script
- **Solução 2:** Use o script de diagnóstico `diagnostico_gcloud.sh` para ver o que está errado
- **Solução 3:** Tente executar os comandos manualmente (veja a Opção 2 - Cloud Run Jobs, que é mais confiável)

**Erro: "No such file or directory" ou "manage.py not found" (Opção 1)**
- ✅ Já resolvido com o uso de `entrypoint: 'sh'` e `args: ['-c']`
- Se ainda ocorrer, tente a Opção 2 (Cloud Run Jobs)

**Erro: "Connection refused" ou erro de conexão com banco (Opção 1)**
- Se você receber erro de conexão com o banco usando a Opção 1, use a **Opção 2** (Cloud Run Jobs) que tem acesso garantido ao Cloud SQL
- Verifique se o nome da conexão está correto: `monpec-sistema-rural:us-central1:monpec-db`
- Confirme no Console do GCP que a instância do Cloud SQL está rodando

**Erro: "Image not found" (Opção 2)**
- Verifique qual é o nome correto da sua imagem: `gcloud container images list --repository=gcr.io/monpec-sistema-rural`
- Use `monpec` ou `sistema-rural` conforme o nome correto da sua imagem

**Erro: "Connection refused" ou erro de conexão com banco (Opção 2)**
- Verifique se o nome da conexão está correto: `monpec-sistema-rural:us-central1:monpec-db`
- Confirme no Console do GCP que a instância do Cloud SQL está rodando
- Verifique se o Cloud Run Job tem permissão para acessar o Cloud SQL

**Comando/Job executou com sucesso mas o formulário ainda dá erro**
- Aguarde 1-2 minutos após o comando/job terminar
- Verifique os logs do Cloud Run para ver se há outros erros
- Confirme que as migrations foram executadas: verifique os logs do build/job

**Job já existe (erro ao criar - Opção 2)**
- Se os jobs já existem, você pode executá-los diretamente: `gcloud run jobs execute NOME_DO_JOB --region=us-central1 --wait`
- Ou atualizar os jobs existentes com: `gcloud run jobs update NOME_DO_JOB --region=us-central1 ...`

---