# 🔄 Guia: Sincronizar GitHub com Google Cloud

Este guia explica como configurar a integração contínua (CI/CD) entre GitHub e Google Cloud, permitindo que cada push no repositório faça deploy automático no Google Cloud Run.

---

## 📋 Pré-requisitos

1. ✅ Repositório no GitHub
2. ✅ Projeto no Google Cloud (`monpec-sistema-rural`)
3. ✅ Acesso de administrador no projeto Google Cloud
4. ✅ Google Cloud SDK instalado localmente (opcional, apenas para configuração inicial)

---

## 🚀 Passo a Passo

### **Passo 1: Criar Service Account no Google Cloud**

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Vá em **IAM & Admin** → **Service Accounts**
3. Clique em **+ CREATE SERVICE ACCOUNT**
4. Preencha:
   - **Nome:** `github-actions-deploy`
   - **Descrição:** `Service account para GitHub Actions fazer deploy`
5. Clique em **CREATE AND CONTINUE**

### **Passo 2: Atribuir Permissões ao Service Account**

No mesmo processo de criação, na etapa de **Grant this service account access to project**:

Adicione estas roles:
- ✅ **Cloud Run Admin** (`roles/run.admin`)
- ✅ **Service Account User** (`roles/iam.serviceAccountUser`)
- ✅ **Storage Admin** (`roles/storage.admin`) - para Cloud Build
- ✅ **Cloud Build Editor** (`roles/cloudbuild.builds.editor`)
- ✅ **Artifact Registry Writer** (`roles/artifactregistry.writer`)

Clique em **CONTINUE** e depois em **DONE**.

### **Passo 3: Criar e Baixar a Chave JSON**

1. Na lista de Service Accounts, clique no service account criado (`github-actions-deploy`)
2. Vá na aba **KEYS**
3. Clique em **ADD KEY** → **Create new key**
4. Escolha **JSON**
5. Clique em **CREATE**
6. O arquivo JSON será baixado automaticamente
7. **⚠️ IMPORTANTE:** Guarde este arquivo em local seguro, você precisará dele no próximo passo!

### **Passo 4: Configurar Secrets no GitHub**

1. Acesse seu repositório no GitHub
2. Vá em **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**

Adicione os seguintes secrets (um por vez):

#### **Secret 1: `GCP_SA_KEY`**
- **Name:** `GCP_SA_KEY`
- **Value:** Abra o arquivo JSON baixado no Passo 3 e copie **TODO o conteúdo** do arquivo (começando com `{` e terminando com `}`)
- Clique em **Add secret**

#### **Secret 2: `SECRET_KEY`**
- **Name:** `SECRET_KEY`
- **Value:** `django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE`
- Clique em **Add secret**

#### **Secret 3: `DB_NAME`**
- **Name:** `DB_NAME`
- **Value:** `monpec_db`
- Clique em **Add secret**

#### **Secret 4: `DB_USER`**
- **Name:** `DB_USER`
- **Value:** `monpec_user`
- Clique em **Add secret**

#### **Secret 5: `DB_PASSWORD`**
- **Name:** `DB_PASSWORD`
- **Value:** `L6171r12@@jjms`
- Clique em **Add secret**

#### **Secret 6: `DJANGO_SUPERUSER_PASSWORD`**
- **Name:** `DJANGO_SUPERUSER_PASSWORD`
- **Value:** `L6171r12@@`
- Clique em **Add secret**

### **Passo 5: Habilitar APIs Necessárias no Google Cloud**

Execute estes comandos (pode ser no Cloud Shell ou localmente com gcloud):

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Habilitar APIs necessárias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable iamcredentials.googleapis.com
```

### **Passo 6: Verificar Workflow do GitHub Actions**

O arquivo `.github/workflows/deploy-google-cloud.yml` já está criado e configurado! 

**Verifique se:**
- ✅ O arquivo existe em `.github/workflows/deploy-google-cloud.yml`
- ✅ Os nomes dos secrets estão corretos (conforme configurado no Passo 4)
- ✅ O branch configurado está correto (padrão: `main` ou `master`)

### **Passo 7: Fazer Push e Testar**

1. Faça commit e push das alterações:
   ```bash
   git add .
   git commit -m "Configurar CI/CD com GitHub Actions"
   git push origin main
   ```

2. Acesse a aba **Actions** no GitHub
3. Você verá o workflow executando
4. Clique no workflow para ver os logs em tempo real
5. Aguarde a conclusão (pode levar 10-20 minutos)

---

## ✅ Como Funciona

Quando você fizer push para o branch `main` (ou `master`):

1. 🔄 GitHub Actions detecta o push
2. 🔐 Autentica no Google Cloud usando o Service Account
3. 🐳 Faz build da imagem Docker
4. 📦 Publica a imagem no Container Registry
5. 🚀 Faz deploy no Cloud Run
6. ✅ Sistema atualizado automaticamente!

---

## 🔍 Verificar se Funcionou

### **No GitHub:**
1. Vá em **Actions** no seu repositório
2. Você deve ver um workflow com status ✅ verde
3. Clique nele para ver os logs detalhados

### **No Google Cloud:**
1. Acesse [Cloud Run Console](https://console.cloud.google.com/run)
2. Procure pelo serviço `monpec`
3. Veja a revisão mais recente (deve ter sido criada agora)

### **No Navegador:**
1. Execute para obter a URL:
   ```bash
   gcloud run services describe monpec --region=us-central1 --format="value(status.url)"
   ```
2. Acesse a URL no navegador
3. Verifique se o sistema está funcionando

---

## ⚙️ Configurações Avançadas

### **Deploy Apenas em Branch Específico**

O workflow já está configurado para fazer deploy apenas quando houver push no branch `main` ou `master`. Para alterar, edite o arquivo `.github/workflows/deploy-google-cloud.yml`:

```yaml
on:
  push:
    branches:
      - main  # Altere para o nome do seu branch
