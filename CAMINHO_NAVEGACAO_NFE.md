# Caminho de Navegação - Nota Fiscal Eletrônica

Este documento descreve os caminhos de navegação no sistema para acessar as funcionalidades de Nota Fiscal Eletrônica (NF-e).

## 📍 Caminhos Principais

### 1. **Emitir NF-e de Saída (Venda)**

**Caminho no Sistema:**
```
Dashboard → Módulos → Compras → Notas Fiscais → Emitir NF-e
```

**URL Direta:**
```
/propriedade/{propriedade_id}/compras/nota-fiscal/emitir/
```

**Passo a Passo:**
1. Acesse o **Dashboard** principal
2. Clique em **Módulos** (ou selecione a propriedade)
3. No menu lateral, expanda **Compras**
4. Clique em **Notas Fiscais**
5. Clique no botão **"Emitir NF-e"** (botão azul)

---

### 2. **Sincronizar NF-e Recebidas (Importação Automática)**

**Caminho no Sistema:**
```
Dashboard → Módulos → Compras → Notas Fiscais → Sincronizar NF-e Recebidas
```

**URL Direta:**
```
/propriedade/{propriedade_id}/compras/sincronizar-nfe-recebidas/
```

**Passo a Passo:**
1. Acesse o **Dashboard** principal
2. Clique em **Módulos** (ou selecione a propriedade)
3. No menu lateral, expanda **Compras**
4. Clique em **Notas Fiscais**
5. Clique no botão **"Sincronizar NF-e Recebidas"** (botão azul claro/info)

---

### 3. **Importar NF-e Manualmente (Upload XML)**

**Caminho no Sistema:**
```
Dashboard → Módulos → Compras → Notas Fiscais → Importar NF-e (XML)
```

**URL Direta:**
```
/propriedade/{propriedade_id}/compras/nota-fiscal/upload/
```

**Passo a Passo:**
1. Acesse o **Dashboard** principal
2. Clique em **Módulos** (ou selecione a propriedade)
3. No menu lateral, expanda **Compras**
4. Clique em **Notas Fiscais**
5. Clique no botão **"Importar NF-e (XML)"** (botão verde)

---

### 4. **Listar Todas as Notas Fiscais**

**Caminho no Sistema:**
```
Dashboard → Módulos → Compras → Notas Fiscais
```

**URL Direta:**
```
/propriedade/{propriedade_id}/compras/notas-fiscais/
```

**Passo a Passo:**
1. Acesse o **Dashboard** principal
2. Clique em **Módulos** (ou selecione a propriedade)
3. No menu lateral, expanda **Compras**
4. Clique em **Notas Fiscais**

---

### 5. **Visualizar Detalhes de uma NF-e**

**Caminho no Sistema:**
```
Dashboard → Módulos → Compras → Notas Fiscais → [Clique em uma NF-e]
```

**URL Direta:**
```
/propriedade/{propriedade_id}/compras/nota-fiscal/{nota_id}/
```

**Passo a Passo:**
1. Acesse a lista de **Notas Fiscais** (caminho acima)
2. Clique no ícone de **lupa** (🔍) ao lado da NF-e desejada

---

## 🗺️ Mapa Visual de Navegação

```
┌─────────────────────────────────────────────────────────┐
│                    DASHBOARD                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    MÓDULOS                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Compras ▼                                        │   │
│  │    ├─ Dashboard                                   │   │
│  │    ├─ Requisições                                 │   │
│  │    ├─ Nova Requisição                             │   │
│  │    ├─ Setores                                     │   │
│  │    ├─ Fornecedores                                │   │
│  │    └─ Notas Fiscais ◄─── AQUI                     │   │
│  │         ├─ Emitir NF-e                            │   │
│  │         ├─ Sincronizar NF-e Recebidas              │   │
│  │         ├─ Importar NF-e (XML)                    │   │
│  │         └─ [Lista de NF-e]                        │   │
│  │              └─ Detalhes da NF-e                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 📋 Menu Lateral - Módulo Compras

Quando você expande o módulo **Compras** no menu lateral, você verá:

- 📊 **Dashboard** - Visão geral do módulo
- 📝 **Requisições** - Lista de requisições de compra
- ➕ **Nova Requisição** - Criar nova requisição
- 🏢 **Setores** - Gerenciar setores
- 👥 **Fornecedores** - Lista de fornecedores
- 📄 **Notas Fiscais** - **← Acesse aqui para NF-e**

## 🎯 Acesso Rápido

### Do Dashboard de Compras

Se você estiver no **Dashboard de Compras**, você pode acessar diretamente:

1. **Card "Notas Fiscais"** → Clique para ver a lista
2. **Botões de ação rápida** (se disponíveis)

### URLs Completas

Substitua `{propriedade_id}` pelo ID da sua propriedade:

- **Lista:** `/propriedade/1/compras/notas-fiscais/`
- **Emitir:** `/propriedade/1/compras/nota-fiscal/emitir/`
- **Sincronizar:** `/propriedade/1/compras/sincronizar-nfe-recebidas/`
- **Importar:** `/propriedade/1/compras/nota-fiscal/upload/`
- **Detalhes:** `/propriedade/1/compras/nota-fiscal/123/` (123 = ID da NF-e)

## 💡 Dicas

1. **Atalho:** Se você já estiver no módulo de Compras, pode acessar diretamente pelo menu lateral
2. **Breadcrumbs:** Use os breadcrumbs (caminho no topo) para navegar de volta
3. **Botões:** Na lista de NF-e, há 3 botões principais:
   - 🔵 **Emitir NF-e** - Para criar NF-e de saída
   - 🔵 **Sincronizar NF-e Recebidas** - Para importar automaticamente
   - 🟢 **Importar NF-e (XML)** - Para fazer upload manual

## 🔐 Permissões

- Todas as funcionalidades de NF-e requerem login
- Você precisa ter permissão de acesso à propriedade
- A emissão de NF-e requer configuração da API (Focus NFe ou NFe.io)

