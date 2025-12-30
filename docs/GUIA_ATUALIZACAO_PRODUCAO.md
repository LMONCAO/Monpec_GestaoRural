# 🚀 Guia de Atualização para Produção - monpec.com.br

Este guia explica como atualizar o sistema Monpec para produção no domínio **monpec.com.br** no Google Cloud Run.

## 📋 Pré-requisitos

1. **Google Cloud CLI instalado** (`gcloud`)
   - Windows: Baixe em https://cloud.google.com/sdk/docs/install
   - Ou instale via Chocolatey: `choco install gcloudsdk`

2. **Autenticado no Google Cloud**
   ```powershell
   gcloud auth login
   ```

3. **Projeto configurado**
   - Projeto: `monpec-sistema-rural`
   - Região: `us-central1`
   - Serviço: `monpec`

## 🎯 Método Rápido (Recomendado)

### Opção 1: Atualização Completa com Script Automático

Execute o script PowerShell na raiz do projeto:

```powershell
.\ATUALIZAR_PRODUCAO_MONPEC.ps1
```

Este script irá:
- ✅ Verificar autenticação
- ✅ Configurar o projeto
- ✅ Habilitar APIs necessárias
- ✅ Verificar arquivos necessários
- ✅ Fazer build da imagem Docker
- ✅ Fazer deploy no Cloud Run
- ✅ Verificar configuração do domínio

### Opção 2: Atualização com Configuração de Domínio

Se você também quiser configurar o domínio automaticamente:

```powershell
.\ATUALIZAR_PRODUCAO_MONPEC.ps1 -ConfigurarDominio
```

⚠️ **IMPORTANTE**: Após configurar o domínio, você receberá registros DNS que precisam ser adicionados no seu provedor de domínio (Registro.br, etc.).

### Opção 3: Apenas Build (sem deploy)

Para fazer apenas o build da imagem:

```powershell
.\ATUALIZAR_PRODUCAO_MONPEC.ps1 -ApenasBuild
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
gcloud services enable containerregistry.googleapis.com
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
    --max-instances=10 `
    --min-instances=1
```

⏳ **Tempo estimado:** 2-3 minutos

### Passo 6: Configurar Domínio (se ainda não configurado)

```powershell
gcloud run domain-mappings create `
    --service monpec `
    --domain monpec.com.br `
    --region us-central1
```

### Passo 7: Obter Registros DNS

Após criar o mapeamento do domínio, você receberá registros DNS. Para ver novamente:

```powershell
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

### Passo 8: Configurar DNS no Provedor de Domínio

1. Acesse o painel do seu provedor de domínio (Registro.br, etc.)
2. Adicione os registros DNS fornecidos pelo Google Cloud
3. Aguarde a propagação DNS (15 minutos - 2 horas)

## 🔍 Verificar Status

### Verificar Status do Serviço

```powershell
gcloud run services describe monpec --region us-central1
```

### Verificar Domínios Mapeados

```powershell
gcloud run domain-mappings list --region us-central1
```

### Ver Logs do Sistema

```powershell
gcloud run services logs read monpec --region us-central1 --limit 50
```

### Ver Logs em Tempo Real

```powershell
gcloud run services logs tail monpec --region us-central1
```

## 🌐 Acessar o Sistema

Após o deploy e configuração do DNS:

- **URL do Cloud Run**: Será exibida após o deploy
- **Domínio personalizado**: https://monpec.com.br (após propagação DNS)

## ⚠️ Problemas Comuns

### Erro: "Dockerfile não encontrado"
- Certifique-se de estar na raiz do projeto
- Verifique se o arquivo `Dockerfile` existe

### Erro: "requirements_producao.txt não encontrado"
- O Dockerfile espera `requirements_producao.txt`
- Verifique se o arquivo existe na raiz do projeto

### Erro: "Build falhou"
- Verifique os logs: `gcloud builds log`
- Verifique se todas as dependências estão no `requirements_producao.txt`

### Erro 503 (Service Unavailable)
- Verifique os logs do serviço
- Verifique se o banco de dados está acessível (se usar Cloud SQL)
- Verifique se as variáveis de ambiente estão corretas

### Domínio não funciona após deploy
- Verifique o mapeamento do domínio:
  ```powershell
  gcloud run domain-mappings describe monpec.com.br --region us-central1
  ```
- Verifique se os registros DNS estão configurados corretamente no provedor
- Aguarde a propagação DNS (pode levar até 2 horas)

### Erro: "Domínio já mapeado"
- Se o domínio já estiver mapeado, o script não tentará criar novamente
- Para verificar: `gcloud run domain-mappings list --region us-central1`

## 🔄 Fluxo Completo de Atualização

1. **Fazer alterações no código localmente**
2. **Testar localmente** (opcional mas recomendado)
3. **Commit e push para Git** (se usar controle de versão)
4. **Executar atualização:**
   ```powershell
   .\ATUALIZAR_PRODUCAO_MONPEC.ps1
   ```
5. **Aguardar conclusão** (15-20 minutos)
6. **Verificar no navegador:** https://monpec.com.br
7. **Verificar logs** se houver problemas

## 📊 Comandos Úteis

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

# Ver informações do domínio
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

## 🔐 Configurações de Segurança

O sistema está configurado com:
- ✅ HTTPS obrigatório (`SECURE_SSL_REDIRECT = True`)
- ✅ HSTS habilitado
- ✅ Cookies seguros
- ✅ CSRF protegido
- ✅ DEBUG desabilitado em produção

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `gcloud run services logs read monpec --region us-central1`
2. Execute o diagnóstico: `.\configurar_dominio_cloud_run.ps1`
3. Verifique o status no console: https://console.cloud.google.com/run

---

**Última atualização:** Janeiro 2025