```

### **Ignorar Arquivos Específicos**

O workflow já ignora mudanças em arquivos `.md`, `.txt`, etc. Para adicionar mais arquivos que não devem disparar deploy:

```yaml
on:
  push:
    paths-ignore:
      - '**.md'
      - '**.txt'
      - 'docs/**'
      # Adicione mais padrões aqui
```

### **Executar Deploy Manualmente**

O workflow está configurado para permitir execução manual através da interface do GitHub:
1. Vá em **Actions** → **Deploy para Google Cloud Run**
2. Clique em **Run workflow**
3. Escolha o branch e clique em **Run workflow**

---

## 🐛 Troubleshooting

### **Erro: "Permission denied" ou "403 Forbidden"**

**Causa:** Service Account não tem permissões suficientes.

**Solução:**
1. Verifique se todas as roles foram atribuídas (Passo 2)
2. Aguarde alguns minutos para as permissões propagarem
3. Tente executar o workflow novamente

### **Erro: "Secret not found"**

**Causa:** Secret não foi configurado ou nome está incorreto.

**Solução:**
1. Verifique se todos os secrets foram criados (Passo 4)
2. Verifique se os nomes estão exatamente iguais no workflow e nos secrets
3. Os nomes são case-sensitive!

### **Erro: "API not enabled"**

**Causa:** Alguma API necessária não está habilitada.

**Solução:**
Execute o Passo 5 novamente para habilitar todas as APIs.

### **Build Falha**

**Causa:** Erro no Dockerfile ou código.

**Solução:**
1. Veja os logs do workflow no GitHub Actions
2. Procure pela mensagem de erro específica
3. Corrija o problema e faça push novamente

### **Deploy Completa mas Sistema Não Funciona**

**Causa:** Erro no runtime (ex: banco de dados, variáveis de ambiente).

**Solução:**
1. Verifique os logs do Cloud Run:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=50
   ```
2. Verifique se todas as variáveis de ambiente foram configuradas
3. Verifique a conexão com o Cloud SQL

---

## 🔒 Segurança

### **Boas Práticas:**

1. ✅ **Nunca commite** o arquivo JSON do Service Account no repositório
2. ✅ **Nunca commite** senhas ou secrets no código
3. ✅ Use **GitHub Secrets** para todas as informações sensíveis
4. ✅ Revise as permissões do Service Account regularmente
5. ✅ Use o princípio do menor privilégio (apenas permissões necessárias)

### **Rotacionar Secrets:**

Para alterar uma senha ou chave:
1. Atualize o secret no GitHub (Settings → Secrets)
2. Faça um push para disparar novo deploy
3. O novo secret será usado automaticamente

---

## 📊 Monitoramento

### **Ver Histórico de Deploys:**

1. No GitHub: **Actions** → **Deploy para Google Cloud Run**
2. No Google Cloud: **Cloud Run** → **monpec** → **Revisões**

### **Logs em Tempo Real:**

No Google Cloud Console:
1. Vá em **Cloud Run** → **monpec**
2. Clique na aba **LOGS**
3. Veja logs em tempo real

Ou via terminal:
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=monpec"
```

---

## 🎯 Próximos Passos

Após configurar tudo:

1. ✅ Faça um push de teste para verificar se funciona
2. ✅ Monitore o primeiro deploy no GitHub Actions
3. ✅ Configure notificações (opcional) para receber alertas de deploy
4. ✅ Documente qualquer configuração adicional específica do seu projeto

---

## 📞 Suporte

Se tiver problemas:

1. Verifique os logs do workflow no GitHub Actions
2. Verifique os logs do Cloud Run
3. Consulte a documentação do [Google Cloud Run](https://cloud.google.com/run/docs)
4. Consulte a documentação do [GitHub Actions](https://docs.github.com/en/actions)

---

**✅ Pronto! Seu projeto agora está sincronizado entre GitHub e Google Cloud!**

Toda vez que você fizer push no branch `main`, o sistema será atualizado automaticamente no Google Cloud Run. 🚀

