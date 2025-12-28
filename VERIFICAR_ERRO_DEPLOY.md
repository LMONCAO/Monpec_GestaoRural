# 🔍 Como Verificar o Erro do Deploy

Se o deploy continuar falhando, siga estes passos para identificar o problema:

## 1️⃣ Verificar Logs no Cloud Build Console

1. Acesse: https://console.cloud.google.com/cloud-build/builds?project=monpec-sistema-rural
2. Clique no build mais recente (com status FAILED)
3. Veja os logs detalhados para identificar o erro exato

## 2️⃣ Verificar Logs no GitHub Actions

1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/actions
2. Clique no workflow que falhou
3. Expanda o step "Build da imagem Docker"
4. Procure por mensagens de erro

## 3️⃣ Verificar Service Account

Execute localmente:
```powershell
.\VERIFICAR_CONFIGURACAO_COMPLETA.ps1
```

## 4️⃣ Verificar Secret no GitHub

Execute:
```powershell
.\VERIFICAR_SECRET_GITHUB.ps1
```

## 5️⃣ Erros Comuns e Soluções

### Erro: "Permission denied"
- **Solução**: Execute `.\CONFIGURAR_SERVICE_ACCOUNT_GCP.ps1` novamente

### Erro: "Secret not found"
- **Solução**: Configure o secret `GCP_SA_KEY` no GitHub

### Erro: "Dockerfile.prod not found"
- **Solução**: Certifique-se de que o arquivo existe na raiz do projeto

### Erro: "Rate limit exceeded"
- **Solução**: Aguarde alguns minutos e tente novamente

### Erro no build do Docker
- **Solução**: Verifique os logs no Cloud Build Console para ver o erro específico do Docker

## 6️⃣ Testar Build Localmente (Opcional)

Se quiser testar o build antes de fazer deploy:

```powershell
# Autenticar
gcloud auth login

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Fazer build local
gcloud builds submit --config=cloudbuild-config.yaml --substitutions=PROJECT_ID=monpec-sistema-rural,COMMIT_SHA=test
```

## 📋 Checklist de Verificação

- [ ] Service Account configurada
- [ ] Secret `GCP_SA_KEY` configurado no GitHub
- [ ] Arquivo `Dockerfile.prod` existe
- [ ] Arquivo `cloudbuild-config.yaml` existe
- [ ] APIs habilitadas no GCP (Cloud Build, Cloud Run, Container Registry)
- [ ] Permissões corretas na Service Account

## 🔗 Links Úteis

- **Cloud Build Console**: https://console.cloud.google.com/cloud-build/builds?project=monpec-sistema-rural
- **GitHub Actions**: https://github.com/LMONCAO/Monpec_GestaoRural/actions
- **Cloud Run Console**: https://console.cloud.google.com/run/detail/us-central1/monpec

