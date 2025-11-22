# 📋 COMANDOS PARA COPIAR E COLAR NO CLOUD SHELL

## ⚠️ IMPORTANTE: Primeiro faça push do código no Windows!

No seu computador Windows (PowerShell), execute:

```powershell
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
git add .
git commit -m "Adicionar meta tag Google Search Console"
git push origin master
```

**Só depois** execute os comandos abaixo no Cloud Shell.

---

## 🚀 COMANDOS PARA CLOUD SHELL

Copie e cole tudo de uma vez no Cloud Shell:

```bash
# 1. Configurar Git (AJUSTE O EMAIL E NOME!)
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

## 🔧 SE O SCRIPT NÃO EXISTIR

Se o arquivo `deploy_completo_cloud_shell.sh` não existir, execute estes comandos:

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Build da imagem
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

---

## ✅ APÓS O DEPLOY

1. Aguarde a mensagem "Deploy concluído!"
2. Anote a URL que aparecer (ex: `https://monpec-xxxxx-uc.a.run.app`)
3. Acesse a URL no navegador
4. Pressione `Ctrl+U` para ver o código-fonte
5. Procure por `google-site-verification` no `<head>`
6. Deve aparecer na linha 10!

---

## 🆘 PROBLEMAS COMUNS

### Erro: "Permission denied"
```bash
chmod +x deploy_completo_cloud_shell.sh
```

### Erro: "Git not configured"
```bash
git config --global user.email "seu-email@gmail.com"
git config --global user.name "Seu Nome"
```

### Erro: "No such file or directory"
```bash
# Verificar se a pasta existe
ls -la ~/Monpec_GestaoRural

# Se não existir, clonar:
git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
cd Monpec_GestaoRural
```

