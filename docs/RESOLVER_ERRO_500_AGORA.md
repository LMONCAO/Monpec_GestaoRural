# 🚨 Resolver Erro 500 AGORA

## ⚡ Solução Rápida (Copiar e Colar)

### Passo 1: Abrir Google Cloud Shell
1. Acesse: https://console.cloud.google.com/
2. Clique no ícone `>_` (Cloud Shell) no canto superior direito

### Passo 2: Copiar e Colar Este Comando Completo

Copie **TODO** o conteúdo abaixo e cole no Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

echo "🔍 Verificando logs de erro..."
gcloud config set project $PROJECT_ID
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=5 --format="value(textPayload)" 2>/dev/null | head -3

echo ""
echo "🔧 Aplicando migrations..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

echo "⏱️  Executando (aguarde 2-4 minutos)..."
gcloud run jobs execute corrigir-500 --region=$REGION --wait

echo ""
echo "🧹 Limpando..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "🔄 Reiniciando serviço..."
gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars="RESTART=$(date +%s)" --quiet

echo ""
echo "✅ Concluído! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
```

### Passo 3: Aguardar e Testar
1. Aguarde 2-4 minutos para o processo terminar
2. Acesse: https://monpec-fzzfjppzva-uc.a.run.app/login/
3. Se ainda houver erro, veja a seção "Ver Logs Detalhados" abaixo

---

## 🔍 Ver Logs Detalhados (Se Ainda Houver Erro)

Se o erro 500 persistir, execute este comando para ver o erro exato:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=20 --format="table(timestamp,severity,textPayload)"
```

Ou use o script completo:

```bash
# Copie o conteúdo do arquivo VER_LOGS_ERRO_500.sh e execute
bash VER_LOGS_ERRO_500.sh
```

---

## 🛠️ Problemas Comuns

### Problema 1: Job falha na execução

**Solução**: Verifique os logs do job:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20
```

### Problema 2: "Connection refused" ou erro de banco

**Solução**: Verifique se o Cloud SQL está rodando:

```bash
gcloud sql instances describe monpec-db
```

Se não estiver, inicie:

```bash
gcloud sql instances patch monpec-db --activation-policy=ALWAYS
```

### Problema 3: Erro de imagem não encontrada

**Solução**: Verifique qual imagem existe:

```bash
gcloud container images list --repository=gcr.io/monpec-sistema-rural
```

Se a imagem for diferente (ex: `monpec` ao invés de `sistema-rural`), ajuste a variável `IMAGE_NAME` no comando.

---

## 📞 Precisa de Mais Ajuda?

1. Execute o script completo: `CORRIGIR_ERRO_500_FINAL.sh`
2. Veja o guia detalhado: `DIAGNOSTICAR_ERRO_500.md`
3. Verifique os logs no Google Cloud Console: https://console.cloud.google.com/logs
