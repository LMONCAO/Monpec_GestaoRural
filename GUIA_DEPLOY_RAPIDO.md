# 🚀 Guia Rápido de Deploy - Sistema MONPEC

Este guia fornece instruções para fazer o deploy completo do sistema no Google Cloud Run.

## 📋 Pré-requisitos

1. **Google Cloud SDK (gcloud)** instalado e configurado
2. **Autenticação no Google Cloud**: `gcloud auth login`
3. **Projeto Google Cloud** criado: `monpec-sistema-rural`
4. **Credenciais configuradas** (opcional, mas recomendado):
   - Mercado Pago (Access Token e Public Key)
   - Email (se for usar envio de emails)

## 🎯 Deploy Rápido

### Opção 1: Windows (PowerShell)

```powershell
# 1. Configure as variáveis de ambiente (opcional, mas recomendado)
$env:DB_PASSWORD = "SuaSenhaSeguraAqui"
$env:SECRET_KEY = "SuaSecretKeyAqui"
$env:MERCADOPAGO_ACCESS_TOKEN = "SeuTokenAqui"
$env:MERCADOPAGO_PUBLIC_KEY = "SuaPublicKeyAqui"

# 2. Execute o script de deploy
.\DEPLOY_COMPLETO_FINAL.ps1
```

### Opção 2: Linux/Mac/Cloud Shell (Bash)

```bash
# 1. Configure as variáveis de ambiente (opcional, mas recomendado)
export DB_PASSWORD="SuaSenhaSeguraAqui"
export SECRET_KEY="SuaSecretKeyAqui"
export MERCADOPAGO_ACCESS_TOKEN="SeuTokenAqui"
export MERCADOPAGO_PUBLIC_KEY="SuaPublicKeyAqui"

# 2. Dar permissão de execução (se necessário)
chmod +x DEPLOY_COMPLETO_FINAL.sh

# 3. Execute o script de deploy
./DEPLOY_COMPLETO_FINAL.sh
```

## 📝 O que o script faz

O script `DEPLOY_COMPLETO_FINAL` executa automaticamente:

1. ✅ **Verifica autenticação** no Google Cloud
2. ✅ **Habilita APIs necessárias** (Cloud Build, Cloud Run, SQL Admin, etc.)
3. ✅ **Verifica/Cria instância Cloud SQL** (PostgreSQL)
4. ✅ **Cria/Atualiza banco de dados e usuário**
5. ✅ **Faz build da imagem Docker** usando `Dockerfile.prod`
6. ✅ **Configura todas as variáveis de ambiente** necessárias
7. ✅ **Faz deploy no Cloud Run** com todas as configurações
8. ✅ **Aplica migrações** do Django via Cloud Run Job
9. ✅ **Coleta arquivos estáticos** via Cloud Run Job
10. ✅ **Configura domínio personalizado** (opcional)
11. ✅ **Verifica status** e testa conectividade

## ⚙️ Configurações Importantes

### Variáveis de Ambiente Obrigatórias

O script usa valores padrão, mas **recomenda-se configurar**:

- `DB_PASSWORD`: Senha do banco de dados PostgreSQL
- `SECRET_KEY`: Chave secreta do Django (gerada automaticamente se não fornecida)

### Variáveis de Ambiente Opcionais (mas recomendadas)

- `MERCADOPAGO_ACCESS_TOKEN`: Token de acesso do Mercado Pago
- `MERCADOPAGO_PUBLIC_KEY`: Chave pública do Mercado Pago
- `MERCADOPAGO_WEBHOOK_SECRET`: Secret para webhooks do Mercado Pago
- `EMAIL_HOST_USER`: Usuário do servidor de email
- `EMAIL_HOST_PASSWORD`: Senha do servidor de email

### Configurações do Projeto

As configurações padrão estão no início dos scripts:

```powershell
# PowerShell
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DOMAIN = "monpec.com.br"
```

```bash
# Bash
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DOMAIN="monpec.com.br"
```

## 🔧 Configuração Manual (se necessário)

Se preferir fazer o deploy manualmente ou ajustar configurações:

### 1. Build da Imagem Docker

```bash
gcloud builds submit --config cloudbuild-config.yaml
```

