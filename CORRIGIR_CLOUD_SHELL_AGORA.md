# 🔧 Corrigir Problemas no Cloud Shell

## Problemas Identificados:
1. ❌ Script sem permissão de execução
2. ❌ Git não configurado (user.email e user.name)
3. ❌ Tentativa de usar caminho Windows no Linux

---

## ✅ SOLUÇÃO RÁPIDA

### 1️⃣ Configurar Git no Cloud Shell

Execute estes comandos no Cloud Shell:

```bash
# Configurar Git (use SEU email e nome)
git config --global user.email "seu-email@gmail.com"
git config --global user.name "Seu Nome"

# Verificar configuração
git config --global --list
```

**Substitua:**
- `seu-email@gmail.com` pelo seu email do GitHub
- `Seu Nome` pelo seu nome

---

### 2️⃣ Dar Permissão ao Script de Deploy

```bash
# Navegar para a pasta do projeto
cd ~/Monpec_GestaoRural

# Dar permissão de execução ao script
chmod +x deploy_completo_cloud_shell.sh

# Verificar se o arquivo existe
ls -la deploy_completo_cloud_shell.sh
```

---

### 3️⃣ Executar o Deploy

```bash
# Executar o script
./deploy_completo_cloud_shell.sh
```

---

## ⚠️ IMPORTANTE: Push do Código

**NÃO faça commit/push no Cloud Shell!**

O código deve ser enviado do seu computador local (Windows) para o GitHub, e depois você faz `git pull` no Cloud Shell.

### No seu computador Windows (PowerShell):

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Verificar status
git status

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Adicionar meta tag Google Search Console"

# Fazer push
git push origin master
```

### Depois, no Cloud Shell:

```bash
cd ~/Monpec_GestaoRural
git pull origin master
./deploy_completo_cloud_shell.sh
```

---

## 🚀 COMANDOS COMPLETOS PARA CLOUD SHELL

Cole tudo de uma vez:

```bash
# 1. Configurar Git (AJUSTE OS VALORES!)
git config --global user.email "seu-email@gmail.com"
git config --global user.name "Seu Nome"

# 2. Ir para a pasta do projeto
cd ~/Monpec_GestaoRural

# 3. Atualizar código do GitHub
git pull origin master

# 4. Dar permissão ao script
chmod +x deploy_completo_cloud_shell.sh

# 5. Executar deploy
./deploy_completo_cloud_shell.sh
```

---

## 📋 Checklist

- [ ] Git configurado no Cloud Shell (user.email e user.name)
- [ ] Código enviado do Windows para GitHub (`git push`)
- [ ] Código atualizado no Cloud Shell (`git pull`)
- [ ] Script com permissão de execução (`chmod +x`)
- [ ] Deploy executado com sucesso

---

## 🆘 Se ainda der erro

Se o script `deploy_completo_cloud_shell.sh` não existir ou der erro, execute os comandos manualmente:

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        DB_NAME=monpec_db,\
        DB_USER=monpec_user,\
        DB_PASSWORD="Monpec2025!",\
        CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,\
        SECRET_KEY="$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

