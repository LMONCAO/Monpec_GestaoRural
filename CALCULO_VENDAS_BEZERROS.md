# 📊 CÁLCULO DE VENDAS DE BEZERROS E BEZERRAS

## 🔑 REGRA PRINCIPAL

**Bezerros e bezerras recém-nascidos NÃO são vendidos no mesmo ano do nascimento.**

---

## 📋 FLUXO DE CÁLCULO

### 1️⃣ **IDENTIFICAÇÃO DE CATEGORIAS**

O sistema identifica automaticamente as categorias de bezerros/bezerras:
- **Bezerro(o) 0-12 M** (machos)
- **Bezerro(a) 0-12 M** (fêmeas)

**Critério de identificação:**
- Nome da categoria contém "bezerro" ou "bezerra"
- E contém "0-12" (indicando idade de 0 a 12 meses)

---

### 2️⃣ **PROTEÇÃO DE RECÉM-NASCIDOS**

Para cada categoria de bezerro/bezerra:

```python
# 1. Contar quantos nasceram no ano atual
nascimentos_categoria = nascimentos_por_categoria.get(categoria_nome, 0)

# 2. Calcular quantidade disponível para venda
quantidade_disponivel = saldo_inicial - nascimentos_categoria

# 3. Garantir que não seja negativo
quantidade_disponivel = max(0, quantidade_disponivel)
```

**Exemplo:**
- Saldo Inicial de Bezerros: 1.620 cabeças
- Nascimentos no ano: 2.005 bezerros
- **Quantidade disponível para venda:** `max(0, 1620 - 2005) = 0`
- **Resultado:** Nenhum bezerro recém-nascido é vendido no mesmo ano

---

### 3️⃣ **CÁLCULO DA VENDA**

Após proteger os recém-nascidos, aplica o percentual configurado:

```python
# Se houver política configurada
quantidade_venda = quantidade_disponivel × (percentual_venda / 100)

# Exemplo com 20% de venda:
# quantidade_disponivel = 1.620 (sem nascimentos do ano)
# percentual_venda = 20%
# quantidade_venda = 1.620 × 0.20 = 324 bezerros
```

---

## 📈 EXEMPLO PRÁTICO

### Cenário: Bezerros 0-12 M

**Ano 2025:**
- **Saldo Inicial:** 1.620 bezerros
- **Nascimentos no ano:** 2.005 bezerros
- **Política de venda:** 20%

**Cálculo:**
1. Quantidade disponível = 1.620 - 2.005 = **0** (proteção ativa)
2. Quantidade a vender = 0 × 20% = **0 bezerros vendidos**

**Resultado:** Nenhum bezerro é vendido porque todos são recém-nascidos.

---

### Cenário: Bezerros do Ano Anterior

**Ano 2026:**
- **Saldo Inicial:** 1.580 bezerros (do ano anterior, já não são recém-nascidos)
- **Nascimentos no ano:** 2.035 bezerros (novos nascimentos)
- **Política de venda:** 20%

**Cálculo:**
1. Quantidade disponível = 1.580 - 2.035 = **0** (ainda protegidos)
2. Quantidade a vender = 0 × 20% = **0 bezerros vendidos**

**Resultado:** Ainda protegidos porque os nascimentos do ano superam o saldo inicial.

---

### Cenário: Bezerros com Saldo Maior que Nascimentos

**Ano 2027 (hipotético):**
- **Saldo Inicial:** 2.000 bezerros (do ano anterior)
- **Nascimentos no ano:** 1.500 bezerros (novos nascimentos)
- **Política de venda:** 20%

**Cálculo:**
1. Quantidade disponível = 2.000 - 1.500 = **500 bezerros** (não recém-nascidos)
2. Quantidade a vender = 500 × 20% = **100 bezerros vendidos**

**Resultado:** 100 bezerros são vendidos (apenas os que não são recém-nascidos).

---

## 🔍 DETALHES TÉCNICOS

### Identificação de Categorias

```python
categorias_bezerros = []
for categoria_nome in saldos_iniciais.keys():
    categoria_lower = categoria_nome.lower()
    if any(termo in categoria_lower for termo in ['bezerro', 'bezerra']) and \
       any(termo in categoria_lower for termo in ['0-12', '0-12m', '0-12 m']):
        categorias_bezerros.append(categoria_nome)
```

### Proteção Aplicada

```python
if categoria_nome in categorias_bezerros:
    nascimentos_categoria = nascimentos_por_categoria.get(categoria_nome, 0)
    if nascimentos_categoria > 0:
        # Subtrair os nascimentos do ano da quantidade disponível
        quantidade_disponivel = max(0, quantidade_disponivel - nascimentos_categoria)
        print(f"🚫 Excluindo {nascimentos_categoria} bezerros recém-nascidos da venda")
```

---

## ✅ REGRAS APLICADAS

1. ✅ **Proteção Total:** Bezerros recém-nascidos nunca são vendidos no mesmo ano
2. ✅ **Cálculo Correto:** Apenas bezerros do ano anterior podem ser vendidos
3. ✅ **Percentual Aplicado:** O percentual de venda é aplicado sobre a quantidade disponível (após excluir nascimentos)
4. ✅ **Valor Calculado:** O valor da venda usa o `valor_por_cabeca` do inventário ou política configurada

---

## 📝 OBSERVAÇÕES

- A proteção funciona **por categoria** (bezerros e bezerras separadamente)
- A proteção funciona **por ano** (nascimentos do ano atual são sempre protegidos)
- Bezerros do **ano anterior** podem ser vendidos normalmente
- O percentual de venda é aplicado sobre a **quantidade disponível** (não sobre o saldo total)

---

## 🎯 RESULTADO ESPERADO

Com a política de **20% de venda** de bezerros:
- **Ano 2025:** 0 bezerros vendidos (todos são recém-nascidos)
- **Ano 2026:** 0 bezerros vendidos (ainda protegidos)
- **Anos seguintes:** Apenas bezerros do ano anterior são vendidos (20% do disponível)

