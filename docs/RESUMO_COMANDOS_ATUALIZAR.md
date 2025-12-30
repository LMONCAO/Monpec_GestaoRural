# ⚡ Resumo: Comandos para Atualizar no Google Cloud

## ⚠️ Se Der Erro de Senha do Banco

Se você ver `password authentication failed`, execute primeiro:

```bash
gcloud sql users set-password monpec_user --instance=monpec-db --password=L6171r12@@jjms
```

## 🚀 Comando Mais Rápido (Copiar e Colar)

Abra o **Cloud Shell** no Google Cloud Console e execute:

```bash
PROJECT_ID="monpec-sistema-rural" && SERVICE_NAME="monpec" && REGION="us-central1" && DB_PASSWORD="L6171r12@@jjms" && echo "🔧 Verificando senha do banco..." && gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>/dev/null || echo "⚠️ Aviso: Não foi possível atualizar senha do banco (pode ser normal se já estiver correta)" && gcloud config set project $PROJECT_ID && grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt && TIMESTAMP=$(date +%Y%m%d%H%M%S) && echo "🔨 Buildando..." && gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP && echo "🚀 Deployando..." && gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances=$PROJECT_ID:$REGION:monpec-db --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD" && echo "✅✅✅ CONCLUÍDO! ✅✅✅"
```

## 📋 O que este comando faz:

1. ✅ Configura o projeto Google Cloud
2. ✅ Garante que `openpyxl` está no requirements
3. ✅ Faz build da imagem Docker
4. ✅ Faz deploy no Cloud Run
5. ✅ Configura todas as variáveis de ambiente
6. ✅ Conecta ao banco de dados Cloud SQL
7. ✅ Cria o admin automaticamente (via Dockerfile)

## 🎯 Após o Deploy

1. **Aguarde 1-2 minutos** para o sistema inicializar
2. **Acesse a URL** que aparecerá no final
3. **Faça login** com:
   - Username: `admin`
   - Senha: `L6171r12@@`

## 🔍 Verificar Status

```bash
# Ver URL do serviço
gcloud run services describe monpec --region=us-central1 --format="value(status.url)"

# Ver logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=20
```

## 🆘 Se algo der errado

### Admin não funciona?
```bash
gcloud run jobs execute garantir-admin --region=us-central1 --args python,manage.py,garantir_admin
```

### Ver erros?
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" --limit=10
```

## 📚 Mais Detalhes

- **Guia Completo**: `COMANDOS_ATUALIZAR_GOOGLE_CLOUD.md`
- **Admin Automático**: `MELHORIAS_ADMIN_AUTOMATICO.md`

---

**Pronto!** Copie o comando acima e cole no Cloud Shell. 🚀

