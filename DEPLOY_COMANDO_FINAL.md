# 🚀 Deploy Final - Comando Corrigido (Resolve Problema do !)

## ⚠️ Problema Identificado

O bash está tentando expandir o `!` no `DB_PASSWORD=Monpec2025!` como comando de histórico.

## ✅ Solução: Use Aspas Simples

Copie e cole este comando **completo** no Cloud Shell:

```bash
cd ~/Monpec_GestaoRural && CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)") && SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())") && gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --platform managed --region us-central1 --allow-unauthenticated --add-cloudsql-instances $CONNECTION_NAME --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME='"$CONNECTION_NAME"',SECRET_KEY='"$SECRET_KEY" --memory=512Mi --cpu=1 --timeout=300 --max-instances=10
```

---

## 📋 Alternativa: Passo a Passo (Mais Seguro)

Execute um comando por vez:

### 1. Navegar para pasta:
```bash
cd ~/Monpec_GestaoRural
```

### 2. Obter connection name:
```bash
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
```

### 3. Gerar SECRET_KEY:
```bash
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
```

### 4. Deploy (com aspas simples para proteger o !):
```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME='"$CONNECTION_NAME"',SECRET_KEY='"$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

---

## 🔧 Se Preferir Usar o Script

O script foi transferido para `~/` (home). Mova para a pasta do projeto:

```bash
cd ~/Monpec_GestaoRural
mv ~/deploy_agora_corrigido.sh .
chmod +x deploy_agora_corrigido.sh
./deploy_agora_corrigido.sh
```

---

## 🔑 Diferença Importante

**❌ ERRADO (aspas duplas - bash expande !):**
```bash
--set-env-vars "DB_PASSWORD=Monpec2025!,..."
```

**✅ CORRETO (aspas simples - protege o !):**
```bash
--set-env-vars 'DB_PASSWORD=Monpec2025!,...'
```

Ou combine aspas simples com variáveis:
```bash
--set-env-vars '...DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME='"$CONNECTION_NAME"'...'
```

---

## ⏱️ Tempo Estimado
- Deploy: **2-3 minutos**

---

**Última atualização:** Novembro 2025














