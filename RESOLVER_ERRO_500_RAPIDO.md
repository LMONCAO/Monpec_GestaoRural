# 🚨 Resolver Erro 500 Rapidamente

O erro 500 geralmente é causado por:
- Migrations não aplicadas
- Problemas de conexão com banco de dados
- Erros no código
- Variáveis de ambiente incorretas

## ⚡ Solução Rápida (3 passos)

### Passo 1: Abrir Google Cloud Shell

1. Acesse https://console.cloud.google.com/
2. Clique no ícone `>_` (Cloud Shell) no canto superior direito

### Passo 2: Copiar e Colar Este Comando

Copie TODO o conteúdo abaixo e cole no Cloud Shell:

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

echo "🔧 Corrigindo erro 500..."
gcloud config set project $PROJECT_ID

# Aplicar migrations
echo "📦 Aplicando migrations..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

gcloud run jobs execute corrigir-500 --region=$REGION --wait
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

# Reiniciar serviço
echo "🔄 Reiniciando serviço..."
gcloud run services update $SERVICE_NAME --region=$REGION --to-latest --quiet

echo ""
echo "✅ Concluído! Teste o sistema em:"
echo "   https://monpec-fzzfjppzva-uc.a.run.app/login/"
```

### Passo 3: Aguardar e Testar

1. Aguarde 1-3 minutos para o processo terminar
2. Acesse: https://monpec-fzzfjppzva-uc.a.run.app/login/
3. Se ainda houver erro, veja a seção "Diagnóstico Detalhado" abaixo

---

## 🔍 Diagnóstico Detalhado

Se a solução rápida não funcionar, execute estes comandos para ver o erro exato:

### Ver Logs de Erro

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=20 --format="table(timestamp,severity,textPayload)"
```

### Ver Todos os Logs Recentes

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50
```

### Habilitar DEBUG Temporariamente (para ver erro completo)

⚠️ **ATENÇÃO**: Isso expõe informações sensíveis. Use apenas para diagnóstico!

```bash
# Habilitar DEBUG
gcloud run services update monpec --region=us-central1 --update-env-vars="DEBUG=True" --quiet

# Testar o sistema (você verá o erro completo)
# Depois, desabilitar DEBUG:
gcloud run services update monpec --region=us-central1 --update-env-vars="DEBUG=False" --quiet
```

---

## 🛠️ Problemas Comuns e Soluções

### Problema 1: "No such table" ou erro de migrations

**Solução**: Execute o comando do Passo 2 acima (aplica migrations)

### Problema 2: "Connection refused" ou erro de banco

**Solução**: Verifique se o Cloud SQL está rodando:

```bash
gcloud sql instances describe monpec-db
```

Se não estiver rodando, inicie:

```bash
gcloud sql instances patch monpec-db --activation-policy=ALWAYS
```

### Problema 3: "DisallowedHost" ou erro de ALLOWED_HOSTS

**Solução**: O middleware já deve corrigir isso automaticamente. Se não corrigir, verifique os logs.

### Problema 4: Erro de código Python

**Solução**: Verifique os logs detalhados para ver o traceback completo do erro.

---

## 📞 Precisa de Mais Ajuda?

1. Execute o script completo de diagnóstico: `CORRIGIR_ERRO_500_COMPLETO.sh`
2. Veja o guia detalhado: `DIAGNOSTICAR_ERRO_500.md`
3. Verifique os logs no Google Cloud Console: https://console.cloud.google.com/logs

---

## ✅ Checklist de Verificação

Após executar a correção, verifique:

- [ ] Migrations foram aplicadas sem erros
- [ ] Serviço foi reiniciado
- [ ] Cloud SQL está rodando
- [ ] Não há erros nos logs recentes
- [ ] Sistema está acessível em https://monpec-fzzfjppzva-uc.a.run.app/login/
