# 🚀 Configuração do GitHub Actions para Deploy Automático no Google Cloud

> 📚 **Para um guia mais completo e detalhado, consulte**: [`CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md`](../CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md)

Este guia explica como configurar o deploy automático do MONPEC para o Google Cloud Run usando GitHub Actions.

## 📋 Pré-requisitos

1. Conta no GitHub com acesso ao repositório
2. Projeto no Google Cloud Platform (GCP)
3. Acesso administrativo ao projeto GCP
4. `gcloud` CLI instalado localmente (para configuração inicial)

## 🔧 Passo 1: Criar Service Account no GCP

1. Acesse o [Console do GCP](https://console.cloud.google.com/)
2. Selecione o projeto `monpec-sistema-rural`
3. Vá em **IAM & Admin** > **Service Accounts**
4. Clique em **+ CREATE SERVICE ACCOUNT**
5. Preencha:
   - **Nome**: `github-actions-deploy`
   - **Descrição**: `Service account para deploy automático via GitHub Actions`
6. Clique em **CREATE AND CONTINUE**
7. Adicione as seguintes roles:
   - `Cloud Run Admin` (para fazer deploy)
   - `Service Account User` (para executar jobs)
   - `Cloud Build Editor` (para fazer build)
   - `Storage Admin` (para acessar Container Registry)
   - `Cloud SQL Client` (se usar Cloud SQL)
8. Clique em **DONE**

## 🔑 Passo 2: Criar Chave JSON para Service Account

1. Clique na service account criada (`github-actions-deploy`)
2. Vá na aba **KEYS**
3. Clique em **ADD KEY** > **Create new key**
4. Selecione **JSON**
5. Clique em **CREATE** (o arquivo será baixado automaticamente)

## 🔐 Passo 3: Configurar Secret no GitHub

1. Acesse seu repositório no GitHub: https://github.com/LMONCAO/monpec
2. Vá em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Configure:
   - **Name**: `GCP_SA_KEY`
   - **Secret**: Cole todo o conteúdo do arquivo JSON baixado (o conteúdo completo do arquivo)
5. Clique em **Add secret**

## 📝 Passo 4: Verificar Configurações do Workflow

O workflow está configurado em `.github/workflows/deploy-gcp.yml` com as seguintes configurações:

```yaml
PROJECT_ID: monpec-sistema-rural
SERVICE_NAME: monpec
REGION: us-central1
```

Se precisar alterar, edite o arquivo do workflow.

## 🚀 Passo 5: Testar o Deploy

### Opção 1: Push para branch main/master
Faça um commit e push para a branch `main` ou `master`:

```bash
git add .
git commit -m "Teste de deploy automático"
git push origin main
```

### Opção 2: Execução Manual
1. Vá em **Actions** no repositório GitHub
2. Selecione o workflow **🚀 Deploy para Google Cloud Run**
3. Clique em **Run workflow**
4. Selecione a branch e clique em **Run workflow**

## 📊 Monitorar o Deploy

1. Acesse a aba **Actions** no GitHub para ver o progresso
2. Cada passo do workflow será exibido em tempo real
3. Se houver erros, os logs detalhados estarão disponíveis

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente

Para adicionar variáveis de ambiente ao Cloud Run, edite o workflow e adicione no comando `gcloud run deploy`:

```yaml
--set-env-vars "VARIAVEL1=valor1,VARIAVEL2=valor2"
```

### Secrets do GCP

Para usar secrets do GCP (recomendado para senhas), configure no workflow:

```yaml
--set-secrets "SECRET_NAME=SECRET_NAME:latest"
```

Primeiro, crie os secrets no GCP:
```bash
echo -n "valor-do-secret" | gcloud secrets create SECRET_NAME --data-file=-
```

### Migrações de Banco

O workflow inclui um job para executar migrações. Se você precisar desabilitar ou modificar, edite a seção:

```yaml
- name: 🔄 Aplicar migrações
```

## 🔍 Troubleshooting

### Erro: "Permission denied"
- Verifique se a service account tem todas as permissões necessárias
- Certifique-se de que o secret `GCP_SA_KEY` está configurado corretamente

### Erro: "Project not found"
- Verifique se o `PROJECT_ID` está correto no workflow
- Certifique-se de que a service account tem acesso ao projeto

### Build falha
- Verifique os logs no Cloud Build console
- Certifique-se de que o `Dockerfile.prod` está correto
- Verifique se o `cloudbuild-config.yaml` existe e está correto

### Deploy falha
- Verifique os logs do Cloud Run
- Certifique-se de que as variáveis de ambiente estão configuradas
- Verifique se o banco de dados está acessível

## 📚 Referências

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google GitHub Actions](https://github.com/google-github-actions)

## ✅ Checklist Final

- [ ] Service account criada no GCP
- [ ] Chave JSON baixada e configurada como secret no GitHub
- [ ] Permissões corretas atribuídas à service account
- [ ] Workflow configurado corretamente
- [ ] Teste de deploy executado com sucesso
- [ ] Variáveis de ambiente configuradas (se necessário)
- [ ] Secrets do GCP configurados (se necessário)

---

**Nota**: O workflow está configurado para executar automaticamente em push para `main` ou `master`. Para outras branches, será necessário fazer push manualmente ou executar via GitHub Actions UI.

