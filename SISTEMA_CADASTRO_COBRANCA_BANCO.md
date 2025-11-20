# 📋 Sistema de Cadastro, Cobrança e Banco de Dados - MONPEC

## 🎯 Visão Geral

O sistema MONPEC utiliza uma arquitetura **multi-tenancy** onde cada cliente possui:
- ✅ **Banco de dados dedicado** (isolamento total de dados)
- ✅ **Sistema de assinaturas** integrado com Stripe
- ✅ **Controle de usuários** por tenant
- ✅ **Cobrança automática** mensal

---

## 1️⃣ COMO FUNCIONA O CADASTRO DE USUÁRIOS

### **Estrutura de Usuários:**

```
┌─────────────────────────────────────────┐
│  User (Django Auth)                     │
│  - Usuário principal do sistema         │
│  - Login e autenticação                 │
└─────────────────────────────────────────┘
              │
              ├─ AssinaturaCliente (1:1)
              │  - Vincula User → Plano
              │  - Status da assinatura
              │  - IDs do Stripe
              │
              └─ TenantUsuario (1:N)
                 - Usuários dentro do tenant
                 - Perfis (Admin, Operador, Visualizador)
                 - Módulos liberados
```

### **Tipos de Usuários:**

#### **1. Usuário Principal (Assinante)**
- É o **dono da conta**
- Faz login e gerencia a assinatura
- Tem acesso total ao sistema
- Vinculado a `AssinaturaCliente`

#### **2. Usuários do Tenant (Colaboradores)**
- Usuários adicionais dentro da conta
- Criados pelo usuário principal
- Podem ter perfis diferentes:
  - **ADMIN**: Acesso total ao tenant
  - **OPERADOR**: Pode criar/editar dados
  - **VISUALIZADOR**: Apenas visualização

### **Como Cadastrar Usuários:**

#### **Opção 1: Via Interface Web (Recomendado)**

1. **Login como usuário principal**
2. **Acesse:** Menu → **Usuários do Sistema**
3. **Clique em:** "Adicionar Novo Usuário"
4. **Preencha:**
   - Nome completo
   - E-mail (único no sistema)
   - Perfil (Admin/Operador/Visualizador)
   - Módulos liberados (opcional)
   - Senha (ou deixe em branco para gerar automática)
5. **Salvar**

**O sistema irá:**
- ✅ Criar o usuário no Django
- ✅ Vincular ao tenant da assinatura
- ✅ Gerar senha temporária (se não informada)
- ✅ Enviar e-mail com credenciais (se configurado)

#### **Opção 2: Via Código Python**

```python
from gestao_rural.services import tenant_access
from gestao_rural.models import AssinaturaCliente

# Obter a assinatura
assinatura = AssinaturaCliente.objects.get(usuario=request.user)

# Criar novo usuário
resultado = tenant_access.criar_ou_atualizar_usuario(
    assinatura=assinatura,
    nome="João Silva",
    email="joao@fazenda.com",
    perfil="OPERADOR",
    modulos=["pecuaria", "financeiro", "projetos"],
    senha_definida="SenhaForte123!@#",
    criado_por=request.user,
)

print(f"Usuário criado: {resultado.usuario.username}")
print(f"Senha temporária: {resultado.senha_temporaria}")
```

### **Limite de Usuários:**

Cada plano tem um **limite máximo de usuários**:
- **Plano Básico**: 1 usuário
- **Plano Intermediário**: 3 usuários
- **Plano Avançado**: 10 usuários
- **Plano Empresarial**: Ilimitado

O sistema **bloqueia** a criação de novos usuários quando o limite é atingido.

---

## 2️⃣ COMO FUNCIONA A COBRANÇA

### **Integração com Stripe:**

O sistema utiliza **Stripe** para processar pagamentos de forma segura.

### **Fluxo de Assinatura:**

```
1. Usuário acessa página de planos
   ↓
2. Seleciona um plano
   ↓
3. Clica em "Assinar"
   ↓
4. Redirecionado para Stripe Checkout
   ↓
5. Preenche dados de pagamento
   ↓
6. Stripe processa pagamento
   ↓
7. Webhook notifica o sistema
   ↓
8. Sistema ativa assinatura
   ↓
9. Banco de dados é provisionado automaticamente
   ↓
10. Usuário recebe e-mail de boas-vindas
```

### **Modelos de Cobrança:**

