# 🔐 Criar Admin via Cloud Run Job (Método Mais Simples)

Este é o método mais fácil e recomendado!

## Passo 1: Criar e Executar o Job

Execute este comando completo no Cloud Shell:

```bash
# Primeiro, obter o connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
echo "Connection Name: $CONNECTION_NAME"

# Criar job
gcloud run jobs create create-admin \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --command python \
  --args criar_admin_producao.py \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
  --set-env-vars DB_NAME=monpec_db \
  --set-env-vars DB_USER=monpec_user \
  --set-env-vars DB_PASSWORD=Monpec2025!SenhaSegura \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1

# Executar o job
gcloud run jobs execute create-admin --region us-central1 --wait
```

**⚠️ IMPORTANTE:** Substitua `Monpec2025!SenhaSegura` pela senha real do seu banco de dados!

## Passo 2: Verificar o Resultado

Se o job executar com sucesso, você verá as mensagens:
- ✅ Superusuário criado/atualizado
- Credenciais: admin / L6171r12@@

## Passo 3: Testar Login

Acesse: https://monpec-29862706245.us-central1.run.app/login/
- Usuário: admin
- Senha: L6171r12@@

## Se o Job Falhar

Verifique os logs:
```bash
gcloud run jobs executions list --job create-admin --region us-central1
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=create-admin" --limit 50 --format json
```

## Limpar o Job (Opcional)

Após usar, você pode deletar o job:
```bash
gcloud run jobs delete create-admin --region us-central1
```

