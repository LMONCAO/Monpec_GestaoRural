# 🔧 Solução: Container Saindo por Migrations Pendentes

## 🚨 Problema Identificado

O container está saindo (`exit(0)`) quando detecta migrations pendentes. Pelos logs:
- "You have 56 unapplied migration(s)"
- "Container called exit(0)"

Isso significa que mesmo após aplicar as migrations no job, quando o serviço inicia, ele ainda detecta migrations pendentes.

## 🔍 Possíveis Causas

1. **Migrations não foram realmente aplicadas** - O job pode ter falhado silenciosamente
2. **Banco diferente** - O serviço pode estar usando um banco diferente do job
3. **Código que força exit** - Pode haver código que verifica migrations e sai

## ✅ Solução: Verificar e Aplicar Migrations no Container

Primeiro, vamos verificar o estado real das migrations:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

gcloud run jobs delete verificar-migrations-estado --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-migrations-estado \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,showmigrations,--list" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute verificar-migrations-estado --region=$REGION --wait
gcloud run jobs delete verificar-migrations-estado --region=$REGION --quiet 2>/dev/null || true
```

## 🎯 Solução Alternativa: Modificar Entrypoint para Não Falhar

Se o problema persistir, podemos modificar o entrypoint para aplicar migrations mas não sair se houver erro:

```bash
# Criar entrypoint que não falha
cat > entrypoint_fix.sh << 'EOF'
#!/bin/sh
set -e

echo "🚀 Iniciando aplicação MONPEC..."

# Executar migrações (não falhar se houver erro)
echo "📦 Executando migrações do banco de dados..."
python manage.py migrate --noinput || echo "⚠️ Aviso: Erro ao aplicar migrations (continuando mesmo assim)"

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput || echo "⚠️ Aviso: Erro ao coletar arquivos estáticos"

# Iniciar servidor (sempre, mesmo se migrations falharam)
echo "🌐 Iniciando servidor Gunicorn..."
PORT=${PORT:-8080}
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
EOF
```

Mas primeiro, vamos verificar o estado real das migrations no banco.
