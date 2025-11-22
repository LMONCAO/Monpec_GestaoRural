# 🚀 Deploy para Atualizar Meta Tag do Google Search Console

## Situação Atual
- ✅ Meta tag já está no código local (`templates/site/landing_page.html`)
- ❌ Meta tag **NÃO** aparece no site em produção (Cloud Run)
- 🔄 **Precisa fazer novo deploy** para atualizar o site

---

## 📋 Passo a Passo

### 1️⃣ Garantir que o código está no GitHub

No seu computador local (PowerShell):

```powershell
# Navegar para a pasta do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Verificar status
git status

# Adicionar alterações (se houver)
git add .

# Fazer commit (se houver alterações)
git commit -m "Adicionar meta tag Google Search Console"

# Fazer push para GitHub
git push origin master
```

### 2️⃣ Fazer Deploy no Cloud Shell

1. **Acesse o Google Cloud Shell:**
   - Vá para: https://console.cloud.google.com/cloudshell
   - Ou clique no ícone do terminal no canto superior direito do console

2. **Execute o script de deploy:**

```bash
# Baixar o script
curl -O https://raw.githubusercontent.com/LMONCAO/Monpec_GestaoRural/master/deploy_completo_cloud_shell.sh

# Dar permissão de execução
chmod +x deploy_completo_cloud_shell.sh

# Executar o deploy
./deploy_completo_cloud_shell.sh
```

**OU** execute os comandos manualmente:

```bash
# Configurar projeto
gcloud config set project monpec-sistema-rural

# Clonar/Atualizar repositório
if [ -d "Monpec_GestaoRural" ]; then
    cd Monpec_GestaoRural
    git pull origin master || git pull origin main
else
    git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
    cd Monpec_GestaoRural
fi

# Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy (ajuste os valores conforme necessário)
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

### 3️⃣ Verificar se a Meta Tag Apareceu

Após o deploy, teste:

1. **Acesse a URL do Cloud Run:**
   ```
   https://monpec-29862706245.us-central1.run.app/
   ```

2. **Verifique o código-fonte:**
   - Pressione `Ctrl+U` (ou clique com botão direito → "Ver código-fonte")
   - Procure por: `google-site-verification`
   - Deve aparecer na linha 10 do `<head>`:
     ```html
     <meta name="google-site-verification" content="vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk" />
     ```

3. **Teste o arquivo HTML de verificação:**
   ```
   https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html
   ```
   Deve retornar: `google-site-verification: google40933139f3b0d469.html`

### 4️⃣ Verificar no Google Search Console

1. Acesse: https://search.google.com/search-console
2. Selecione a propriedade `monpec.com.br` (ou adicione se ainda não tiver)
3. Vá em **Configurações** → **Verificação de propriedade**
4. Escolha o método **Tag HTML** ou **Arquivo HTML**
5. O Google deve detectar automaticamente a meta tag ou arquivo

---

## ⚠️ Importante

- O deploy leva **10-20 minutos** (build + deploy)
- Após o deploy, pode levar alguns minutos para a meta tag aparecer (cache)
- Se não aparecer, limpe o cache do navegador (`Ctrl+Shift+Delete`)

---

## 🆘 Problemas?

Se a meta tag não aparecer após o deploy:

1. **Verifique se o template foi atualizado:**
   ```bash
   # No Cloud Shell, após clonar
   grep "google-site-verification" Monpec_GestaoRural/templates/site/landing_page.html
   ```

2. **Verifique se o build incluiu o template:**
   - Os templates devem estar na imagem Docker
   - Verifique os logs do build no Cloud Console

3. **Force atualização do cache:**
   - No navegador: `Ctrl+Shift+R` (recarregar sem cache)
   - Ou teste em modo anônimo

---

## ✅ Checklist Final

- [ ] Código local tem meta tag
- [ ] Código foi enviado para GitHub (`git push`)
- [ ] Deploy foi executado no Cloud Shell
- [ ] Build foi concluído com sucesso
- [ ] Deploy foi concluído com sucesso
- [ ] Meta tag aparece no código-fonte do site
- [ ] Arquivo HTML de verificação funciona
- [ ] Google Search Console detecta a verificação

