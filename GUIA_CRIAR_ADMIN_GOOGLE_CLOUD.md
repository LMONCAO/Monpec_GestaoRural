# 🔐 Como Criar Superusuário Admin no Google Cloud

Este guia mostra como criar um superusuário administrador para acessar o sistema Monpec no Google Cloud.

## 📋 Método Recomendado: Google Cloud Shell (Mais Simples)

### Passo 1: Abrir Google Cloud Shell

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Clique no ícone `>_` (Cloud Shell) no canto superior direito
3. Aguarde o Cloud Shell abrir (pode levar alguns segundos)

### Passo 2: Configurar o Projeto

No Cloud Shell, execute:

```bash
gcloud config set project monpec-sistema-rural
```

### Passo 3: Criar o Admin (Opção A - Script Automático)

Copie e cole o seguinte comando completo no Cloud Shell:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

# Credenciais do admin (você pode alterar)
USERNAME="admin"
EMAIL="admin@monpec.com.br"
PASSWORD="L6171r12@@"

# Detectar imagem
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

echo "🚀 Criando usuário admin..."
echo "   Username: $USERNAME"
echo "   Email: $EMAIL"
echo ""

# Deletar job anterior se existir
gcloud run jobs delete criar-admin --region=$REGION --quiet 2>/dev/null || true

# Criar job
gcloud run jobs create criar-admin \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py garantir_admin --username $USERNAME --email $EMAIL --senha $PASSWORD" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

echo ""
echo "✅ Job criado! Executando..."
echo "⏱️  Aguarde 1-3 minutos..."
echo ""

# Executar o job
gcloud run jobs execute criar-admin --region=$REGION --wait

echo ""
echo "============================================================"
echo "✅ SUCESSO! Usuário admin criado!"
echo "============================================================"
echo ""
echo "📝 Credenciais para login:"
echo "   Username: $USERNAME"
echo "   Senha: $PASSWORD"
echo ""
echo "🌐 Acesse: https://monpec-fzzfjppzva-uc.a.run.app/login/"
echo ""
```

### Passo 4: Fazer Login

Após o comando terminar com sucesso:

1. Acesse: https://monpec-fzzfjppzva-uc.a.run.app/login/
2. Use as credenciais:
   - **Username**: `admin`
   - **Senha**: `L6171r12@@`

---

## 🔧 Método Alternativo: Com Credenciais Personalizadas

Se você quiser usar um email diferente (como o seu próprio email), use este comando:

```bash
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

# ALTERE AQUI SUAS CREDENCIAIS
USERNAME="admin"
EMAIL="l.moncaosilva@gmail.com"  # <-- SEU EMAIL
PASSWORD="SuaSenhaSegura123@@"   # <-- SUA SENHA (mínimo 12 caracteres)

IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

gcloud run jobs delete criar-admin --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create criar-admin \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py garantir_admin --username $USERNAME --email $EMAIL --senha $PASSWORD" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

gcloud run jobs execute criar-admin --region=$REGION --wait

echo "✅ Admin criado!"
echo "Username: $USERNAME"
echo "Email: $EMAIL"
echo "Senha: $PASSWORD"
```

---

## 🔍 Verificar se Funcionou

### Ver Logs do Job

```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=criar-admin" --limit=50
```

### Ver Execuções do Job

```bash
gcloud run jobs executions list --job=criar-admin --region=us-central1
```

---

## ❓ Solução de Problemas

### Erro: "Image not found"

Verifique qual é o nome correto da sua imagem:

```bash
gcloud container images list --repository=gcr.io/monpec-sistema-rural
```

Se sua imagem tiver outro nome (ex: `monpec`), ajuste a variável `IMAGE_NAME`:

```bash
IMAGE_NAME="gcr.io/monpec-sistema-rural/monpec:latest"
```

### Erro: "Connection refused" ou erro de conexão com banco

1. Verifique se a instância do Cloud SQL está rodando:
   ```bash
   gcloud sql instances describe monpec-db
   ```

2. Verifique o nome da conexão:
   - Deve ser: `monpec-sistema-rural:us-central1:monpec-db`

### Job executou mas não consigo fazer login

1. Verifique se a senha está correta (mínimo 12 caracteres)
2. Tente forçar a atualização da senha:

```bash
gcloud run jobs update criar-admin \
  --region=us-central1 \
  --args="manage.py,garantir_admin,--username,admin,--email,admin@monpec.com.br,--senha,L6171r12@@,--forcar"

gcloud run jobs execute criar-admin --region=us-central1 --wait
```

### Erro: "You do not currently have an active account selected"

No Cloud Shell, você já está autenticado automaticamente. Apenas configure o projeto:

```bash
gcloud config set project monpec-sistema-rural
```

---

## 🗑️ Limpar (Opcional)

Após criar o usuário com sucesso, você pode deletar o job para economizar recursos:

```bash
gcloud run jobs delete criar-admin --region=us-central1
```

---

## 📝 Notas Importantes

⚠️ **Segurança:**
- Sempre use senhas fortes (mínimo 12 caracteres)
- Altere a senha padrão após o primeiro acesso
- Não compartilhe credenciais de admin

⚠️ **Tempo:**
- A criação do job e execução podem levar 1-3 minutos
- Aguarde a conclusão antes de tentar fazer login

⚠️ **Email:**
- O email pode ser usado para recuperação de senha
- Use um email válido que você tenha acesso

---

## ✅ Checklist de Sucesso

- [ ] Comando executado sem erros no Cloud Shell
- [ ] Job executado com status `SUCCEEDED`
- [ ] Conseguir acessar https://monpec-fzzfjppzva-uc.a.run.app/login/
- [ ] Conseguir fazer login com as credenciais criadas
- [ ] (Opcional) Job deletado após uso

---

## 🆘 Precisa de Ajuda?

Se ainda tiver problemas:

1. Verifique os logs do job (comando acima)
2. Verifique se o Cloud SQL está rodando
3. Verifique se a imagem Docker existe
4. Tente executar o comando novamente
