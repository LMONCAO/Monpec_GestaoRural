# 🔧 Resolver Problema do Dockerfile

## ⚠️ Problema Identificado

O arquivo `Dockerfile.prod` não foi encontrado no Cloud Shell.

## ✅ Solução Rápida

### Opção 1: Verificar se existe Dockerfile (sem .prod)

No terminal do Cloud Shell, execute:

```bash
ls -la Dockerfile
```

Se existir, podemos usar ele ou renomear.

### Opção 2: Criar Dockerfile.prod

Execute este comando no Cloud Shell para criar o arquivo:

```bash
cat > Dockerfile.prod << 'EOF'
# Dockerfile para deploy no Google Cloud Run
# Imagem base otimizada para Python 3.11
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Expor porta (Cloud Run usa a variável PORT)
ENV PORT=8080
EXPOSE 8080

# Comando para iniciar a aplicação
# Cloud Run injeta a variável PORT automaticamente
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
EOF
```

### Opção 3: Verificar se gunicorn está no requirements.txt

```bash
grep -i gunicorn requirements.txt
```

Se não estiver, adicione:

```bash
echo "gunicorn" >> requirements.txt
```

---

## 🚀 Após Resolver, Continue com o Deploy

### 1. Verificar se tudo está OK

```bash
ls -la Dockerfile.prod manage.py requirements.txt
```

### 2. Fazer Build

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
```

### 3. Fazer Deploy

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

---

## 📝 Comandos Rápidos (Copy & Paste)

Execute estes comandos no Cloud Shell, um de cada vez:

```bash
# 1. Verificar Dockerfile
ls -la Dockerfile

# 2. Se não existir Dockerfile.prod, criar:
cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN mkdir -p /app/staticfiles /app/media /app/logs
ENV PORT=8080
EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
EOF

# 3. Verificar se gunicorn está no requirements
grep -i gunicorn requirements.txt || echo "gunicorn" >> requirements.txt

# 4. Verificar tudo
ls -la Dockerfile.prod manage.py requirements.txt

# 5. Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest
```