### 2. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,SECRET_KEY=...,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=...,CLOUD_SQL_CONNECTION_NAME=..." \
  --add-cloudsql-instances "PROJECT_ID:REGION:INSTANCE_NAME" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --port 8080
```

### 3. Aplicar Migrações

```bash
# Criar job de migração
gcloud run jobs create migrate-monpec \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-cloudsql-instances "PROJECT_ID:REGION:INSTANCE_NAME" \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,SECRET_KEY=...,DB_NAME=...,DB_USER=...,DB_PASSWORD=..." \
  --command python \
  --args "manage.py,migrate,--noinput"

# Executar migração
gcloud run jobs execute migrate-monpec --region us-central1 --wait
```

### 4. Coletar Arquivos Estáticos

```bash
# Criar job de collectstatic
gcloud run jobs create collectstatic-monpec \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-cloudsql-instances "PROJECT_ID:REGION:INSTANCE_NAME" \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,SECRET_KEY=..." \
  --command python \
  --args "manage.py,collectstatic,--noinput"

# Executar collectstatic
gcloud run jobs execute collectstatic-monpec --region us-central1 --wait
```

## 🔐 Configurar Variáveis de Ambiente no Cloud Run

Se precisar atualizar variáveis de ambiente após o deploy:

```bash
gcloud run services update monpec \
  --region us-central1 \
  --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=SEU_TOKEN,MERCADOPAGO_PUBLIC_KEY=SUA_KEY"
```

## 👤 Criar Superusuário

Após o deploy, crie um superusuário:

```bash
gcloud run jobs create create-superuser \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-cloudsql-instances "PROJECT_ID:REGION:INSTANCE_NAME" \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,SECRET_KEY=...,DB_NAME=...,DB_USER=...,DB_PASSWORD=..." \
  --command python \
  --args "manage.py,createsuperuser" \
  --interactive

# Executar criação de superusuário
gcloud run jobs execute create-superuser --region us-central1
```

## 🌐 Configurar Domínio Personalizado

```bash
# Criar domain mapping
gcloud run domain-mappings create \
  --service monpec \
  --domain monpec.com.br \
  --region us-central1

gcloud run domain-mappings create \
  --service monpec \
  --domain www.monpec.com.br \
  --region us-central1

# Ver registros DNS necessários
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

Configure os registros DNS no seu provedor de domínio conforme indicado pelo comando acima.

## 📊 Verificar Status

```bash
# Ver status do serviço
gcloud run services describe monpec --region us-central1

# Ver logs em tempo real
gcloud run services logs tail monpec --region us-central1

# Ver URL do serviço
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

## 🐛 Troubleshooting

### Erro: "502 Bad Gateway"
- Verifique se o serviço está rodando
- Verifique os logs: `gcloud run services logs read monpec --region us-central1`
- Verifique se as variáveis de ambiente estão corretas

### Erro: "503 Service Unavailable"
- Verifique se há instâncias mínimas configuradas
- Verifique se o Cloud SQL está acessível
- Verifique os limites de quota do projeto

### Erro de Conexão com Banco de Dados
- Verifique se o Cloud SQL está na mesma região
- Verifique se o Cloud Run tem permissão para acessar o Cloud SQL
- Verifique se `CLOUD_SQL_CONNECTION_NAME` está correto
- Verifique se o usuário e senha estão corretos

### Arquivos Estáticos Não Carregam
- Verifique se o `collectstatic` foi executado
- Verifique se o WhiteNoise está configurado corretamente
- Verifique os logs do job de collectstatic

## 📚 Documentação Adicional

- [Guia Completo de Deploy](DEPLOY_GCP_COMPLETO.md)
- [Configuração do Banco de Dados](CONFIGURACAO_BANCO_DADOS.md)
- [Configuração do Mercado Pago](CONFIGURAR_MERCADO_PAGO.md)

## ✅ Checklist de Deploy

- [ ] Google Cloud SDK instalado e autenticado
- [ ] Projeto Google Cloud configurado
- [ ] Variáveis de ambiente configuradas (opcional)
- [ ] Script de deploy executado
- [ ] Migrações aplicadas com sucesso
- [ ] Arquivos estáticos coletados
- [ ] Serviço respondendo corretamente
- [ ] Domínio configurado (se aplicável)
- [ ] Superusuário criado
- [ ] Sistema testado e funcionando

---

**Última atualização:** 2025-01-27
