# 🔧 Solução: Erro "workload_identity_provider" ou "credentials_json" no GitHub Actions

## ❌ Erro Encontrado

```
Error: google-github-actions/auth failed with: the GitHub Action workflow must specify exactly one of "workload_identity_provider" or "credentials_json"! If you are specifying input values via GitHub secrets, ensure the secret is being injected into the environment. By default, secrets are not passed to workflows triggered from forks, including Dependabot.
```

## 🔍 Causa do Problema

O secret `GCP_SA_KEY` **não está configurado** no GitHub ou está **vazio**. O workflow está tentando usar `credentials_json: ${{ secrets.GCP_SA_KEY }}`, mas como o secret não existe ou está vazio, a ação de autenticação falha.

## ✅ Solução Passo a Passo

### Opção 1: Usar Script Automatizado (Recomendado)

Execute o script que cria tudo automaticamente:

```powershell
.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1
```

Este script vai:
- ✅ Criar a Service Account no Google Cloud
- ✅ Configurar todas as permissões necessárias
- ✅ Gerar a chave JSON
- ✅ Mostrar instruções para adicionar no GitHub

### Opção 2: Configuração Manual

#### Passo 1: Criar Service Account no Google Cloud

1. **Acesse o Console do Google Cloud**: https://console.cloud.google.com/
2. **Selecione o projeto**: `monpec-sistema-rural`
3. **Vá para**: IAM & Admin > Service Accounts
4. **Clique em**: "Create Service Account"
5. **Preencha**:
   - Service account name: `github-actions-deploy`
   - Service account ID: `github-actions-deploy`
   - Description: `Service Account para GitHub Actions Deploy`
6. **Clique em**: "Create and Continue"

#### Passo 2: Atribuir Permissões

Adicione as seguintes roles:
- ✅ `Cloud Build Service Account`
- ✅ `Cloud Run Admin`
- ✅ `Service Account User`
- ✅ `Storage Admin` (para Container Registry)
- ✅ `Cloud SQL Client` (se usar Cloud SQL)

Clique em "Continue" e depois "Done".

#### Passo 3: Gerar Chave JSON

1. **Clique na Service Account** criada (`github-actions-deploy`)
2. **Vá para a aba**: "Keys"
3. **Clique em**: "Add Key" > "Create new key"
4. **Selecione**: JSON
5. **Clique em**: "Create"
6. **O arquivo JSON será baixado** automaticamente

#### Passo 4: Configurar Secret no GitHub

1. **Abra o arquivo JSON baixado** no Bloco de Notas (ou editor de texto)
2. **Copie TODO o conteúdo** (desde o `{` inicial até o `}` final)
3. **Acesse**: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions
4. **Clique em**: "New repository secret"
5. **Preencha**:
   - **Name**: `GCP_SA_KEY` (exatamente este nome, tudo maiúsculo)
   - **Secret**: Cole o conteúdo completo do arquivo JSON
6. **Clique em**: "Add secret"

#### Passo 5: Verificar Configuração

Execute o script de verificação:

```powershell
.\VERIFICAR_SECRET_GITHUB.ps1
```

Ou verifique manualmente em:
https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions

Você deve ver `GCP_SA_KEY` na lista de secrets (com ícone de olho fechado).

#### Passo 6: Testar Deploy

1. **Faça commit e push** das alterações
2. **Acesse**: https://github.com/LMONCAO/Monpec_GestaoRural/actions
3. **O workflow deve executar automaticamente**
4. **Verifique se o erro foi resolvido**

## 🔍 Verificações Adicionais

### Verificar se o Secret está Configurado

Você pode verificar usando o GitHub CLI:

```powershell
gh secret list --repo LMONCAO/Monpec_GestaoRural
```

Deve mostrar `GCP_SA_KEY` na lista.

### Verificar se o Workflow está Usando o Secret Corretamente

O workflow em `.github/workflows/deploy-gcp.yml` deve ter:

```yaml
- name: 🔐 Autenticação no Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}
```

✅ Isso já está configurado corretamente nos workflows.

## ⚠️ Problemas Comuns

### 1. Secret está vazio

**Sintoma**: O erro persiste mesmo após configurar o secret.

**Solução**: 
- Verifique se copiou TODO o conteúdo do JSON (incluindo `{` e `}`)
- Tente deletar e recriar o secret
- Certifique-se de que não há espaços extras no início/fim

### 2. Nome do secret está errado

**Sintoma**: O workflow ainda não encontra o secret.

**Solução**: 
- O nome deve ser exatamente: `GCP_SA_KEY` (tudo maiúsculo)
- Verifique a grafia (sem espaços, sem underscores extras)

### 3. Workflow executado a partir de fork

**Sintoma**: O erro menciona "secrets are not passed to workflows triggered from forks"

**Solução**: 
- Secrets não são passados para workflows de forks por segurança
- Execute o workflow na branch principal do repositório original

### 4. Permissões insuficientes na Service Account

**Sintoma**: O workflow autentica, mas falha em etapas posteriores.

**Solução**: 
- Verifique se a Service Account tem todas as permissões necessárias
- Execute novamente o script `CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1` para garantir todas as permissões

## 📚 Arquivos Relacionados

- `CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1` - Script para criar Service Account automaticamente
- `VERIFICAR_SECRET_GITHUB.ps1` - Script para verificar se o secret está configurado
- `.github/workflows/deploy-gcp.yml` - Workflow principal de deploy

## 🎉 Após Configurar

Depois de configurar o secret corretamente:

1. ✅ O workflow vai autenticar no Google Cloud
2. ✅ O build da imagem Docker vai executar
3. ✅ O deploy no Cloud Run vai funcionar
4. ✅ Você verá a URL do serviço no final do workflow

---

**Precisa de ajuda?** Verifique os logs do workflow em:
https://github.com/LMONCAO/Monpec_GestaoRural/actions

