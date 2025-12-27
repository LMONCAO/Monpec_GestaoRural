# 🚨 RECONSTRUÇÃO COMPLETA DO PROJETO GCP - INSTRUÇÕES

## ⚠️ AVISOS IMPORTANTES

**ANTES DE EXECUTAR ESTE SCRIPT, LEIA TODAS AS INSTRUÇÕES!**

Este script irá:
- ❌ **REMOVER** todos os serviços Cloud Run existentes
- ❌ **REMOVER** todos os jobs Cloud Run existentes  
- ❌ **REMOVER** todas as imagens Docker do Container Registry
- ⚠️ **OPCIONALMENTE REMOVER** a instância do banco de dados (TODOS OS DADOS SERÃO PERDIDOS!)

## 📋 Pré-requisitos

1. **Google Cloud SDK instalado**
   ```powershell
   # Verificar instalação
   gcloud --version
   
   # Se não tiver, instale:
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Autenticado no Google Cloud**
   ```powershell
   gcloud auth login
   ```

3. **Permissões necessárias no projeto**
   - Cloud Run Admin
   - Cloud SQL Admin
   - Cloud Build Editor
   - Service Account User

4. **Backup dos dados (RECOMENDADO)**
   ```powershell
   # Fazer backup do banco de dados antes de executar
   gcloud sql export sql monpec-db gs://seu-bucket/backup-$(Get-Date -Format "yyyyMMdd-HHmmss").sql --database=monpec_db
   ```

## 🔄 Opções de Execução

### Opção 1: Reconstruir TUDO (incluindo banco de dados)

⚠️ **ATENÇÃO**: Todos os dados do banco serão perdidos!

```powershell
.\RECONSTRUIR_GCP_DO_ZERO.ps1
```

O script pedirá duas confirmações:
1. Digite `SIM` para iniciar o processo
2. Digite `CONFIRMO` para confirmar a remoção do banco de dados

### Opção 2: Reconstruir mantendo o banco de dados

✅ **RECOMENDADO**: Mantém os dados existentes

```powershell
.\RECONSTRUIR_GCP_DO_ZERO.ps1 -SkipDatabase
```

### Opção 3: Executar sem confirmações (NÃO RECOMENDADO)

```powershell
.\RECONSTRUIR_GCP_DO_ZERO.ps1 -SkipDatabase -Force
```

## 📝 O Que o Script Faz

### Fase 1: Listagem
- Lista todos os serviços Cloud Run
- Lista todos os jobs Cloud Run
- Lista todas as imagens Docker
- Lista instâncias Cloud SQL (se aplicável)

### Fase 2: Remoção
- Remove serviços Cloud Run
- Remove jobs Cloud Run
- Remove imagens Docker do Container Registry
- Remove instância Cloud SQL (opcional)

### Fase 3: Habilitação de APIs
- Habilita APIs necessárias do Google Cloud

### Fase 4: Criação do Banco de Dados
- Cria nova instância Cloud SQL (se foi removida)
- Cria banco de dados `monpec_db`
- Cria usuário `monpec_user` com senha padrão

### Fase 5: Build da Imagem
- Constrói nova imagem Docker usando `Dockerfile.prod`
- Faz push para o Container Registry

### Fase 6: Deploy do Serviço
- Cria novo serviço Cloud Run
- Configura variáveis de ambiente básicas
- Conecta ao Cloud SQL

### Fase 7: Migrações
- Cria job de migração
- Executa migrações do Django

## ⚙️ Configurações Padrão

O script usa as seguintes configurações:

- **Projeto**: `monpec-sistema-rural`
- **Região**: `us-central1`
- **Serviço**: `monpec`
- **Job de Migração**: `migrate-monpec`
- **Instância Cloud SQL**: `monpec-db`
- **Banco de Dados**: `monpec_db`
- **Usuário**: `monpec_user`
- **Senha Padrão**: `Django2025@` ⚠️ **ALTERE APÓS O DEPLOY!**

## 🔐 Segurança - ALTERE IMEDIATAMENTE APÓS O DEPLOY

Após o deploy, você DEVE:

1. **Alterar a senha do banco de dados:**
   ```powershell
   gcloud sql users set-password monpec_user --instance=monpec-db --password="SUA_SENHA_FORTE_AQUI"
   ```

2. **Atualizar a SECRET_KEY do Django:**
   ```powershell
   # Gere uma nova SECRET_KEY
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   
   # Configure no Cloud Run
   gcloud run services update monpec --region us-central1 --update-env-vars SECRET_KEY="SUA_NOVA_SECRET_KEY"
   ```

3. **Configurar variáveis de ambiente sensíveis:**
   ```powershell
   .\CONFIGURAR_VARIAVEIS_GCP.ps1
   ```

## 🔍 Verificação Pós-Deploy

### 1. Verificar Status do Serviço
```powershell
gcloud run services describe monpec --region us-central1 --project monpec-sistema-rural
```

### 2. Verificar Logs
```powershell
gcloud run services logs read monpec --region us-central1 --project monpec-sistema-rural --limit 50
```

### 3. Testar Acesso
```powershell
# Obter URL
$url = gcloud run services describe monpec --region us-central1 --format='value(status.url)'
Write-Host "Acesse: $url"
```

### 4. Criar Superusuário
```powershell
.\criar_admin_cloud_run.ps1
```

## 🐛 Resolução de Problemas

### Erro: "Permission denied"
- Verifique suas permissões no projeto
- Execute: `gcloud projects get-iam-policy monpec-sistema-rural`

### Erro: "Instance already exists"
- A instância do banco já existe
- Use `-SkipDatabase` para manter o banco existente

### Erro: "Build failed"
- Verifique se o `Dockerfile.prod` existe
- Verifique se o `requirements.txt` está atualizado
- Veja os logs: `gcloud builds list --limit=1`

### Erro: "Service deployment failed"
- Verifique as variáveis de ambiente
- Verifique a conexão com o Cloud SQL
- Veja os logs do serviço

### Migrações falhando
- Execute manualmente: `gcloud run jobs execute migrate-monpec --region us-central1 --wait`
- Verifique os logs: `gcloud run jobs executions list --job migrate-monpec --region us-central1`

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs do Cloud Build
2. Verifique os logs do Cloud Run
3. Verifique os logs do Cloud SQL
4. Verifique as permissões IAM

## ✅ Checklist Pós-Deploy

- [ ] Serviço Cloud Run criado e funcionando
- [ ] Migrações executadas com sucesso
- [ ] Senha do banco de dados alterada
- [ ] SECRET_KEY do Django atualizada
- [ ] Variáveis de ambiente configuradas
- [ ] Superusuário criado
- [ ] Domínio personalizado configurado (se necessário)
- [ ] Sistema acessível e funcionando

---

**⚠️ LEMBRE-SE**: Este script é destrutivo! Use com cuidado e sempre faça backup antes de executar.







