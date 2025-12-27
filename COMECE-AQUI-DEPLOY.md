# 🚀 GUIA RÁPIDO - Deploy do Sistema MONPEC

## ⚡ Deploy em 3 Passos

### 1️⃣ Configure o Projeto (se ainda não fez)

```bash
# Linux/Mac/Cloud Shell
export GCP_PROJECT="seu-projeto-id"
gcloud config set project seu-projeto-id

# Windows PowerShell
$env:GCP_PROJECT = "seu-projeto-id"
gcloud config set project seu-projeto-id
```

### 2️⃣ Configure Variáveis (Importante!)

```bash
# Linux/Mac/Cloud Shell
export SECRET_KEY="sua-secret-key-django"
export DB_NAME="nome-do-banco"
export DB_USER="usuario"
export DB_PASSWORD="senha"
export CLOUD_SQL_CONNECTION_NAME="projeto:regiao:instancia"

# Windows PowerShell
$env:SECRET_KEY = "sua-secret-key-django"
$env:DB_NAME = "nome-do-banco"
$env:DB_USER = "usuario"
$env:DB_PASSWORD = "senha"
$env:CLOUD_SQL_CONNECTION_NAME = "projeto:regiao:instancia"
```

### 3️⃣ Execute o Deploy

```bash
# Linux/Mac/Cloud Shell
./deploy-gcp.sh

# Windows PowerShell
.\deploy-gcp.ps1
```

## ✅ Pronto! 

O script vai:
- ✅ Fazer build da imagem Docker
- ✅ Fazer deploy no Cloud Run
- ✅ Executar migrações automaticamente

## 🔧 Se Algo Der Errado

### Problema: "Job creation failed"

**Solução**: O script tenta criar/atualizar o job automaticamente. Se falhar, execute:

```bash
./executar-migracoes.sh
```

### Problema: "Build timeout"

**Solução**: O `.gcloudignore` já está otimizado. Se ainda acontecer:
1. Verifique sua conexão com a internet
2. Tente novamente (pode ser temporário)

### Problema: "Migration failed"

**Solução**: Execute as migrações manualmente:

```bash
# Criar job de migração
gcloud run jobs create migrate-monpec \
  --image gcr.io/SEU-PROJETO/monpec:latest \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --set-cloudsql-instances SEU-CONNECTION-NAME \
  --command python \
  --args "manage.py,migrate,--noinput"

# Executar
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

## 📚 Documentação Completa

Para mais detalhes, veja:
- **README-DEPLOY.md** - Documentação completa
- **RESUMO-DEPLOY-OTIMIZADO.md** - Resumo das melhorias

## 🎯 O Que Foi Otimizado?

✅ **Arquivos desnecessários excluídos** do build (build mais rápido)  
✅ **Jobs de migração** não causam mais conflitos  
✅ **Scripts organizados** e fáceis de usar  
✅ **Tratamento de erros** robusto  

---

**Dica**: Se você já tentou fazer deploy várias vezes antes, use os novos scripts! Eles resolvem os problemas anteriores.




