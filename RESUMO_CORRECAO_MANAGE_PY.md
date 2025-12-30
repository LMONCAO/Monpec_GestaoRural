# Correção: Problema com manage.py não encontrado no Cloud Run Jobs

## 🔍 Problema Identificado

Quando executamos comandos Django via Cloud Run Jobs usando:
```bash
--command="python"
--args="manage.py,garantir_admin,..."
```

O erro ocorria porque o `manage.py` não estava no PATH do container.

## ✅ Solução

O Dockerfile define `WORKDIR /app`, então o `manage.py` está em `/app/manage.py`.

**Solução:** Usar `sh -c` com `cd /app` antes de executar o comando:

```bash
--command="sh"
--args="-c,cd /app && python manage.py garantir_admin --username admin --email admin@monpec.com.br --senha L6171r12@@"
```

## 📝 Exemplos de Comandos Corrigidos

### Criar Admin
```bash
gcloud run jobs create criar-admin \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && python manage.py garantir_admin --username admin --email admin@monpec.com.br --senha L6171r12@@" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2
```

### Aplicar Migrações
```bash
gcloud run jobs create aplicar-migracoes \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2
```

## 📂 Arquivos Atualizados

Os seguintes arquivos foram corrigidos com esta solução:

1. ✅ `CRIAR_ADMIN_PRODUCAO_SIMPLES.sh`
2. ✅ `CRIAR_ADMIN_PRODUCAO.sh`
3. ✅ `CRIAR_ADMIN_PRODUCAO_CORRIGIDO.sh`
4. ✅ `CORRIGIR_FORMULARIO_DEMO.sh`
5. ✅ `COMANDO_CRIAR_ADMIN_CLOUD_SHELL.txt`
6. ✅ `COMANDOS_CORRIGIR_DEMO_CLOUD_SHELL.txt`

## 🎯 Diferença Principal

**❌ Antes (não funcionava):**
```bash
--command="python"
--args="manage.py,garantir_admin,--username,admin"
```

**✅ Agora (funciona):**
```bash
--command="sh"
--args="-c,cd /app && python manage.py garantir_admin --username admin"
```

## 💡 Por que funciona?

1. `sh -c` executa um comando shell completo
2. `cd /app` muda para o diretório de trabalho do container
3. `&&` garante que o comando Python só executa se o `cd` for bem-sucedido
4. Agora o `manage.py` é encontrado em `/app/manage.py`

