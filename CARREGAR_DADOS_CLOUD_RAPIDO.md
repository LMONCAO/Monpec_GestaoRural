# 🚀 Carregar Dados no Google Cloud - Guia Rápido

## ⚡ Método Mais Rápido (Google Cloud Shell)

### Passo 1: Abrir Cloud Shell
1. Acesse: https://console.cloud.google.com/
2. Clique no ícone do terminal no topo (Cloud Shell)

### Passo 2: Copiar e Colar Este Comando

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"
FONTE="sincronizar"
USUARIO_ID="1"

gcloud config set project $PROJECT_ID
gcloud run jobs delete carregar-dados-banco --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create carregar-dados-banco \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,carregar_dados_banco,--fonte,$FONTE,--usuario-id,$USUARIO_ID" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=1800

gcloud run jobs execute carregar-dados-banco --region=$REGION --wait
```

### Pronto! ✅
O comando vai:
1. Criar um Cloud Run Job
2. Executar o comando de carregar dados
3. Mostrar o resultado

**Tempo estimado:** 2-5 minutos

---

## 📝 Outras Opções

### Opção 2: Usar Script (Mais Organizado)

Se você fez upload dos arquivos do projeto:

```bash
chmod +x scripts/deploy/CARREGAR_DADOS_CLOUD_SHELL.sh
./scripts/deploy/CARREGAR_DADOS_CLOUD_SHELL.sh sincronizar "" 1
```

### Opção 3: PowerShell (Local)

Se você tem Google Cloud SDK instalado localmente:

```powershell
.\scripts\deploy\CARREGAR_DADOS_CLOUD_RUN.ps1 -Fonte sincronizar -UsuarioId 1
```

---

## 🔍 Verificar Resultado

```bash
# Ver logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=carregar-dados-banco" --limit=20

# Ver execuções
gcloud run jobs executions list --job=carregar-dados-banco --region=us-central1
```

---

## ❓ Problemas?

1. **Erro "Image not found"**: Faça deploy da imagem primeiro
2. **Erro "Permission denied"**: Verifique suas permissões no projeto
3. **Timeout**: Aumente o timeout com `--timeout=3600`

Veja documentação completa em: `docs/CARREGAR_DADOS_GOOGLE_CLOUD.md`

