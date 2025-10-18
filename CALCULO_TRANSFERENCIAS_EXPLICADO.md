# Como o Campo "Transferências" é Calculado

## 🎯 Explicação do Cálculo das Transferências

### **O que são Transferências?**
As transferências representam a **promoção de categoria** dos animais, ou seja, quando eles "envelhecem" e passam de uma categoria para outra (ex: Bezerros → Garrotes → Bois Magros).

## 📊 Lógica de Cálculo

### **1. Regras de Promoção Definidas**
O sistema possui regras automáticas de promoção:

#### **Para Fêmeas:**
- `Bezerras (0-12m)` → `Novilhas (12-24m)` (aos 12 meses)
- `Novilhas (12-24m)` → `Primíparas (24-36m)` (aos 24 meses)
- `Primíparas (24-36m)` → `Multíparas (>36m)` (aos 36 meses)

#### **Para Machos:**
- `Bezerros (0-12m)` → `Garrotes (12-24m)` (aos 12 meses)
- `Garrotes (12-24m)` → `Bois Magros (24-36m)` (aos 24 meses)

### **2. Processo de Cálculo**

#### **Passo 1: Identificar Animais para Promoção**
```python
# Para cada regra de promoção ativa
for regra in regras_promocao:
    categoria_origem = regra.categoria_origem
    categoria_destino = regra.categoria_destino
    
    # Quantidade a ser promovida = saldo atual da categoria origem
    quantidade_promocao = saldo_atual.get(categoria_origem, 0)
```

#### **Passo 2: Registrar Transferências**
```python
if quantidade_promocao > 0:
    # TRANSFERENCIA_SAIDA da categoria origem
    MovimentacaoProjetada.objects.create(
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_origem,
        quantidade=quantidade_promocao
    )
    
    # TRANSFERENCIA_ENTRADA na categoria destino
    MovimentacaoProjetada.objects.create(
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_destino,
        quantidade=quantidade_promocao
    )
```

#### **Passo 3: Atualizar Saldos**
```python
# Atualizar saldos após promoção
novo_saldo[categoria_destino] += quantidade_promocao
novo_saldo[categoria_origem] = 0  # Categoria origem fica zerada
```

## 🔍 Exemplo Prático dos Seus Dados

### **Cenário Analisado:**
```
Bezerras (0-12m): 350 → +0 → +0 → -0 → +0/-312 → -38 → -350 → 0
Bezerros (0-12m): 350 → +0 → +0 → -0 → +0/-312 → -38 → -350 → 0
```

### **Explicação das Transferências:**

#### **Bezerras (0-12m):**
- **Saldo Inicial**: 350
- **Transferências**: +0/-312
  - **+0**: Nenhuma transferência de entrada (não recebe animais de outras categorias)
  - **-312**: 312 bezerras foram promovidas para "Novilhas (12-24m)"
- **Saldo Final**: 0 (350 - 312 - 38 = 0)

#### **Bezerros (0-12m):**
- **Saldo Inicial**: 350
- **Transferências**: +0/-312
  - **+0**: Nenhuma transferência de entrada
  - **-312**: 312 bezerros foram promovidos para "Garrotes (12-24m)"
- **Saldo Final**: 0 (350 - 312 - 38 = 0)

#### **Garrotes (12-24m):**
- **Saldo Inicial**: 350
- **Transferências**: +312/-121
  - **+312**: Recebeu 312 garrotes promovidos de "Bezerros (0-12m)"
  - **-121**: 121 garrotes foram promovidos para "Bois Magros (24-36m)"
- **Saldo Final**: 312 (350 + 312 - 121 - 3 = 312)

## 📈 Fórmula de Cálculo

### **Transferências = Entradas - Saídas**

```python
transferencias_entrada = sum(movimentacoes where tipo='TRANSFERENCIA_ENTRADA')
transferencias_saida = sum(movimentacoes where tipo='TRANSFERENCIA_SAIDA')
transferencias_liquidas = transferencias_entrada - transferencias_saida
```

### **Saldo Final = Saldo Inicial + Nascimentos + Compras + Transferências Entrada - Vendas - Transferências Saída - Mortes**

```python
saldo_final = (
    saldo_inicial + 
    nascimentos + 
    compras + 
    transferencias_entrada - 
    vendas - 
    transferencias_saida - 
    mortes
)
```

## 🎯 Quando as Transferências Ocorrem?

### **Timing das Promoções:**
- **Frequência**: A cada virada de ano (final do ano)
- **Condição**: Apenas se `ano < anos - 1` (não no último ano da projeção)
- **Processo**: Automático baseado nas regras de promoção

### **Exemplo de Timeline:**
```
Ano 1:
- Bezerros (0-12m): 350 animais
- Final do Ano 1: 312 promovidos para Garrotes (12-24m)
- Resultado: 38 bezerros restantes + 312 garrotes

Ano 2:
- Garrotes (12-24m): 312 animais
- Final do Ano 2: 121 promovidos para Bois Magros (24-36m)
- Resultado: 191 garrotes restantes + 121 bois magros
```

## 🔧 Configuração das Regras

### **Arquivo**: `gestao_rural/management/commands/popular_categorias.py`

```python
regras_promocao = [
    # Fêmeas
    ('Bezerras (0-12m)', 'Novilhas (12-24m)', 12, 12),
    ('Novilhas (12-24m)', 'Primíparas (24-36m)', 24, 24),
    ('Primíparas (24-36m)', 'Multíparas (>36m)', 36, 36),
    
    # Machos
    ('Bezerros (0-12m)', 'Garrotes (12-24m)', 12, 12),
    ('Garrotes (12-24m)', 'Bois Magros (24-36m)', 24, 24),
]
```

## 🎉 Resumo

**As transferências são calculadas automaticamente pelo sistema baseado em regras de promoção de categoria, simulando o envelhecimento natural dos animais e sua progressão através das diferentes categorias do rebanho.**

**O formato "+X/-Y" significa:**
- **+X**: Animais que entraram na categoria (promovidos de categorias mais jovens)
- **-Y**: Animais que saíram da categoria (promovidos para categorias mais velhas)

**Isso garante que o rebanho evolua de forma realista, refletindo o ciclo de vida natural dos animais!** 🐄📊✨

