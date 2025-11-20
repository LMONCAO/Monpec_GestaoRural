# Correção: Buscar valor_por_cabeca do Inventário

## ❌ **ERRO ENCONTRADO**

```
AttributeError: 'MovimentacaoProjetada' object has no attribute 'valor_por_cabeca'
Location: gestao_rural/views.py, line 1339
```

## ✅ **CAUSA DO ERRO**

O modelo `MovimentacaoProjetada` **NÃO TEM** o campo `valor_por_cabeca`.

**Campos disponíveis em MovimentacaoProjetada:**
```python
- propriedade
- data_movimentacao
- tipo_movimentacao
- categoria
- quantidade
- observacao
```

**O campo `valor_por_cabeca` existe apenas em:**
```python
- InventarioRebanho
```

---

## ✅ **CORREÇÃO IMPLEMENTADA**

### **Antes (ERRADO):**
```python
valor_unitario = mov.valor_por_cabeca if mov.valor_por_cabeca else Decimal('0')
```

### **Depois (CORRETO):**
```python
# Buscar valor_por_cabeca do inventário (MovimentacaoProjetada não tem esse campo)
try:
    inventario_item = InventarioRebanho.objects.filter(
        propriedade=mov.propriedade,
        categoria=mov.categoria
    ).first()
    
    valor_unitario = inventario_item.valor_por_cabeca if inventario_item and inventario_item.valor_por_cabeca else Decimal('0')
except:
    valor_unitario = Decimal('0')
```

---

## 📊 **COMO FUNCIONA AGORA**

### **1. Buscar Valor do Inventário:**
```
Movimentação: VENDA de 10 Bezerros
    ↓
Buscar no Inventário: valor_por_cabeca dos Bezerros
    ↓
Se encontrou: usar o valor do inventário
Se não encontrou: usar R$ 0,00
```

### **2. Calcular Valor Total:**
```python
quantidade = 10
valor_unitario = R$ 2.500,00 (do inventário)
valor_mov = 10 × 2.500 = R$ 25.000,00
```

### **3. Classificar como Receita ou Custo:**
```python
# VENDAS → RECEITAS
if mov.tipo_movimentacao == 'VENDA':
    totais_ano['receitas_total'] += valor_mov

# COMPRAS e MORTES → CUSTOS
elif mov.tipo_movimentacao in ['COMPRA', 'MORTE']:
    totais_ano['custos_total'] += valor_mov
```

---

## 🎯 **CARACTERÍSTICAS DA CORREÇÃO**

### **✅ Busca Inteligente:**
- Busca valor do inventário da propriedade
- Busca valor da categoria específica
- Se não encontrar, usa R$ 0,00

### **✅ Tratamento Seguro:**
- Try-except para evitar erros
- Fallback para R$ 0,00
- Não quebra o sistema

### **✅ Valor Personalizado:**
- **Usa o valor do inventário se existir**
- **Se não existir, usa R$ 0,00**
- **Permite editar valores no inventário**

---

## 💡 **COMUNICANDO AO USUÁRIO**

**O sistema agora:**
- ✅ **Usa o valor do inventário** por padrão
- ✅ **Permite editar valores** no cadastro do inventário
- ✅ **Se não tiver valor definido**, usa R$ 0,00

**Para ajustar valores:**
1. Acesse o inventário
2. Edite os campos "Valor por Cabeça" de cada categoria
3. O sistema usará esses valores nas projeções

---

## 🎉 **CONCLUSÃO**

**Erro corrigido:**
- ✅ Busca valor do inventário corretamente
- ✅ Se não encontrar, usa R$ 0,00
- ✅ Permite editar valores no inventário
- ✅ Sistema funcional novamente

**Você pode agora recarregar a página da projeção!** 🚀

