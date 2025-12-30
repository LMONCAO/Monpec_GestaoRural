# 🚨 CRIAR ADMIN - SOLUÇÃO URGENTE

## Problema
Não consegue fazer login com admin / L6171r12@@

## ✅ SOLUÇÃO RÁPIDA (Escolha uma)

### Opção 1: Via Cloud SQL (Se tiver acesso)

1. Acesse o Cloud SQL no console do Google Cloud
2. Conecte ao banco de dados `monpec_db`
3. Execute este SQL:

```sql
-- Verificar se o usuário existe
SELECT id, username, email, is_staff, is_superuser, is_active 
FROM auth_user 
WHERE username = 'admin';

-- Se não existir, criar:
INSERT INTO auth_user (username, email, password, is_staff, is_superuser, is_active, date_joined, last_login)
VALUES ('admin', 'admin@monpec.com.br', 'pbkdf2_sha256$600000$...', true, true, true, NOW(), NULL);

-- Mas é melhor usar o Django para gerar o hash da senha corretamente
```

### Opção 2: Via Cloud Shell (RECOMENDADO)

1. Acesse: https://console.cloud.google.com/cloudshell
2. Execute:

```bash
# Conectar ao Cloud Run
gcloud run services proxy monpec --region us-central1 --port 8080 &
```

3. Em outro terminal do Cloud Shell:

```bash
# Executar Django shell
gcloud run jobs create monpec-admin-shell \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args manage.py,shell \
  --max-retries 1 \
  --task-timeout 300

# Depois execute o job e entre no shell interativo
```

### Opção 3: Criar via Python Local (Se tiver acesso ao banco)

1. Configure as variáveis de ambiente para o banco do Cloud Run:

```bash
export DB_NAME=monpec_db
export DB_USER=monpec_user
export DB_PASSWORD=sua_senha_aqui
export DB_HOST=IP_DO_CLOUD_SQL
export DB_PORT=5432
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
```

2. Execute:

```python
python criar_admin_simples.py
```

### Opção 4: Via Django Admin (Se conseguir acessar)

Se você tem outro usuário admin ou acesso ao Django admin:

1. Acesse: https://monpec-fzzfjppzva-uc.a.run.app/admin/
2. Vá em "Users" > "Add user"
3. Crie o usuário admin com as permissões corretas

### Opção 5: Resetar via Interface Web (Se houver)

Alguns sistemas têm uma página de reset de senha. Verifique se há uma rota como:
- `/reset-password/`
- `/admin/reset/`
- `/criar-admin/`

## 🔍 Verificar o Problema

Execute no Cloud Shell para ver os logs:

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=monpec-create-admin" \
  --limit 50 \
  --format="table(timestamp,textPayload)" \
  --project monpec-sistema-rural
```

## 📝 Credenciais Esperadas

- **URL**: https://monpec-fzzfjppzva-uc.a.run.app
- **Usuário**: admin
- **Senha**: L6171r12@@
- **Email**: admin@monpec.com.br

## ⚠️ Se Nada Funcionar

1. Verifique se o banco de dados está acessível
2. Verifique as configurações de conexão no `settings_gcp.py`
3. Verifique se o Cloud SQL está configurado corretamente
4. Entre em contato com suporte técnico










































