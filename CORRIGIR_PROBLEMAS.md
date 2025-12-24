# 🔧 Problemas Identificados e Soluções

## Problemas Encontrados nos Logs

### 1. ❌ Erro de ALLOWED_HOSTS
```
ERROR: Invalid HTTP_HOST header: 'monpec-29862706245.us-central1.run.app'. 
You may need to add 'monpec-29862706245.us-central1.run.app' to ALLOWED_HOSTS.
```

**Solução:** ✅ Já corrigido no código. O host foi adicionado ao `settings_gcp.py`.

### 2. ❌ Erro de Conexão Cloud SQL
```
ERROR: Cloud SQL instance ".s.PGSQL.5432" is not reachable. 
Deploy a new revision adding the Cloud SQL connection.
```

**Causa:** As variáveis de ambiente do banco de dados não estão configuradas.

**Solução:** Execute:
```powershell
gcloud run services update monpec --region=us-central1 `
  --update-env-vars="DB_NAME=monpec_db" `
  --update-env-vars="DB_USER=monpec_user" `
  --update-env-vars="DB_PASSWORD=SUA_SENHA_DB" `
  --update-env-vars="CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db
```

### 3. ⚠️ Timeouts e Problemas de Memória
```
CRITICAL: WORKER TIMEOUT (pid:X)
ERROR: Worker (pid:X) was sent SIGKILL! Perhaps out of memory?
```

**Causa:** O serviço pode estar com pouca memória ou timeout muito baixo.

**Solução:** Aumentar memória e timeout:
```powershell
gcloud run services update monpec --region=us-central1 `
  --memory=4Gi `
  --timeout=600 `
  --cpu=2
```

## ✅ Ações Imediatas Necessárias

1. **Configurar variáveis de ambiente do banco:**
   - DB_NAME
   - DB_USER  
   - DB_PASSWORD
   - CLOUD_SQL_CONNECTION_NAME

2. **Conectar Cloud SQL:**
   - Adicionar `--add-cloudsql-instances`

3. **Aumentar recursos (se necessário):**
   - Memória: 2Gi → 4Gi
   - Timeout: 300s → 600s

## 📋 Comando Completo de Correção

```powershell
# 1. Configurar variáveis de ambiente
gcloud run services update monpec --region=us-central1 `
  --update-env-vars="DB_NAME=monpec_db" `
  --update-env-vars="DB_USER=monpec_user" `
  --update-env-vars="DB_PASSWORD=SUA_SENHA_AQUI" `
  --update-env-vars="CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --memory=4Gi `
  --timeout=600

# 2. Verificar status
gcloud run services describe monpec --region=us-central1

# 3. Ver logs novamente
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.location=us-central1" --limit=20 --format="table(timestamp,severity,textPayload)" --project=monpec-sistema-rural
```

## 🔍 Verificar se Está Funcionando

Após aplicar as correções:

1. Acesse: https://monpec-29862706245.us-central1.run.app
2. Verifique os logs novamente
3. Teste o acesso ao admin: https://monpec-29862706245.us-central1.run.app/admin

