# Configurações de Projeção de Rebanho - Guia de Uso

## 📊 **PARÂMETROS ATUAIS CONFIGURADOS**

### ✅ **1. Taxa Reprodutiva (Natalidade)**
```python
taxa_natalidade_anual = 85.00%  # Padrão: 85%
```
**Como funciona:**
- Calcula quantos bezerros nascem por ano
- Baseado no número de matrizes (Multíparas + Primíparas)
- Conversão mensal automática: 85% / 12 = 7.08% ao mês

**Exemplo:**
```
30 matrizes × 7.08% mensal = 2 bezerros/mês
2 bezerros × 12 meses = 24 bezerros/ano (80% de 30)
```

---

### ✅ **2. Taxa de Mortalidade**

#### **Bezerros (0-12 meses):**
```python
taxa_mortalidade_bezerros_anual = 5.00%  # Padrão: 5%
```
**Como funciona:**
- Mortalidade mensal: 5% / 12 = 0.42% ao mês
- Aplicada em: Bezerros, Bezerras (0-12m)

#### **Adultos (>12 meses):**
```python
taxa_mortalidade_adultos_anual = 2.00%  # Padrão: 2%
```
**Como funciona:**
- Mortalidade mensal: 2% / 12 = 0.17% ao mês
- Aplicada em: Garrotes, Novilhas, Primíparas, Multíparas, Bois

**Exemplo:**
```
100 Bezerros × 0.42% = 0.4 mortes/mês → 5 mortes/ano
100 Adultos × 0.17% = 0.2 mortes/mês → 2 mortes/ano
```

---

### ✅ **3. Política de Vendas**

#### **Machos:**
```python
percentual_venda_machos_anual = 90.00%  # Padrão: 90%
```
**Como funciona:**
- Vende 90% dos machos disponíveis durante o ano
- Distribuído mensalmente conforme o perfil da fazenda

#### **Fêmeas:**
```python
percentual_venda_femeas_anual = 10.00%  # Padrão: 10%
```
**Como funciona:**
- Vende apenas 10% das fêmeas (manutenção de matrizes)
- Conserva 90% para reprodução

**Exemplo:**
```
50 Novilhos × 90% = 45 vendas/ano
50 Novilhas × 10% = 5 vendas/ano
```

---

### ✅ **4. Periodicidade**
```python
periodicidade = 'MENSAL'  # Padrão: Mensal
```
**Opções disponíveis:**
- `MENSAL`: Movimentações a cada mês
- `TRIMESTRAL`: Movimentações a cada 3 meses
- `SEMESTRAL`: Movimentações a cada 6 meses
- `ANUAL`: Movimentações uma vez por ano

---

### ✅ **5. Evolução Automática de Idade**
```python
# Mapeamento automático de categorias:
evolucoes = {
    'Bezerros (0-12m)': 'Garrotes (12-24m)',
    'Bezerras (0-12m)': 'Novilhas (12-24m)',
    'Garrotes (12-24m)': 'Bois (24-36m)',
    'Novilhas (12-24m)': 'Primíparas (24-36m)',
    'Primíparas (24-36m)': 'Multíparas (>36m)'
}
```

**Taxa de evolução:**
- 8.33% por mês (equivale a 100% em 12 meses)
- Baseada no **saldo final** após todas as movimentações

**Exemplo:**
```
100 Bezerros → 8.33% evoluem/mês = 8 animais
Após 12 meses: 92% dos animais evoluiram para a próxima categoria
```

---

## 🚀 **COMO UTILIZAR A PROJEÇÃO**

### **📋 Passo 1: Cadastrar Inventário Inicial**
```python
# Acesse: /propriedade/{id}/pecuaria/inventario/

# Exemplo de cadastro:
Propriedade: Fazenda Santa Rita
├─ Bezerros (0-12m): 20 animais
├─ Bezerras (0-12m): 18 animais
├─ Garrotes (12-24m): 15 animais
├─ Novilhas (12-24m): 12 animais
├─ Primíparas (24-36m): 8 animais
├─ Multíparas (>36m): 25 animais
└─ Touros: 2 animais

TOTAL: 100 animais
```

---

### **📊 Passo 2: Configurar Parâmetros**
```python
# Acesse: /propriedade/{id}/pecuaria/parametros/

# Parâmetros configurados (valores padrão):
Taxa de Natalidade: 85%
Mortalidade Bezerros: 5%
Mortalidade Adultos: 2%
Venda Machos: 90%
Venda Fêmeas: 10%
Periodicidade: Mensal
```

---

### **🎯 Passo 3: Gerar Projeção**
```python
# Acesse: /propriedade/{id}/pecuaria/projecao/

# Escolha o período:
Anos de Projeção: 5 anos

# Clique em "Gerar Projeção"
```

---

## 🔄 **COMO A PROJEÇÃO FUNCIONA**

### **📅 Processo Mensal Automático:**

#### **Durante o mês:**
```
📆 Mês 01/2025

Saldo Inicial: 100 animais
├─ 👶 Nascimentos: +8 animais (85% natalidade em 30 matrizes)
├─ 💀 Mortes: -0.4 animais (5% mortalidade bezerros, 2% adultos)
├─ 💰 Vendas: -10 animais (90% machos, 10% fêmeas)
└─ 🛒 Compras: +2 animais (reposição)

Saldo Final: 99.6 animais
```

#### **Final do mês (Evolução):**
```
🔄 Evolução de Idade:

93 Bezerros (0-12m) → 8 animais evoluem (8.33%)
├─ PROMOCAO_SAIDA: -8 Bezerros
└─ PROMOCAO_ENTRADA: +8 Garrotes (12-24m)

15 Garrotes (12-24m) → 1 animal evolui
├─ PROMOCAO_SAIDA: -1 Garrote
└─ PROMOCAO_ENTRADA: +1 Boi (24-36m)

... assim por diante para todas as categorias
```

