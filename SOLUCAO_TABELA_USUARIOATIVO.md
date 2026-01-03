# 🔧 Solução: Tabela UsuarioAtivo Não Existe

## 🚨 Problema Identificado

O erro mostra que a tabela `gestao_rural_usuarioativo` não existe:

```
django.db.utils.ProgrammingError: relation "gestao_rural_usuarioativo" does not exist
```

**Causa**: A migration `0081_add_usuario_ativo` foi marcada como fake junto com todas as outras, mas a tabela não existe no banco.

## ✅ Solução

Desmarcar a migration 0081 como fake e aplicá-la para criar a tabela.

### Comando Completo

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Criando tabela UsuarioAtivo..."
gcloud run jobs delete criar-usuarioativo --region=$REGION --quiet 2>/dev/null || true

# Passo 1: Desmarcar migration 0081 como fake
echo "📦 Passo 1: Desmarcando migration 0081 como fake..."
gcloud run jobs create criar-usuarioativo \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"DELETE FROM django_migrations WHERE app='gestao_rural' AND name='0081_add_usuario_ativo'\");print('✅ Migration 0081 desmarcada')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute criar-usuarioativo --region=$REGION --wait

# Passo 2: Aplicar migration 0081
echo ""
echo "📦 Passo 2: Aplicando migration 0081..."
gcloud run jobs update criar-usuarioativo \
  --region=$REGION \
  --args="manage.py,migrate,gestao_rural,0081_add_usuario_ativo" \
  --quiet

gcloud run jobs execute criar-usuarioativo --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tabela UsuarioAtivo criada!"
    echo ""
    echo "🔄 Fazendo deploy..."
    gcloud run deploy monpec \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --memory=2Gi \
      --cpu=2 \
      --timeout=300 \
      --allow-unauthenticated \
      --quiet
    
    echo ""
    echo "✅ Pronto! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
else
    echo ""
    echo "❌ Erro. Verifique os logs."
fi

gcloud run jobs delete criar-usuarioativo --region=$REGION --quiet 2>/dev/null || true
```

## 📝 O que o comando faz

1. **Passo 1**: Remove o registro fake da migration 0081 da tabela `django_migrations`
2. **Passo 2**: Aplica a migration 0081 para criar a tabela `UsuarioAtivo`
3. **Deploy**: Faz deploy do serviço após criar a tabela

## 🎯 Por que isso resolve

- **Antes**: Tabela `UsuarioAtivo` não existe → erro ao fazer login → erro 500
- **Depois**: Tabela criada → login funciona → sistema funciona

Execute o comando acima e me avise o resultado!

