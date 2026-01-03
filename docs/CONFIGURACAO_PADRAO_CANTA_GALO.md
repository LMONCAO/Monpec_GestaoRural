# CONFIGURAÇÃO PADRÃO - FAZENDA CANTA GALO

## REGRAS PERMANENTES DE PROJEÇÃO

Este documento descreve as regras **PERMANENTES** e **PADRÃO** para geração de projeções da Fazenda Canta Galo. Estas regras estão implementadas no código e **NÃO DEVEM SER ALTERADAS** sem autorização.

---

## 1. REGRA CRÍTICA: TRANSFERÊNCIAS DE VACAS DESCARTE

### Regra Principal
**NÃO TRANSFERIR SE SALDO FOR NEGATIVO OU ZERO**

### Implementação
- Sempre verificar saldo **REAL** após promoções antes de criar transferência
- Transferir apenas se houver saldo disponível suficiente
- Se saldo <= 0, **NÃO CRIAR** transferência

### Código Envolvido
- `gestao_rural/management/commands/gerar_projecao_completa_canta_galo.py`
  - Método: `_processar_transferencias`
  - Linha: ~773-783
  
- `gestao_rural/ia_movimentacoes_automaticas.py`
  - Método: `_gerar_transferencias_automaticas`
  - Linha: ~1072-1079

### Anos Permitidos
- **2022-2023**: Transferências para Invernada Grande
- **2024+**: Transferências para Favo de Mel

---

## 2. TAXA DE NATALIDADE

### Configuração Padrão
- **Taxa de Natalidade**: 80% das matrizes
- **Alteração**: Modificado de 70% para 80%

### Implementação
- `gestao_rural/management/commands/gerar_projecao_completa_canta_galo.py`
  - Método: `_processar_nascimentos`
  - Valor: `Decimal('0.80')`

---

## 3. POLÍTICAS DE VENDAS

### Bezerras Fêmeas
- **Percentual de Venda**: 30%
- **Alteração**: Modificado de 20% para 30%

### Bezerros Machos
- **Percentual de Venda**: 20%
- **Status**: Mantido

### Implementação
- `gestao_rural/management/commands/configurar_politicas_vendas_canta_galo.py`

---

## 4. ORDEM DE PROCESSAMENTO

### Sequência Correta
1. **Nascimentos** (julho a dezembro)
2. **Mortes** (mensal)
3. **Evoluções/Promoções** (ANTES das transferências)
4. **Vendas** (após evoluções)
5. **Compras** (após evoluções)
6. **Transferências** (janeiro, DEPOIS das promoções)

### Importante
- As promoções devem ser criadas **ANTES** das transferências
- O saldo após promoções deve ser verificado antes de transferir
- Transferências só ocorrem em **janeiro** de cada ano

---

## 5. VERIFICAÇÃO DE SALDO

### Função Utilizada
```python
calcular_rebanho_por_movimentacoes(propriedade, data_referencia)
```

### O que faz
- Calcula saldo REAL considerando:
  - Inventário inicial
  - Todas as movimentações até a data de referência
  - Promoções já criadas
  - Vendas, mortes e outras saídas

### Quando usar
- **SEMPRE** antes de criar uma transferência
- Para verificar saldo disponível real

---

## 6. CÓDIGO DE VALIDAÇÃO

### Exemplo de Validação
```python
# Calcular saldo REAL
saldos_reais = calcular_rebanho_por_movimentacoes(propriedade, data)
estoque_descarte_real = saldos_reais.get(categoria.nome, 0)

# REGRA PERMANENTE: NÃO TRANSFERIR SE SALDO <= 0
if estoque_descarte_real <= 0:
    return transferencias  # Não cria transferência

# Só transferir se houver saldo suficiente
quantidade_transferir = min(quantidade_desejada, estoque_descarte_real)
```

---

## 7. MANUTENÇÃO

### Ao Modificar o Código
1. **NUNCA** remover a verificação de saldo <= 0
2. **SEMPRE** usar `calcular_rebanho_por_movimentacoes` para saldo real
3. **SEMPRE** verificar saldo após promoções, não antes
4. **SEMPRE** manter a ordem de processamento correta

### Ao Gerar Nova Projeção
- O sistema automaticamente aplica estas regras
- Não é necessário executar scripts de correção para esta regra específica
- Se houver saldo negativo, verifique se a regra está sendo aplicada

---

## 8. HISTÓRICO DE ALTERAÇÕES

### 2025-01-XX
- **Implementada** regra permanente: Não transferir se saldo <= 0
- **Alterada** taxa de natalidade: 70% → 80%
- **Alterada** venda de bezerras: 20% → 30%
- **Corrigida** ordem de processamento: Promoções antes de transferências

---

## 9. CONTATO

Em caso de dúvidas ou necessidade de alteração destas regras, consulte a documentação do código ou o desenvolvedor responsável.

---

**ÚLTIMA ATUALIZAÇÃO**: 2025-01-XX
**VERSÃO**: 1.0
**STATUS**: ATIVA E PERMANENTE
























