# 🚀 COMECE AQUI - Google Cloud Platform

## ⚡ Deploy em 3 Passos

### 1️⃣ Autenticar e Configurar

```bash
# Autenticar
gcloud auth login

# Configurar projeto
gcloud config set project SEU-PROJETO-ID

# Ou definir variável de ambiente
export GCP_PROJECT=seu-projeto-id
```

### 2️⃣ Executar Deploy Automático

**Linux/Mac:**
```bash
chmod +x DEPLOY_GOOGLE_CLOUD_COMPLETO.sh
./DEPLOY_GOOGLE_CLOUD_COMPLETO.sh
```

**Windows:**
```powershell
.\DEPLOY_GOOGLE_CLOUD_COMPLETO.ps1
```

### 3️⃣ Configurar Variáveis de Ambiente

```bash
# Editar .env_producao com suas configurações
nano .env_producao

# Aplicar variáveis
chmod +x CONFIGURAR_VARIAVEIS_GCP.sh
./CONFIGURAR_VARIAVEIS_GCP.sh
```

## 📋 O Que Foi Feito

✅ **settings_gcp.py** - Corrigido para suportar HTTP e HTTPS  
✅ **Scripts de Deploy** - Automatizados para Cloud Run  
✅ **Migrações** - Script para aplicar automaticamente  
✅ **Variáveis de Ambiente** - Script para configurar facilmente  

## 🔍 Se Precisar de Ajuda

- **Guia Completo**: `GUIA_COMPLETO_GOOGLE_CLOUD.md`
- **Ver Logs**: `gcloud run services logs read monpec --region us-central1`
- **Status do Serviço**: `gcloud run services describe monpec --region us-central1`

## ⚙️ Variáveis Importantes

Antes do deploy, configure no `.env_producao`:

```env
SECRET_KEY=sua-chave-secreta
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=sua-senha
CLOUD_SQL_CONNECTION_NAME=projeto:regiao:instancia
```

---

**Pronto!** Execute o deploy e o sistema estará no ar! 🎉









