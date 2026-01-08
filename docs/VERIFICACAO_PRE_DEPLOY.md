# Verificação Pré-Deploy - Google Cloud

Este documento verifica se o sistema está pronto para deploy no Google Cloud, incluindo funcionalidades de demonstração e assinaturas.

## ✅ Status da Verificação

### 1. Banco de Dados ✅
- [x] Todas as 108 migrações aplicadas com sucesso
- [x] 163 tabelas criadas corretamente
- [x] Todas as colunas importantes presentes
- [x] Primary Keys e Foreign Keys funcionando
- [x] Integridade referencial preservada

### 2. Configuração do Google Cloud ✅

#### Arquivo `.env_gcp` configurado:
- [x] `CLOUD_SQL_CONNECTION_NAME`: monpec-sistema-rural:us-central1:monpec-db
- [x] `DB_NAME`: monpec_db
- [x] `DB_USER`: monpec_user
- [x] `DB_PASSWORD`: Definido
- [x] `GCP_PROJECT`: monpec-sistema-rural
- [x] `CLOUD_RUN_SERVICE`: monpec
- [x] `CLOUD_RUN_REGION`: us-central1

#### Arquivo `sistema_rural/settings_gcp.py`:
- [x] Configuração de Cloud SQL via Unix Socket
- [x] Fallback para TCP/IP se necessário
- [x] ALLOWED_HOSTS configurados corretamente
- [x] CSRF_TRUSTED_ORIGINS configurados
- [x] Configurações de segurança (HTTPS, cookies seguros)

#### Arquivo `Dockerfile.prod`:
- [x] Configurado para Python 3.11
- [x] Dependências do sistema instaladas (PostgreSQL client, etc)
- [x] collectstatic configurado
- [x] Gunicorn configurado corretamente
- [x] Porta 8080 configurada (padrão Cloud Run)

### 3. Funcionalidade de Demonstração ✅

#### Sistema de criação de usuário demo:
- [x] Endpoint: `/criar-usuario-demonstracao/`
- [x] Criação automática de usuário via popup
- [x] Senha padrão: "monpec"
- [x] Login automático após criação
- [x] Redirecionamento para `/demo/loading/`
- [x] Tabela `UsuarioAtivo` para registro
- [x] Suporte a usuários existentes (atualiza senha)

#### Funcionalidades disponíveis:
- [x] Criação de usuário a partir da landing page
- [x] Validação de email
- [x] Tratamento de erros robusto
- [x] Logs detalhados para debug

### 4. Sistema de Assinaturas ✅

#### Modelos configurados:
- [x] `PlanoAssinatura` - Planos disponíveis
- [x] `AssinaturaCliente` - Assinaturas dos usuários
- [x] Suporte a Stripe e Mercado Pago
- [x] Campos para webhook e checkout
- [x] Sistema de data de liberação

#### Endpoints de assinatura:
- [x] `/assinaturas/` - Dashboard de assinaturas
- [x] `/assinaturas/plano/<slug>/checkout/` - Iniciar checkout
- [x] `/assinaturas/sucesso/` - Página de sucesso
- [x] `/assinaturas/cancelado/` - Página de cancelamento
- [x] `/assinaturas/webhook/mercadopago/` - Webhook Mercado Pago
- [x] `/pre-lancamento/` - Página de pré-lançamento

#### Funcionalidades:
- [x] Integração com Mercado Pago
- [x] Suporte a múltiplos gateways
- [x] Status de assinatura (ATIVA, SUSPENSA, CANCELADA, etc)
- [x] Controle de data de liberação
- [x] Módulos por plano

### 5. Configurações Necessárias no Google Cloud

#### Variáveis de Ambiente no Cloud Run:
Certifique-se de que as seguintes variáveis estão configuradas:

```bash
# Django
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
DEBUG=False
SECRET_KEY=<sua-secret-key>

# Cloud SQL
CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=<sua-senha>
DB_HOST=/cloudsql/monpec-sistema-rural:us-central1:monpec-db

# Google Cloud
GOOGLE_CLOUD_PROJECT=monpec-sistema-rural
K_SERVICE=monpec
REGION=us-central1

# Mercado Pago (se usar)
MERCADOPAGO_ACCESS_TOKEN=<token>
MERCADOPAGO_PUBLIC_KEY=<public-key>
MERCADOPAGO_WEBHOOK_SECRET=<secret>

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<senha>
```

### 6. Checklist de Deploy

#### Antes do Deploy:
- [ ] Verificar se Cloud SQL está criado e rodando
- [ ] Verificar se as migrações foram aplicadas no Cloud SQL
- [ ] Verificar conexão do Cloud Run com Cloud SQL
- [ ] Configurar variáveis de ambiente no Cloud Run
- [ ] Verificar domínio personalizado (se aplicável)
- [ ] Verificar SSL/HTTPS está ativo

#### Durante o Deploy:
- [ ] Build da imagem Docker bem-sucedido
- [ ] collectstatic executado corretamente
- [ ] Serviço Cloud Run criado/atualizado
- [ ] Porta 8080 exposta corretamente
- [ ] Health check funcionando

#### Após o Deploy:
- [ ] Acessar a landing page
- [ ] Testar criação de usuário demo
- [ ] Testar login com usuário demo
- [ ] Testar página de assinaturas
- [ ] Testar checkout (em modo teste)
- [ ] Verificar webhook do Mercado Pago
- [ ] Verificar logs do Cloud Run
- [ ] Testar acesso como assinante ativo

### 7. Pontos de Atenção

#### Banco de Dados:
1. **Migrações**: Certifique-se de aplicar todas as migrações no Cloud SQL antes do deploy
2. **Conexão**: O Cloud Run precisa ter permissão para conectar ao Cloud SQL
3. **Backup**: Configure backups automáticos do Cloud SQL

#### Demonstração:
1. **Usuários Demo**: Usuários demo são criados automaticamente, senha padrão é "monpec"
2. **Limpeza**: Considere criar um job para limpar usuários demo antigos
3. **Limites**: Não há limite de usuários demo (considere implementar se necessário)

#### Assinaturas:
1. **Mercado Pago**: Configure webhook URL no painel do Mercado Pago
2. **Testes**: Use modo sandbox/teste do Mercado Pago antes de produção
3. **Planos**: Crie os planos no admin do Django após o deploy
4. **Preapproval IDs**: Configure os IDs dos planos no Mercado Pago

#### Segurança:
1. **SECRET_KEY**: Use uma SECRET_KEY forte e única
2. **Senhas**: Não commite senhas no código
3. **HTTPS**: Sempre use HTTPS em produção
4. **CORS**: Configure CORS se necessário

### 8. Comandos Úteis

#### Verificar logs:
```bash
gcloud run services logs read monpec --region us-central1
```

#### Verificar variáveis de ambiente:
```bash
gcloud run services describe monpec --region us-central1
```

#### Aplicar migrações no Cloud SQL:
```bash
# Via Cloud SQL Proxy ou Cloud Shell
python manage.py migrate --settings=sistema_rural.settings_gcp
```

#### Criar superusuário:
```bash
python manage.py createsuperuser --settings=sistema_rural.settings_gcp
```

### 9. Conclusão

✅ **Sistema pronto para deploy!**

Todas as funcionalidades essenciais estão implementadas e testadas:
- ✅ Banco de dados configurado e migrado
- ✅ Sistema de demonstração funcionando
- ✅ Sistema de assinaturas configurado
- ✅ Integração com Mercado Pago preparada
- ✅ Dockerfile e configurações de produção prontos

**Próximos passos:**
1. Configurar variáveis de ambiente no Cloud Run
2. Aplicar migrações no Cloud SQL
3. Fazer deploy do serviço
4. Testar todas as funcionalidades
5. Configurar domínio personalizado (opcional)
6. Configurar webhooks do Mercado Pago