---

### **📊 Exemplo de Projeção (1 Mês):**

#### **Entradas:**
```
Saldo Inicial: 100 animais
├─ Nascimentos: +8 bezerros
├─ Compras: +2 novilhas
└─ Transferências: +1 bezerra

Total Entradas: +11 animais
```

#### **Saídas:**
```
├─ Vendas: -10 animais
│  ├─ Machos: -9 animais (90% de 10)
│  └─ Fêmeas: -1 animal (10% de 10)
├─ Mortes: -0.5 animais
└─ Transferências: -0.2 animais

Total Saídas: -10.7 animais
```

#### **Evolução Final:**
```
Saldo Final: 100 + 11 - 10.7 = 100.3 animais

EVOLUÇÃO DE IDADE:
50 Bezerros → 4 evoluem para Garrotes
30 Garrotes → 2 evoluem para Bois
20 Novilhas → 2 evoluem para Primíparas

NOVO SALDO:
├─ 46 Bezerros (0-12m)
├─ 28 Garrotes (12-24m) +4 (evoluiram de bezerros) = 32
├─ 20 Bois (24-36m) +2 (evoluíram de garrotes) = 22
├─ 22 Primíparas (24-36m) +2 (evoluíram de novilhas) = 24
└─ ... demais categorias
```

---

## 🎯 **TIPOS DE MOVIMENTAÇÕES GERADAS**

### **1. NASCIMENTO**
```python
Tipo: NASCIMENTO
Categoria: Bezerros, Bezerras
Quantidade: Calculado pela natalidade
Valor: R$ 0 (sem custo, é cria própria)
```

### **2. MORTE**
```python
Tipo: MORTE
Categoria: Qualquer
Quantidade: Calculado pela mortalidade
Valor: Custo de reposição
```

### **3. VENDA**
```python
Tipo: VENDA
Categoria: Machos 90%, Fêmeas 10%
Quantidade: Calculado pela política de vendas
Valor: Receita de venda
```

### **4. COMPRA**
```python
Tipo: COMPRA
Categoria: Conforme perfil da fazenda
Quantidade: Baseado em estratégia de reposição
Valor: Custo de aquisição
```

### **5. PROMOCAO_SAIDA / PROMOCAO_ENTRADA**
```python
Tipo: PROMOCAO
Categoria: Evolução automática de idade
Quantidade: 8.33% dos animais/mês
Valor: R$ 0 (apenas mudança de categoria)
```

### **6. TRANSFERENCIA**
```python
Tipo: TRANSFERENCIA_SAIDA / TRANSFERENCIA_ENTRADA
Categoria: Entre fazendas do mesmo produtor
Quantidade: Configurado pelo usuário
Valor: R$ 0 (movimentação interna)
```

---

## 📈 **RESULTADOS DA PROJEÇÃO**

### **📊 Resumo por Ano:**
```
Ano 1:
├─ Saldo Inicial: 100 animais
├─ Nascimentos: 96 bezerros
├─ Mortes: 7 animais
├─ Vendas: 180 animais
├─ Compras: 50 animais
├─ Evolução: 85 animais mudaram de categoria
└─ Saldo Final: 134 animais (+34%)

Ano 2:
├─ Saldo Inicial: 134 animais
├─ Nascimentos: 129 bezerros
├─ Mortes: 9 animais
├─ Vendas: 240 animais
├─ Compras: 60 animais
├─ Evolução: 115 animais mudaram de categoria
└─ Saldo Final: 179 animais (+34%)

... e assim por diante por 5 anos
```

---

### **💰 Análise Financeira:**
```
Ano 1:
├─ Receitas (Vendas): R$ 450.000,00
├─ Custos (Compras + Mortes): R$ 280.000,00
└─ Lucro: R$ 170.000,00

Ano 2:
├─ Receitas (Vendas): R$ 600.000,00
├─ Custos (Compras + Mortes): R$ 350.000,00
└─ Lucro: R$ 250.000,00

... evolução ao longo dos 5 anos
```

---

## ✅ **CHECKLIST DE CONFIGURAÇÃO**

### **Antes de Gerar a Projeção:**
- ✅ Inventário cadastrado (animais iniciais)
- ✅ Parâmetros configurados (natalidade, mortalidade)
- ✅ Política de vendas definida
- ✅ Periodicidade escolhida
- ✅ Categorias de animais cadastradas

### **Após Gerar a Projeção:**
- ✅ Revisar nascimentos gerados
- ✅ Verificar se mortalidade está correta
- ✅ Analisar se vendas são realistas
- ✅ Conferir se rebanho está crescendo
- ✅ Validar se receita é suficiente

---

## 🎉 **PRONTO PARA USAR!**

### **Sistema Completo:**
- ✅ Configurações definidas
- ✅ Parâmetros realistas (85% natalidade, 5% mortalidade bezerros, 2% adultos)
- ✅ Evolução automática baseada no saldo final
- ✅ Política de vendas integrada
- ✅ Histórico de movimentações
- ✅ Análise financeira automática

**Você já pode gerar projeções de rebanho com esses parâmetros!** 🚀

### **Como começar:**
1. Acesse: `/propriedade/{id}/pecuaria/inventario/`
2. Cadastre os animais iniciais
3. Configure os parâmetros (ou use os padrões)
4. Acesse: `/propriedade/{id}/pecuaria/projecao/`
5. Clique em "Gerar Projeção" e escolha o período (5 anos recomendado)
6. Visualize os resultados e análises financeiras

**Sistema pronto e funcional!** ✅

