# 📋 Resumo: Cadastro, Cobrança e Banco de Dados

## 🎯 COMO FUNCIONA EM 3 PASSOS

### 1️⃣ CADASTRO DE USUÁRIOS

**Estrutura:**
```
Usuário Principal (Assinante)
  └─ Pode criar N usuários colaboradores
     ├─ Perfil: Admin, Operador ou Visualizador
     └─ Limite: Depende do plano contratado
```

**Como cadastrar:**
1. Login como admin
2. Menu → "Usuários do Sistema"
3. Preencher: Nome, E-mail, Perfil, Senha
4. Salvar

**Limites por plano:**
- Básico: 1 usuário
- Intermediário: 3 usuários
- Avançado: 10 usuários
- Empresarial: Ilimitado

---

### 2️⃣ COBRANÇA (STRIPE)

**Fluxo:**
```
Cliente escolhe plano → Stripe Checkout → Pagamento → Assinatura ativa
```

**Planos:**
- Cada plano tem: Nome, Preço, Limite de usuários, Módulos
- Cobrança: Mensal automática
- Renovação: Automática

**Status:**
- ✅ ATIVA: Funcionando
- ⏳ PENDENTE: Aguardando pagamento
- ⚠️ SUSPENSA: Pagamento falhou
- ❌ CANCELADA: Cancelada

**Configurar:**
1. Criar produto no Stripe
2. Copiar Price ID
3. Criar plano no Django Admin
4. Configurar webhook

---

### 3️⃣ BANCO DE DADOS

**Arquitetura:**
```
Banco Principal (db.sqlite3)
  └─ Dados compartilhados:
     - Usuários
     - Assinaturas
     - Planos

Bancos dos Tenants (databases/)
  ├─ tenant_1.sqlite3 (Cliente 1)
  ├─ tenant_2.sqlite3 (Cliente 2)
  └─ tenant_3.sqlite3 (Cliente 3)
     └─ Dados do cliente:
        - Produtores
        - Propriedades
        - Rebanho
        - Custos
        - Projetos
```

**Isolamento:**
- ✅ Cada cliente tem seu próprio banco
- ✅ Dados completamente isolados
- ✅ Backup individual
- ✅ Provisionamento automático

**Quando criar:**
- Automaticamente quando assinatura é ativada
- Local: `/var/www/monpec/databases/tenant_X.sqlite3`

---

## 🔄 FLUXO COMPLETO

```
1. Cliente acessa site
   ↓
2. Escolhe plano e faz checkout
   ↓
3. Stripe processa pagamento
   ↓
4. Sistema cria:
   - User
   - AssinaturaCliente
   - TenantWorkspace
   - Banco dedicado
   ↓
5. Cliente recebe e-mail
   ↓
6. Cliente faz login
   ↓
7. Pode adicionar usuários colaboradores
   ↓
8. Todos usam o mesmo banco do tenant
```

---

## 📝 EXEMPLO PRÁTICO

**Cenário:** João quer usar o sistema

1. **João acessa:** `monpec.com.br/assinaturas`
2. **Escolhe:** Plano Avançado (R$ 299/mês, 10 usuários)
3. **Clica:** "Assinar Agora"
4. **Redirecionado:** Stripe Checkout
5. **Paga:** Cartão de crédito
6. **Sistema cria:**
   - Usuário: `joao@fazenda.com`
   - Assinatura: ATIVA
   - Banco: `tenant_5.sqlite3`
7. **João recebe:** E-mail com login e senha
8. **João faz login** e começa a usar
9. **João adiciona:** 3 colaboradores
10. **Todos acessam:** O mesmo banco `tenant_5.sqlite3`

---

## ⚙️ CONFIGURAÇÃO RÁPIDA

### 1. Criar Plano no Stripe:
```
Stripe Dashboard → Products → Add Product
- Nome: "Plano Básico"
- Preço: R$ 99,00/mês
- Copiar Price ID: price_xxxxx
```

### 2. Criar Plano no Django:
```
Admin → Planos de Assinatura → Adicionar
- Nome: "Plano Básico"
- Stripe Price ID: price_xxxxx
- Preço: R$ 99,00
- Limite usuários: 1
```

### 3. Configurar Webhook:
```
Stripe Dashboard → Webhooks → Add endpoint
- URL: https://monpec.com.br/webhooks/stripe/
- Events: checkout.session.completed, customer.subscription.*
- Copiar Secret: whsec_xxxxx
```

---

## 📚 DOCUMENTAÇÃO COMPLETA

Veja `SISTEMA_CADASTRO_COBRANCA_BANCO.md` para detalhes completos.