#### **1. Assinatura Mensal (Recorrente)**
- Cobrança automática todo mês
- Renovação automática
- Cancelamento a qualquer momento

#### **2. Planos Disponíveis:**

Cada plano tem:
- **Nome**: Ex: "Plano Básico", "Plano Avançado"
- **Preço mensal**: Valor em R$
- **Stripe Price ID**: ID do produto no Stripe
- **Limite de usuários**: Quantos usuários podem acessar
- **Módulos disponíveis**: Quais funcionalidades estão liberadas

### **Status da Assinatura:**

- **PENDENTE**: Aguardando pagamento
- **ATIVA**: Assinatura ativa e funcionando
- **SUSPENSA**: Pagamento não processado
- **INADIMPLENTE**: Pagamento em atraso
- **CANCELADA**: Assinatura cancelada

### **Como Configurar Planos:**

#### **Via Admin Django:**

1. Acesse: `/admin/gestao_rural/planoassinatura/`
2. Clique em "Adicionar Plano"
3. Preencha:
   - Nome: "Plano Básico"
   - Slug: "plano-basico"
   - Descrição: "Ideal para pequenos produtores"
   - Stripe Price ID: `price_xxxxx` (criar no Stripe primeiro)
   - Preço mensal de referência: R$ 99,00
   - Ativo: ✅

#### **Via Código:**

```python
from gestao_rural.models import PlanoAssinatura

plano = PlanoAssinatura.objects.create(
    nome="Plano Básico",
    slug="plano-basico",
    descricao="Ideal para pequenos produtores",
    stripe_price_id="price_1234567890",
    preco_mensal_referencia=99.00,
    ativo=True,
)
```

### **Webhooks do Stripe:**

O sistema recebe eventos do Stripe via webhook:

- `checkout.session.completed`: Pagamento confirmado
- `customer.subscription.created`: Assinatura criada
- `customer.subscription.updated`: Assinatura atualizada
- `customer.subscription.deleted`: Assinatura cancelada
- `invoice.payment_failed`: Pagamento falhou

**Configurar Webhook:**
1. Acesse: Stripe Dashboard → Webhooks
2. Adicione endpoint: `https://seudominio.com/webhooks/stripe/`
3. Selecione eventos acima
4. Copie o **Webhook Secret**
5. Configure no `settings.py`: `STRIPE_WEBHOOK_SECRET`

---

## 3️⃣ COMO FUNCIONA O BANCO DE DADOS POR USUÁRIO

### **Arquitetura Multi-Tenancy:**

Cada assinatura possui um **banco de dados SQLite dedicado**:

```
/var/www/monpec/databases/
├── tenant_1.sqlite3    (Cliente 1)
├── tenant_2.sqlite3    (Cliente 2)
├── tenant_3.sqlite3    (Cliente 3)
└── ...
```

### **Banco Principal (Shared):**

Armazena dados compartilhados:
- `User` (usuários do sistema)
- `PlanoAssinatura` (planos disponíveis)
- `AssinaturaCliente` (assinaturas)
- `TenantWorkspace` (workspaces provisionados)

### **Banco do Tenant (Dedicado):**

Cada tenant tem seu próprio banco com:
- `ProdutorRural` (produtores do cliente)
- `Propriedade` (fazendas)
- `InventarioRebanho` (rebanho)
- `CustoFixo`, `CustoVariavel` (custos)
- `Financiamento` (dívidas)
- `ProjetoBancario` (projetos)
- E **todos os outros modelos** do sistema

### **Isolamento Total:**

✅ **Dados completamente isolados** entre clientes  
✅ **Sem risco de vazamento** de informações  
✅ **Backup individual** por cliente  
✅ **Performance independente** (um cliente não afeta outro)

### **Provisionamento Automático:**

Quando uma assinatura é ativada:

```python
from gestao_rural.services.provisionamento import provisionar_workspace

# 1. Cria registro do workspace
workspace = TenantWorkspace.objects.create(
    assinatura=assinatura,
    alias=f"tenant_{assinatura.pk}",
    caminho_banco="/var/www/monpec/databases/tenant_1.sqlite3",
)

# 2. Cria arquivo do banco
# 3. Executa migrations
# 4. Cria estrutura completa
# 5. Marca como ATIVO
```

### **Acesso ao Banco do Tenant:**

O sistema usa **Django Database Router** para direcionar queries:

```python
# Ao acessar dados do tenant
from gestao_rural.services.tenant_access import obter_assinatura_do_usuario

assinatura = obter_assinatura_do_usuario(request.user)
workspace = assinatura.workspace

# Todas as queries vão para o banco do tenant
propriedades = Propriedade.objects.all()  # Busca no tenant_1.sqlite3
```

### **Estrutura de Diretórios:**

```
/var/www/monpec/
├── manage.py
├── sistema_rural/
│   └── settings.py
├── gestao_rural/
│   ├── models.py
│   └── ...
├── databases/              # ← Bancos dos tenants
│   ├── tenant_1.sqlite3
│   ├── tenant_2.sqlite3
│   └── ...
└── db.sqlite3              # ← Banco principal (shared)
```

### **Backup e Restauração:**

#### **Backup Individual:**

```bash
# Backup do tenant 1
cp /var/www/monpec/databases/tenant_1.sqlite3 \
   /backups/tenant_1_$(date +%Y%m%d).sqlite3
```

#### **Backup de Todos:**

```bash
# Script de backup
for db in /var/www/monpec/databases/*.sqlite3; do
    cp "$db" "/backups/$(basename $db)_$(date +%Y%m%d).sqlite3"
done
```

#### **Restauração:**

```bash
# Restaurar tenant 1
cp /backups/tenant_1_20250101.sqlite3 \
   /var/www/monpec/databases/tenant_1.sqlite3
```

---

## 📊 RESUMO DO FLUXO COMPLETO

### **1. Novo Cliente:**

```
Cliente acessa site
  ↓
Escolhe plano
  ↓
Faz checkout no Stripe
  ↓
Pagamento confirmado
  ↓
Sistema cria:
  - User
  - AssinaturaCliente
  - TenantWorkspace
  - Banco de dados dedicado
  ↓
Cliente recebe e-mail com credenciais
  ↓
Cliente faz login e começa a usar
```

### **2. Adicionar Usuário:**

```
Admin acessa "Usuários"
  ↓
Preenche formulário
  ↓
Sistema verifica limite do plano
  ↓
Cria User + TenantUsuario
  ↓
Gera senha temporária
  ↓
Envia e-mail (opcional)
```

### **3. Renovação Mensal:**

```
Stripe cobra automaticamente
  ↓
Pagamento processado
  ↓
Webhook atualiza status
  ↓
Assinatura continua ATIVA
  ↓
Cliente continua usando normalmente
```

### **4. Cancelamento:**

```
Cliente cancela no Stripe
  ↓
Webhook notifica sistema
  ↓
Status muda para CANCELADA
  ↓
Banco permanece (para possível reativação)
  ↓
Após 90 dias: backup e exclusão (opcional)
```

---

## 🔧 CONFIGURAÇÕES NECESSÁRIAS

### **1. Variáveis de Ambiente:**

```bash
# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Django
SECRET_KEY=seu-secret-key-aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Banco de Dados
TENANT_DATABASE_DIR=/var/www/monpec/databases
```

### **2. Settings.py:**

```python
# settings.py
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

TENANT_DATABASE_DIR = Path(os.getenv('TENANT_DATABASE_DIR', 'databases'))
TENANT_DATABASE_DIR.mkdir(exist_ok=True)
```

### **3. URLs:**

```python
# urls.py
urlpatterns = [
    path('assinaturas/', include('gestao_rural.urls_assinaturas')),
    path('webhooks/stripe/', views_assinaturas.stripe_webhook),
    # ...
]
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Configurar Stripe (criar produtos e preços)
- [ ] Configurar webhook no Stripe
- [ ] Criar planos no admin Django
- [ ] Testar fluxo de checkout
- [ ] Testar provisionamento de banco
- [ ] Configurar e-mail de boas-vindas
- [ ] Configurar backup automático
- [ ] Documentar processo para suporte

---

## 📚 ARQUIVOS RELACIONADOS

- `gestao_rural/models.py` - Modelos de assinatura e tenant
- `gestao_rural/services/provisionamento.py` - Provisionamento de banco
- `gestao_rural/services/stripe_client.py` - Integração Stripe
- `gestao_rural/services/tenant_access.py` - Gerenciamento de usuários
- `gestao_rural/views_assinaturas.py` - Views de assinatura
- `gestao_rural/views_usuarios_tenant.py` - Views de usuários

---

**Última atualização:** Janeiro 2025






