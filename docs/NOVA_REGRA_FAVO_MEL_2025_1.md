# NOVA REGRA FAVO DE MEL - 2025

## REGRA IMPLEMENTADA

**O valor vendido de bezerras fêmeas (0-12 meses) vira compra de garrotes (machos 12-24 meses) para Favo de Mel**

---

## 1. COMO FUNCIONA

### Fluxo
1. **Venda de Bezerras Fêmeas**: Quando há venda de bezerras fêmeas (0-12 meses) em qualquer fazenda
2. **Cálculo do Valor**: Sistema calcula o valor total da venda
3. **Conversão em Compras**: O valor é convertido em compra de garrotes (machos 12-24 meses) para Favo de Mel
4. **Criação Automática**: A compra é criada automaticamente na mesma data da venda

### Fórmula
```
Quantidade de Garrotes = Valor Total da Venda / Preço do Garrote
```

**Preço do Garrote (referência)**: R$ 2.660,00 por cabeça

---

## 2. IMPLEMENTAÇÃO TÉCNICA

### Arquivo
`gestao_rural/configuracao_padrao_favo_mel.py`

### Função
`criar_compras_garrotes_de_vendas_bezerras(favo_mel, planejamento_favo)`

### Quando é Executada
- Automaticamente após gerar nova projeção para Favo de Mel
- Chamada dentro de `aplicar_configuracao_padrao_favo_mel()`

---

## 3. DETALHES DA IMPLEMENTAÇÃO

### Busca de Vendas
- Busca **TODAS** as vendas de bezerras fêmeas (0-12 meses) em **TODAS** as propriedades
- Categoria: `Bezerro(a) 0-12 F`
- Tipo: `VENDA`

### Cálculo do Valor
1. **Prioridade 1**: Usa `valor_total` da `VendaProjetada` se disponível
2. **Prioridade 2**: Calcula: `valor_por_kg × peso_medio_kg × quantidade`
3. **Fallback**: Usa valor padrão R$ 1.600,00 por bezerra (200kg × R$ 8,00/kg)

### Criação da Compra
- **Tipo**: `COMPRA`
- **Categoria**: `Garrote 12-24 M`
- **Propriedade**: Favo de Mel
- **Data**: Mesma data da venda
- **Quantidade**: Calculada baseada no valor
- **Valor**: Valor total da venda convertido

### Agrupamento
- Vendas na mesma data são agrupadas
- Uma única compra é criada por data com o valor total consolidado

---

## 4. EXEMPLO PRÁTICO

### Cenário
- **Venda**: 100 bezerras fêmeas em 15/07/2022
- **Valor por bezerra**: R$ 1.600,00
- **Valor total**: R$ 160.000,00

### Cálculo
```
Quantidade de Garrotes = R$ 160.000,00 / R$ 2.660,00
Quantidade de Garrotes = 60 garrotes (arredondado para baixo)
```

### Resultado
- **Compra criada**: 60 garrotes em 15/07/2022 para Favo de Mel
- **Valor total**: R$ 160.000,00
- **Valor por cabeça**: R$ 2.666,67 (ajustado)

---

## 5. OBSERVAÇÕES IMPORTANTES

### Preço do Garrote
- **Atual**: R$ 2.660,00 (valor de referência)
- **Ajustável**: Pode ser modificado no código se necessário
- **Localização**: `gestao_rural/configuracao_padrao_favo_mel.py` linha ~240

### Vendas Sem Valor
- Se a venda não tiver valor definido, usa valor padrão
- Valor padrão: R$ 1.600,00 por bezerra

### Compras Duplicadas
- Sistema verifica se já existe compra na mesma data
- Se existir, atualiza a quantidade e valor
- Se não existir, cria nova compra

---

## 6. INTEGRAÇÃO AUTOMÁTICA

### Aplicação Automática
- A regra é aplicada automaticamente após gerar nova projeção
- Não requer intervenção manual
- Funciona em conjunto com outras regras do Favo de Mel

### Ordem de Execução
1. Criar entradas da Canta Galo
2. Criar transferências para Girassol (480 a cada 90 dias)
3. **Criar compras de garrotes com valor das vendas de bezerras** ← NOVA REGRA

---

## 7. MANUTENÇÃO

### Para Modificar o Preço do Garrote
Editar `gestao_rural/configuracao_padrao_favo_mel.py`:
```python
preco_garrote = Decimal('2660.00')  # Alterar este valor
```

### Para Modificar o Valor Padrão da Bezerra
Editar a mesma função:
```python
valor_venda = Decimal('1600.00') * Decimal(str(venda.quantidade))  # Alterar 1600.00
```

---

## 8. TESTE

### Script de Teste
`testar_nova_regra_favo_mel.py`

### Verificação
`verificar_compras_favo_mel.py`

---

## 9. STATUS

✅ **IMPLEMENTADO E FUNCIONANDO**

A regra está ativa e será aplicada automaticamente quando houver vendas de bezerras fêmeas.

---

**ÚLTIMA ATUALIZAÇÃO**: 2025-11-28
**VERSÃO**: 1.0
**STATUS**: ATIVA
























