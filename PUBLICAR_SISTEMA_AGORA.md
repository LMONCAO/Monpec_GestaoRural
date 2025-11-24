# 🚀 Publicar Sistema - Guia Rápido

## ✅ Sincronização Concluída

O repositório local foi sincronizado com o GitHub:
- ✅ Alterações locais commitadas
- ✅ Conflitos resolvidos
- ✅ Push para GitHub concluído

**Repositório:** https://github.com/LMONCAO/Monpec_GestaoRural

---

## 📋 Publicar no Google Cloud Run

### Opção 1: Usar Script Automático (Recomendado)

1. **Acesse o Google Cloud Shell:**
   - Vá para: https://console.cloud.google.com/
   - Clique no ícone do Cloud Shell (terminal) no topo

2. **Clone/Atualize o repositório:**
   ```bash
   cd ~
   git clone https://github.com/LMONCAO/Monpec_GestaoRural.git || cd Monpec_GestaoRural && git pull origin master
   ```

3. **Execute o script de deploy:**
   ```bash
   cd ~/Monpec_GestaoRural
   chmod +x deploy_completo_corrigido.sh
   ./deploy_completo_corrigido.sh
   ```

4. **Aguarde o processo:**
   - Build: ~10-15 minutos
   - Deploy: ~2-3 minutos
   - **Total: ~15-20 minutos**

---

### Opção 2: Comandos Manuais

Se preferir executar passo a passo:

```bash
# 1. Atualizar código
cd ~/Monpec_GestaoRural
git pull origin master

# 2. Build da imagem
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# 3. Obter connection name do banco
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

# 4. Gerar SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

# 5. Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10
```

---

## ✅ Verificar Deploy

Após o deploy, verifique:

1. **Obter URL do serviço:**
   ```bash
   gcloud run services describe monpec --region us-central1 --format 'value(status.url)'
   ```

2. **Acessar no navegador:**
   - Abra a URL retornada
   - Verifique se a página carrega corretamente

3. **Verificar logs (se houver erro):**
   ```bash
   gcloud run services logs read monpec --region us-central1 --limit 50
   ```

---

## 🔧 Configurações do Deploy

- **Projeto:** monpec-sistema-rural
- **Região:** us-central1
- **Serviço:** monpec
- **Banco de Dados:** monpec-db (Cloud SQL)
- **Memória:** 512Mi
- **CPU:** 1
- **Timeout:** 300 segundos
- **Máx. Instâncias:** 10

---

## 📝 Notas Importantes

1. **Primeira vez:** Se for a primeira vez fazendo deploy, certifique-se de que:
   - O projeto está configurado no Google Cloud
   - O Cloud SQL está criado
   - As APIs necessárias estão habilitadas

2. **Atualizações futuras:** 
   - Faça alterações localmente
   - Commit e push para GitHub
   - Execute o script de deploy novamente

3. **Tempo de deploy:** O build da imagem Docker pode levar 10-15 minutos na primeira vez

---

## 🆘 Problemas Comuns

### Erro: "Permission denied"
```bash
# Verifique se está autenticado
gcloud auth login
gcloud config set project monpec-sistema-rural
```

### Erro: "Instance not found"
```bash
# Verifique se a instância do banco existe
gcloud sql instances list
```

### Erro: "Build failed"
- Verifique o Dockerfile
- Verifique se todas as dependências estão no requirements.txt
- Veja os logs: `gcloud builds log --stream`

---

**Última atualização:** Novembro 2025













