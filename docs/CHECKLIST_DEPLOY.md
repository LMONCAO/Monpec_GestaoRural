# ✅ CHECKLIST DE DEPLOY - MONPEC

## Status da Investigação

**Data**: 23/12/2025  
**Versão**: Pronta para deploy com ressalvas

---

## ✅ Verificações Realizadas

### 1. Erros de Sintaxe e Imports
- ✅ **Status**: Nenhum erro crítico encontrado
- ⚠️ **Avisos de Segurança** (não bloqueiam deploy):
  - `SECURE_HSTS_SECONDS` não configurado (OK para desenvolvimento)
  - `SECURE_SSL_REDIRECT` não está True (OK para desenvolvimento)
  - `SESSION_COOKIE_SECURE` não está True (OK para desenvolvimento)
  - `CSRF_COOKIE_SECURE` não está True (OK para desenvolvimento)
  - `DEBUG=True` em desenvolvimento (correto, será False em produção via `settings_gcp.py`)

### 2. Migrações
- ✅ **Status**: Todas as migrações aplicadas
- ✅ Migração 0078 aplicada (Cocho, Pastagem, Funcionario, etc.)
- ✅ Migração 0079 aplicada (AssinaturaCliente)

### 3. Arquivos Estáticos
- ✅ **Status**: staticfiles coletado
- ✅ Tamanho: 44.33 MB
- ✅ Pronto para deploy

### 4. URLs e Rotas
- ✅ **Status**: URLs verificadas
- ✅ Nenhum erro de rota encontrado

### 5. Dependências
- ✅ **Status**: requirements.txt presente
- ✅ Conflito de `openpyxl` corrigido (3.1.2 → >=3.1.5)
- ✅ Todas as dependências listadas

### 6. Configurações
- ✅ **Status**: Configurações corretas
- ✅ `MessageMiddleware` corrigido (ordem ajustada)
- ✅ `settings_gcp.py` configurado para produção
- ✅ `app.yaml` atualizado para Python 3.11

### 7. Problemas Conhecidos
- ✅ **Status**: Nenhum problema crítico
- ⚠️ **Observações**:
  - Vários `TODO` e `FIXME` no código (não bloqueiam deploy)
  - Logs de debug presentes (não afetam produção)

---

## ⚠️ Ações Necessárias ANTES do Deploy

### 1. Configurar Variáveis de Ambiente no GCP

Acesse: https://console.cloud.google.com/appengine/settings

**Variáveis Obrigatórias:**
```
DEBUG=False
SECRET_KEY=[gerar uma chave secreta forte]
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
PYTHONUNBUFFERED=1
ALLOWED_HOSTS=monpec-sistema-rural.rj.r.appspot.com,monpec.com.br,www.monpec.com.br
```

**Variáveis do Banco de Dados (se usar Cloud SQL):**
```
DB_NAME=[nome-do-banco]
DB_USER=[usuario]
DB_PASSWORD=[senha]
DB_HOST=[ip-ou-cloudsql-connection]
DB_PORT=5432
CLOUD_SQL_CONNECTION_NAME=[se-usar-cloud-sql]
```

**Variáveis de Pagamento (se usar):**
```
MERCADOPAGO_ACCESS_TOKEN=[token]
MERCADOPAGO_PUBLIC_KEY=[chave-publica]
STRIPE_PUBLIC_KEY=[se-usar-stripe]
STRIPE_SECRET_KEY=[se-usar-stripe]
```

**Variáveis de Email (se usar):**
```
EMAIL_HOST=[servidor-smtp]
EMAIL_PORT=587
EMAIL_HOST_USER=[usuario]
EMAIL_HOST_PASSWORD=[senha]
EMAIL_USE_TLS=True
```

### 2. Executar Migrações no App Engine

Após o deploy, execute via Cloud Shell:

```bash
# Conectar ao App Engine
gcloud app shell

# Executar migrações
python manage.py migrate

# Criar superusuário (se necessário)
python manage.py createsuperuser
```

### 3. Verificar Logs Após Deploy

```bash
# Ver logs em tempo real
gcloud app logs tail -s default

# Ver últimos 100 logs
gcloud app logs read -s default --limit=100
```

---

## ✅ Checklist Final de Deploy

### Antes do Deploy
- [x] Código sem erros críticos
- [x] Migrações aplicadas localmente
- [x] Arquivos estáticos coletados
- [x] requirements.txt atualizado
- [x] app.yaml configurado
- [x] Dockerfile criado
- [x] .gcloudignore configurado
- [ ] Variáveis de ambiente preparadas

### Durante o Deploy
- [ ] Executar: `gcloud app deploy`
- [ ] Aguardar conclusão do build
- [ ] Verificar se não há erros

### Após o Deploy
- [ ] Configurar variáveis de ambiente no GCP Console
- [ ] Executar migrações via Cloud Shell
- [ ] Criar superusuário (se necessário)
- [ ] Verificar logs para erros
- [ ] Testar acesso à URL: https://monpec-sistema-rural.rj.r.appspot.com
- [ ] Testar funcionalidades principais

---

## 🔧 Comandos Úteis

### Deploy
```bash
# Deploy normal
gcloud app deploy

# Deploy com nova versão
gcloud app deploy --version=$(date +%Y%m%d-%H%M%S)

# Deploy sem promover (testar primeiro)
gcloud app deploy --no-promote
```

### Verificar Status
```bash
# Ver versões
gcloud app versions list

# Ver detalhes
gcloud app describe

# Ver logs
gcloud app logs tail -s default
```

### Rollback (se necessário)
```bash
# Listar versões
gcloud app versions list

# Fazer rollback para versão anterior
gcloud app versions migrate [VERSION_ANTERIOR]
```

---

## ⚠️ Problemas Conhecidos e Soluções

### 1. 502 Bad Gateway
**Causa**: Aplicação não está iniciando ou variáveis de ambiente faltando  
**Solução**: Verificar logs e configurar variáveis de ambiente

### 2. Erro de Banco de Dados
**Causa**: Migrações não executadas ou credenciais incorretas  
**Solução**: Executar migrações e verificar credenciais

### 3. Erro de Arquivos Estáticos
**Causa**: collectstatic não executado  
**Solução**: Já executado localmente, mas verificar se está no deploy

### 4. Erro de Mensagens (MessageFailure)
**Causa**: Ordem do middleware incorreta  
**Solução**: ✅ Já corrigido em `settings.py`

---

## 📋 Resumo

### ✅ Pronto para Deploy
- Código verificado
- Migrações aplicadas
- Arquivos estáticos coletados
- Configurações corretas
- Dependências atualizadas

### ⚠️ Atenção Necessária
- Configurar variáveis de ambiente no GCP
- Executar migrações após deploy
- Verificar logs após deploy
- Testar funcionalidades principais

### 🚀 Próximos Passos
1. Configurar variáveis de ambiente
2. Fazer deploy: `gcloud app deploy`
3. Executar migrações
4. Testar sistema
5. Monitorar logs

---

**Status Final**: ✅ **PRONTO PARA DEPLOY** (com configurações necessárias)





























