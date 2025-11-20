# 🔧 CORREÇÕES CRÍTICAS - SISTEMA MONPEC

## 📋 PROBLEMAS IDENTIFICADOS

### **1. ERRO: valor_total como campo**
```
Cannot resolve keyword 'valor_total' into field
```

**Problema:** Código tenta usar `.valor_total` como campo do banco, mas é uma `@property` calculada.

**Local:** `gestao_rural/views_projetos_bancarios.py:41`
```python
'valor_total': sum(item.valor_total for item in inventario if item.valor_total)
```

**Solução:**
```python
# ANTES (errado):
'valor_total': sum(item.valor_total for item in inventario if item.valor_total)

# DEPOIS (correto):
'valor_total': sum(
    item.quantidade * item.valor_por_cabeca 
    for item in inventario
)
```

---

### **2. ERRO: Tipo Decimal vs Float**
```
unsupported operand type(s) for -: 'decimal.Decimal' and 'float'
```

**Problema:** Mistura de tipos ao fazer operações.

**Solução:**
```python
from decimal import Decimal

# ANTES:
valor = 100.0  # float
resultado = Decimal(valor) - 50.0  # ERRO

# DEPOIS:
valor = Decimal('100.0')
resultado = valor - Decimal('50.0')
```

---

### **3. ERRO: Campo valor_depreciado**
```
Cannot resolve keyword 'valor_depreciado' into field
```

**Problema:** Campo que não existe no modelo BemImobilizado.

**Local:** `gestao_rural/views_imobilizado.py:26`

**Solução:** Usar propriedade calculada ou método existente.

---

## 🛠️ ARQUIVOS PARA CORRIGIR

### **1. gestao_rural/views_projetos_bancarios.py**

**Linha 41:** Usar cálculo manual em vez de property
```python
# ANTES:
'valor_total': sum(item.valor_total for item in inventario if item.valor_total),

# DEPOIS:
'valor_total': sum(
    Decimal(str(item.quantidade)) * Decimal(str(item.valor_por_cabeca)) 
    for item in inventario
),
```

### **2. gestao_rural/views_capacidade_pagamento.py**

**Problema:** Mistura de tipos Decimal com float

**Solução:** Converter tudo para Decimal
```python
from decimal import Decimal

# Encontrar todas as operações e converter
receita_mensal = Decimal(str(receita_anual)) / Decimal('12')
custos_mensais = Decimal(str(custo_total)) / Decimal('12')
```

### **3. gestao_rural/views_imobilizado.py**

**Linha 26:** Corrigir campo depreciado
```python
# ANTES:
valor_depreciado = bens.aggregate(Sum('valor_depreciado'))

# DEPOIS:
valor_depreciado = sum(
    b.valor_aquisicao - b.depreciacao_acumulada 
    for b in bens
)
```

---

## 🎯 PLANO DE CORREÇÃO

### **PASSO 1:** Corrigir cálculo de valor_total
- Trocar todos os usos de `.valor_total` por cálculo manual
- Padronizar para uso de Decimal

### **PASSO 2:** Padronizar tipos numéricos
- Converter todas as operações para Decimal
- Adicionar conversões explícitas

### **PASSO 3:** Corrigir campos inexistentes
- Verificar modelos
- Usar properties ou métodos calculados

### **PASSO 4:** Testar correções
- Executar sistema
- Verificar se erros desapareceram

---

## 📝 RESUMO

| Erro | Local | Severidade | Solução |
|------|-------|------------|---------|
| valor_total como campo | views_projetos_bancarios.py:41 | 🔴 Alta | Calcular manualmente |
| Decimal vs Float | views_capacidade_pagamento.py | 🔴 Alta | Padronizar tipos |
| valor_depreciado | views_imobilizado.py:26 | 🔴 Alta | Usar property ou método |

**TODAS AS CORREÇÕES DEVEM SER FEITAS JÁ!**

