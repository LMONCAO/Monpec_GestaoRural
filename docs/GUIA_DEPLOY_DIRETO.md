# 🚀 Guia: Deploy Direto para Google Cloud (Sem Git)

Este guia mostra como fazer deploy direto do seu sistema para o Google Cloud Run, **sem precisar configurar Git**.

## ⚡ Método Rápido (Recomendado)

### Passo 1: Abrir Google Cloud SDK Shell

1. Abra o **Google Cloud SDK Shell** (que você já tem aberto)
2. Navegue até o diretório do projeto:
   ```powershell
   cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
   ```

### Passo 2: Executar o Script de Deploy

Execute o script que acabei de criar:

```powershell
.\DEPLOY_DIRETO_GOOGLE_CLOUD.ps1
```

O script vai:
- ✅ Verificar sua autenticação no Google Cloud
- ✅ Configurar o projeto automaticamente
- ✅ Fazer build da imagem Docker
- ✅ Fazer deploy no Cloud Run
- ✅ Mostrar a URL do serviço

### Passo 3: Configurar Variáveis de Ambiente (Importante!)

Após o deploy, você **PRECISA** configurar as variáveis de ambiente no Cloud Run:

#### Opção A: Via Console Web
1. Acesse: https://console.cloud.google.com/run
2. Clique no serviço `monpec`
3. Clique em **"EDIT & DEPLOY NEW REVISION"**
4. Vá em **"Variables & Secrets"**
5. Adicione as variáveis necessárias:
   - `DJANGO_SETTINGS_MODULE` = `sistema_rural.settings_gcp`
   - `DEBUG` = `False`
   - `DB_HOST` = (seu host do banco)
   - `DB_NAME` = (nome do banco)
   - `DB_USER` = (usuário do banco)
   - `DB_PASSWORD` = (senha do banco)
   - `SECRET_KEY` = (sua chave secreta Django)
6. Clique em **"DEPLOY"**

#### Opção B: Via Linha de Comando
```powershell
gcloud run services update monpec `
  --region us-central1 `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_HOST=SEU_HOST,DB_NAME=SEU_BANCO,DB_USER=SEU_USUARIO,DB_PASSWORD=SUA_SENHA,SECRET_KEY=SUA_SECRET_KEY"
```

### Passo 4: Aplicar Migrações

Execute as migrações do Django:

```powershell
gcloud run jobs create migrate-monpec `
  --image gcr.io/monpec-sistema-rural/monpec:latest `
  --region us-central1 `
  --command python `
  --args manage.py,migrate `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
  --add-cloudsql-instances=PROJECT_ID:REGION:INSTANCE_NAME

gcloud run jobs execute migrate-monpec --region us-central1
```

## 🔄 Para Atualizar o Sistema no Futuro

Sempre que fizer alterações no código, execute novamente:

```powershell
.\DEPLOY_DIRETO_GOOGLE_CLOUD.ps1
```

O script vai:
1. Fazer build da nova versão
2. Atualizar o serviço no Cloud Run automaticamente

## ⚙️ Configurações do Script

Se precisar ajustar as configurações, edite o arquivo `DEPLOY_DIRETO_GOOGLE_CLOUD.ps1` e altere:

```powershell
$PROJECT_ID = "monpec-sistema-rural"  # Seu projeto GCP
$SERVICE_NAME = "monpec"              # Nome do serviço
$REGION = "us-central1"               # Região
```

## 🆘 Problemas Comuns

### ❌ Erro: "Dockerfile.prod não encontrado"
- Certifique-se de estar no diretório correto do projeto
- Verifique se o arquivo `Dockerfile.prod` existe na raiz

### ❌ Erro: "Permission denied"
- Execute: `gcloud auth login`
- Verifique se você tem permissões no projeto GCP

### ❌ Erro: "Project not found"
- Verifique se o `PROJECT_ID` está correto
- Execute: `gcloud projects list` para ver seus projetos

### ❌ Build falha
- Verifique os logs: `gcloud builds list --limit=1`
- Verifique se o `Dockerfile.prod` está correto

### ❌ Serviço não inicia após deploy
- Configure as variáveis de ambiente (Passo 3)
- Verifique os logs: `gcloud run services logs tail monpec --region us-central1`

## 📋 Checklist Rápido

- [ ] Estou no diretório correto do projeto
- [ ] Google Cloud SDK Shell está aberto
- [ ] Executei o script `DEPLOY_DIRETO_GOOGLE_CLOUD.ps1`
- [ ] Deploy concluído com sucesso
- [ ] Configurei as variáveis de ambiente
- [ ] Apliquei as migrações
- [ ] Sistema está funcionando

## 🎉 Pronto!

Agora seu sistema está no Google Cloud e você pode atualizá-lo sempre que quiser executando o script novamente!

---

**Nota:** Este método não usa Git, então você pode fazer deploy direto do seu código local para o Google Cloud sem precisar configurar repositório Git.



