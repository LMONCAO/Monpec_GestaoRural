# 🚀 Deploy no Google Cloud Platform - Sistema MONPEC

## ✅ Pré-requisitos

1. Conta Google Cloud ativa
2. Projeto criado no GCP
3. Google Cloud Shell aberto OU `gcloud` CLI instalado localmente
4. APIs habilitadas (o script faz isso automaticamente)

## 📋 Scripts Disponíveis

### 1. DEPLOY_GCP_COMPLETO.sh (Recomendado)
Script completo com todas as verificações e configurações.

```bash
chmod +x DEPLOY_GCP_COMPLETO.sh
./DEPLOY_GCP_COMPLETO.sh
```

**O que faz:**
- ✅ Verifica autenticação
- ✅ Habilita APIs necessárias
- ✅ Verifica dependências
- ✅ Verifica Dockerfile (cria se não existir)
- ✅ Faz build da imagem Docker
- ✅ Faz deploy no Cloud Run
- ✅ Mostra URL do serviço
- ✅ Instruções para próximos passos

### 2. DEPLOY_GCP_RAPIDO.sh
Script rápido para deploy direto (sem verificações extras).

```bash
chmod +x DEPLOY_GCP_RAPIDO.sh
./DEPLOY_GCP_RAPIDO.sh
```

## 🚀 Passo a Passo

### Opção 1: Usando Google Cloud Shell (Recomendado)

1. **Abra o Google Cloud Shell**
   - Acesse: https://console.cloud.google.com
   - Clique no ícone de terminal no canto superior direito

2. **Clone ou faça upload do projeto**
   ```bash
   # Se já estiver no diretório do projeto, pule esta etapa
   # Caso contrário, faça upload dos arquivos ou clone do repositório
   ```

3. **Navegue até o diretório do projeto**
   ```bash
   cd Monpec_GestaoRural  # ou o nome do seu diretório
   ```

4. **Configure o projeto GCP**
   ```bash
   gcloud config set project SEU_PROJETO_ID
   ```

5. **Execute o script de deploy**
   ```bash
   chmod +x DEPLOY_GCP_COMPLETO.sh
   ./DEPLOY_GCP_COMPLETO.sh
   ```

### Opção 2: Usando CLI Local

1. **Instale o Google Cloud SDK**
   - https://cloud.google.com/sdk/docs/install

2. **Autentique-se**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Configure o projeto**
   ```bash
   gcloud config set project SEU_PROJETO_ID
   ```

4. **Execute o script**
   ```bash
   chmod +x DEPLOY_GCP_COMPLETO.sh
   ./DEPLOY_GCP_COMPLETO.sh
   ```

## 🔧 Após o Deploy

### 1. Aplicar Migrações do Banco de Dados

```bash
# Criar job para migrações
gcloud run jobs create migrate-monpec \
  --image gcr.io/SEU_PROJETO_ID/monpec:latest \
  --region us-central1 \
  --command python \
  --args 'manage.py,migrate,--noinput' \
  --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'

# Executar o job
gcloud run jobs execute migrate-monpec --region us-central1
```

### 2. Configurar Variáveis de Ambiente

Se precisar configurar variáveis adicionais:

```bash
gcloud run services update monpec \
  --region us-central1 \
  --set-env-vars 'SECRET_KEY=SUA_CHAVE,DB_HOST=SEU_HOST,DB_NAME=SEU_DB'
```

### 3. Configurar Domínio Personalizado (Opcional)

```bash
gcloud run domain-mappings create \
  --service monpec \
  --domain monpec.com.br \
  --region us-central1

gcloud run domain-mappings create \
  --service monpec \
  --domain www.monpec.com.br \
  --region us-central1
```

### 4. Verificar Status do Serviço

```bash
gcloud run services describe monpec --region us-central1
```

## 📝 Variáveis de Ambiente Importantes

Configure estas variáveis no Cloud Run:

- `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`
- `DEBUG=False`
- `SECRET_KEY=sua_chave_secreta_aqui`
- `DB_HOST=seu_host_do_cloud_sql`
- `DB_NAME=nome_do_banco`
- `DB_USER=usuario_do_banco`
- `DB_PASSWORD=senha_do_banco`

## 🐳 Dockerfile

O script verifica se existe um `Dockerfile`. Se não existir, cria um básico automaticamente.

Se você quiser usar um Dockerfile customizado, crie antes de executar o script.

## 🔍 Ver Logs

```bash
# Logs do serviço
gcloud run services logs read monpec --region us-central1

# Logs em tempo real
gcloud run services logs tail monpec --region us-central1
```

## ⚠️ Troubleshooting

**Erro: "Permission denied" ao executar script**
```bash
chmod +x DEPLOY_GCP_COMPLETO.sh
```

**Erro: "Project not set"**
```bash
gcloud config set project SEU_PROJETO_ID
```

**Erro: "Not authenticated"**
```bash
gcloud auth login
```

**Erro no build: "Dockerfile not found"**
- O script cria um Dockerfile básico automaticamente
- Ou crie um Dockerfile customizado antes de executar

**Serviço não inicia:**
- Verifique os logs: `gcloud run services logs read monpec --region us-central1`
- Verifique variáveis de ambiente
- Verifique configurações do banco de dados

## 📚 Recursos Adicionais

- Console Cloud Run: https://console.cloud.google.com/run
- Documentação Cloud Run: https://cloud.google.com/run/docs
- Cloud Shell: https://shell.cloud.google.com





