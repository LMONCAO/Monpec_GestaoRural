# 🛠️ Solução Definitiva: Sincronização em Massa de Migrations

## 🎯 Problema Identificado

O banco de dados e o histórico de migrations do Django estão desencontrados:
- **41 migrations pendentes** no Django
- Mas as **tabelas já existem** no banco
- Django tenta criar tabelas que já existem → erro `relation already exists`
- Django se recusa a iniciar enquanto houver migrations pendentes → erro 500

## ✅ Solução: Sincronização em Massa

Marcar **TODAS** as migrations de `gestao_rural` como fake de uma vez, sincronizando o histórico do Django com o estado atual do banco.

### Comando Completo (Copiar e Colar)

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🛠️ Sincronizando migrations em massa..."
gcloud run jobs delete sincronizar-migrations --region=$REGION --quiet 2>/dev/null || true

echo "📦 Passo 1: Marcando TODAS as migrations de gestao_rural como fake..."
gcloud run jobs create sincronizar-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,gestao_rural,--fake" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

echo "⏱️  Executando passo 1 (aguarde 2-3 minutos)..."
gcloud run jobs execute sincronizar-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Passo 1 concluído!"
    echo ""
    echo "📦 Passo 2: Aplicando migrations de sistema..."
    
    gcloud run jobs update sincronizar-migrations \
      --region=$REGION \
      --args="manage.py,migrate,--noinput" \
      --quiet
    
    echo "⏱️  Executando passo 2 (aguarde 1-2 minutos)..."
    gcloud run jobs execute sincronizar-migrations --region=$REGION --wait
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Sincronização concluída!"
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
        echo "❌ Erro no passo 2. Verifique os logs."
    fi
else
    echo ""
    echo "❌ Erro no passo 1. Verifique os logs."
fi

gcloud run jobs delete sincronizar-migrations --region=$REGION --quiet 2>/dev/null || true
```

## 📝 O que este comando faz

1. **Passo 1**: Marca TODAS as migrations de `gestao_rural` como fake
   - Isso sincroniza o histórico do Django com o banco atual
   - Resolve o problema de "relation already exists"

2. **Passo 2**: Aplica migrations de sistema (admin, sessions, etc.)
   - Garante que tabelas de sistema estejam atualizadas

3. **Deploy**: Faz deploy do serviço após sincronização

## 🎯 Por que isso resolve o erro 500?

- **Antes**: Django via 41 migrations pendentes → se recusava a iniciar → erro 500
- **Depois**: Django vê todas as migrations como aplicadas → inicia normalmente → sistema funciona

## ✅ Verificação Pós-Execução

Após o comando terminar:

1. **Aguarde 1-2 minutos** para o serviço inicializar
2. **Teste**: https://monpec-fzzfjppzva-uc.a.run.app/login/
3. **Se ainda houver erro 500**, verifique os logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=5 --format="value(textPayload)"
   ```

## 🔍 Se Ainda Houver Problemas

Se o erro 500 persistir, pode ser:
- Tabela `usuarioativo` não existe (criar manualmente se necessário)
- Problema de ALLOWED_HOSTS
- Problema de SECRET_KEY

Execute o comando acima e me avise o resultado!


