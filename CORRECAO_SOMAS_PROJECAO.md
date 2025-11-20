# Correção de Somas na Projeção

## Data: 27 de Outubro de 2025

## ✅ **PROBLEMAS CORRIGIDOS**

### 1. **Totais de Animais Incorretos** ❌

**Problema:**
- A função `preparar_dados_graficos` buscava campos que não existiam em `resumo_por_ano`
- Estrutura incorreta: `dados_ano.get('total_animais')` não existia

**Solução:** ✅
- Calcular fêmeas e machos por categoria no loop
- Somar todos os `saldo_final` para total_animais
- Classificar por sexo baseado no nome da categoria

---

### 2. **Receitas e Custos Não Calculados** ❌

**Problema:**
- Receitas e custos não eram calculados por ano
- Função `preparar_dados_graficos` tentava acessar campos inexistentes

**Solução:** ✅
- Iterar `movimentacoes_ano` para calcular receitas (VENDA) e custos (COMPRA, MORTE)
- Adicionar campos `receitas_total` e `custos_total` aos TOTAIS
- Incluir `lucro` nos TOTAIS

---

### 3. **Fêmeas e Machos Não Contados** ❌

**Problema:**
- Totais de fêmeas e machos não eram calculados

**Solução:** ✅
- Contar fêmeas e machos por categoria no loop
- Usar termos: 'fêmea', 'femea', 'bezerra', 'novilha', 'primípara', 'multípara', 'vaca'
- Usar termos: 'macho', 'bezerro', 'garrote', 'boi', 'touro'

---

## 📊 **CÓDIGO CORRIGIDO**

### Função `gerar_resumo_projecao_por_ano`:

```python
# Adicionados campos aos totais
totais_ano = {
    # ... campos existentes ...
    'receitas_total': Decimal('0.00'),
    'custos_total': Decimal('0.00'),
    'total_femeas': 0,
    'total_machos': 0,
}

# Calcular fêmeas e machos
for categoria_nome, dados in resultado_ano.items():
    # ... cálculos existentes ...
    
    # Contar fêmeas e machos
    nome_lower = categoria_nome.lower()
    if any(termo in nome_lower for termo in ['fêmea', 'femea', 'bezerra', ...]):
        totais_ano['total_femeas'] += dados['saldo_final']
    elif any(termo in nome_lower for termo in ['macho', 'bezerro', ...]):
        totais_ano['total_machos'] += dados['saldo_final']

# Calcular receitas e custos
for mov in movimentacoes_ano:
    valor_mov = mov.valor_total if mov.valor_total else Decimal('0')
    if mov.tipo_movimentacao == 'VENDA':
        totais_ano['receitas_total'] += valor_mov
    elif mov.tipo_movimentacao in ['COMPRA', 'MORTE']:
        totais_ano['custos_total'] += valor_mov

# Adicionar aos TOTAIS
resultado_ano['TOTAIS'] = {
    # ... campos existentes ...
    'receitas': totais_ano['receitas_total'],
    'custos': totais_ano['custos_total'],
    'lucro': totais_ano['receitas_total'] - totais_ano['custos_total'],
    'total_femeas': totais_ano['total_femeas'],
    'total_machos': totais_ano['total_machos'],
    'total_animais': totais_ano['saldo_final_total'],
}
```

### Função `preparar_dados_graficos`:

```python
# Simplificada para usar TOTAIS já calculados
for ano, dados_ano in resumo_por_ano.items():
    totais = dados_ano.get('TOTAIS', {})
    
    # Extrair dados dos TOTAIS
    total_animais = totais.get('total_animais', 0)
    total_femeas = totais.get('total_femeas', 0)
    total_machos = totais.get('total_machos', 0)
    receitas = float(totais.get('receitas', 0))
    custos = float(totais.get('custos', 0))
    lucro = receitas - custos
    
    dados['labels'].append(str(ano))
    dados['total_animais'].append(float(total_animais))
    dados['femeas'].append(float(total_femeas))
    dados['machos'].append(float(total_machos))
    dados['receitas'].append(float(receitas))
    dados['custos'].append(float(custos))
    dados['lucro'].append(float(lucro))
```

---

## 🎯 **RESULTADO**

### Agora os cálculos estão corretos:
- ✅ **Total de Animais**: Soma de todos os `saldo_final`
- ✅ **Fêmeas**: Contadas corretamente por categoria
- ✅ **Machos**: Contados corretamente por categoria
- ✅ **Receitas**: Soma de todas as VENDAS do ano
- ✅ **Custos**: Soma de todas as COMPRAS e MORTES do ano
- ✅ **Lucro**: Receitas - Custos

---

## 📄 **ARQUIVO MODIFICADO**

1. ✅ `gestao_rural/views.py` - Funções corrigidas

---

**Soma de tabelas corrigida e funcionando!** ✅

