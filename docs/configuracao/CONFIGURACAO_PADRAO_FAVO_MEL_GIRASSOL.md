# CONFIGURAÇÃO PADRÃO - TRANSFERÊNCIAS FAVO DE MEL -> GIRASSOL

## REGRAS PERMANENTES DE PROJEÇÃO

Este documento descreve as regras **PERMANENTES** e **PADRÃO** para transferências da Fazenda Favo de Mel para Fazenda Girassol.

---

## 1. REGRA PRINCIPAL: TRANSFERÊNCIAS

### Configuração Padrão
**480 cabeças a cada 90 dias (3 meses)**

### Implementação
- **Quantidade:** 480 cabeças por transferência
- **Intervalo:** 90 dias (3 meses)
- **Primeira transferência:** 01/04/2022
- **Datas:** 01/04, 01/07, 01/10, 01/01 (do ano seguinte)
- **Categoria:** Garrote 12-24 M

### Regra Crítica
**SEMPRE respeitar saldo disponível - NUNCA transferir se saldo for negativo ou zero**

### Código Envolvido
- `gestao_rural/management/commands/gerar_projecao_completa_canta_galo.py`
  - Método: `_processar_favo_mel`
  - Linha: ~941-960
  
- `corrigir_transferencias_favo_mel_para_girassol_com_saldo.py`
  - Quantidade: 480 (alterado de 350)
  - Intervalo: 3 meses (90 dias)

---

## 2. VERIFICAÇÃO DE SALDO

### Função Utilizada
```python
calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento)
```

### O que faz
- Calcula saldo REAL considerando:
  - Inventário inicial
  - Todas as movimentações até a data de referência
  - Transferências de entrada
  - Transferências de saída já criadas

### Quando usar
- **SEMPRE** antes de criar uma transferência
- Para verificar saldo disponível real

---

## 3. LÓGICA DE TRANSFERÊNCIA

### Exemplo de Validação
```python
# Calcular saldo REAL
saldo_disponivel = calcular_saldo_disponivel(favo_mel, categoria_garrote, data_transferencia, planejamento)

# REGRA PERMANENTE: NÃO TRANSFERIR SE SALDO <= 0
if saldo_disponivel <= 0:
    continue  # Pula para próxima data

# Quantidade a transferir: mínimo entre 480 e saldo disponível
quantidade_transferir = min(480, saldo_disponivel)

# Criar transferências (saída e entrada)
```

---

## 4. CRIAÇÃO DE TRANSFERÊNCIAS

### Transferência de Saída (Favo de Mel)
- Tipo: `TRANSFERENCIA_SAIDA`
- Quantidade: `min(480, saldo_disponivel)`
- Observação: Inclui saldo disponível e indica configuração padrão

### Transferência de Entrada (Girassol)
- Tipo: `TRANSFERENCIA_ENTRADA`
- Quantidade: Mesma da saída
- Observação: Indica origem e configuração padrão

---

## 5. DATAS DE TRANSFERÊNCIA

### Padrão
- **Abril:** 01/04
- **Julho:** 01/07
- **Outubro:** 01/10
- **Janeiro (ano seguinte):** 01/01

### Cálculo
```python
data_primeira_transferencia = date(2022, 4, 1)
intervalo_meses = 3  # 90 dias
data_transferencia = adicionar_meses(data_transferencia, intervalo_meses)
```

---

## 6. EXEMPLOS DE TRANSFERÊNCIAS

### 2022
- 01/04/2022: 480 cabeças (saldo disponível: 1180)
- 01/07/2022: 480 cabeças (saldo disponível: 700)
- 01/10/2022: 480 cabeças (saldo disponível: 570)
- 01/01/2023: 90 cabeças (saldo disponível: 90) - quantidade ajustada

### 2023
- 01/04/2023: 480 cabeças (saldo disponível: 1355)
- 01/07/2023: 480 cabeças (saldo disponível: 875)
- 01/10/2023: 395 cabeças (saldo disponível: 395) - quantidade ajustada
- 01/01/2024: 0 cabeças (saldo disponível: 0) - **NÃO TRANSFERE**

---

## 7. MANUTENÇÃO

### Ao Modificar o Código
1. **NUNCA** remover a verificação de saldo <= 0
2. **SEMPRE** usar `calcular_saldo_disponivel` para saldo real
3. **SEMPRE** usar `min(480, saldo_disponivel)` para quantidade
4. **SEMPRE** manter o intervalo de 90 dias (3 meses)

### Ao Gerar Nova Projeção
- **AUTOMÁTICO:** A configuração padrão é aplicada automaticamente após gerar uma nova projeção
- O sistema chama `aplicar_configuracao_padrao_favo_mel()` automaticamente na view
- **OPCIONAL:** Se necessário, execute manualmente:
  - `garantir_configuracao_favo_mel_apos_projecao.py` (script completo)
  - `EXECUTAR_APOS_PROJECAO_FAVO_MEL.bat` (script batch)

---

## 8. HISTÓRICO DE ALTERAÇÕES

### 2025-01-XX
- **Alterada** quantidade de transferência: 350 → 480 cabeças
- **Mantido** intervalo: 90 dias (3 meses)
- **Implementada** verificação obrigatória de saldo antes de transferir
- **Implementada** aplicação automática após gerar nova projeção
- **Criado** módulo `configuracao_padrao_favo_mel.py` para aplicação automática
- **Documentada** todas as regras e procedimentos

---

## 9. CONTATO

Em caso de dúvidas ou necessidade de alteração destas regras, consulte a documentação do código ou o desenvolvedor responsável.

---

**ÚLTIMA ATUALIZAÇÃO**: 2025-01-XX
**VERSÃO**: 1.0
**STATUS**: ATIVA E PERMANENTE

**CONFIGURAÇÃO PADRÃO**: 480 cabeças a cada 90 dias, respeitando saldo disponível

