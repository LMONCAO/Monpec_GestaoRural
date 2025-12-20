# 🚀 Como Atualizar o Sistema no Domínio (Google Cloud)

Este guia explica como atualizar o sistema Monpec no domínio **monpec.com.br** hospedado no Google Cloud Run.

## 📋 Pré-requisitos

1. **Google Cloud CLI instalado** (`gcloud`)
   - Windows: Baixe em https://cloud.google.com/sdk/docs/install
   - Ou instale via Chocolatey: `choco install gcloudsdk`

2. **Autenticado no Google Cloud**
   ```powershell
   gcloud auth login
   ```

3. **Projeto configurado**
   ```powershell
   gcloud config set project monpec-sistema-rural
   ```

## 🎯 Método Rápido (Recomendado)

### Opção 1: Usando o Script PowerShell (Windows)

```powershell
.\DEPLOY_GCP.ps1
```

Este script irá:
- ✅ Verificar autenticação
- ✅ Configurar o projeto
- ✅ Habilitar APIs necessárias
- ✅ Fazer build da imagem Docker
- ✅ Fazer deploy no Cloud Run
- ✅ Mostrar a URL do serviço

### Opção 2: Usando o Script Bash (Linux/Mac/Cloud Shell)

```bash
bash DEPLOY_AGORA.sh
```

## 📝 Método Manual Passo a Passo

### Passo 1: Verificar Autenticação

```powershell
gcloud auth list
```

Se não estiver autenticado:
```powershell
gcloud auth login
```

### Passo 2: Configurar Projeto

```powershell
gcloud config set project monpec-sistema-rural
```

### Passo 3: Habilitar APIs (se necessário)

```powershell
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### Passo 4: Fazer Build da Imagem Docker

```powershell
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

⏳ **Tempo estimado:** 10-15 minutos

### Passo 5: Fazer Deploy no Cloud Run

```powershell
gcloud run deploy monpec `
    --image gcr.io/monpec-sistema-rural/monpec `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --memory=512Mi `
    --cpu=1 `
    --timeout=300 `
    --max-instances=10
```

⏳ **Tempo estimado:** 2-3 minutos

### Passo 6: Verificar Deploy

```powershell
gcloud run services describe monpec --region us-central1
```

### Passo 7: Obter URL do Serviço

```powershell
gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
```

## 🌐 Verificar Domínio

Para verificar se o domínio **monpec.com.br** está configurado corretamente:

```powershell
.\CONFIGURAR_DOMINIO_CLOUD_RUN.ps1
```

Ou manualmente:

```powershell
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

## 🔍 Verificar Status do Sistema

```powershell
.\VERIFICAR_STATUS_CLOUD_RUN.sh
```

Ou via PowerShell:

```powershell
gcloud run services describe monpec --region us-central1 --format 'table(status.url,status.conditions[0].status)'
```

## 📊 Ver Logs do Sistema

```powershell
gcloud run services logs read monpec --region us-central1 --limit 50
```

## ⚠️ Problemas Comuns

### Erro: "Dockerfile não encontrado"
- Certifique-se de estar na raiz do projeto
- Verifique se o arquivo `Dockerfile` existe

### Erro: "requirements_producao.txt não encontrado"
- O Dockerfile espera `requirements_producao.txt`
- Crie o arquivo copiando de `requirements.txt`:
  ```powershell
  Copy-Item requirements.txt requirements_producao.txt
  ```

### Erro: "Build falhou"
- Verifique os logs: `gcloud builds log`
- Verifique se todas as dependências estão no `requirements.txt`

### Erro 503 (Service Unavailable)
- Execute o script de correção:
  ```powershell
  bash CORRIGIR_503_CLOUD_RUN.sh
  ```

### Domínio não funciona após deploy
- Verifique o mapeamento do domínio:
  ```powershell
  gcloud run domain-mappings list --region us-central1
  ```
- Se não existir, crie:
  ```powershell
  gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
  ```
- Configure os registros DNS no seu provedor de domínio

## 🔄 Fluxo Completo de Atualização

1. **Fazer alterações no código localmente**
2. **Testar localmente** (opcional mas recomendado)
3. **Commit e push para Git** (se usar controle de versão)
4. **Executar deploy:**
   ```powershell
   .\DEPLOY_GCP.ps1
   ```
5. **Aguardar conclusão** (15-20 minutos)
6. **Verificar no navegador:** https://monpec.com.br
7. **Verificar logs** se houver problemas

## 📱 Usando Google Cloud Shell (Alternativa)

Se preferir usar o Cloud Shell diretamente no navegador:

1. Acesse: https://shell.cloud.google.com
2. Faça upload dos arquivos ou clone do repositório
3. Execute:
   ```bash
   bash DEPLOY_AGORA.sh
   ```

## 🎯 Comandos Úteis

```powershell
# Listar serviços Cloud Run
gcloud run services list --region us-central1

# Ver detalhes do serviço
gcloud run services describe monpec --region us-central1

# Ver logs em tempo real
gcloud run services logs tail monpec --region us-central1

# Revisar histórico de revisões
gcloud run revisions list --service monpec --region us-central1

# Fazer rollback para revisão anterior
gcloud run services update-traffic monpec --to-revisions REVISION_NAME=100 --region us-central1
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `gcloud run services logs read monpec --region us-central1`
2. Execute o diagnóstico: `bash VERIFICAR_STATUS_CLOUD_RUN.sh`
3. Verifique o status no console: https://console.cloud.google.com/run

---

**Última atualização:** Dezembro 2025
