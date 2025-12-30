# Como Criar Usuário Admin no Sistema Web (Produção - Google Cloud Run)

Este guia explica como criar um usuário administrador no sistema em produção (Google Cloud Run).

## 📋 Pré-requisitos

1. Acesso ao **Google Cloud Shell** ou **Google Cloud Console**
2. Permissões para criar Cloud Run Jobs no projeto `monpec-sistema-rural`

## 🚀 Método 1: Script Simples (Recomendado)

### Passo 1: Abrir Google Cloud Shell

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Clique no ícone `>_` no canto superior direito para abrir o Cloud Shell

### Passo 2: Upload do Script (se necessário)

Se o script não estiver no Cloud Shell, você pode:

**Opção A: Copiar e colar o conteúdo do script diretamente**

**Opção B: Fazer upload do arquivo**
- Clique no menu do Cloud Shell (três pontos)
- Selecione "Upload file"
- Selecione o arquivo `CRIAR_ADMIN_PRODUCAO_SIMPLES.sh`

### Passo 3: Executar o Script

```bash
bash CRIAR_ADMIN_PRODUCAO_SIMPLES.sh
```

Este script cria um usuário admin com as credenciais padrão:
- **Username**: `admin`
- **Email**: `admin@monpec.com.br`
- **Senha**: `L6171r12@@`

### Passo 4: Fazer Login

Após o script terminar com sucesso, acesse:
- **URL**: https://monpec.com.br/login/
- **Username**: `admin`
- **Senha**: `L6171r12@@`

---

## 🔧 Método 2: Script Interativo (Com Credenciais Personalizadas)

Se você quiser definir credenciais personalizadas:

### Passo 1: Executar o Script Interativo

```bash
bash CRIAR_ADMIN_PRODUCAO.sh
```

O script solicitará:
- Username (padrão: `admin`)
- Email (padrão: `admin@monpec.com.br`)
- Senha (mínimo 12 caracteres)

### Passo 2: Aguardar Execução

O script criará um Cloud Run Job e executará automaticamente. Isso pode levar 1-3 minutos.

---

## ⚙️ Método 3: Comandos Manuais (Avançado)

Se preferir executar os comandos manualmente:

### 1. Configurar Projeto

```bash
gcloud config set project monpec-sistema-rural
```

### 2. Criar Cloud Run Job

```bash
gcloud run jobs create criar-admin \
  --region=us-central1 \
  --image=gcr.io/monpec-sistema-rural/sistema-rural:latest \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,garantir_admin,--username,admin,--email,admin@monpec.com.br,--senha,L6171r12@@" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2
```

### 3. Executar o Job

```bash
gcloud run jobs execute criar-admin --region=us-central1 --wait
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

### Listar Todos os Jobs

```bash
gcloud run jobs list --region=us-central1
```

---

## 🗑️ Limpar (Opcional)

Após criar o usuário com sucesso, você pode deletar o job para economizar recursos:

```bash
gcloud run jobs delete criar-admin --region=us-central1
```

---

## ❓ Solução de Problemas

### Erro: "Image not found"

Verifique qual é o nome correto da sua imagem:

```bash
gcloud container images list --repository=gcr.io/monpec-sistema-rural
```

Se sua imagem for `monpec` ao invés de `sistema-rural`, ajuste o comando:

```bash
# Trocar sistema-rural por monpec
--image=gcr.io/monpec-sistema-rural/monpec:latest
```

### Erro: "Connection refused" ou erro de conexão com banco

1. Verifique se a instância do Cloud SQL está rodando:
   ```bash
   gcloud sql instances describe monpec-db
   ```

2. Verifique o nome da conexão:
   - Deve ser: `monpec-sistema-rural:us-central1:monpec-db`

### Erro: "You do not currently have an active account selected"

No Cloud Shell, você já está autenticado automaticamente. Apenas configure o projeto:

```bash
gcloud config set project monpec-sistema-rural
```

### Job executou mas não consigo fazer login

1. Verifique se a senha está correta (mínimo 12 caracteres)
2. Tente forçar a atualização da senha:

```bash
gcloud run jobs update criar-admin \
  --region=us-central1 \
  --args="manage.py,garantir_admin,--username,admin,--email,admin@monpec.com.br,--senha,L6171r12@@,--forcar"

gcloud run jobs execute criar-admin --region=us-central1 --wait
```

### Ver Detalhes de uma Execução Específica

```bash
# Listar execuções
gcloud run jobs executions list --job=criar-admin --region=us-central1

# Ver detalhes de uma execução específica
gcloud run jobs executions describe EXECUTION_NAME --job=criar-admin --region=us-central1
```

---

## 📝 Notas Importantes

⚠️ **Segurança:**
- Sempre use senhas fortes (mínimo 12 caracteres)
- Altere a senha padrão após o primeiro acesso
- Não compartilhe credenciais de admin

⚠️ **Imagens:**
- O script tenta usar `sistema-rural:latest` por padrão
- Se sua imagem tiver outro nome, ajuste o script ou use os comandos manuais

⚠️ **Tempo:**
- A criação do job e execução podem levar 1-3 minutos
- Aguarde a conclusão antes de tentar fazer login

---

## ✅ Checklist de Sucesso

- [ ] Script executado sem erros
- [ ] Job executado com status `SUCCEEDED`
- [ ] Conseguir acessar https://monpec.com.br/login/
- [ ] Conseguir fazer login com as credenciais criadas
- [ ] (Opcional) Job deletado após uso

